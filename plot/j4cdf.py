"""
Json for CDF Zipf (j4cdf)
"""
from typing import TextIO

import numpy
import pandas as pd


def read_data(file: TextIO):
    data = pd.read_csv(file, names=["rank", "freq"])
    raw = numpy.array(data[["freq"]])
    y = [i[0].split('/') for i in raw]
    y = [float(a[0]) / float(a[-1]) for a in y]
    x = list(numpy.array(data[['rank']]))
    return x, y