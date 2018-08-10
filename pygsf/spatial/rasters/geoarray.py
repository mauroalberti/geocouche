# -*- coding: utf-8 -*-

import math

from .exceptions import *
from .fields import *
from ..generics.general import *


def ijPixToijArray(i_pix: Number, j_pix: Number) -> Tuple[Number, Number]:
    """
    Converts from pixel (geotransform-derived) to array indices.

    :param i_pix: the geotransform i value.
    :type i_pix: Number.
    :param j_pix: the geotransform j value.
    :type j_pix: Number.
    :return: the array-equivalent i and j indices.
    :rtype: a tuple of two numbers.

    Examples:
      >>> ijPixToijArray(0, 0)
      (-0.5, -0.5)
      >>> ijPixToijArray(0.5, 0.5)
      (0.0, 0.0)
      >>> ijPixToijArray(0.5, 1.5)
      (0.0, 1.0)
    """

    return i_pix - 0.5, j_pix - 0.5


def ijArrToijPix(i_arr: Number, j_arr: Number) -> Tuple[Number, Number]:
    """
    Converts from array indices to geotransform-related pixel indices.

    :param i_arr: the array i value.
    :type i_arr: Number.
    :param j_arr: the array j value.
    :type j_arr: Number.
    :return: the geotransform-equivalent i and j indices.
    :rtype: a tuple of two numbers.

    Examples:
      >>> ijArrToijPix(0, 0)
      (0.5, 0.5)
      >>> ijArrToijPix(0.5, 0.5)
      (1.0, 1.0)
      >>> ijArrToijPix(1.5, 0.5)
      (2.0, 1.0)
    """

    return i_arr + 0.5, j_arr + 0.5


