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

from auxiliary_windows import *


class StereoplotWidget(QWidget):

    window_closed = pyqtSignal()

    def __init__(self, canvas, plugin_name):

        super(StereoplotWidget, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.mapCanvas = canvas
        self.pluginName = plugin_name

        self.dPlotStyles = dict()
        self.dPlotStyles["line_color"] = 1., 0., 0.
        self.dPlotStyles["line_thickn"] = 1.
        self.dPlotStyles["line_opacity"] = 1.
        self.dPlotStyles["point_color"] = 1., 0., 0.
        self.dPlotStyles["point_size"] = 6.
        self.dPlotStyles["point_opacity"] = 1.

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

        def parse_azimuth_values(azimuths, az_type):

            if az_type == "dip_dir":
                offset = 0.0
            elif az_type == "strike_rhr":
                offset = 90.0
            else:
                raise Exception("Invalid azimuth data type")

            return map(lambda val: (val + offset) % 360.0, azimuths)

        def layer_input_type_valid(dInputLayerParams):

            if dInputLayerParams["plane_azimuth_name_field"] is not None and \
              dInputLayerParams["plane_dip_name_field"] is not None:
                return True
            elif dInputLayerParams["axis_azimuth_name_field"] is not None and \
              dInputLayerParams["axis_dip_name_field"] is not None:
                return True
            else:
                return False

        def layer_input_type(dInputParams):
            # define type for planar data

            if dInputParams["plane_azimuth_name_field"] is not None and \
                            dInputParams["plane_dip_name_field"] is not None:
                plane_data = True
                if dInputParams["plane_azimuth_type"] == "dip direction":
                    plane_az_type = "dip_dir"
                else:
                    plane_az_type = "strike_rhr"
                plane_dip_type = "dip"
            else:
                plane_data = False
                plane_az_type = None
                plane_dip_type = None

            # define type for linear data
            if dInputParams["axis_azimuth_name_field"] is not None and \
                            dInputParams["axis_dip_name_field"] is not None:
                axis_data = True
                axis_az_type = "trend"
                axis_dip_type = "plunge"
            else:
                axis_data = False
                axis_az_type = None
                axis_dip_type = None

            return dict(plane_data=plane_data,
                        plane_az_type=plane_az_type,
                        plane_dip_type=plane_dip_type,
                        axis_data=axis_data,
                        axis_az_type=axis_az_type,
                        axis_dip_type=axis_dip_type)

        def orientations_from_layer(input_data_types, structural_data):

            xy_vals = [(float(rec[0]), float(rec[1])) for rec in structural_data]

            try:
                if input_data_types["plane_data"]:
                    azimuths = [float(rec[2]) for rec in structural_data]
                    dipdir_vals = parse_azimuth_values(azimuths,
                                                       input_data_types["plane_az_type"])
                    dipangle_vals = [float(rec[3]) for rec in structural_data]
                    plane_vals = zip(dipdir_vals, dipangle_vals)
                    line_data_ndx_start = 4
                else:
                    plane_vals = None
                    line_data_ndx_start = 2
            except Exception as e:
                raise Exception("Error in planar data parsing: {}".format(e.message))

            try:
                if input_data_types["axis_data"]:
                    line_vals = [(float(rec[line_data_ndx_start]), float(rec[line_data_ndx_start + 1])) for rec in
                                 structural_data]
                else:
                    line_vals = None
            except Exception as e:
                raise Exception("Error in linear data parsing: {}".format(e.message))

            return xy_vals, plane_vals, line_vals

        def orientations_from_text(data_type, azimuth_type, text, sep=','):

            def extract_values(row):

                def parse_plane_azim(az_raw):
                    if azimuth_type == "strike rhr":
                        az = az_raw + 90.0
                    else:
                        az = az_raw
                    return az % 360.0

                raw_values = row.split(sep)
                if data_type == "planes":
                    az, dip = map(float, raw_values)
                    planes.append([parse_plane_azim(az), dip])
                elif data_type == "axes":
                    trend, plunge = map(float, raw_values)
                    axes.append([trend, plunge])
                else:
                    az, dip, trend, plunge = map(float, raw_values)
                    planes.append([parse_plane_azim(az), dip])
                    axes.append([trend, plunge])

            if text is None or text == '':
                return False, "No value available"

            lines = text.split("\n")
            if len(lines) == 0:
                return False, "No value available"

            planes = []
            axes = []
            try:
                map(extract_values, lines)
                return True, (planes, axes)
            except:
                return False, "Error in input values"

        llyrLoadedPointLayers = loaded_point_layers()
        dialog = StereoplotInputDialog(llyrLoadedPointLayers)
        if dialog.exec_():
            if dialog.tabWdgt.currentIndex() == 0:
                try:
                    lyrInputLayer = llyrLoadedPointLayers[dialog.cmbInputLayers.currentIndex() - 1]
                except:
                    self.warn("Incorrect point layer choice")
                    return
                dInputLayerParams = dict()
                try:
                    dInputLayerParams["plane_azimuth_type"] = dialog.cmbInputPlaneOrAzimType.currentText()

                    dInputLayerParams["plane_azimuth_name_field"] = parse_field_choice(dialog.cmbInputPlaneAzimSrcFld.currentText(),
                                                                                        tFieldUndefined)

                    dInputLayerParams["plane_dip_type"] = dialog.cmbInputPlaneOrientDipType.currentText()
                    dInputLayerParams["plane_dip_name_field"] = parse_field_choice(dialog.cmbInputPlaneDipSrcFld.currentText(),
                                                                                    tFieldUndefined)

                    dInputLayerParams["axis_azimuth_type"] = dialog.cmbInputAxisAzimType.currentText()
                    dInputLayerParams["axis_azimuth_name_field"] = parse_field_choice(dialog.cmbInputAxisAzimSrcFld.currentText(),
                                                                                      tFieldUndefined)

                    dInputLayerParams["axis_dip_type"] = dialog.cmbInputAxisDipType.currentText()
                    dInputLayerParams["axis_dip_name_field"] = parse_field_choice(dialog.cmbInputAxisDipSrcFld.currentText(),
                                                                                  tFieldUndefined)
                except:
                    self.warn("Incorrect input field definitions")
                    return

                if not layer_input_type_valid(dInputLayerParams):
                    self.warn("Invalid/incomplete parameters")
                    return

                # get used field names in the point attribute table
                ltAttitudeFldNms = [dInputLayerParams["plane_azimuth_name_field"],
                                   dInputLayerParams["plane_dip_name_field"],
                                   dInputLayerParams["axis_azimuth_name_field"],
                                   dInputLayerParams["axis_dip_name_field"]]

                # get input data presence and type
                lGeoStructurData = pt_geoms_attrs(lyrInputLayer, ltAttitudeFldNms)
                dInputDataTypes = layer_input_type(dInputLayerParams)

                try:
                    _, lPlaneOrientations, lAxisOrientations = orientations_from_layer(dInputDataTypes, lGeoStructurData)
                except Exception, msg:
                    self.warn(str(msg))
                    return
            elif dialog.tabWdgt.currentIndex() == 1:
                try:
                    tDataType = dialog.cmbInputDataType.currentText()
                    tPlaneAzimType = dialog.cmbInputPlaneOrAzimType.currentText()
                    tRawValues = dialog.plntxtedInputValues.toPlainText()
                except:
                    self.warn("Incorrect text input")
                    return

                bValidValues, tResult = orientations_from_text(tDataType, tPlaneAzimType, tRawValues)
                if not bValidValues:
                    self.warn(tResult)
                    return
                else:
                    lPlaneOrientations, lAxisOrientations = tResult
            else:
                self.warn("Error with input data choice")
                return
    
            if not lPlaneOrientations and not lAxisOrientations:
                self.warn("No available structural data to plot")
            else:
                self.lPlaneOrientations, self.lAxisOrientations = lPlaneOrientations, lAxisOrientations
                self.info("Input data read")

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
            self.dPlotStyles["line_opacity"] = parse_transparency(dialog.cmbLineTransp.currentText())

            self.dPlotStyles["point_color"] = parse_color(dialog.btnPointColor.color())
            self.dPlotStyles["point_size"] = parse_thickness(dialog.cmbPointSize.currentText())
            self.dPlotStyles["point_opacity"] = parse_transparency(dialog.cmbPointTransp.currentText())

    def define_stereoplot(self):

        def plot_dataset(tStereoplotStatus, bPlotPlanes, tPlotPlanesFormat, bPlotAxes, tPlotAxesFormat):

            def plot_new_stereonet(plane_data, line_data):

                stereoplot = StereoNet()

                if bPlotPlanes and plane_data is not None:
                    if tPlotPlanesFormat == "great circles":
                        for plane in plane_data:
                            p = Fol(*plane)
                            stereoplot.plane(p,
                                             linewidth=self.dPlotStyles["line_thickn"],
                                             color=self.dPlotStyles["line_color"],
                                             alpha=self.dPlotStyles["line_opacity"])
                    elif tPlotPlanesFormat == "normal axes":
                        pass
                    else:
                        pass

                if bPlotAxes and line_data is not None:
                    if tPlotAxesFormat == "poles":
                        for line_rec in line_data:
                            l = Lin(*line_rec)
                            stereoplot.line(l,
                                            markersize=self.dPlotStyles["point_size"],
                                            color=self.dPlotStyles["point_color"],
                                            alpha=self.dPlotStyles["point_opacity"])
                    elif tPlotAxesFormat == "perpendicular planes":
                        pass
                    else:
                        pass

                return stereoplot

            def add_to_stereonet(stereoplot, plane_data, line_data):

                if plane_data is not None:
                    for plane in plane_data:
                        p = Fol(*plane)
                        stereoplot.plane(p,
                                         linewidth=self.dPlotStyles["line_thickn"],
                                         color=self.dPlotStyles["line_color"],
                                         alpha=self.dPlotStyles["line_opacity"])

                if line_data is not None:
                    for line_rec in line_data:
                        l = Lin(*line_rec)
                        stereoplot.line(l)

            if bPlotPlanes and not self.lPlaneOrientations:
                self.warn("No plane data to plot")
                return
            elif bPlotAxes and not self.lAxisOrientations:
                self.warn("No axis data to plot")
                return

            if tStereoplotStatus == "new stereoplot":
                self.currStereoplot = plot_new_stereonet(self.lPlaneOrientations,
                                                         self.lAxisOrientations)
                self.currStereoplot.show()
            elif tStereoplotStatus == "previous stereoplot":
                if self.currStereoplot is None:
                    self.warn("No already existing stereoplot")
                    return
                add_to_stereonet(self.currStereoplot,
                                 self.lPlaneOrientations,
                                 self.lAxisOrientations)
                self.currStereoplot.show()
            else:
                self.warn("Choice for stereonet not defined correctly")

        if not self.lPlaneOrientations and not self.lAxisOrientations:
            self.warn("No data to plot")
            return

        dialog = PlotStereonetDialog()

        if dialog.exec_():
            plot_dataset(tStereoplotStatus=dialog.cmbStereonetFigure.currentText(),
                         bPlotPlanes=dialog.chkPlanes.isChecked(),
                         tPlotPlanesFormat=dialog.cmbPlanesType.currentText(),
                         bPlotAxes=dialog.chkAxes.isChecked(),
                         tPlotAxesFormat=dialog.cmbAxesType.currentText())

    def info(self, msg):

        QMessageBox.information(self, self.pluginName, msg)

    def warn(self, msg):

        QMessageBox.warning(self, self.pluginName, msg)

    def closeEvent(self, event):

        settings = QSettings("alberese", "geocouche")
        settings.setValue("stereplot_QWidget/Size", self.size())
        settings.setValue("stereplot_QWidget/Position", self.pos())

        self.window_closed.emit()



