import rasterio as rio
import os


class Dem:
    """Digital Elevation Model

    Args:
        data: Rasterio memory file containing DEM data
    """
    def __init__(self, data: rio.MemoryFile):
        assert type(data) == rio.MemoryFile
        self.data = data

    def write(self, path):
        with self.data.open() as dataset:
            with rio.open(
                os.path.join(path, 'Domain_DEM.ASC'),
                'w',
                **{**dataset.profile, 'driver': 'AAIGRID'},

            ) as output:
                output.write(dataset.read())
