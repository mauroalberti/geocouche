# -*- coding: utf-8 -*-


import os

import numpy as np

from ...defaults.typing import *
from ...defaults.constants import *
from ...mathematics.scalars import areClose
from .geoarray import GeoArray


def try_write_esrigrid(geoarray: GeoArray, outgrid_fn: str, esri_nullvalue: Number=GRID_NULL_VALUE, level_ndx: int=0) -> Tuple[bool, str]:
    """
    Writes ESRI ascii grid.
    
    :param geoarray: 
    :param outgrid_fn: 
    :param esri_nullvalue: 
    :param level_ndx: index of the level array to write.
    :type level_ndx: int.
    :return: success and descriptive message
    :rtype: tuple made up by a boolean and a string
    """
    
    outgrid_fn = str(outgrid_fn)

    # checking existence of output slope grid

    if os.path.exists(outgrid_fn):
        return False, "Output grid '{}' already exists".format(outgrid_fn)

    try:
        outputgrid = open(outgrid_fn, 'w')  # create the output ascii file
    except Exception:
        return False, "Unable to create output grid '{}'".format(outgrid_fn)

    if outputgrid is None:
        return False, "Unable to create output grid '{}'".format(outgrid_fn)

    if geoarray.has_rotation:
        return False, "Grid has axes rotations defined"

    cell_size_x = geoarray.cellsize_x
    cell_size_y = geoarray.cellsize_y

    if not areClose(cell_size_x, cell_size_y):
        return False, "Cell sizes in the x- and y- directions are not similar"

    arr = geoarray.level(level_ndx)
    if arr is None:
        return False, "Array with index {} does not exist".format((level_ndx))

    num_rows, num_cols = arr.shape
    llc_x, llc_y = geoarray.level_llc(level_ndx)

    # writes header of grid ascii file

    outputgrid.write("NCOLS %d\n" % num_cols)
    outputgrid.write("NROWS %d\n" % num_rows)
    outputgrid.write("XLLCORNER %.8f\n" % llc_x)
    outputgrid.write("YLLCORNER %.8f\n" % llc_y)
    outputgrid.write("CELLSIZE %.8f\n" % cell_size_x)
    outputgrid.write("NODATA_VALUE %f\n" % esri_nullvalue)

    esrigrid_outvalues = np.where(np.isnan(arr), esri_nullvalue, arr)

    # output of results

    for i in range(0, num_rows):
        for j in range(0, num_cols):
            outputgrid.write("%.8f " % (esrigrid_outvalues[i, j]))
        outputgrid.write("\n")

    outputgrid.close()

    return True, "Data saved in {}".format(outgrid_fn)



