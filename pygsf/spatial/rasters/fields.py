# -*- coding: utf-8 -*-

from ...mathematics.exceptions import InputValuesException
from .geotransform import *


def ij_transfer_func(
        i: Number,
        j: Number,
        geotransform: GeoTransform,
        z_transfer_func: Callable,
        i_shift=0.5,
        j_shift=0.5) -> float:
    """
    Return a z value as the result of a function (transfer_func_z) applied to a
    (i+i_shift,j+j_shift) point (i.e., with defaultvalues, the cell center, not the cell top-left corner)
    given a geotransform.

    :param  i:  array i (-y) coordinate of a single point.
    :type  i:  Number.
    :param  j:  array j (x) coordinate of a single point.
    :type  j:  Number.
    :param  geotransform:  geotransform
    :type  geotransform:  GeoTransform.
    :param  z_transfer_func:  function that calculates the z value given x and y input
    :type  z_transfer_func:  function.
    :param i_shift: cell unit shift in the i direction with respect to the cell top-left corner. Default is 0.5, i.e. half the cell size
    :type i_shift: Number
    :param j_shift: cell unit shift in the j direction with respect to the cell top-left corner. Default is 0.5, i.e. half the cell size
    :type j_shift: Number
    :return: z value
    :rtype: float.

    Examples:
    """

    return z_transfer_func(*ijPixToxyGeogr(geotransform, i + i_shift, j + j_shift))


def array_from_function(
        row_num: int,
        col_num: int,
        geotransform: GeoTransform,
        z_transfer_func: Callable) -> 'array':
    """
    Creates an array of z values based on functions that map (i,j) indices (to be created)
    into (x, y) values and then z values.

    :param  row_num:  row number of the array to be created.
    :type  row_num:  int.
    :param  col_num:  column number of the array to be created.
    :type  col_num:  int.
    :param  geotransform:  the used geotransform.
    :type  geotransform:  GeoTransform.
    :param  z_transfer_func:  function that derives z given a (x, y) point.
    :type  z_transfer_func:  Function.

    :return:  array of z values
    :rtype: np.array of float numbers.

    Examples:
    """

    return np.fromfunction(
        function=ij_transfer_func,
        shape=(row_num, col_num),
        dtype=np.float64,
        geotransform=geotransform,
        z_transfer_func=z_transfer_func)


def grad_x(
        fld: 'array',
        cell_size_x: Number,
        edge_order: int=2) -> 'array':
    """
    Calculates the array gradient along the x axis.

    :param fld: array.
    :type fld: np.array.
    :param cell_size_x: the cell spacing in the x direction.
    :type cell_size_x: Number.
    :param edge_order: the type of edge order used in the Numpy gradient method.
    :type edge_order: int.
    :return: gradient field.
    :rtype: np.array.

    Examples:
    """

    return np.gradient(fld, edge_order=edge_order, axis=1) / cell_size_x


def grad_y(
        fld: 'array',
        cell_size_y: Number,
        edge_order: int=2) -> 'array':
    """
    Calculates the array gradient along the y axis.

    :param fld: array.
    :type fld: np.array.
    :param cell_size_y: the cell spacing in the y direction.
    :type cell_size_y: Number.
    :param edge_order: the type of edge order used in the Numpy gradient method.
    :type edge_order: int.
    :return: gradient field.
    :rtype: np.array.

    Examples:
    """

    return - np.gradient(fld, edge_order=edge_order, axis=0) / cell_size_y


def dir_deriv(
        fld: 'array',
        cell_size_x: Number,
        cell_size_y: Number,
        direct_rad: Number,
        dx_edge_order: int=2,
        dy_edge_order: int=2) -> 'array':
    """
    Calculates the directional derivative in the provided direction.

    :param fld: the field.
    :type fld: Numpy array.
    :param cell_size_x: the cell size along the x axis.
    :type cell_size_x: Number.
    :param cell_size_y: the cell size along the y
    :param direct_rad: the direction, expressed as radians.
    :type direct_rad: Number.
    :param dx_edge_order: the edge order of the gradient along x.
    :type dx_edge_order: int.
    :param dy_edge_order: the edge order of the gradient along y.
    :type dy_edge_order: int.
    :return: the directional derivative array.
    :rtype: Numpy array.
    """

    df_dx = grad_x(
        fld=fld,
        cell_size_x=cell_size_x,
        edge_order=dx_edge_order)

    df_dy = grad_y(
        fld=fld,
        cell_size_y=cell_size_y,
        edge_order=dy_edge_order)

    return df_dx * sin(direct_rad) + df_dy * cos(direct_rad)


def magnitude(
        fld_x: 'array',
        fld_y: 'array') -> 'array':
    """
    Calculates the magnitude given two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :type fld_x: np.array.
    :param fld_y: vector field y component.
    :type fld_y: np.array.
    :return: magnitude field.
    :rtype: np.array.

    Examples:
    """

    return np.sqrt(fld_x ** 2 + fld_y ** 2)


