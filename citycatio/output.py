import netCDF4 as nc
import pandas as pd
import os
import numpy as np
from osgeo import osr
from datetime import datetime
import rasterio as rio
import click


datatype = "f4"
fill_value = nc.default_fillvals[datatype]


def to_netcdf(
        in_path, 
        out_path=None,
        start_time: datetime = datetime(1, 1, 1),
        srid: int = None,
        attributes: dict = None):
    """Converts CityCAT results to a netCDF file

    Args:
        in_path: path where CityCAT results files are located
        out_path: path to create netCDF file
            If not given then in_path will be used with an appended extension
        start_time: Start time to use when creating time steps
        srid: EPSG Spatial Reference System Identifier of results files
        attributes: Dictionary of key-value pairs to store as netCDF attributes
            Keys must begin with an alphabetic character and be alphanumeric, underscore is allowed
    """
    
    if attributes is not None:
        for key in attributes.keys():
            assert type(key) == str, 'Attribute names must be strings, {} is a {}'.format(key, type(key))
            assert key[0].isalpha(), '{} must begin with an alphabetic character'.format(key)
            assert all(char == '_' or char.isdigit() or char.isalpha() for char in key), \
                '{} is not alphanumeric (including underscore)'.format(key)
            val = attributes[key]
            allowed_attribute_types = [float, int, str]
            try:
                assert all(type(item) in allowed_attribute_types for item in val), \
                    'Attribute value types must be one of {}'.format(allowed_attribute_types)
            except TypeError:
                assert type(val) in allowed_attribute_types, \
                    '{} type must be one of {}'.format(key, allowed_attribute_types)

    if out_path is None:
        out_path = os.path.join(os.path.dirname(in_path), os.path.basename(in_path) + '.nc')

    if os.path.exists(out_path):
        os.remove(out_path)

    ds = nc.Dataset(out_path, "w", format="NETCDF4")
    file_paths = [os.path.join(in_path, rsl) for rsl in os.listdir(in_path) if rsl.lower().endswith('.rsl')]
    file_paths.sort(key=path_to_step)

    times = [path_to_time(path) for path in file_paths]

    steps = [path_to_step(path) for path in file_paths]

    locations = pd.read_csv(file_paths[0], usecols=['XCen', 'YCen'], delimiter=' ')

    _, unique_x, unique_y, x_index, y_index = get_transform(locations.XCen, locations.YCen)

    x_size = len(unique_x)
    y_size = len(unique_y)

    depth_array = np.full((y_size, x_size), fill_value)
    x_vel_array = np.full((y_size, x_size), fill_value)
    y_vel_array = np.full((y_size, x_size), fill_value)

    ds.createDimension("time", None)
    ds.createDimension("x", x_size)
    ds.createDimension("y", y_size)

    depth_var = ds.createVariable("depth", datatype, ("time", "y", "x",), zlib=True, least_significant_digit=3)
    x_vel_var = ds.createVariable("x_vel", datatype, ("time", "y", "x",), zlib=True, least_significant_digit=3)
    y_vel_var = ds.createVariable("y_vel", datatype, ("time", "y", "x",), zlib=True, least_significant_digit=3)
    x_var = ds.createVariable("x", datatype, ("x",), zlib=True)
    y_var = ds.createVariable("y", datatype, ("y",), zlib=True)
    times_var = ds.createVariable("time", "f8", ("time",), zlib=True)

    depth_var.units = 'm'
    x_vel_var.units = 'm/s'
    y_vel_var.units = 'm/s'
    x_var.units = 'm'
    y_var.units = 'm'

    times_var.units = "minutes since {:%Y-%m-%d}".format(start_time).replace("-0", "-")
    times_var.calendar = "gregorian"
    times_var.long_name = "Time in minutes since {:%Y-%m-%d}".format(start_time).replace("-0", "-")

    for i in range(len(file_paths)):
        variables = pd.read_csv(file_paths[i], usecols=['Depth', 'Vx', 'Vy'], delimiter=' ')
        depth_array[y_index, x_index] = variables.Depth.values
        x_vel_array[y_index, x_index] = variables.Vx.values
        y_vel_array[y_index, x_index] = variables.Vy.values

        depth_var[steps[i], :, :] = depth_array
        x_vel_var[steps[i], :, :] = x_vel_array
        y_vel_var[steps[i], :, :] = y_vel_array

    times_var[:] = times
    x_var[:] = unique_x
    y_var[:] = unique_y

    if srid is not None:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(srid)
        depth_var.grid_mapping = 'crs'
        x_vel_var.grid_mapping = 'crs'
        y_vel_var.grid_mapping = 'crs'

        crs = ds.createVariable('crs', 'i4')
        crs.spatial_ref = srs.ExportToWkt()
        crs.grid_mapping_name = srs.GetAttrValue('projection').lower()
        crs.scale_factor_at_central_meridian = srs.GetProjParm('scale_factor')
        crs.longitude_of_central_meridian = srs.GetProjParm('central_meridian')
        crs.latitude_of_projection_origin = srs.GetProjParm('latitude_of_origin')
        crs.false_easting = srs.GetProjParm('false_easting')
        crs.false_northing = srs.GetProjParm('false_northing')

    ds.Conventions = 'CF-1.6'
    ds.institution = 'Newcastle University'
    ds.source = 'CityCAT Model Results'
    ds.references = 'Glenis, V., Kutija, V. & Kilsby, C.G. (2018) ' \
                    'A fully hydrodynamic urban flood modelling system ' \
                    'representing buildings, green space and interventions. ' \
                    'Environmental Modelling and Software. 109 (August), 272–292'

    ds.title = 'CityCAT Model Results'
    ds.history = 'Created {}'.format(datetime.now())

    if attributes is not None:
        for key in attributes.keys():
            ds.setncattr(key, attributes[key])

    ds.close()


