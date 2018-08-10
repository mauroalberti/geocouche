# -*- coding: utf-8 -*-


from ..defaults.typing import Number


def interp_linear(frac_s: Number, v0: Number, v1:Number) -> Number:
    """
    Interpolate a number in a linear way.

    :param frac_s: the fractional distance between the start and end point. Range 0-1.
    :type frac_s: Number.
    :param v0: the value at the start point.
    :type v0: Number.
    :param v1: the value at the end point.
    ;:type v1: Number.
    :return: the interpolated value.

    Examples:
      >>> interp_linear(0, 10, 20)
      10
      >>> interp_linear(1, 10, 20)
      20
      >>> interp_linear(-1, 10, 20)
      0
      >>> interp_linear(2, 10, 20)
      30
      >>> interp_linear(0.3, 0, 10)
      3.0
      >>> interp_linear(0.75, 0, 10)
      7.5
    """

    delta_z = v1 - v0
    return v0 + frac_s * delta_z


def interp_bilinear(i: Number, j: Number, v00: Number, v01: Number, v10: Number, v11: Number) -> Number:
    """
    Return an interpolated number based on a bilinear interpolation.

    :param i: the delta i relative to the preceding cell center.
    :type i: Number.
    :param j: the delta j relative to the preceding cell center.
    :type j: Number.
    :param v00: the z value of the (i=0, j=0) cell center.
    :type v00: Number.
    :param v01: the z value of the (i=0, j=1) cell center.
    :type v01: Number.
    :param v10: the z value of the (i=1, j=0) cell center.
    :type v10: Number.
    :param v11: the z value of the (i=1, j=1) cell center.
    :type v11: Number.
    :return: the interpèolated z value.
    :rtype: Number.
    """

    grid_val_y0 = v00 + (v10 - v00) * i
    grid_val_y1 = v01 + (v11 - v01) * i

    return grid_val_y0 + (grid_val_y1 - grid_val_y0) * j


if __name__ == "__main__":

    import doctest

    doctest.testmod()
