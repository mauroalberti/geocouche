from __future__ import division

from builtins import str

import numpy as np

from qgis.core import *
from qgis.gui import *

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from .errors import VectorIOException
from ..gsf.geometry import Point


def get_on_the_fly_projection(canvas):

    on_the_fly_projection = True

    if on_the_fly_projection:
        project_crs = canvas.mapSettings().destinationCrs()
    else:
        project_crs = None

    return on_the_fly_projection, project_crs


def vector_type(layer):

    if not layer.type() == QgsMapLayer.VectorLayer:
        raise VectorIOException("Layer is not vector")

    if layer.geometryType() == QgsWkbTypes.PointGeometry:
        return "point"
    elif layer.geometryType() == QgsWkbTypes.LineGeometry:
        return "line"
    elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
        return "polygon"
    else:
        raise VectorIOException("Unknown vector type")


def loaded_layers():

    return list(QgsProject.instance().mapLayers().values())


def loaded_vector_layers():

    return [layer for layer in loaded_layers() if layer.type() == QgsMapLayer.VectorLayer]


def loaded_polygon_layers():

    return [layer for layer in loaded_vector_layers() if layer.geometryType() == QgsWkbTypes.PolygonGeometry]


def loaded_line_layers():

    return [layer for layer in loaded_vector_layers() if layer.geometryType() == QgsWkbTypes.LineGeometry]


def loaded_point_layers():

    return [layer for layer in loaded_vector_layers() if layer.geometryType() == QgsWkbTypes.PointGeometry]


def loaded_raster_layers():

    return [layer for layer in loaded_layers() if layer.type() == QgsMapLayer.RasterLayer]


def loaded_monoband_raster_layers():

    return [layer for layer in loaded_raster_layers() if layer.bandCount() == 1]


def pt_geoms_attrs(pt_layer, field_list=None):

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

    assert len(qgsline) > 0
    return [(qgspoint.x(), qgspoint.y()) for qgspoint in qgsline]


def multipolyline_to_xytuple_list2(qgspolyline):

    return [polyline_to_xytuple_list(qgsline) for qgsline in qgspolyline]


def field_values(layer, curr_field_ndx):

    values = []

    if layer.selectedFeatureCount() > 0:
        features = layer.selectedFeatures()
    else:
        features = layer.getFeatures()

    for feature in features:
        values.append(feature.attributes()[curr_field_ndx])

    return values


def vect_attrs(layer, field_list):

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


def qgs_point_2d(x, y):
    return QgsPoint(x, y)


def project_qgs_point(qgsPt, srcCrs, destCrs):

    return QgsCoordinateTransform(srcCrs, destCrs, QgsProject.instance()).transform(qgsPt)


def project_point(pt, srcCrs, destCrs):

    qgs_pt = QgsPointXY(pt.x, pt.y)
    proj_qgs_pt = project_qgs_point(qgs_pt, srcCrs, destCrs)
    proj_x, proj_y = proj_qgs_pt.x(), proj_qgs_pt.y()

    return Point(proj_x, proj_y)


def project_xy_list(src_crs_xy_list, srcCrs, destCrs):

    pt_list_dest_crs = []
    for x, y in src_crs_xy_list.pts:
        srcPt = QgsPointXY(x, y)
        destPt = project_qgs_point(srcPt, srcCrs, destCrs)
        pt_list_dest_crs = pt_list_dest_crs.append([destPt.x(), destPt.y()])

    return pt_list_dest_crs


def qcolor2rgbmpl(qcolor):

    red = qcolor.red() / 255.0
    green = qcolor.green() / 255.0
    blue = qcolor.blue() / 255.0
    return red, green, blue

