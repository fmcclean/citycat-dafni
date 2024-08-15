import geopandas as gpd
from ..utils import geoseries_to_string
import os


class Buildings:
    """Areas representing buildings which are extracted from the domain

    Args:
        data: Table containing building polygons
    """
    def __init__(self, data: gpd.GeoDataFrame):
        assert type(data) == gpd.GeoDataFrame
        self.data = data

    def write(self, path):
        with open(os.path.join(path, 'Buildings.txt'), 'w') as f:
            f.write(geoseries_to_string(self.data.geometry))