class GeoArray(object):
    """
    GeoArray class.
    Stores and process georeferenced raster data.

    """

    def __init__(self, inGeotransform: GeoTransform, inProjection: str, inLevels: Optional[List['np.array']]=None) -> None:
        """
        GeoArray class constructor.

        :param  inGeotransform:  the geotransform
        :type  inGeotransform:  GeoTransform.
        :param inProjection: the projection
        :type inProjection: str
        :param  inLevels:  the nd-array storing the data.
        :type  inLevels:  np.array.

        :return:  None.

        Examples:
        """

        self.gt = inGeotransform
        self.prj = inProjection
        if inLevels is None:
            self._levels = []
        else:
            self._levels = inLevels

    @property
    def cellsize_x(self) -> float:
        """
        Get the cell size of the grid in the x direction.

        :return: cell size in the x (j) direction.
        :rtype: float.

        Examples:
        """

        return abs(self.gt.pixWidth)

    @property
    def cellsize_y(self) -> float:
        """
        Get the cell size of the grid in the y direction.

        :return: cell size in the y (-i) direction.
        :rtype: float.

        Examples:
        """

        return abs(self.gt.pixHeight)

    @property
    def levels_num(self) -> int:
        """
        Returns the number of levels (dimensions) of the grid.

        :return: number of levels.
        :rtype: int.

        Examples:
          >>> gt = GeoTransform(0, 0, 10, 10)
          >>> GeoArray(gt, "", [array([[1, 2], [3, 4]])]).levels_num
          1
          >>> GeoArray(gt, "", [array([[1, 2], [3, 4]]), np.ones((4, 3, 2))]).levels_num
          2
        """

        return len(self._levels)

    def level(self, level_ndx: int=0):
        """
        Return the array corresponding to the requested level
        if existing else None.

        :param level_ndx: the index of the requested level.
        :type level_ndx: int.
        :return: the array or None.
        :rtype: optional array.

        Examples:
        """

        if 0 <= level_ndx < self.levels_num:
            return self._levels[level_ndx]
        else:
            return None

    def level_shape(self, level_ndx: int=0) -> Optional[Tuple[int, int]]:
        """
        Returns the shape (num. rows and num. columns) of the considered level grid.

        :param level_ndx: index of the level (grid) to consider.
        :type level_ndx: int.
        :return: number of rows and columns of the specific grid.
        :rtype: optional tuple of two int values.

        Examples:
          >>> gt = GeoTransform(0, 0, 10, 10)
          >>> GeoArray(gt, "", [array([[1, 2], [3, 4]])]).level_shape()
          (2, 2)
          >>> GeoArray(gt, "", [array([[1, 2], [3, 4]]), np.ones((4, 3, 2))]).level_shape(1)
          (4, 3, 2)
        """

        if 0 <= level_ndx < self.levels_num:
            return self._levels[level_ndx].shape
        else:
            return None

    def level_llc(self, level_ndx: int=0) -> Optional[Tuple[int, int]]:
        """
        Returns the coordinates of the lower-left corner.

        :param level_ndx: index of the level (grid) to consider.
        :type level_ndx: int.
        :return: x and y values of the lower-left corner of the specific grid.
        :rtype: optional tuple of two int values.

        Examples:
        """

        shape = self.level_shape(level_ndx)
        if not shape:
            return None

        llc_i_pix, llc_j_pix = shape[0], 0

        return self.ijPixToxy(llc_i_pix, llc_j_pix)

    def xyToijArr(self, x: Number, y: Number) -> Tuple[Number, Number]:
        """
        Converts from geographic to array coordinates.

        :param x: x geographic component.
        :type x: Number.
        :param y: y geographic component.
        :type y: Number.
        :return: i and j values referred to array.
        :type: tuple of two float values.

        Examples:
        """

        return ijPixToijArray(*xyGeogrToijPix(self.gt, x, y))

    def xyToijPix(self, x: Number, y: Number) -> Tuple[Number, Number]:
        """
        Converts from geographic to pixel coordinates.

        :param x: x geographic component
        :type x: Number
        :param y: y geographic component
        :type y: Number
        :return: i and j values referred to grid.
        :type: tuple of two float values

        Examples:
        """

        return xyGeogrToijPix(self.gt, x, y)

    def ijArrToxy(self, i: Number, j: Number) -> Tuple[Number, Number]:
        """
        Converts from array indices to geographic coordinates.

        :param i: i array component.
        :type i: Number.
        :param j: j array component.
        :type j: Number.
        :return: x and y geographic coordinates.
        :type: tuple of two float values.

        Examples:
        """

        i_pix, j_pix = ijArrToijPix(i, j)

        return ijPixToxyGeogr(self.gt, i_pix, j_pix)

    def ijPixToxy(self, i: Number, j: Number) -> Tuple[Number, Number]:
        """
        Converts from grid indices to geographic coordinates.

        :param i: i pixel component.
        :type i: Number.
        :param j: j pixel component.
        :type j: Number.
        :return: x and y geographic coordinates.
        :type: tuple of two float values.

        Examples:
        """

        return ijPixToxyGeogr(self.gt, i, j)

    @property
    def has_rotation(self) -> bool:
        """
        Determines if a geoarray has axis rotations defined.

        :return: true if there are rotations, false otherwise.
        :rtype: bool.

        Examples:
        """

        return self.gt.has_rotation

    def interpolate_bilinear(self, x: Number, y: Number, level_ndx=0) -> Optional[float]:
        """
        Interpolate the z value at a point, given its geographic coordinates.
        Interpolation method: bilinear.

        :param x: x geographic coordinate.
        :type x: Number.
        :param y: y geographic coordinate.
        :type y: Number.
        :param level_ndx: the index of the used array.
        :type level_ndx: int.
        :return: a geoarray storing the interpolated z value
        :rtype: optional float.

        Examples:
        """

        i, j = self.xyToijArr(x, y)

        inter_res = interp_bilinear(self._levels[level_ndx], i, j)

        if inter_res is None:
            return None
        elif math.isnan(inter_res):
            return None
        else:
            return inter_res

    def magnitude_field(self, ndx_fx=0, ndx_fy=1) -> 'GeoArray':
        """
        Calculates magnitude field as a geoarray.

        :param ndx_fx: index of x field.
        :type ndx_fx: integer.
        :param ndx_fy: index of y field.
        :type ndx_fy: integer.
        :return: a geoarray storing the magnitude field.
        :rtype: GeoArray.

        Examples:
        """

        magn = magnitude(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy])

        return GeoArray(
            inGeotransform=self.gt,
            inProjection=self.prj,
            inLevels=[magn]
        )

    def orientations(self, ndx_fx=0, ndx_fy=1) -> 'GeoArray':
        """
        Calculates orientations field as a geoarray.

        :param ndx_fx: index of x field.
        :type ndx_fx: integer.
        :param ndx_fy: index of y field.
        :type ndx_fy: integer.
        :return: a geoarray storing the orientation field.
        :rtype: GeoArray.

        Examples:
        """

        orient = orients_d(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy])

        return GeoArray(
            inGeotransform=self.gt,
            inProjection=self.prj,
            inLevels=[orient]
        )

    def divergence_2D(self, ndx_fx=0, ndx_fy=1) -> 'GeoArray':
        """
        Calculates divergence of a 2D field as a geoarray.

        :param ndx_fx: index of x field.
        :type ndx_fx: integer.
        :param ndx_fy: index of y field.
        :type ndx_fy: integer.
        :return: a geoarray storing the divergence field.
        :rtype: GeoArray.

        Examples:
        """

        div = divergence(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy],
            cell_size_x=self.cellsize_x,
            cell_size_y=self.cellsize_y)

        return GeoArray(
            inGeotransform=self.gt,
            inProjection=self.prj,
            inLevels=[div]
        )

    def curl_module(self, ndx_fx=0, ndx_fy=1) -> 'GeoArray':
        """
        Calculates curl module of a 2D field as a geoarray.

        :param ndx_fx: index of x field.
        :type ndx_fx: integer.
        :param ndx_fy: index of y field.
        :type ndx_fy: integer.
        :return: a geoarray storing the curl module field.
        :rtype: GeoArray.

        Examples:
        """

        curl_m = curl_module(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy],
            cell_size_x=self.cellsize_x,
            cell_size_y=self.cellsize_y)

        return GeoArray(
            inGeotransform=self.gt,
            inProjection=self.prj,
            inLevels=[curl_m])

    def magnitude_grads(self, axis: str= '', ndx_fx: int=0, ndx_fy: int=1) -> 'GeoArray':
        """
        Calculates the magnitude gradient along the x, y axis or both, of a 2D field as a geoarray.

        :param axis: axis along wich to calculate the gradient, 'x' or 'y', or '' (predefined) for both x and y.
        :type axis: str.
        :param ndx_fx: index of x field.
        :type ndx_fx: integer.
        :param ndx_fy: index of y field.
        :type ndx_fy: integer.
        :return: a geoarray storing the magnitude gradient along the x, y axis (or both) field.
        :rtype: GeoArray.
        :raises: GeoArrayIOException.

        Examples:
        """

        if axis == 'x':
            cell_sizes = [self.cellsize_x]
        elif axis == 'y':
            cell_sizes = [self.cellsize_y]
        elif axis == '':
            cell_sizes = [self.cellsize_x, self.cellsize_y]
        else:
            raise GeoArrayIOException("Axis must be 'x' or 'y. '{}' given".format(axis))

        magnitude_gradients = magn_grads(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy],
            dir_cell_sizes=cell_sizes,
            axis=axis)

        return GeoArray(
            inGeotransform=self.gt,
            inProjection=self.prj,
            inLevels=magnitude_gradients)

    def grad_flowlines(self, ndx_fx: int=0, ndx_fy: int=1) -> 'GeoArray':
        """
        Calculates gradient along flow lines.

        :param ndx_fx: index of x field.
        :type ndx_fx: integer.
        :param ndx_fy: index of y field.
        :type ndx_fy: integer.
        :return: a geoarray storing the flowline gradient field
        :rtype: GeoArray
        """

        flowln_grad = magn_grad_along_flowlines(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy],
            cell_size_x=self.cellsize_x,
            cell_size_y=self.cellsize_y)

        return GeoArray(
            inGeotransform=self.gt,
            inProjection=self.prj,
            inLevels=[flowln_grad])


