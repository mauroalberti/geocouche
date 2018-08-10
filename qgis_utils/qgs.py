# -*- coding: utf-8 -*-

from __future__ import division

from builtins import str
from builtins import object

from math import floor, ceil

from typing import Tuple, List

import numpy as np

from osgeo import osr

from qgis.core import *
from qgis.gui import *

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from .exceptions import *

from ..pygsf.libs_utils.gdal.gdal import *


class QGisRasterParameters(object):

    def __init__(self, name, cellsizeEW, cellsizeNS, rows, cols, xMin, xMax, yMin, yMax, nodatavalue, crs):
        """

        :param name:
        :param cellsizeEW:
        :param cellsizeNS:
        :param rows:
        :param cols:
        :param xMin:
        :param xMax:
        :param yMin:
        :param yMax:
        :param nodatavalue:
        :param crs:
        """

        self.name = name
        self.cellsizeEW = cellsizeEW
        self.cellsizeNS = cellsizeNS
        self.rows = rows
        self.cols = cols
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        self.nodatavalue = nodatavalue
        self.crs = crs

    def point_in_dem_area(self, point):
        """
        Check that a point is within or on the boundary of the grid area.
        Assume grid has no rotation.

        :param point: pygsf.vectorial.vectorial.Point
        :return: bool
        """

        if self.xMin <= point.x <= self.xMax and \
                self.yMin <= point.y <= self.yMax:
            return True
        else:
            return False

    def point_in_interpolation_area(self, point):
        """
        Check that a point is within or on the boundary of the area defined by
        the extreme cell center values.
        Assume grid has no rotation.

        :param point: pygsf.vectorial.vectorial.Point
        :return: bool
        """

        if self.xMin + self.cellsizeEW / 2.0 <= point.x <= self.xMax - self.cellsizeEW / 2.0 and \
                self.yMin + self.cellsizeNS / 2.0 <= point.y <= self.yMax - self.cellsizeNS / 2.0:
            return True
        else:
            return False

    def geogr2raster(self, point):
        """
        Convert from geographic to rasters-based coordinates.
        Assume grid has no rotation.

        :param point: qProf.gsf.geometry.Point
        :return: dict
        """

        x = (point.x - (self.xMin + self.cellsizeEW / 2.0)) / self.cellsizeEW
        y = (point.y - (self.yMin + self.cellsizeNS / 2.0)) / self.cellsizeNS

        return dict(x=x, y=y)

    def raster2geogr(self, array_dict):
        """
        Convert from rasters-based to geographic coordinates.
        Assume grid has no rotation.

        :param array_dict: dict
        :return: qProf.gsf.geometry.Point instance
        """

        assert 'x' in array_dict
        assert 'y' in array_dict

        x = self.xMin + (array_dict['x'] + 0.5) * self.cellsizeEW
        y = self.yMin + (array_dict['y'] + 0.5) * self.cellsizeNS

        return x, y


def get_on_the_fly_projection(canvas):
    """
    Determines if the on-the-fly projection is set and, when set, its value

    :param canvas:
    :return:
    """

    on_the_fly_projection = True

    if on_the_fly_projection:
        project_crs = canvas.mapSettings().destinationCrs()
    else:
        project_crs = None

    return on_the_fly_projection, project_crs


def vector_type(layer):
    """
    Determines the vectorial geometry type of layer features.

    :param layer:
    :return: text representing the geometry type
    """

    if not layer.type() == QgsMapLayer.VectorLayer:
        raise QgisIOException("Layer is not vector")

    if layer.geometryType() == QgsWkbTypes.PointGeometry:
        return "point"
    elif layer.geometryType() == QgsWkbTypes.LineGeometry:
        return "line"
    elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
        return "polygon"
    else:
        raise QgisIOException("Unknown vector type")


def loaded_layers():
    """
    Returns the layers, rasters and vectorial, loaded in the map.

    :return:
    """

    return list(QgsProject.instance().mapLayers().values())


def loaded_vector_layers():
    """
    Returns the vectorial layers loaded in the map.

    :return:
    """

    return list(filter(lambda layer: layer.type() == QgsMapLayer.VectorLayer,
                  loaded_layers()))


