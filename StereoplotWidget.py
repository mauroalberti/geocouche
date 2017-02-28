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

from apsg import *

from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs
from auxiliary_windows import *


class StereoplotWidget(QWidget):

    window_closed = pyqtSignal()

    def __init__(self, canvas, plugin_name):

        super(StereoplotWidget, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.mapCanvas = canvas
        self.pluginName = plugin_name
        self.dPlotStyles = dict()
        self.inputPtLayerParams = dict()

        """
        self.inputPtLayer = None
        self.inputPtLayerParams = None
        self.currStereoplot = None
        self.tColorName = '255,0,0,255'
        self.dPlotTypes = dict(plane_plot_greatcircle=True,
                               plane_plot_perpoles=False,
                               line_plot_poles=True,
                               line_plot_perplanes=False)
        self.dPlotStyles = dict()
        """

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

        self.setLayout(self.layout)
        self.setWindowTitle("Stereonet")
        self.adjustSize()


    def define_input(self):

        def parse_field_choice(val, choose_message):

            if val == choose_message:
                return None
            else:
                return val

        def ptlayer_valid_params():

            if self.inputPtLayerParams["plane_azimuth_name_field"] is not None and \
                            self.inputPtLayerParams["plane_dip_name_field"] is not None:
                return True
            elif self.inputPtLayerParams["line_azimuth_name_field"] is not None and \
                            self.inputPtLayerParams["line_dip_name_field"] is not None:
                return True
            else:
                return False

        def get_ptlayer_stereoplot_data_type(stereoplot_input_params):
            # define type for planar data

            if stereoplot_input_params["plane_azimuth_name_field"] is not None and \
                            stereoplot_input_params["plane_dip_name_field"] is not None:
                planar_data = True
                if stereoplot_input_params["plane_azimuth_type"] == "dip dir.":
                    planar_az_type = "dip_dir"
                elif stereoplot_input_params["plane_azimuth_type"] == "strike rhr":
                    planar_az_type = "strike_rhr"
                planar_dip_type = "dip"
            else:
                planar_data = False
                planar_az_type = None
                planar_dip_type = None

            # define type for linear data
            if stereoplot_input_params["line_azimuth_name_field"] is not None and \
                            stereoplot_input_params["line_dip_name_field"] is not None:
                linear_data = True
                linear_az_type = "trend"
                linear_dip_type = "plunge"
            else:
                linear_data = False
                linear_az_type = None
                linear_dip_type = None

            return dict(planar_data=planar_data,
                        planar_az_type=planar_az_type,
                        planar_dip_type=planar_dip_type,
                        linear_data=linear_data,
                        linear_az_type=linear_az_type,
                        linear_dip_type=linear_dip_type)

        def parse_ptlayer_geodata(input_data_types, structural_data):

            def format_azimuth_values(azimuths, az_type):

                if az_type == "dip_dir":
                    offset = 0.0
                elif az_type == "strike_rhr":
                    offset = 90.0
                else:
                    raise Exception("Invalid azimuth data type")

                return map(lambda val: (val + offset) % 360.0, azimuths)

            xy_vals = [(float(rec[0]), float(rec[1])) for rec in structural_data]

            try:
                if input_data_types["planar_data"]:
                    azimuths = [float(rec[2]) for rec in structural_data]
                    dipdir_vals = format_azimuth_values(azimuths,
                                                        input_data_types["planar_az_type"])
                    dipangle_vals = [float(rec[3]) for rec in structural_data]
                    plane_vals = zip(dipdir_vals, dipangle_vals)
                    line_data_ndx_start = 4
                else:
                    plane_vals = None
                    line_data_ndx_start = 2
            except Exception as e:
                raise Exception("Error in planar data parsing: {}".format(e.message))

            try:
                if input_data_types["linear_data"]:
                    line_vals = [(float(rec[line_data_ndx_start]), float(rec[line_data_ndx_start + 1])) for rec in
                                 structural_data]
                else:
                    line_vals = None
            except Exception as e:
                raise Exception("Error in linear data parsing: {}".format(e.message))

            return xy_vals, plane_vals, line_vals

        llyrLoadedPointLayers = loaded_point_layers()
        if len(llyrLoadedPointLayers) == 0:
            self.warn("No available point layers")
            return

        dialog = StereoplotInputDialog(llyrLoadedPointLayers)
        if dialog.exec_():
            try:
                self.inputPtLayer = llyrLoadedPointLayers[dialog.cmbInputLayers.currentIndex() - 1]
            except:
                self.warn("Incorrect point layer choice")
                return
                
            try:
                self.inputPtLayerParams["plane_azimuth_type"] = dialog.cmbInputPlaneOrAzimType.currentText()

                self.inputPtLayerParams["plane_azimuth_name_field"] = parse_field_choice(dialog.cmbInputPlaneAzimSrcFld.currentText(),
                                                                                         tFieldUndefined)

                self.inputPtLayerParams["plane_dip_type"] = dialog.cmbInputPlaneOrientDipType.currentText()
                self.inputPtLayerParams["plane_dip_name_field"] = parse_field_choice(dialog.cmbInputPlaneDipSrcFld.currentText(),
                                                                                     tFieldUndefined)

                self.inputPtLayerParams["line_azimuth_type"] = dialog.cmbInputLineOrientAzimType.currentText()
                self.inputPtLayerParams["line_azimuth_name_field"] = parse_field_choice(dialog.cmbInputLineAzimSrcFld.currentText(),
                                                                                        tFieldUndefined)

                self.inputPtLayerParams["line_dip_type"] = dialog.cmbInputLineOrientDipType.currentText()
                self.inputPtLayerParams["line_dip_name_field"] = parse_field_choice(dialog.cmbInputLineDipSrcFld.currentText(),
                                                                                    tFieldUndefined)
            except:
                self.warn("Incorrect input field definitions")
                return

            if not ptlayer_valid_params():
                self.warn("Invalid/incomplete parameters")
                return
            else:
                self.info("Input data defined")

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

    def define_style(self):

        def parse_color(color):
            """
            return tuple of three float values [0,1]
            """

            red = color.red() / 255.0
            green = color.green() / 255.0
            blue = color.blue() / 255.0

            return red, green, blue

        def parse_thickness(tThickn):

            return float(tThickn.split()[0])

        def parse_transparency(tTranspar):

            return 1.0 - (float(tTranspar[:-1]) / 100.0)  # removes final '%' from input value

        dialog = PlotStyleDialog()

        if dialog.exec_():

            self.dPlotStyles["line_color"] = parse_color(dialog.btnLineColor.color())
            self.dPlotStyles["line_thickn"] = parse_thickness(dialog.cmbLineThickn.currentText())
            self.dPlotStyles["line_transp"] = parse_transparency(dialog.cmbLineTransp.currentText())

            self.dPlotStyles["point_color"] = parse_color(dialog.btnPointColor.color())
            self.dPlotStyles["point_thickn"] = parse_thickness(dialog.cmbPointSize.currentText())
            self.dPlotStyles["point_transp"] = parse_transparency(dialog.cmbPointTransp.currentText())

    def define_stereoplot(self):

        dialog = PlotStereonetDialog()

        if dialog.exec_():
            self.plot_dataset(tStereoplotStatus=dialog.cmbStereonetFigure.currentText(),
                              bPlotPlanes=dialog.chkPlanes.isChecked(),
                              tPlotPlanesFormat=dialog.cmbPlanesType.currentText(),
                              bPlotAxes=dialog.chkAxes.isChecked(),
                              tPlotAxesFormat=dialog.cmbAxesType.currentText())

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

    def plot_dataset(self, tStereoplotStatus, bPlotPlanes, tPlotPlanesFormat, bPlotAxes, tPlotAxesFormat):

        def plot_new_stereonet(plane_data, line_data):

            stereoplot = StereoNet()

            if plane_data is not None:
                for plane in plane_data:
                    p = Fol(*plane)
                    stereoplot.plane(p,
                                     linewidth=self.dPlotStyles["line_thickn"],
                                     color=self.dPlotStyles["line_color"],
                                     alpha=self.dPlotStyles["line_transp"])

            if line_data is not None:
                for line_rec in line_data:
                    l = Lin(*line_rec)
                    stereoplot.line(l)

            return stereoplot

        def add_to_stereonet(stereoplot, plane_data, line_data):

            if plane_data is not None:
                for plane in plane_data:
                    p = Fol(*plane)
                    stereoplot.plane(p,
                                     linewidth=self.dPlotStyles["line_thickn"],
                                     color=self.dPlotStyles["line_color"],
                                     alpha=self.dPlotStyles["line_transp"])

            if line_data is not None:
                for line_rec in line_data:
                    l = Lin(*line_rec)
                    stereoplot.line(l)

        if tStereoplotStatus == "new stereoplot":
            self.currStereoplot = plot_new_stereonet(self.plane_orientations,
                                                     self.lineament_orientations)
            self.currStereoplot.show()
        elif tStereoplotStatus == "previous stereoplot":
            if self.currStereoplot is None:
                self.warn("No already existing stereoplot")
                return
            add_to_stereonet(self.currStereoplot,
                             self.plane_orientations,
                             self.lineament_orientations)
            self.currStereoplot.show()
        else:
            self.warn("Choice for stereonet not defined correctly")

    def info(self, msg):

        QMessageBox.information(self, self.pluginName, msg)

    def warn(self, msg):

        QMessageBox.warning(self, self.pluginName, msg)

    def closeEvent(self, event):

        settings = QSettings("alberese", "geocouche")
        settings.setValue("stereplot_QWidget/Size", self.size())
        settings.setValue("stereplot_QWidget/Position", self.pos())

        self.window_closed.emit()



