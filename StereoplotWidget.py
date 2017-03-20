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

from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QColor
from apsg import *

from auxiliary_windows import *
from geosurf.spatial import GeolPlane, GeolAxis



class StereoplotWidget(QWidget):

    window_closed = pyqtSignal()

    def __init__(self, canvas, plugin_name):

        super(StereoplotWidget, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.mapCanvas = canvas
        self.pluginName = plugin_name

        settings = QSettings("alberese", "geocouche")
        self.dPlotStyles = dict()
        self.dPlotStyles["line_color"] = settings.value("StereoplotWidget/line_color", "#FF0000")
        self.dPlotStyles["line_style"] = settings.value("StereoplotWidget/line_style", "solid")
        self.dPlotStyles["line_width"] = settings.value("StereoplotWidget/line_width", "1 pt(s)")
        self.dPlotStyles["line_transp"] = settings.value("StereoplotWidget/line_transp", "0%")
        self.dPlotStyles["marker_color"] = settings.value("StereoplotWidget/marker_color", "#0000FF")
        self.dPlotStyles["marker_style"] = settings.value("StereoplotWidget/marker_style", "circle")
        self.dPlotStyles["marker_size"] = settings.value("StereoplotWidget/marker_size", "6 pt(s)")
        self.dPlotStyles["marker_transp"] = settings.value("StereoplotWidget/point_transp", "0%")
        
        self.lPlaneOrientations = []
        self.lAxisOrientations = []

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
                    dInputLayerParams["plane_azimuth_type"] = dialog.cmbInputLyrPlaneOrAzimType.currentText()

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

        dialog = PlotStyleDialog(self.dPlotStyles)

        if dialog.exec_():

            self.dPlotStyles["line_color"] = dialog.btnLineColor.color().name()
            self.dPlotStyles["line_style"] = dialog.cmbLineStyle.currentText()
            self.dPlotStyles["line_width"] = dialog.cmbLineWidth.currentText()
            self.dPlotStyles["line_transp"] = dialog.cmbLineTransp.currentText()

            self.dPlotStyles["marker_color"] = dialog.btnPointColor.color().name()
            self.dPlotStyles["marker_style"] = dialog.cmbPointStyle.currentText()
            self.dPlotStyles["marker_size"] = dialog.cmbPointSize.currentText()
            self.dPlotStyles["marker_transp"] = dialog.cmbPointTransp.currentText()


    def define_stereoplot(self):

        def plot_dataset(tStereoplotStatus, bPlotPlanes, tPlotPlanesFormat, bPlotAxes, tPlotAxesFormat):

            def plot_data_in_stereonet(plane_data, line_data):

                def parse_color(color_name):
                    """
                    return tuple of three float values [0,1]
                    """

                    color = QColor(color_name)
                    red = color.red() / 255.0
                    green = color.green() / 255.0
                    blue = color.blue() / 255.0

                    return red, green, blue

                def parse_size(tSizePts):

                    return float(tSizePts.split()[0])

                def parse_transparency(tTranspar):

                    return 1.0 - (float(tTranspar[:-1]) / 100.0)  # removes final '%' from input value

                line_style = self.dPlotStyles["line_style"]
                line_width = parse_size(self.dPlotStyles["line_width"])
                line_color = parse_color(self.dPlotStyles["line_color"])
                line_alpha = parse_transparency(self.dPlotStyles["line_transp"])

                marker_style = ltMarkerStyles[self.dPlotStyles["marker_style"]]
                marker_size = parse_size(self.dPlotStyles["marker_size"])
                marker_color = parse_color(self.dPlotStyles["marker_color"])
                marker_transp = parse_transparency(self.dPlotStyles["marker_transp"])

                if bPlotPlanes and plane_data is not None:
                    assert tPlotPlanesFormat in ["great circles", "normal axes"]
                    for plane in plane_data:
                        if tPlotPlanesFormat == "great circles":                            
                            p = Fol(*plane)
                            self.currStereonet.plane(p,
                                                     linestyle=line_style,
                                                     linewidth=line_width,
                                                     color=line_color,
                                                     alpha=line_alpha)
                        else:
                            line_rec = GeolPlane(*plane).as_normalgeolaxis().as_downgeolaxis().vals
                            l = Lin(*line_rec)
                            self.currStereonet.line(l,
                                                    marker=marker_style,
                                                    markersize=marker_size,
                                                    color=marker_color,
                                                    alpha=marker_transp)
                            
                if bPlotAxes and line_data is not None:
                    assert tPlotAxesFormat in ["poles", "perpendicular planes"]
                    for line_rec in line_data:
                        if tPlotAxesFormat == "poles":                            
                            l = Lin(*line_rec)
                            self.currStereonet.line(l,
                                                    marker=marker_style,
                                                    markersize=marker_size,
                                                    color=marker_color,
                                                    alpha=marker_transp)
                        else:
                            plane = GeolAxis(*line_rec).as_normalgeolplane().vals
                            p = Fol(*plane)
                            self.currStereonet.plane(p,
                                                     linestyle=line_style,
                                                     linewidth=line_width,
                                                     color=line_color,
                                                     alpha=line_alpha)

            if bPlotPlanes and not self.lPlaneOrientations:
                self.warn("No plane data to plot")
                return
            elif bPlotAxes and not self.lAxisOrientations:
                self.warn("No axis data to plot")
                return

            if tStereoplotStatus == "new stereonet":
                self.currStereonet = StereoNet()
            else:
                if self.currStereonet.closed:
                    self.warn("Previous stereonet is closed. Plot in a new one")
                    return

            plot_data_in_stereonet(self.lPlaneOrientations,
                                   self.lAxisOrientations)
            self.currStereonet.show()

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

        settings.setValue("StereoplotWidget/size", self.size())
        settings.setValue("StereoplotWidget/position", self.pos())

        settings.setValue("StereoplotWidget/line_color", self.dPlotStyles["line_color"])
        settings.setValue("StereoplotWidget/line_style", self.dPlotStyles["line_style"])
        settings.setValue("StereoplotWidget/line_width", self.dPlotStyles["line_width"])
        settings.setValue("StereoplotWidget/line_transp", self.dPlotStyles["line_transp"])

        settings.setValue("StereoplotWidget/marker_color", self.dPlotStyles["marker_color"])
        settings.setValue("StereoplotWidget/marker_style", self.dPlotStyles["marker_style"])
        settings.setValue("StereoplotWidget/marker_size", self.dPlotStyles["marker_size"])
        settings.setValue("StereoplotWidget/point_transp", self.dPlotStyles["marker_transp"])

        self.window_closed.emit()