def loaded_polygon_layers():
    """
    Returns the polygonal layers loaded in the map.

    :return:
    """

    return list(filter(lambda layer: layer.geometryType() == QgsWkbTypes.PolygonGeometry,
                  loaded_vector_layers()))


def loaded_line_layers():
    """
    Returns the line layers loaded in the map.

    :return:
    """

    return list(filter(lambda layer: layer.geometryType() == QgsWkbTypes.LineGeometry,
                  loaded_vector_layers()))


def loaded_point_layers():
    """
    Returns the point layers loaded in the map.

    :return:
    """

    return list(filter(lambda layer: layer.geometryType() == QgsWkbTypes.PointGeometry,
                  loaded_vector_layers()))


def loaded_raster_layers():
    """
    Returns the rasters layers loaded in the map.

    :return:
    """

    return list(filter(lambda layer: layer.type() == QgsMapLayer.RasterLayer,
                  loaded_layers()))


def loaded_monoband_raster_layers():
    """
    Returns the single-band rasters layers loaded in the map.

    :return:
    """

    return list(filter(lambda layer: layer.bandCount() == 1,
                  loaded_raster_layers()))


def layer_name_source(layer: QgsMapLayer) -> Tuple[str, str]:
    """
    Returns the name and the source path of the layer.

    :param layer: the layer from which to extract name and source.
    :type layer: QgsMapLayer.
    :return: the layer name and source.
    :rtype: tuple of two strings.

    Examples:
    """

    return layer.name(), layer.source()


def layers_names_sources(layers: List[QgsMapLayer]) -> List[Tuple[str, str]]:
    """
    Returns the name and the source path of the layer.

    :param layers: list of the layers from which to extract names and sources.
    :type layers: list of QgsMapLayer instances.
    :return: a list storing for each layer its name and source.
    :rtype: list of tuples made up by two strings.

    Examples:
    """

    return list(map(layer_name_source, layers))


def pt_geoms_attrs(pt_layer, field_list=None):
    """
    Returns list of points coordinates and attributes.

    :param pt_layer:
    :param field_list:
    :return:
    """

    if field_list is None:
        field_list = []

    if pt_layer.selectedFeatureCount() > 0:
        features = pt_layer.selectedFeatures()
    else:
        features = pt_layer.getFeatures()

    provider = pt_layer.dataProvider()
    field_indices = [provider.fieldNameIndex(field_name) for field_name in field_list if field_name]

    # retrieve selected features with their geometry and relevant attributes
    rec_list = []
    for feature in features:

        # fetch point geometry
        pt = feature.geometry().asPoint()

        attrs = feature.fields().toList()

        # creates feature attribute list
        feat_list = [pt.x(), pt.y()]
        for field_ndx in field_indices:
            feat_list.append(str(feature.attribute(attrs[field_ndx].name())))

        # add to result list
        rec_list.append(feat_list)

    return rec_list


def line_geoms_attrs(line_layer, field_list=None):
    """
    Returns list of line points coordinates and attributes.

    :param line_layer:
    :param field_list:
    :return:
    """

    if field_list is None:
        field_list = []

    lines = []

    if line_layer.selectedFeatureCount() > 0:
        features = line_layer.selectedFeatures()
    else:
        features = line_layer.getFeatures()

    provider = line_layer.dataProvider()
    field_indices = [provider.fieldNameIndex(field_name) for field_name in field_list]

    for feature in features:
        geom = feature.geometry()
        if geom.isMultipart():
            rec_geom = multipolyline_to_xytuple_list2(geom.asMultiPolyline())
        else:
            rec_geom = [polyline_to_xytuple_list(geom.asPolyline())]

        attrs = feature.fields().toList()
        rec_data = [str(feature.attribute(attrs[field_ndx].name())) for field_ndx in field_indices]

        lines.append([rec_geom, rec_data])

    return lines


def line_geoms_with_id(line_layer, curr_field_ndx):
    """
    Returns list of counter, point coordinates and attributes.

    :param line_layer:
    :param curr_field_ndx:
    :return:
    """

    lines = []
    progress_ids = []

    if line_layer.selectedFeatureCount() > 0:
        features = line_layer.selectedFeatures()
    else:
        features = line_layer.getFeatures()

    dummy_progressive = 0
    for feature in features:
        try:
            progress_ids.append(int(feature[curr_field_ndx]))
        except:
            dummy_progressive += 1
            progress_ids.append(dummy_progressive)

        geom = feature.geometry()
        if geom.isMultipart():
            lines.append(
                ('multiline', multipolyline_to_xytuple_list2(geom.asMultiPolyline())))  # typedef QVector<QgsPolyline>
            # now is a list of list of (x,y) tuples
        else:
            lines.append(('line', polyline_to_xytuple_list(geom.asPolyline())))  # typedef QVector<QgsPointXY>

    return lines, progress_ids


