# -*- coding: utf-8 -*-

from PyQt4.QtGui import *


from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs
from auxiliary_windows import StereoplotSrcPtLyrDia
from processing import plot_stereonet
from structural_userdefs import parse_stereoplot_geodata, formally_valid_stereoplot_params, \
                                get_stereoplot_input_params, get_stereoplot_field_names, \
                                get_stereoplot_data_type


class stereoplot_QWidget(QWidget):

    def __init__(self, canvas, plugin_name):

        super(stereoplot_QWidget, self).__init__()
        self.mapcanvas = canvas
        self.plugin_name = plugin_name

        self.point_layer = None
        self.stereoplot_input_params = None

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

        self.define_point_layer_QPushButton = QPushButton(self.tr("Define point layer"))
        self.define_point_layer_QPushButton.clicked.connect(self.user_define_stereoplot_inparams)
        layout.addWidget(self.define_point_layer_QPushButton)

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

    def user_define_stereoplot_inparams(self):

        self.stereoplot_input_params = None

        if len(loaded_point_layers()) == 0:
            self.warn("No available point layers")
            return

        dialog = StereoplotSrcPtLyrDia()
        if dialog.exec_():
            try:
                point_layer, structural_input_params = get_stereoplot_input_params(dialog)
            except:
                self.warn("Incorrect definition")
                return
        else:
            self.warn("Nothing defined")
            return

        if not formally_valid_stereoplot_params(structural_input_params):
            self.warn("Invalid/incomplete parameters")
            return
        else:
            self.info("Input data defined")

        self.point_layer = point_layer
        self.stereoplot_input_params = structural_input_params

    def plot_stereoplot(self):

        # check definition of input point layer
        if self.point_layer is None or \
           self.stereoplot_input_params is None:
            self.warn(str("Input point layer/parameters not defined"))
            return

        # get used field names in the point attribute table
        actual_field_names = get_stereoplot_field_names(self.stereoplot_input_params)

        # get input data presence and type
        structural_data = pt_geoms_attrs(self.point_layer, actual_field_names)
        input_data_types = get_stereoplot_data_type(self.stereoplot_input_params)

        try:
            _, plane_orientations, lineament_orientations = parse_stereoplot_geodata(input_data_types, structural_data)
        except Exception, msg:
            self.warn(str(msg))
            return

        plot_stereonet(plane_orientations, lineament_orientations)

    def info(self, msg):

        QMessageBox.information(self, self.plugin_name, msg)

    def warn(self, msg):

        QMessageBox.warning(self, self.plugin_name, msg)

        