def orients_r(
        fld_x: 'array',
        fld_y: 'array') -> 'array':
    """
    Calculates the orientations (as radians) given two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :type fld_x: np.array.
    :param fld_y: vector field y component.
    :type fld_y: np.array.
    :return: orientation field, in radians.
    :rtype: np.array.

    Examples:
    """

    azimuth_rad = np.arctan2(fld_x, fld_y)
    azimuth_rad = np.where(azimuth_rad < 0.0, azimuth_rad + 2*np.pi, azimuth_rad)

    return azimuth_rad


def orients_d(
        fld_x: 'array',
        fld_y: 'array') -> 'array':
    """
    Calculates the orientations (as decimal degrees) given two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :type fld_x: np.array.
    :param fld_y: vector field y component.
    :type fld_y: np.array.
    :return: orientation field, in decimal degrees.
    :rtype: np.array.

    Examples:
    """

    return np.degrees(orients_r(fld_x, fld_y))


def divergence(
        fld_x: 'array',
        fld_y: 'array',
        cell_size_x: Number,
        cell_size_y: Number) -> 'array':
    """
    Calculates the divergence from two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :type fld_x: np.array.
    :param fld_y: vector field y component.
    :type fld_y: np.array.
    :param cell_size_x: the cell spacing in the x direction.
    :type cell_size_x: Number.
    :param cell_size_y: the cell spacing in the y direction.
    :type cell_size_y: Number.
    :return: divergence field.
    :rtype: np.array.

    Examples:
    """

    dfx_dx = grad_x(fld_x, cell_size_x)
    dfy_dy = grad_y(fld_y, cell_size_y)

    return dfx_dx + dfy_dy


def curl_module(
        fld_x: 'array',
        fld_y: 'array',
        cell_size_x: Number,
        cell_size_y: Number) -> 'array':
    """
    Calculates the curl module from two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :type fld_x: np.array.
    :param fld_y: vector field y component.
    :type fld_y: np.array.
    :param cell_size_x: the cell spacing in the x direction.
    :type cell_size_x: Number.
    :param cell_size_y: the cell spacing in the y direction.
    :type cell_size_y: Number.
    :return: curl field.
    :rtype: np.array.

    Examples:
    """

    dfx_dy = grad_y(fld_x, cell_size_y, edge_order=2)
    dfy_dx = grad_x(fld_y, cell_size_x, edge_order=1)

    return dfy_dx - dfx_dy


def magn_grads(
        fld_x: 'array',
        fld_y: 'array',
        dir_cell_sizes: List[Number],
        axis: str='') -> List['array']:
    """
    Calculates the magnitude gradient along the given direction, based on the field-defining two 2D arrays:
    the first representing the x component, the second the y component.

    :param fld_x: vector field x component.
    :type fld_x: np.array.
    :param fld_y: vector field y component.
    :type fld_y: np.array.
    :param dir_cell_sizes: list of cell spacing(s) in the considered direction(s).
    :type dir_cell_sizes: list of Number(s).
    :param axis: declares the axis ('x' or 'y') or the axes('', i.e., empty string) for both x and y directions.
    :type axis: str.
    :return: magnitude gradient field(s) along the considered direction.
    :rtype: list of np.array.
    :raises: InputValuesException.

    Examples:
    """

    magn = magnitude(fld_x, fld_y)
    if axis == 'x':
        return [grad_x(magn, dir_cell_sizes[0])]
    elif axis == 'y':
        return [grad_y(magn, dir_cell_sizes[0])]
    elif axis == '':
        return [grad_x(magn, dir_cell_sizes[0]), grad_y(magn, dir_cell_sizes[1])]
    else:
        raise InputValuesException("Axis must be 'x' or 'y' or '' (for both x and y). '{}' given".format(axis))


def magn_grad_along_flowlines(
        fld_x: 'array',
        fld_y: 'array',
        cell_size_x: Number,
        cell_size_y: Number) -> 'array':
    """
    Calculates gradient along flow lines.

    :param fld_x: vector field x component.
    :type fld_x: np.array.
    :param fld_y: vector field y component.
    :type fld_y: np.array.
    :param cell_size_x: the cell spacing in the x direction.
    :type cell_size_x: Number.
    :param cell_size_y: the cell spacing in the y direction.
    :type cell_size_y: Number.
    :return: the flowline gradient field
    :rtype: np.array.
    """

    orien_rad = orients_r(fld_x, fld_y)

    dm_dx, dm_dy = magn_grads(
        fld_x=fld_x,
        fld_y=fld_y,
        dir_cell_sizes=[cell_size_x, cell_size_y])

    velocity_gradient = dm_dx * np.sin(orien_rad) + dm_dy * np.cos(orien_rad)

    return velocity_gradient