def polyline_to_xytuple_list(qgsline):
    """

    :param qgsline:
    :return:
    """

    if len(qgsline) == 0:
        raise QgisIOException("Input line is null")

    return [(qgspoint.x(), qgspoint.y()) for qgspoint in qgsline]


def multipolyline_to_xytuple_list2(qgspolyline):
    """

    :param qgspolyline:
    :return:
    """

    return [polyline_to_xytuple_list(qgsline) for qgsline in qgspolyline]


def field_values(layer, curr_field_ndx):
    """
    Returns the values of the selected records associated with a given field index.

    :param layer:
    :param curr_field_ndx:
    :return:
    """

    values = []

    if layer.selectedFeatureCount() > 0:
        features = layer.selectedFeatures()
    else:
        features = layer.getFeatures()

    for feature in features:
        values.append(feature.attributes()[curr_field_ndx])

    return values


def vect_attrs(layer, field_list):
    """
    Returns the values of the selected records associated with a given field names list.

    :param layer:
    :param field_list:
    :return:
    """

    if layer.selectedFeatureCount() > 0:
        features = layer.selectedFeatures()
    else:
        features = layer.getFeatures()

    provider = layer.dataProvider()
    field_indices = [provider.fieldNameIndex(field_name) for field_name in field_list]

    # retrieve (selected) attributes features
    data_list = []
    for feature in features:
        attrs = feature.fields().toList()
        data_list.append([feature.attribute(attrs[field_ndx].name()) for field_ndx in field_indices])

    return data_list


def raster_qgis_params(raster_layer):
    """
    Extracts parameters for a given rasters layer.

    :param raster_layer:
    :return:
    """

    name = raster_layer.name()

    rows = raster_layer.height()
    cols = raster_layer.width()

    extent = raster_layer.extent()

    xMin = extent.xMinimum()
    xMax = extent.xMaximum()
    yMin = extent.yMinimum()
    yMax = extent.yMaximum()

    cellsizeEW = (xMax - xMin) / float(cols)
    cellsizeNS = (yMax - yMin) / float(rows)

    # TODO: get real no data value from QGIS
    if raster_layer.dataProvider().sourceHasNoDataValue(1):
        nodatavalue = raster_layer.dataProvider().sourceNoDataValue(1)
    else:
        nodatavalue = np.nan

    try:
        crs = raster_layer.crs()
    except:
        crs = None

    return name, cellsizeEW, cellsizeNS, rows, cols, xMin, xMax, yMin, yMax, nodatavalue, crs


def qgs_pt(x, y):
    """
    Creates a QGIS point from a x-y values pair.

    :param x:
    :param y:
    :return:
    """

    return QgsPointXY(x, y)


def project_qgs_point(qgsPt, srcCrs, destCrs):
    """
    Project a QGIS point to a given CRS from a source CRS.

    :param qgsPt:
    :param srcCrs:
    :param destCrs:
    :return:
    """

    return QgsCoordinateTransform(srcCrs, destCrs, QgsProject.instance()).transform(qgsPt)


def project_point(pt, srcCrs, destCrs):
    """
    Project a point to a given CRS from a source CRS.

    :param pt:
    :param srcCrs:
    :param destCrs:
    :return:
    """

    qgs_pt = QgsPointXY(pt.x, pt.y)
    proj_qgs_pt = project_qgs_point(qgs_pt, srcCrs, destCrs)
    proj_x, proj_y = proj_qgs_pt.x(), proj_qgs_pt.y()

    return proj_x, proj_y


def project_xy_list(src_crs_xy_list, srcCrs, destCrs):
    """

    :param src_crs_xy_list:
    :param srcCrs:
    :param destCrs:
    :return:
    """

    pt_list_dest_crs = []
    for x, y in src_crs_xy_list.pts:
        srcPt = QgsPointXY(x, y)
        destPt = project_qgs_point(srcPt, srcCrs, destCrs)
        pt_list_dest_crs = pt_list_dest_crs.append([destPt.x(), destPt.y()])

    return pt_list_dest_crs


