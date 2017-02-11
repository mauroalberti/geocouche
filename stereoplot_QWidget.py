# -*- coding: utf-8 -*-

from PyQt4.QtGui import *
from qgis.gui import QgsColorButtonV2

from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs
from auxiliary_windows import StereoplotInputDialog
from processing import plot_new_stereonet, add_to_stereonet
from structural_userdefs import parse_ptlayer_geodata, ptlayer_valid_params, \
                                get_input_ptlayer_params, get_ptlayer_stereoplot_data_type, \
                                get_input_values_params, define_num_values


class stereoplot_QWidget(QWidget):

    def __init__(self, canvas, plugin_name):

        super(stereoplot_QWidget, self).__init__()
        self.mapcanvas = canvas
        self.plugin_name = plugin_name

        self.input_ptlayer = None
        self.input_ptlayer_params = None
        self.current_stereoplot = None
        self.color_name = '255,0,0,255'

        self.setup_gui()

    def setup_gui(self):

        self.layout = QVBoxLayout()

        self.define_input_QPB = QPushButton(self.tr("Input"))
        self.define_input_QPB.clicked.connect(self.define_input)
        self.layout.addWidget(self.define_input_QPB)

        self.define_plotas_QPB = QPushButton(self.tr("Plot as"))
        self.define_plotas_QPB.clicked.connect(self.define_plot_as)
        self.layout.addWidget(self.define_plotas_QPB)

        self.define_style_QPB = QPushButton(self.tr("Style"))
        self.define_style_QPB.clicked.connect(self.define_style)
        self.layout.addWidget(self.define_style_QPB)

        self.define_stereoplot_QPB = QPushButton(self.tr("Stereoplot"))
        self.define_stereoplot_QPB.clicked.connect(self.define_stereoplot)
        self.layout.addWidget(self.define_stereoplot_QPB)

        """
        DEAD CODE - to remove unused methods:
        self.dialog_layout.addWidget(self.setup_inputdata())
        self.dialog_layout.addWidget(self.setup_styling())
        self.dialog_layout.addWidget(self.setup_plotting())
        """

        self.setLayout(self.layout)
        self.adjustSize()
        self.setWindowTitle(self.plugin_name)


    def define_input(self):

        dialog = StereoplotInputDialog()
        if dialog.exec_():
            try:
                pass
                #input_ptlayer, input_ptlayer_params = get_input_ptlayer_params(dialog)
            except:
                self.warn("Incorrect definition")
                return
        else:
            return


    def define_plot_as(self):
        pass


    def define_style(self):
        pass


    def define_stereoplot(self):
        pass


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

    def setup_styling(self):

        style_QGroupBox = QGroupBox(self)
        style_QGroupBox.setTitle("Style")
        layout = QHBoxLayout()

        # color
        layout.addWidget(QLabel("Color"))
        red, green, blue, alpha = map(int, self.color_name.split(","))
        self.linecolor_QgsColorButtonV2 = QgsColorButtonV2()
        self.linecolor_QgsColorButtonV2.setColor(QColor(red, green, blue, alpha))
        #self.pencolor_QgsColorButtonV2.colorChanged['QColor'].connect(self.update_color_transparency)

        layout.addWidget(self.linecolor_QgsColorButtonV2)
        
        # transparency
        layout.addWidget(QLabel("Transp."))
        pen_transparencies = [0, 25, 50, 75]
        self.transparency_QComboBox = QComboBox()
        self.pen_transparencies_percent = [str(val) + "%" for val in pen_transparencies]
        self.transparency_QComboBox.insertItems(0, self.pen_transparencies_percent)
        #self.transparency_QComboBox.currentIndexChanged['QString'].connect(self.update_color_transparency)
        layout.addWidget(self.transparency_QComboBox)

        style_QGroupBox.setLayout(layout)

        return style_QGroupBox


    def setup_plotting(self):

        processing_QGroupBox = QGroupBox("Plotting")

        layout = QGridLayout()

        self.plot_new_stereonet_QPushButton = QPushButton(self.tr("New stereonet"))
        self.plot_new_stereonet_QPushButton.clicked.connect(self.plot_new_stereoplot)
        layout.addWidget(self.plot_new_stereonet_QPushButton, 0, 0, 1, 1)

        self.add_to_stereonet_QPushButton = QPushButton(self.tr("Add to existing"))
        self.add_to_stereonet_QPushButton.clicked.connect(self.add_to_stereoplot)
        layout.addWidget(self.add_to_stereonet_QPushButton, 1, 0, 1, 1)

        processing_QGroupBox.setLayout(layout)

        return processing_QGroupBox

    def define_pointlayer_params(self):

        self.input_ptlayer_params = None

        if len(loaded_point_layers()) == 0:
            self.warn("No available point layers")
            return

        dialog = StereoplotInputDialog()
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
        input_data_types = get_ptlayer_stereoplot_data_type(self.input_ptlayer_params)
        
        try:
            _, plane_orientations, lineament_orientations = parse_ptlayer_geodata(input_data_types, structural_data)
        except Exception, msg:
            self.warn(str(msg))
            return
        
        if plane_orientations is None and lineament_orientations is None:
            self.warn("No available structural data to plot")
            return
        else:
            self.plane_orientations, self.lineament_orientations = plane_orientations, lineament_orientations
                       
    """
    def define_numvalues_params(self):

            self.plane_orientations = None
            self.lineament_orientations = None

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

            valid_values, attachment = define_num_values(values)
            if not valid_values:
                self.warn(attachment)
                return
            else:
                self.plane_orientations = attachment
                self.info("Input data defined")
    """

    def get_color_transparency(self):

        color = self.linecolor_QgsColorButtonV2.color()
        red = color.red() / 255.0
        green = color.green() / 255.0
        blue = color.blue() / 255.0
        transparency = 1.0 - (float(self.transparency_QComboBox.currentText()[:-1]) / 100.0)
        #color_name = "%d,%d,%d,%d" % (red, green, blue, transparency)

        return (red, green, blue), transparency

    def plot_new_stereoplot(self):

        color_name, transparency = self.get_color_transparency()
        self.current_stereoplot = plot_new_stereonet(self.plane_orientations, 
                                                     self.lineament_orientations,
                                                     color_name,
                                                     transparency)

        self.current_stereoplot.show()


    def add_to_stereoplot(self):

        if self.current_stereoplot is None:
            self.warn("No already existing stereoplot")
            return


        color_name, transparency = self.get_color_transparency()
        add_to_stereonet(self.current_stereoplot,
                         self.plane_orientations,
                         self.lineament_orientations,
                         color_name,
                         transparency)

        self.current_stereoplot.show()

    def info(self, msg):

        QMessageBox.information(self, self.plugin_name, msg)

    def warn(self, msg):

        QMessageBox.warning(self, self.plugin_name, msg)

        


