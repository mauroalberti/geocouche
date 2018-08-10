# -*- coding: utf-8 -*-


import os

from osgeo import ogr, osr

from .exceptions import *


def read_line_shapefile_via_ogr(line_shp_path):
    """
    Read line shapefile using OGR.

    :param  line_shp_path:  parameter to check.
    :type  line_shp_path:  QString or string
    """

    # reset layer parameters

    if line_shp_path is None or line_shp_path == '':
        return dict(success=False, error_message='No input path')

        # open input vector layer
    shape_driver = ogr.GetDriverByName("ESRI Shapefile")

    line_shape = shape_driver.Open(str(line_shp_path), 0)

    # layer not read
    if line_shape is None:
        return dict(success=False, error_message='Unable to open input shapefile')

        # get internal layer
    lnLayer = line_shape.GetLayer(0)

    # set vector layer extent
    layer_extent = lnLayer.GetExtent()
    lines_extent = {'xmin': layer_extent[0], 'xmax': layer_extent[1], 'ymin': layer_extent[2], 'ymax': layer_extent[3]}

    # initialize lists storing vertex coordinates of line
    lines_points = []

    # start reading layer features
    curr_line = lnLayer.GetNextFeature()

    # loop in layer features
    while curr_line:

        line_points = []

        line_geom = curr_line.GetGeometryRef()

        if line_geom is None:
            line_shape.Destroy()
            return dict(success=False, error_message='No geometry ref')

        if line_geom.GetGeometryType() != ogr.wkbLineString and \
                        line_geom.GetGeometryType() != ogr.wkbMultiLineString:
            line_shape.Destroy()
            return dict(success=False, error_message='Not a linestring/multilinestring')

        for i in range(line_geom.GetPointCount()):
            x, y, z = line_geom.GetX(i), line_geom.GetY(i), line_geom.GetZ(i)

            line_points.append((x, y, z))

        lines_points.append(line_points)

        curr_line = lnLayer.GetNextFeature()

    line_shape.Destroy()

    return dict(success=True, extent=lines_extent, vertices=lines_points)


def shapefile_create_def_field(field_def):
    """

    :param field_def:
    :return:
    """

    fieldDef = ogr.FieldDefn(field_def['name'], field_def['ogr_type'])
    if field_def['ogr_type'] == ogr.OFTString:
        fieldDef.SetWidth(field_def['width'])

    return fieldDef


def shapefile_create(path, geom_type, fields_dict_list, crs=None):
    """
    crs_prj4: projection in Proj4 text format
    geom_type = OGRwkbGeometryType: ogr.wkbPoint, ....
    list of:
        field dict: 'name',
                    'type': ogr.OFTString,
                            ogr.wkbLineString,
                            ogr.wkbLinearRing,
                            ogr.wkbPolygon,

                    'width',
    """

    driver = ogr.GetDriverByName("ESRI Shapefile")

    outShapefile = driver.CreateDataSource(str(path))
    if outShapefile is None:
        raise OGRIOException('Unable to save shapefile in provided path')

    if crs is not None:
        spatialReference = osr.SpatialReference()
        spatialReference.ImportFromProj4(crs)
        outShapelayer = outShapefile.CreateLayer("layer", geom_type, spatialReference)
    else:
        outShapelayer = outShapefile.CreateLayer("layer", geom_type=geom_type)

    map(lambda field_def_params: outShapelayer.CreateField(shapefile_create_def_field(field_def_params)),
        fields_dict_list)

    return outShapefile, outShapelayer


def ogr_get_solution_shapefile(path, fields_dict_list):
    """

    :param path:
    :param fields_dict_list:
    :return:
    """

    driver = ogr.GetDriverByName("ESRI Shapefile")

    dataSource = driver.Open(str(path), 0)

    if dataSource is None:
        raise OGRIOException("Unable to open shapefile in provided path")

    point_shapelayer = dataSource.GetLayer()

    prev_solution_list = []
    in_point = point_shapelayer.GetNextFeature()
    while in_point:
        rec_id = int(in_point.GetField('id'))
        x = in_point.GetField('x')
        y = in_point.GetField('y')
        z = in_point.GetField('z')
        dip_dir = in_point.GetField('dip_dir')
        dip_ang = in_point.GetField('dip_ang')
        descript = in_point.GetField('descript')
        prev_solution_list.append([rec_id, x, y, z, dip_dir, dip_ang, descript])
        in_point.Destroy()
        in_point = point_shapelayer.GetNextFeature()

    dataSource.Destroy()

    if os.path.exists(path):
        driver.DeleteDataSource(str(path))

    outShapefile, outShapelayer = shapefile_create(path, ogr.wkbPoint25D, fields_dict_list, crs=None)
    return outShapefile, outShapelayer, prev_solution_list


def ogr_write_point_result(point_shapelayer, field_list, rec_values_list2, geom_type=ogr.wkbPoint25D):
    """

    :param point_shapelayer:
    :param field_list:
    :param rec_values_list2:
    :param geom_type:
    :return:
    """

    outshape_featdef = point_shapelayer.GetLayerDefn()

    for rec_value_list in rec_values_list2:

        # pre-processing for new feature in output layer
        curr_Pt_geom = ogr.Geometry(geom_type)
        if geom_type == ogr.wkbPoint25D:
            curr_Pt_geom.AddPoint(rec_value_list[1], rec_value_list[2], rec_value_list[3])
        else:
            curr_Pt_geom.AddPoint(rec_value_list[1], rec_value_list[2])

        # create a new feature
        curr_Pt_shape = ogr.Feature(outshape_featdef)
        curr_Pt_shape.SetGeometry(curr_Pt_geom)

        for fld_name, fld_value in zip(field_list, rec_value_list):
            curr_Pt_shape.SetField(fld_name, fld_value)

        # add the feature to the output layer
        point_shapelayer.CreateFeature(curr_Pt_shape)

        # destroy no longer used objects
        curr_Pt_geom.Destroy()
        curr_Pt_shape.Destroy()


