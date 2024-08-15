import geopandas as gpd
from ..utils import geoseries_to_string
import os


class GreenAreas:
    """Areas representing permeable land cover

    Args:
        data: Table containing green areas polygons

    """
    def __init__(self, data: gpd.GeoDataFrame):
        assert type(data) == gpd.GeoDataFrame
        self.data = data

    def write(self, path):
        if 'Value' in self.data:
            with open(os.path.join(path, 'Spatial_GreenAreas.txt'), 'w') as f:
                f.write(geoseries_to_string(self.data.geometry,self.data.Value,index=True, index_first=True))

        else:
            with open(os.path.join(path, 'GreenAreas.txt'), 'w') as f:
                f.write(geoseries_to_string(self.data.geometry))
                
                