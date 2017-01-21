# -*- coding: utf-8 -*-

from PyQt4.QtGui import *


from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs
from auxiliary_windows import StereoplotSrcPtLyrDia, StereoplotSrcValuesDia
from processing import plot_stereonet
from structural_userdefs import parse_stereoplot_geodata, ptlayer_valid_params, \
                                get_input_ptlayer_params, get_stereoplot_data_type, \
                                get_input_values_params


class stereoplot_QWidget(QWidget):

    def __init__(self, canvas, plugin_name):

        super(stereoplot_QWidget, self).__init__()
        self.mapcanvas = canvas
        self.plugin_name = plugin_name

        self.input_ptlayer = None
        self.input_ptlayer_params = None

        self.setup_gui()

    def setup_gui(self):

        self.dialog_layout = QHBoxLayout()

        self.dialog_layout.addWidget(self.setup_inputdata())
        self.dialog_layout.addWidget(self.setup_processing())

        self.setLayout(self.dialog_layout)
        self.adjustSize()
        self.setWindowTitle(self.plugin_name)

    def setup_inputdata(self):

        input_QGroupBox = QGroupBox("Input")

        layout = QVBoxLayout()

        self.define_point_layer_QPushButton = QPushButton(self.tr("Point layer"))
        self.define_point_layer_QPushButton.clicked.connect(self.define_pointlayer_params)
        layout.addWidget(self.define_point_layer_QPushButton)

        self.define_values_QPushButton = QPushButton(self.tr("Numeric values"))
        self.define_values_QPushButton.clicked.connect(self.define_numvalues_params)
        layout.addWidget(self.define_values_QPushButton)

        input_QGroupBox.setLayout(layout)

        return input_QGroupBox

    def setup_processing(self):

        processing_QGroupBox = QGroupBox("Processing")

        layout = QGridLayout()

        self.plot_stereonet_QPushButton = QPushButton(self.tr("Plot stereonet"))
        self.plot_stereonet_QPushButton.clicked.connect(self.plot_stereoplot)
        layout.addWidget(self.plot_stereonet_QPushButton, 0, 0, 1, 1)

        processing_QGroupBox.setLayout(layout)

        return processing_QGroupBox

    def define_pointlayer_params(self):

        self.input_ptlayer_params = None

        if len(loaded_point_layers()) == 0:
            self.warn("No available point layers")
            return

        dialog = StereoplotSrcPtLyrDia()
        if dialog.exec_():
            try:
                input_ptlayer, input_ptlayer_params = get_input_ptlayer_params(dialog)
            except:
                self.warn("Incorrect definition")
                return
        else:
            self.warn("Nothing defined")
            return

        if not ptlayer_valid_params(input_ptlayer_params):
            self.warn("Invalid/incomplete parameters")
            return
        else:
            self.info("Input data defined")

        self.input_ptlayer = input_ptlayer
        self.input_ptlayer_params = input_ptlayer_params

    def plot_stereoplot(self):

        # check definition of input point layer
        if self.input_ptlayer is None or \
           self.input_ptlayer_params is None:
            self.warn(str("Input point layer/parameters not defined"))
            return

        # get used field names in the point attribute table
        attitude_fldnms = [self.input_ptlayer_params["plane_azimuth_name_field"],
                           self.input_ptlayer_params["plane_dip_name_field"],
                           self.input_ptlayer_params["line_azimuth_name_field"],
                           self.input_ptlayer_params["line_dip_name_field"]]

        # get input data presence and type
        structural_data = pt_geoms_attrs(self.input_ptlayer, attitude_fldnms)
        input_data_types = get_stereoplot_data_type(self.input_ptlayer_params)

        try:
            _, plane_orientations, lineament_orientations = parse_stereoplot_geodata(input_data_types, structural_data)
        except Exception, msg:
            self.warn(str(msg))
            return

        if plane_orientations is None and lineament_orientations is None:
            self.warn("No available structural data to plot")
            return

        plot_stereonet(plane_orientations, lineament_orientations)

    def define_numvalues_params(self):

        self.stereoplot_numvalues_params = None

        dialog = StereoplotSrcValuesDia()
        if dialog.exec_():
            try:
                plane_azimuth_type, values = get_input_values_params(dialog)
            except:
                self.warn("Incorrect definition")
                return
        else:
            self.warn("Nothing defined")
            return

        self.warn("Processings to be implemented")















    def info(self, msg):

        QMessageBox.information(self, self.plugin_name, msg)

    def warn(self, msg):

        QMessageBox.warning(self, self.plugin_name, msg)

        