def path_to_step(path):
    return int(os.path.basename(path).split('min')[0].split('_')[2][1:])


def path_to_time(path):
    return int(os.path.basename(path).split('min')[0].split('_')[-1].split('.')[0])


def get_transform(x, y):
    res = np.diff(np.unique(x)).min()
    unique_x = np.arange(x.min(), x.max() + res, res)
    unique_y = np.arange(y.max(), y.min() - res, -res)

    x_index = ((x - x.min()) / res).round(0).astype(int)
    y_index = ((y.max() - y) / res).round(0).astype(int)

    return res, unique_x, unique_y, x_index, y_index


def to_geotiff(in_path, out_path, srid: int = None, delimiter: str = ','):
    """Converts single CityCAT results file to GeoTIFF

    Args:
        in_path: path where CityCAT results file is located
        out_path: path to create GeoTIFF file
        srid: EPSG Spatial Reference System Identifier of results file
        delimiter: Delimiter to use when reading the results file
    """
    from rasterio.transform import from_origin
    df = pd.read_csv(in_path, delimiter=delimiter)

    res, unique_x, unique_y, x_index, y_index = get_transform(df.XCen, df.YCen)

    width = len(unique_x)
    height = len(unique_y)

    depth = np.full((height, width), fill_value)

    depth[y_index, x_index] = df.Depth.values

    with rio.open(
            out_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=depth.dtype,
            crs=f'EPSG:{srid}' if srid is not None else None,
            transform=from_origin(unique_x.min() - res/2, unique_y.max() + res/2, res, res),
            nodata=fill_value,
            compress='lzw'
    ) as dst:
        dst.write(depth, 1)


@click.command()
@click.option('--in_path', help='Input path')
@click.option('--out_path', help='Output path')
@click.option('--srid', help='Coordinate reference system')
@click.option('--delimiter', help='Column delimiter of CSV file', default=',')
def ccat2gtif(in_path, out_path, srid, delimiter):
    to_geotiff(in_path, out_path, srid, delimiter)


@click.command()
@click.option('--in_path', help='Input path')
@click.option('--out_path', help='Output path')
@click.option('--srid', help='Coordinate reference system')
@click.option('--start_time', help='Start time of run', type=click.DateTime(formats=["%Y-%m-%dT%H:%M:%S"]))
def ccat2netcdf(in_path, out_path, srid, start_time):
    to_netcdf(in_path, out_path, start_time, srid)
