# -*- coding: utf-8 -*-


from ..defaults.typing import Tuple

from ..mathematics.defaults import *

from ..spatial.rasters.geoarray import GeoArray
from ..spatial.vectorial.vectorial import Point

from ..orientations.orientations import Plane


def topo_plane_intersection(grid: GeoArray, srcPt: Point, srcPlaneAttitude: Plane) -> Tuple['array', 'array', 'array', 'array']:
    """
    Calculates the intersections (as points) between the grid and a planar analytical surface.

    :param surf_type: type of considered surface (i.e., plane, the only case implemented at present).
    :type surf_type: String.
    :param srcPt: point, expressed in geographical coordinates, that the plane must contain.
    :type srcPt: Point.
    :param srcPlaneAttitude: orientation of the surface (currently only planes).
    :type srcPlaneAttitude: class Plane.

    :return: tuple of four arrays

    Examples:
    """

    # closures to compute the geographic coordinates (in x- and y-) of a cell center
    # the grid coordinates of the cell center are expressed by i and j
    grid_coord_to_geogr_coord_x_closure = lambda j: grid.domain.llcorner.x + grid.cellsize_x * (0.5 + j)
    grid_coord_to_geogr_coord_y_closure = lambda i: grid.domain.trcorner.y - grid.cellsize_y * (0.5 + i)

    # arrays storing the geographical coordinates of the cell centers along the x- and y- axes
    cell_center_x_array = grid.x()
    cell_center_y_array = grid.y()

    ycoords_x, xcoords_y = np.broadcast_arrays(cell_center_x_array, cell_center_y_array)

    #### x-axis direction intersections

    # 2D array of DEM segment parameters
    x_dem_m = grid.grad_forward_x()
    x_dem_q = grid.data - cell_center_x_array * x_dem_m

    # closure for the planar surface that, given (x,y), will be used to derive z
    plane_z_closure = srcPlaneAttitude.plane_from_geo(srcPt)

    # 2D array of plane segment parameters
    x_plane_m = srcPlaneAttitude.plane_x_coeff()
    x_plane_q = np.array_from_function(grid.row_num(), 1, lambda j: 0, grid_coord_to_geogr_coord_y_closure,
                                       plane_z_closure)

    # 2D array that defines denominator for intersections between local segments
    x_inters_denomin = np.where(x_dem_m != x_plane_m, x_dem_m - x_plane_m, np.NaN)

    coincident_x = np.where(x_dem_q != x_plane_q, np.NaN, ycoords_x)

    xcoords_x = np.where(x_dem_m != x_plane_m, (x_plane_q - x_dem_q) / x_inters_denomin, coincident_x)
    xcoords_x = np.where(xcoords_x < ycoords_x, np.NaN, xcoords_x)
    xcoords_x = np.where(xcoords_x >= ycoords_x + grid.cellsize_x, np.NaN, xcoords_x)

    #### y-axis direction intersections

    # 2D array of DEM segment parameters
    y_dem_m = grid.grad_forward_y()
    y_dem_q = grid.data - cell_center_y_array * y_dem_m

    # 2D array of plane segment parameters
    y_plane_m = srcPlaneAttitude.plane_y_coeff()
    y_plane_q = np.array_from_function(1, grid.col_num, grid_coord_to_geogr_coord_x_closure, lambda i: 0,
                                       plane_z_closure)

    # 2D array that defines denominator for intersections between local segments
    y_inters_denomin = np.where(y_dem_m != y_plane_m, y_dem_m - y_plane_m, np.NaN)
    coincident_y = np.where(y_dem_q != y_plane_q, np.NaN, xcoords_y)

    ycoords_y = np.where(y_dem_m != y_plane_m, (y_plane_q - y_dem_q) / y_inters_denomin, coincident_y)

    # filter out cases where intersection is outside cell range
    ycoords_y = np.where(ycoords_y < xcoords_y, np.NaN, ycoords_y)
    ycoords_y = np.where(ycoords_y >= xcoords_y + grid.cellsize_y, np.NaN, ycoords_y)

    for i in range(xcoords_x.shape[0]):
        for j in range(xcoords_x.shape[1]):
            if abs(xcoords_x[i, j] - ycoords_x[i, j]) < MIN_SEPARATION_THRESHOLD and abs(
                    ycoords_y[i, j] - xcoords_y[i, j]) < MIN_SEPARATION_THRESHOLD:
                ycoords_y[i, j] = np.NaN

    return xcoords_x, xcoords_y, ycoords_x, ycoords_y

