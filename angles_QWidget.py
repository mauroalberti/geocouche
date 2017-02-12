# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from osgeo import ogr

from geosurf.qgs_tools import pt_geoms_attrs, loaded_point_layers
from geosurf.spatial import GeolPlane
from geosurf.geo_io import shapefile_create, ogr_write_point_result
from auxiliary_windows import AnglesSrcPtLyrDia
from structural_userdefs import get_anglecalc_input_params, formally_valid_angles_params, \
                                parse_angles_geodata, get_angle_data_type


class angles_QWidget(QWidget):

    window_closed = pyqtSignal()

    def __init__(self, canvas, plugin_name):

        super(angles_QWidget, self).__init__()
        self.mapcanvas = canvas        
        self.plugin_name = plugin_name

        self.point_layer = None
        self.angles_analysis_params = None

        self.setup_gui()

    def setup_gui(self): 

        self.layout = QHBoxLayout()
        
        self.layout.addWidget(self.setup_inputdata())
        self.layout.addWidget(self.setup_processing())
                                                           
        self.setLayout(self.layout)
        self.setWindowTitle("Angles")
        self.adjustSize()

    def setup_inputdata(self):
        
        input_QGroupBox = QGroupBox("Input")
        
        layout = QVBoxLayout() 
        
        self.define_point_layer_QPushButton = QPushButton(self.tr("Define input/output parameters"))
        self.define_point_layer_QPushButton.clicked.connect(self.user_define_angles_inparams)
        layout.addWidget(self.define_point_layer_QPushButton)
        
        input_QGroupBox.setLayout(layout)
        
        return input_QGroupBox

    def setup_processing(self):
        
        processing_QGroupBox = QGroupBox("Processing")
        
        layout = QGridLayout()

        self.calculate_angles_QPushButton = QPushButton(self.tr("Calculate angles"))
        self.calculate_angles_QPushButton.clicked.connect(self.calculate_angles)
        layout.addWidget(self.calculate_angles_QPushButton, 0, 0, 1, 1)

        processing_QGroupBox.setLayout(layout)
        
        return processing_QGroupBox

    def user_define_angles_inparams(self):

        self.angles_analysis_params = None

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

        self.point_layer, self.angles_analysis_params = point_layer, structural_input_params

    def calculate_angles(self):

        # check definition of input point layer
        if self.point_layer is None or \
           self.angles_analysis_params is None:
            self.warn(str("Input point layer/parameters not defined"))
            return

        # get used field names in the point attribute table 
        attitude_fldnms = [self.angles_analysis_params["plane_azimuth_name_field"],
                           self.angles_analysis_params["plane_dip_name_field"]]

        # get input data presence and type
        structural_data = pt_geoms_attrs(self.point_layer, attitude_fldnms)
        input_data_types = get_angle_data_type(self.angles_analysis_params)
           
        try:  
            xy_coords, plane_orientations = parse_angles_geodata(input_data_types, structural_data)
        except Exception, msg:
            self.warn(str(msg))
            return

        if plane_orientations is None:
            self.warn("Plane orientations are not available")
            return

        target_plane_dipdir = self.angles_analysis_params["target_dipdir"]
        target_plane_dipangle = self.angles_analysis_params["target_dipangle"]
        trgt_geolplane = GeolPlane(target_plane_dipdir, target_plane_dipangle)
        angles = []
        for plane_or in plane_orientations:
            angles.append(trgt_geolplane.angle_degr(GeolPlane(*plane_or)))

        fields_dict_list = [dict(name='id', ogr_type=ogr.OFTInteger),
                            dict(name='x', ogr_type=ogr.OFTReal),
                            dict(name='y', ogr_type=ogr.OFTReal),
                            dict(name='results', ogr_type=ogr.OFTReal)]

        point_shapefile, point_shapelayer = shapefile_create(self.angles_analysis_params["output_shapefile_path"],
                                                             ogr.wkbPoint,
                                                             fields_dict_list)

        field_list = [field_dict["name"] for field_dict in fields_dict_list]

        ids = range(len(angles))
        x = map(lambda val: val[0], xy_coords)
        y = map(lambda val: val[1], xy_coords)
        rec_values_list2 = zip(ids, x, y, angles)
        ogr_write_point_result(point_shapelayer, field_list, rec_values_list2, geom_type=ogr.wkbPoint)

        self.info("Output shapefile written")


    def info(self, msg):
        
        QMessageBox.information(self, self.plugin_name, msg)

    def warn(self, msg):
    
        QMessageBox.warning(self, self.plugin_name, msg)

    def closeEvent(self, event):

        settings = QSettings("www.malg.eu", "geocouche")
        settings.setValue("angles_QWidget/Size", self.size())
        settings.setValue("angles_QWidget/Position", self.pos())

        self.window_closed.emit()