# -*- coding: utf-8 -*-

"""
/***************************************************************************
 geocouche - plugin for Quantum GIS

 geologic stereoplots
-------------------

    Begin                : 2015.04.18
    Date                 : 2017.02.25
    Copyright            : (C) 2015-2017 by Mauro Alberti
    Email                : alberti dot m65 at gmail dot com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from osgeo import ogr

from geosurf.qgs_tools import pt_geoms_attrs, loaded_point_layers
from geosurf.spatial import GeolPlane
from geosurf.geo_io import shapefile_create, ogr_write_point_result
from auxiliary_windows import AnglesSrcPtLyrDia
from structural_userdefs import get_anglecalc_input_params, formally_valid_angles_params, \
                                parse_angles_geodata, get_angle_data_type


class AnglesWidget(QWidget):

    sgnWindowClosed = pyqtSignal()

    def __init__(self, canvas, plugin_name):

        super(AnglesWidget, self).__init__()
        self.mapCanvas = canvas
        self.pluginName = plugin_name

        self.pointLayer = None
        self.anglesAnalysisParams = None

        self.setup_gui()

    def setup_gui(self): 

        self.layout = QHBoxLayout()
        
        self.layout.addWidget(self.setup_inputdata())
        self.layout.addWidget(self.setup_processing())
                                                           
        self.setLayout(self.layout)
        self.setWindowTitle("Angles")
        self.adjustSize()

    def setup_inputdata(self):
        
        grpInput = QGroupBox("Input")
        
        layout = QVBoxLayout() 
        
        self.pshDefinePointLayer = QPushButton(self.tr("Define input/output parameters"))
        self.pshDefinePointLayer.clicked.connect(self.user_define_angles_inparams)
        layout.addWidget(self.pshDefinePointLayer)
        
        grpInput.setLayout(layout)
        
        return grpInput

    def setup_processing(self):
        
        grpProcessing = QGroupBox("Processing")
        
        layout = QGridLayout()

        self.pshCalculateAngles = QPushButton(self.tr("Calculate angles"))
        self.pshCalculateAngles.clicked.connect(self.calculate_angles)
        layout.addWidget(self.pshCalculateAngles, 0, 0, 1, 1)

        grpProcessing.setLayout(layout)
        
        return grpProcessing

    def user_define_angles_inparams(self):

        self.anglesAnalysisParams = None

        if len(loaded_point_layers()) == 0:
            self.warn("No available point layers")
            return

        dialog = AnglesSrcPtLyrDia()
        if dialog.exec_():
            try:
                point_layer, structural_input_params = get_anglecalc_input_params(dialog)
            except:
                self.warn("Incorrect definition")
                return
        else:
            self.warn("Nothing defined")
            return

        if not formally_valid_angles_params(structural_input_params):
            self.warn("Invalid/incomplete parameters")
            return
        else:
            self.info("Input data defined")

        self.pointLayer, self.anglesAnalysisParams = point_layer, structural_input_params

    def calculate_angles(self):

        # check definition of input point layer
        if self.pointLayer is None or \
           self.anglesAnalysisParams is None:
            self.warn(str("Input point layer/parameters not defined"))
            return

        # get used field names in the point attribute table 
        lAttitudeFldnms = [self.anglesAnalysisParams["plane_azimuth_name_field"],
                           self.anglesAnalysisParams["plane_dip_name_field"]]

        # get input data presence and type
        structural_data = pt_geoms_attrs(self.pointLayer, lAttitudeFldnms)
        input_data_types = get_angle_data_type(self.anglesAnalysisParams)
           
        try:  
            xy_coords, plane_orientations = parse_angles_geodata(input_data_types, structural_data)
        except Exception, msg:
            self.warn(str(msg))
            return

        if plane_orientations is None:
            self.warn("Plane orientations are not available")
            return

        target_plane_dipdir = self.anglesAnalysisParams["target_dipdir"]
        target_plane_dipangle = self.anglesAnalysisParams["target_dipangle"]
        trgt_geolplane = GeolPlane(target_plane_dipdir, target_plane_dipangle)
        angles = []
        for plane_or in plane_orientations:
            angles.append(trgt_geolplane.angle_degr(GeolPlane(*plane_or)))

        fields_dict_list = [dict(name='id', ogr_type=ogr.OFTInteger),
                            dict(name='x', ogr_type=ogr.OFTReal),
                            dict(name='y', ogr_type=ogr.OFTReal),
                            dict(name='results', ogr_type=ogr.OFTReal)]

        point_shapefile, point_shapelayer = shapefile_create(self.anglesAnalysisParams["output_shapefile_path"],
                                                             ogr.wkbPoint,
                                                             fields_dict_list)

        lFields = [field_dict["name"] for field_dict in fields_dict_list]

        rngIds = range(len(angles))
        x = map(lambda val: val[0], xy_coords)
        y = map(lambda val: val[1], xy_coords)
        llRecValues = zip(rngIds, x, y, angles)
        ogr_write_point_result(point_shapelayer, lFields, llRecValues, geom_type=ogr.wkbPoint)

        self.info("Output shapefile written")


    def info(self, msg):
        
        QMessageBox.information(self, self.pluginName, msg)

    def warn(self, msg):
    
        QMessageBox.warning(self, self.pluginName, msg)

    def closeEvent(self, event):

        settings = QSettings("www.malg.eu", "geocouche")
        settings.setValue("AnglesWidget/Size", self.size())
        settings.setValue("AnglesWidget/Position", self.pos())

        self.sgnWindowClosed.emit()