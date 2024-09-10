import geopandas as gpd
from ..utils import geoseries_to_string
import os


class Reservoir:
    """Areas with custom reservoir elevations

    Args:
        data: Table containing reservoir polygons

    """
    def __init__(self, data: gpd.GeoDataFrame):
        assert type(data) == gpd.GeoDataFrame
        self.data = data

    def write(self, path):
        with open(os.path.join(path, 'InitSurfaceWaterElev_Polygons.txt'), 'w') as f:
            f.write(geoseries_to_string(self.data.geometry,self.data.Value, index=True, index_first=False))
           
          