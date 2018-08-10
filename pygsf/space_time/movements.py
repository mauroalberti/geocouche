# -*- coding: utf-8 -*-


from ..defaults.typing import *
from ..spatial.vectorial.vectorial import Point
from ..spatial.rasters.geoarray import GeoArray


def point_velocity(geoarray: GeoArray, pt: Point) -> Tuple[Optional[float], Optional[float]]:
    """
    Return the velocity components of a 2D-flow field at a point location, based on bilinear interpolation.

    :param geoarray: the flow field expressed as a GeoArray.
    :type geoarray: GeoArray.
    :param pt: the point for which the velocity comnponents are extracted.
    :type pt: Point.
    :return: the x and y velocity components of the flow field at the point location.
    :rtype: tuple of two float values.

    Examples:
    """

    x, y, _ = pt.toXYZ()
    vx = geoarray.interpolate_bilinear(
        x=x,
        y=y,
        level_ndx=0)
    vy = geoarray.interpolate_bilinear(
        x=x,
        y=y,
        level_ndx=1)

    return vx, vy


def interpolate_rkf(geoarray: GeoArray, delta_time: Number, start_pt: Point) -> Tuple[Optional[Point], Optional[float]]:
    """
    Interpolate point-like object position according to the Runge-Kutta-Fehlberg method.

    :param geoarray: the flow field expressed as a GeoArray.
    :type geoarray: GeoArray.
    :param delta_time: the flow field expressed as a GeoArray.
    :type delta_time: GeoArray.
    :param start_pt: the initial point.
    :type start_pt: Point.
    :return: the estimated point-like object position at the incremented time, with the estimation error.
    :rtype: tuple of optional point and optional float.

    Examples:
    """

    k1_vx, k1_vy = point_velocity(geoarray, start_pt)

    if k1_vx is None or k1_vy is None:
        return None, None

    k2_pt = Point(
        start_pt.x + (0.25) * delta_time * k1_vx,
        start_pt.y + (0.25) * delta_time * k1_vy
    )

    k2_vx, k2_vy = point_velocity(geoarray, k2_pt)

    if k2_vx is None or k2_vy is None:
        return None, None

    k3_pt = Point(
        start_pt.x + (3.0 / 32.0) * delta_time * k1_vx + (9.0 / 32.0) * delta_time * k2_vx,
        start_pt.y + (3.0 / 32.0) * delta_time * k1_vy + (9.0 / 32.0) * delta_time * k2_vy
    )

    k3_vx, k3_vy = point_velocity(geoarray, k3_pt)

    if k3_vx is None or k3_vy is None:
        return None, None

    k4_pt = Point(
        start_pt.x + (1932.0 / 2197.0) * delta_time * k1_vx - (7200.0 / 2197.0) * delta_time * k2_vx + (7296.0 / 2197.0) * delta_time * k3_vx,
        start_pt.y + (1932.0 / 2197.0) * delta_time * k1_vy - (7200.0 / 2197.0) * delta_time * k2_vy + (7296.0 / 2197.0) * delta_time * k3_vy)

    k4_vx, k4_vy = point_velocity(geoarray, k4_pt)

    if k4_vx is None or k4_vy is None:
        return None, None

    k5_pt = Point(
        start_pt.x + (439.0 / 216.0) * delta_time * k1_vx - (8.0) * delta_time * k2_vx + (3680.0 / 513.0) * delta_time * k3_vx - (845.0 / 4104.0) * delta_time * k4_vx,
        start_pt.y + (439.0 / 216.0) * delta_time * k1_vy - (8.0) * delta_time * k2_vy + (3680.0 / 513.0) * delta_time * k3_vy - (845.0 / 4104.0) * delta_time * k4_vy)

    k5_vx, k5_vy = point_velocity(geoarray, k5_pt)

    if k5_vx is None or k5_vy is None:
        return None, None

    k6_pt = Point(
        start_pt.x - (8.0 / 27.0) * delta_time * k1_vx + (2.0) * delta_time * k2_vx - (3544.0 / 2565.0) * delta_time * k3_vx + (1859.0 / 4104.0) * delta_time * k4_vx - (
                          11.0 / 40.0) * delta_time * k5_vx,
        start_pt.y - (8.0 / 27.0) * delta_time * k1_vy + (2.0) * delta_time * k2_vy - (3544.0 / 2565.0) * delta_time * k3_vy + (1859.0 / 4104.0) * delta_time * k4_vy - (
                          11.0 / 40.0) * delta_time * k5_vy)

    k6_vx, k6_vy = point_velocity(geoarray, k6_pt)

    if k6_vx is None or k6_vy is None:
        return None, None

    rkf_4o_x = start_pt.x + delta_time * (
            (25.0 / 216.0) * k1_vx + (1408.0 / 2565.0) * k3_vx + (2197.0 / 4104.0) * k4_vx - (
            1.0 / 5.0) * k5_vx)
    rkf_4o_y = start_pt.y + delta_time * (
            (25.0 / 216.0) * k1_vy + (1408.0 / 2565.0) * k3_vy + (2197.0 / 4104.0) * k4_vy - (
            1.0 / 5.0) * k5_vy)
    temp_pt = Point(
        rkf_4o_x,
        rkf_4o_y)

    interp_x = start_pt.x + delta_time * (
            (16.0 / 135.0) * k1_vx + (6656.0 / 12825.0) * k3_vx + (28561.0 / 56430.0) * k4_vx - (
            9.0 / 50.0) * k5_vx + (2.0 / 55.0) * k6_vx)
    interp_y = start_pt.y + delta_time * (
            (16.0 / 135.0) * k1_vy + (6656.0 / 12825.0) * k3_vy + (28561.0 / 56430.0) * k4_vy - (
            9.0 / 50.0) * k5_vy + (2.0 / 55.0) * k6_vy)
    interp_pt = Point(
        interp_x,
        interp_y)

    interp_pt_error_estim = interp_pt.dist2DWith(temp_pt)

    return interp_pt, interp_pt_error_estim

