# -*- coding: utf-8 -*-


from typing import Any, Tuple, Dict, Optional, Union

import numpy as np

import gdal

from .exceptions import *

from ...defaults.constants import *
from ...spatial.rasters.geotransform import GeoTransform


def read_raster(file_ref: Any) -> Tuple[gdal.Dataset, Optional[GeoTransform], int, str]:
    """
    Read a raster layer.

    :param file_ref: the reference to the raster
    :type file_ref: Any
    :return: the dataset, its geotransform, the number of bands, the projection.
    :rtype: tuple made up by a gdal.Dataset instance, an optional Geotransform object, and int and a string.
    :raises: RasterIOException

    Examples:
    """

    # open raster file and check operation success

    dataset = gdal.Open(file_ref, gdal.GA_ReadOnly)
    if not dataset:
        raise RasterIOException("No input data open")

    # get raster descriptive infos

    gt = dataset.GetGeoTransform()
    if gt:
        geotransform = GeoTransform.fromGdalGt(gt)
    else:
        geotransform = None

    num_bands = dataset.RasterCount

    projection = dataset.GetProjection()

    return dataset, geotransform, num_bands, projection


def read_band(dataset: gdal.Dataset, bnd_ndx: int=1) -> Tuple[dict, 'np.array']:
    """
    Read data and metadata of a rasters band based on GDAL.

    :param dataset: the source raster dataset
    :type dataset: gdal.Dataset
    :param bnd_ndx: the index of the band (starts from 1)
    :type bnd_ndx: int
    :return: the band parameters and the data values
    :rtype: dict of data parameters and values as a numpy.array
    :raises: RasterIOException

    Examples:

    """

    band = dataset.GetRasterBand(bnd_ndx)
    data_type = gdal.GetDataTypeName(band.DataType)

    unit_type = band.GetUnitType()

    stats = band.GetStatistics(False, False)
    if stats is None:
        dStats = dict(
            min=None,
            max=None,
            mean=None,
            std_dev=None)
    else:
        dStats = dict(
            min=stats[0],
            max=stats[1],
            mean=stats[2],
            std_dev=stats[3])

    noDataVal = band.GetNoDataValue()

    nOverviews = band.GetOverviewCount()

    colorTable = band.GetRasterColorTable()

    if colorTable:
        nColTableEntries = colorTable.GetCount()
    else:
        nColTableEntries = 0

    # read data from band

    grid_values = band.ReadAsArray()
    if grid_values is None:
        raise RasterIOException("Unable to read data from rasters")

    # transform data into numpy array

    data = np.asarray(grid_values)

    # if nodatavalue exists, set null values to NaN in numpy array

    if noDataVal is not None:
        data = np.where(abs(data - noDataVal) > 1e-10, data, np.NaN)

    band_params = dict(
        dataType=data_type,
        unitType=unit_type,
        stats=dStats,
        noData=noDataVal,
        numOverviews=nOverviews,
        numColorTableEntries=nColTableEntries)

    return band_params, data


def try_read_raster_band(raster_source: str, bnd_ndx: int=1) -> Tuple[bool, Union[str, Tuple[GeoTransform, str, Dict, 'np.array']]]:

    # get raster parameters and data
    try:
        dataset, geotransform, num_bands, projection = read_raster(raster_source)
    except (IOError, TypeError, RasterIOException) as err:
        return False, "Exception with reading {}: {}".format(raster_source, err)

    band_params, data = read_band(dataset, bnd_ndx)

    return True, (geotransform, projection, band_params, data)


if __name__ == "__main__":

    import doctest
    doctest.testmod()

