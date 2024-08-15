import pandas as pd
import os
import decimal

ctx = decimal.Context()
ctx.prec = 20


def float_to_str(f):
    return format(ctx.create_decimal(repr(f)), 'f')


class Rainfall:
    """Rainfall time series

    Args:
        data: Pandas DataFrame containing rainfall values
        spatial: Whether the rainfall is spatially distributed or not
            If more than one column is included in data then then spatial must be True

    """
    def __init__(self, data: pd.DataFrame, spatial=False):
        assert type(data) == pd.DataFrame
        assert len(data) > 0, 'Rainfall DataFrame is empty'
        if len(data.columns) > 1:
            assert spatial, 'if len(data.columns) > 1, spatial must be True'
        self.data = data
        self.spatial = spatial

    def write(self, path):
        with open(os.path.join(path, '{}Rainfall_Data_1.txt'.format('Spatial_' if self.spatial else '')), 'w') as f:
            f.write('* * *\n')
            f.write('* * * rainfall * * *\n')
            f.write('* * *\n')
            f.write('{}\n'.format(len(self.data)))
            f.write('* * *\n')
            self.data.applymap(float_to_str).to_csv(f, sep=' ', header=False, lineterminator='\n')
