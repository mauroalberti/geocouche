# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import QgsColorButtonV2

from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs
from auxiliary_windows import StereoplotInputDialog, PlotStyleDialog, PlotStereonetDialog
from processing import plot_new_stereonet, add_to_stereonet
from structural_userdefs import parse_ptlayer_geodata, ptlayer_valid_params, \
                                getInputPtLayerParams, get_ptlayer_stereoplot_data_type, \
                                get_input_values_params, define_num_values


class stereoplot_QWidget(QWidget):

    window_closed = pyqtSignal()

    def __init__(self, canvas, plugin_name):

        super(stereoplot_QWidget, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.mapCanvas = canvas
        self.pluginName = plugin_name

        self.inputPtLayer = None
        self.inputPtLayerParams = None
        self.currStereoplot = None
        self.tColorName = '255,0,0,255'

        self.dPlotTypes = dict(plane_plot_greatcircle=True,
                               plane_plot_perpoles=False,
                               line_plot_poles=True,
                               line_plot_perplanes=False)

        self.dPlotStyles = dict()

        self.setup_gui()

    def setup_gui(self):

        self.layout = QVBoxLayout()

        self.pshDefineInput = QPushButton(self.tr("Input data"))
        self.pshDefineInput.clicked.connect(self.define_input)
        self.layout.addWidget(self.pshDefineInput)

        self.pshDefineStyle = QPushButton(self.tr("Plot style"))
        self.pshDefineStyle.clicked.connect(self.define_style)
        self.layout.addWidget(self.pshDefineStyle)

        self.pshDefineStereoplot = QPushButton(self.tr("Plot stereonet"))
        self.pshDefineStereoplot.clicked.connect(self.define_stereoplot)
        self.layout.addWidget(self.pshDefineStereoplot)

        """
        unused methods to remove:
        self.dialog_layout.addWidget(self.setup_inputdata())
        self.dialog_layout.addWidget(self.setup_styling())
        self.dialog_layout.addWidget(self.setup_plotting())
        """

        self.setLayout(self.layout)
        self.setWindowTitle("Stereonet")
        self.adjustSize()

    def define_input(self):

        dialog = StereoplotInputDialog()
        if dialog.exec_():
            try:
                input_ptlayer_name, input_ptlayer_params = getInputPtLayerParams(dialog)
                self.info("Input defined")
            except:
                self.warn("Incorrect definition")

    def define_style(self):

        dialog = PlotStyleDialog()
        if dialog.exec_():
            self.dPlotStyles["line_color"] = dialog.btnLineColor.color()
            self.dPlotStyles["line_thickn"] = dialog.cmbLineThickn.currentText()
            self.dPlotStyles["line_transp"] = dialog.cmbLineTransp.currentText()

            self.dPlotStyles["point_color"] = dialog.btnPointColor.color()
            self.dPlotStyles["point_thickn"] = dialog.cmbPointSize.currentText()
            self.dPlotStyles["point_transp"] = dialog.cmbPointTransp.currentText()

    def define_stereoplot(self):

        dialog = PlotStereonetDialog()

        if dialog.exec_():
            pass
            """
            self.plot_types['plane_plot_greatcircle'] = dialog.planes_greatcircles_QCheckBox.isChecked()
            self.plot_types['plane_plot_perpoles'] = dialog.planes_greatcircles_QCheckBox.isChecked()
            self.plot_types['line_plot_poles'] = dialog.planes_greatcircles_QCheckBox.isChecked()
            self.plot_types['line_plot_perplanes'] = dialog.planes_greatcircles_QCheckBox.isChecked()
            """

    def setup_inputdata(self):

        grpInput = QGroupBox("Input")

        layout = QVBoxLayout()

        self.pshDefinePointLayer = QPushButton(self.tr("Point layer"))
        self.pshDefinePointLayer.clicked.connect(self.define_pt_layer_params)
        layout.addWidget(self.pshDefinePointLayer)

        self.pshDefineValues = QPushButton(self.tr("Numeric values"))
        self.pshDefineValues.clicked.connect(self.define_numvalues_params)
        layout.addWidget(self.pshDefineValues)

        grpInput.setLayout(layout)

        return grpInput

    def setup_styling(self):

        grpStyle = QGroupBox(self)
        grpStyle.setTitle("Style")
        layout = QHBoxLayout()

        # color
        layout.addWidget(QLabel("Color"))
        red, green, blue, alpha = map(int, self.tColorName.split(","))
        self.btnLineColor = QgsColorButtonV2()
        self.btnLineColor.setColor(QColor(red, green, blue, alpha))
        layout.addWidget(self.btnLineColor)
        
        # transparency
        layout.addWidget(QLabel("Transp."))
        lPenTransparencies = [0, 25, 50, 75]
        self.cmbTransparency = QComboBox()
        self.lPenTransparenciesPrcnt = [str(val) + "%" for val in lPenTransparencies]
        self.cmbTransparency.insertItems(0, self.lPenTransparenciesPrcnt)
        layout.addWidget(self.cmbTransparency)

        grpStyle.setLayout(layout)

        return grpStyle

    def setup_plotting(self):

        grpPlotting = QGroupBox("Plotting")

        layout = QGridLayout()

        self.pshPlotNewStereonet = QPushButton(self.tr("New stereonet"))
        self.pshPlotNewStereonet.clicked.connect(self.plot_new_stereoplot)
        layout.addWidget(self.pshPlotNewStereonet, 0, 0, 1, 1)

        self.pshAddToStereonet = QPushButton(self.tr("Add to existing"))
        self.pshAddToStereonet.clicked.connect(self.add_to_stereoplot)
        layout.addWidget(self.pshAddToStereonet, 1, 0, 1, 1)

        grpPlotting.setLayout(layout)

        return grpPlotting

    def define_pt_layer_params(self):

        self.inputPtLayerParams = None

        if len(loaded_point_layers()) == 0:
            self.warn("No available point layers")
            return

        dialog = StereoplotInputDialog()
        if dialog.exec_():
            try:
                input_ptlayer, input_ptlayer_params = getInputPtLayerParams(dialog)
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

        self.inputPtLayer = input_ptlayer
        self.inputPtLayerParams = input_ptlayer_params

        # check definition of input point layer
        if self.inputPtLayer is None or \
                        self.inputPtLayerParams is None:
            self.warn(str("Input point layer/parameters not defined"))
            return
        
        # get used field names in the point attribute table
        attitude_fldnms = [self.inputPtLayerParams["plane_azimuth_name_field"],
                           self.inputPtLayerParams["plane_dip_name_field"],
                           self.inputPtLayerParams["line_azimuth_name_field"],
                           self.inputPtLayerParams["line_dip_name_field"]]
        
        # get input data presence and type
        structural_data = pt_geoms_attrs(self.inputPtLayer, attitude_fldnms)
        input_data_types = get_ptlayer_stereoplot_data_type(self.inputPtLayerParams)
        
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

        color = self.btnLineColor.color()
        red = color.red() / 255.0
        green = color.green() / 255.0
        blue = color.blue() / 255.0
        transparency = 1.0 - (float(self.cmbTransparency.currentText()[:-1]) / 100.0)

        return (red, green, blue), transparency

    def plot_new_stereoplot(self):

        color_name, transparency = self.get_color_transparency()
        self.currStereoplot = plot_new_stereonet(self.plane_orientations,
                                                 self.lineament_orientations,
                                                 color_name,
                                                 transparency)

        self.currStereoplot.show()

    def add_to_stereoplot(self):

        if self.currStereoplot is None:
            self.warn("No already existing stereoplot")
            return

        color_name, transparency = self.get_color_transparency()
        add_to_stereonet(self.currStereoplot,
                         self.plane_orientations,
                         self.lineament_orientations,
                         color_name,
                         transparency)

        self.currStereoplot.show()

    def info(self, msg):

        QMessageBox.information(self, self.pluginName, msg)

    def warn(self, msg):

        QMessageBox.warning(self, self.pluginName, msg)

    def closeEvent(self, event):

        settings = QSettings("www.malg.eu", "geocouche")
        settings.setValue("stereplot_QWidget/Size", self.size())
        settings.setValue("stereplot_QWidget/Position", self.pos())

        self.window_closed.emit()



