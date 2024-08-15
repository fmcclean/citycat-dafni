import geopandas as gpd
import click


def geoseries_to_string(geoseries: gpd.GeoSeries, value= None, index=False, index_first=True):
    """GeoSeries to CityCAT string representation

    Args:
        geoseries: Polygons to convert
        index: Whether or not to include the index
        index_first: Whether or not to place the index before the number of points
    Returns:
        s (str): String representation readable by CityCAT

    """
    assert (geoseries.geom_type == 'Polygon').all(), 'Geometries must be of type Polygon'

    s = '{}\n'.format(len(geoseries))

    for idx, geometry in geoseries.items():
        if not index:
            s += '{}'.format(len(geometry.exterior.coords))
        elif index_first:
            s += '{} {}'.format(value[idx], len(geometry.exterior.coords))
        else:
            s += '{} {}'.format(len(geometry.exterior.coords), value[idx])
        x, y = geometry.exterior.coords.xy
        for x_val in x:
            s += ' {}'.format(x_val)
        for y_val in y:
            s += ' {}'.format(y_val)
        s += '\n'

    return s


@click.command()
@click.option('--in_path', help='Input path')
@click.option('--out_path', help='Output path')
def geom2ccat(in_path, out_path):
    with open(out_path, 'w') as f:
        f.write(geoseries_to_string(gpd.read_file(in_path).geometry))