def levelCreateParams(gt: GeoTransform, prj: str, data: array) -> Dict:
    """
    Create parameter dictionary from level parameters.

    :param gt: the level geotransform.
    :type gt: GeoTransform.
    :param prj: the level projection string.
    :type prj: str.
    :param data: the level data.
    :type data: Numpy array.
    :return: the dictionary of the relevant parameters.
    :rtype: dictinary.

    Examples:
    """

    return dict(
        geotransform=gt,
        projection=prj,
        data_shape=data.shape
    )

def levelsEquival(level_params_1: Dict, level_params_2: dict) -> bool:
    """
    Compares two level paramenters for equivalence.

    :param level_params_1: the first level dictionary.
    :type level_params_1: dictionary.
    :param level_params_2: the second level dictionary.
    :type level_params_2: dictionary.
    :return: the equivalence result.
    :rtype: bool.
    """

    if not gtEquiv(
        gt1=level_params_1["geotransform"],
        gt2=level_params_2["geotransform"]):
        return False

    if not prjEquiv(
        prj1=level_params_1["projection"],
        prj2=level_params_2["projection"]):
        return False

    if level_params_1["data_shape"] != level_params_2["data_shape"]:
        return False

    return True


if __name__ == "__main__":

    import doctest
    doctest.testmod()

