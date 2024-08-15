import geopandas as gpd
from ..utils import geoseries_to_string
import os


class OpenBoundaries:
    """Areas where the domain boundary should be open

    Args:
        data: Table containing boundary polygons
    """
    def __init__(self, data: gpd.GeoDataFrame):
        assert type(data) == gpd.GeoDataFrame
        self.data = data

    def write(self, path):
        with open(os.path.join(path, 'BCs_open.txt'), 'w') as f:
            f.write(geoseries_to_string(self.data.geometry))