def get_z(dem_layer, point):
    """
    Get the z value from a grid given a sampling point.

    :param dem_layer:
    :param point:
    :return:
    """

    identification = dem_layer.dataProvider().identify(QgsPointXY(point.x, point.y), QgsRaster.IdentifyFormatValue)
    if not identification.isValid():
        return np.nan
    else:
        try:
            result_map = identification.results()
            return float(result_map[1])
        except:
            return np.nan


def interpolate_bilinear(dem, qrpDemParams, point):
    """
    Interpolate the z value from a grid using the bilinear convolution.

    :param dem: qgis_utils._core.QgsRasterLayer
    :param qrpDemParams: qProf.gis_utils.qgs_tools.QGisRasterParameters
    :param point: qProf.gis_utils.features.Point
    :return: float
    """

    dArrayCoords = qrpDemParams.geogr2raster(point)

    floor_x_raster = floor(dArrayCoords["x"])
    ceil_x_raster = ceil(dArrayCoords["x"])
    floor_y_raster = floor(dArrayCoords["y"])
    ceil_y_raster = ceil(dArrayCoords["y"])

    # bottom-left center
    p1 = qrpDemParams.raster2geogr(dict(x=floor_x_raster,
                                        y=floor_y_raster))
    # bottom-right center
    p2 = qrpDemParams.raster2geogr(dict(x=ceil_x_raster,
                                        y=floor_y_raster))
    # top-left center
    p3 = qrpDemParams.raster2geogr(dict(x=floor_x_raster,
                                        y=ceil_y_raster))
    # top-right center
    p4 = qrpDemParams.raster2geogr(dict(x=ceil_x_raster,
                                        y=ceil_y_raster))

    z1 = get_z(dem, p1)
    z2 = get_z(dem, p2)
    z3 = get_z(dem, p3)
    z4 = get_z(dem, p4)

    delta_x = point.x - p1.x
    delta_y = point.y - p1.y

    z_x_a = z1 + (z2 - z1) * delta_x / qrpDemParams.cellsizeEW
    z_x_b = z3 + (z4 - z3) * delta_x / qrpDemParams.cellsizeEW

    return z_x_a + (z_x_b - z_x_a) * delta_y / qrpDemParams.cellsizeNS


def interpolate_z(dem, dem_params, point):
    """
    Interpolate the z value from a grid using bilinear convolution when possible.

    :type dem:
    :type dem_params: type qProf.gis_utils.qgs_tools.QGisRasterParameters
    :type point: type qProf.gis_utils.features.Point
    :return: interpolated z value
    :rtype: float
    """

    if dem_params.point_in_interpolation_area(point):
        return interpolate_bilinear(dem, dem_params, point)
    elif dem_params.point_in_dem_area(point):
        return get_z(dem, point)
    else:
        return np.nan


def get_zs_from_dem(struct_pts_2d, demObj):
    """
    Extracts interpolated z values from dem.

    :param struct_pts_2d:
    :param demObj:
    :return: interpolated z values
    :rtype: list of float values
    """

    z_list = []
    for point_2d in struct_pts_2d:
        interp_z = interpolate_z(demObj.layer, demObj.params, point_2d)
        z_list.append(interp_z)

    return z_list


def xy_from_canvas(canvas, position):
    """
    Returns tuple of x, y coordinates from a position in the canvas.

    :param canvas:
    :param position:
    :return: x and y coordinates
    :rtype: tuple of two float values
    """

    mapPos = canvas.getCoordinateTransform().toMapCoordinates(position["x"], position["y"])

    return mapPos.x(), mapPos.y()


def get_prjcrs_as_proj4str(canvas):
    """
    Get project CRS information.

    :param canvas:
    :return:
    """

    hasOTFP, project_crs = get_on_the_fly_projection(canvas)
    if hasOTFP:
        proj4_str = str(project_crs.toProj4())
        project_crs_osr = osr.SpatialReference()
        project_crs_osr.ImportFromProj4(proj4_str)
        return project_crs_osr
    else:
        return None





