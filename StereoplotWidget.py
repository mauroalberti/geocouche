# -*- coding: utf-8 -*-

"""
/***************************************************************************
 geocouche - plugin for Quantum GIS

 geologic stereoplots
-------------------

    Begin                : 2015.04.18
    Date                 : 2017.05.06
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

# from PyQt4.QtCore import QSettings
# from PyQt4.QtGui import QColor

from .apsg import *

from .auxiliary_windows import *
from .gsf.geometry import GPlane, GAxis
from .gis_utils.qgs_tools import pt_geoms_attrs
from .mpl_utils.save_figure import FigureExportDialog


class StereoplotWidget(QWidget):

    window_closed = pyqtSignal()

    def __init__(self, canvas, plugin_name):

        super(StereoplotWidget, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.mapCanvas = canvas
        self.pluginName = plugin_name

        # settings stored for geocouche plugin

        settings = QSettings("alberese", "geocouche")

        # stored setting values for plot style

        self.dPlotStyles = dict()
        self.dPlotStyles["line_color"] = settings.value("StereoplotWidget/line_color", "#FF0000")
        self.dPlotStyles["line_style"] = settings.value("StereoplotWidget/line_style", "solid")
        self.dPlotStyles["line_width"] = settings.value("StereoplotWidget/line_width", "1 pt(s)")
        self.dPlotStyles["line_transp"] = settings.value("StereoplotWidget/line_transp", "0%")
        self.dPlotStyles["marker_color"] = settings.value("StereoplotWidget/marker_color", "#0000FF")
        self.dPlotStyles["marker_style"] = settings.value("StereoplotWidget/marker_style", "circle")
        self.dPlotStyles["marker_size"] = settings.value("StereoplotWidget/marker_size", "6 pt(s)")
        self.dPlotStyles["marker_transp"] = settings.value("StereoplotWidget/point_transp", "0%")

        # stored setting values for figure export

        self.dExportParams = dict()
        self.dExportParams["expfig_width_inch"] = settings.value("StereoplotWidget/expfig_width_inch", "10")
        self.dExportParams["expfig_res_dpi"] = settings.value("StereoplotWidget/expfig_res_dpi", "200")
        self.dExportParams["expfig_font_size_pts"] = settings.value("StereoplotWidget/expfig_font_size_pts", "12")

        # reset all data definitions

        self.reset_layer_src_data()
        self.reset_text_src_data()

        # create gui window

        self.setup_gui()

    def reset_layer_src_data(self):

        self.dLayerSrcParams = dict(LayerSrcData=False,
                                    GeoStructurData=[],
                                    InputDataTypes=[])

    def reset_text_src_data(self):

        self.dTextSrcParams = dict(TextSrcData=False,
                                   PlaneOrientations=[],
                                   AxisOrientations=[])

    def setup_gui(self):

        self.layout = QVBoxLayout()

        self.stereonet = StereoNet()
        self.layout.addWidget(self.stereonet.fig.canvas)

        self.pshDefineInput = QPushButton(self.tr("Input data"))
        self.pshDefineInput.clicked.connect(self.define_input)
        self.layout.addWidget(self.pshDefineInput)

        self.pshDefineStyle = QPushButton(self.tr("Plot style"))
        self.pshDefineStyle.clicked.connect(self.define_style)
        self.layout.addWidget(self.pshDefineStyle)

        self.pshDefineStereoplot = QPushButton(self.tr("Plot data"))
        self.pshDefineStereoplot.clicked.connect(self.define_stereoplot)
        self.layout.addWidget(self.pshDefineStereoplot)

        self.pshClearStereoplot = QPushButton(self.tr("Clear stereonet"))
        self.pshClearStereoplot.clicked.connect(self.clear_stereoplot)
        self.layout.addWidget(self.pshClearStereoplot)

        self.pshSaveFigure = QPushButton(self.tr("Save figure"))
        self.pshSaveFigure.clicked.connect(self.save_figure)
        self.layout.addWidget(self.pshSaveFigure)

        self.setLayout(self.layout)
        self.setWindowTitle("Stereonet")
        self.adjustSize()

    def define_input(self):

        def parse_field_choice(val, choose_message):

            if val == choose_message:
                return None
            else:
                return val

        def layer_input_type_valid(dInputLayerParams):

            if dInputLayerParams["pln_azimuth_name_field"] is not None and \
              dInputLayerParams["pln_dip_name_field"] is not None:
                return True
            elif dInputLayerParams["ln_azimuth_name_field"] is not None and \
              dInputLayerParams["ln_dip_name_field"] is not None:
                return True
            else:
                return False

        def layer_input_type(dInputParams):

            # define type for planar data

            if dInputParams["pln_azimuth_name_field"] is not None and \
                            dInputParams["pln_dip_name_field"] is not None:
                plane_data = True
                if dInputParams["pln_azimuth_type"] == "dip direction":
                    pln_az_type = "dip_dir"
                else:
                    pln_az_type = "strike_rhr"
                pln_dip_type = "dip"
                if dInputParams["pln_rake_name_field"] is not None:
                    pln_rake_value = True
                    pln_rake_type = "rake"
                else:
                    pln_rake_value = False
                    pln_rake_type = None
            else:
                plane_data = False
                pln_az_type = None
                pln_dip_type = None
                pln_rake_value = False
                pln_rake_type = None

            # define type for linear data

            if dInputParams["ln_azimuth_name_field"] is not None and \
                            dInputParams["ln_dip_name_field"] is not None:
                line_data = True
                ln_az_type = "trend"
                ln_dip_type = "plunge"
                if dInputParams["ln_movsen_name_field"] is not None:
                    ln_ms_value = True
                    ln_ms_type = "movement_sense"
                else:
                    ln_ms_value = False
                    ln_ms_type = None
            else:
                line_data = False
                ln_az_type = None
                ln_dip_type = None
                ln_ms_value = False
                ln_ms_type = None

            return dict(plane_data=plane_data,
                        pln_az_type=pln_az_type,
                        pln_dip_type=pln_dip_type,
                        pln_rake_type=pln_rake_type,
                        pln_rake_value=pln_rake_value,
                        line_data=line_data,
                        ln_az_type=ln_az_type,
                        ln_dip_type=ln_dip_type,
                        ln_ms_type=ln_ms_type,
                        ln_ms_value=ln_ms_value)

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
        dialog = StereoplotInputDlg(llyrLoadedPointLayers)
        if dialog.exec_():
            if dialog.tabWdgt.currentIndex() == 0:
                try:
                    lyrInputLayer = llyrLoadedPointLayers[dialog.cmbInputLayers.currentIndex() - 1]
                except:
                    self.warn("Incorrect point layer choice")
                    return
                dInputLayerParams = dict()
                try:
                    dInputLayerParams["pln_azimuth_type"] = dialog.cmbInputLyrPlaneOrAzimType.currentText()

                    dInputLayerParams["pln_azimuth_name_field"] = parse_field_choice(dialog.cmbInputPlaneAzimSrcFld.currentText(),
                                                                                        tFieldUndefined)

                    dInputLayerParams["pln_dip_type"] = dialog.cmbInputPlaneOrientDipType.currentText()
                    dInputLayerParams["pln_dip_name_field"] = parse_field_choice(dialog.cmbInputPlaneDipSrcFld.currentText(),
                                                                                    tFieldUndefined)

                    dInputLayerParams["pln_rake_type"] = dialog.cmbInputPlaneRakeType.currentText()
                    dInputLayerParams["pln_rake_name_field"] = parse_field_choice(dialog.cmbInputPlaneRakeSrcFld.currentText(),
                                                                                    tFieldUndefined)

                    dInputLayerParams["ln_azimuth_type"] = dialog.cmbInputAxisAzimType.currentText()
                    dInputLayerParams["ln_azimuth_name_field"] = parse_field_choice(dialog.cmbInputAxisAzimSrcFld.currentText(),
                                                                                      tFieldUndefined)

                    dInputLayerParams["ln_dip_type"] = dialog.cmbInputAxisDipType.currentText()
                    dInputLayerParams["ln_dip_name_field"] = parse_field_choice(dialog.cmbInputAxisDipSrcFld.currentText(),
                                                                                  tFieldUndefined)

                    dInputLayerParams["ln_movsen_type"] = dialog.cmbInputAxisMovSenseType.currentText()
                    dInputLayerParams["ln_movsen_name_field"] = parse_field_choice(dialog.cmbInputAxisMovSenseSrcFld.currentText(),
                                                                                      tFieldUndefined)
                except:
                    self.warn("Incorrect input field definitions")
                    return

                if not layer_input_type_valid(dInputLayerParams):
                    self.warn("Invalid/incomplete parameters")
                    return

                # get used field names in the point attribute table

                ltAttitudeFldNms = [dInputLayerParams["pln_azimuth_name_field"],
                                    dInputLayerParams["pln_dip_name_field"],
                                    dInputLayerParams["pln_rake_name_field"],
                                    dInputLayerParams["ln_azimuth_name_field"],
                                    dInputLayerParams["ln_dip_name_field"],
                                    dInputLayerParams["ln_movsen_name_field"]]

                # set input data presence and type

                self.dLayerSrcParams = dict(LayerSrcData=True,
                                            SrcLayer=lyrInputLayer,
                                            AttidudeFldNames=ltAttitudeFldNms,
                                            InputDataTypes=layer_input_type(dInputLayerParams))
                self.reset_text_src_data()  # discard text-derived data

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
                    self.dTextSrcParams["PlaneOrientations"], self.dTextSrcParams["AxisOrientations"] = tResult
                    self.dTextSrcParams["TextSrcData"] = True
                    self.reset_layer_src_data()  # discard layer-derived data
            else:
                self.warn("Error with input data choice")
                return
    
            self.info("Input data defined")

    def define_style(self):

        dialog = PlotStyleDlg(self.dPlotStyles)

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

        def parse_layer_data(input_data_types, structural_data):

            def parse_azimuth(azimuth, az_type=input_data_types["pln_az_type"]):

                if az_type == "dip_dir":
                    offset = 0.0
                elif az_type == "strike_rhr":
                    offset = 90.0
                else:
                    raise Exception("Invalid azimuth data type")

                return (float(azimuth) + offset) % 360.0

            def parse_rake(dip_dir, dip_angle, rake):

                plane = GPlane(dip_dir, dip_angle)
                return plane.rake_to_gv(float(rake))

            def parse_movsense(mov_sense):

                pass

            # create list of text holders for data to extract

            data_types_to_extract = [("x", float), ("y", float)]
            if input_data_types["plane_data"]:
                data_types_to_extract += [("pln_dipdir", parse_azimuth), ("pln_dipang", float)]
                if input_data_types["pln_rake_value"]:
                    data_types_to_extract.append(("pln_rk", float))
            if input_data_types["line_data"]:
                data_types_to_extract += [("ln_tr", float), ("ln_pl", float)]
                if input_data_types["ln_ms_type"]:
                    data_types_to_extract.append(("ln_ms", str))

            # extract and parse raw data

            lSrcStructuralVals = []
            print "data_types_to_extract: {}".format(data_types_to_extract)
            for rec in structural_data:
                dRecord = dict()
                for ndx, (key, func) in enumerate(data_types_to_extract):
                    dRecord[key] = func(rec[ndx])
                lSrcStructuralVals.append(dRecord)

            """
            # source point coordinates

            xy_vals = [(float(rec[x_ndx]), float(rec[y_ndx])) for rec in structural_data]


            try:
                if input_data_types["plane_data"]:
                    azimuths = [float(rec[2]) for rec in structural_data]
                    dipdir_vals = parse_azimuth_values(azimuths,
                                                       input_data_types["pln_az_type"])
                    dipangle_vals = [float(rec[3]) for rec in structural_data]
                    plane_vals = zip(dipdir_vals, dipangle_vals)
                    line_data_ndx_start = 4
                else:
                    plane_vals = None
                    line_data_ndx_start = 2
            except Exception as e:
                raise Exception("Error in planar data parsing: {}".format(e.message))

            try:
                if input_data_types["line_data"]:
                    line_vals = [(float(rec[line_data_ndx_start]), float(rec[line_data_ndx_start + 1])) for rec in
                                 structural_data]
                else:
                    line_vals = None
            except Exception as e:
                raise Exception("Error in linear data parsing: {}".format(e.message))

            return xy_vals, plane_vals, line_vals
            """

            return lSrcStructuralVals

        def plot_dataset(struc_vals, plot_setts):

            def plot_data_in_stereonet(structural_values):

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

                def get_plane_data(struct_vals):

                    for row in struct_vals:
                        if not "pln_dipdir" in row or not "pln_dipang" in row:
                            return None
                        else:
                            continue

                    return map(lambda row: (row["pln_dipdir"], row["pln_dipang"]), struct_vals)

                def get_line_data(struct_vals):

                    for row in struct_vals:
                        if not "ln_tr" in row or not "ln_pl" in row:
                            return None
                        else:
                            print row["ln_tr"], row["ln_pl"]
                            continue

                    return map(lambda row: (row["ln_tr"], row["ln_pl"]), struct_vals)

                line_style = self.dPlotStyles["line_style"]
                line_width = parse_size(self.dPlotStyles["line_width"])
                line_color = parse_color(self.dPlotStyles["line_color"])
                line_alpha = parse_transparency(self.dPlotStyles["line_transp"])

                marker_style = ltMarkerStyles[self.dPlotStyles["marker_style"]]
                marker_size = parse_size(self.dPlotStyles["marker_size"])
                marker_color = parse_color(self.dPlotStyles["marker_color"])
                marker_transp = parse_transparency(self.dPlotStyles["marker_transp"])

                if plot_setts["bPlotPlanes"]:
                    assert plot_setts["tPlotPlanesFormat"] in ["great circles", "normal axes"]
                    plane_data = get_plane_data(structural_values)
                    if not plane_data:
                        self.warn(("No plane data"))
                    else:
                        for plane in plane_data:
                            if plot_setts["tPlotPlanesFormat"] == "great circles":
                                p = Fol(*plane)
                                self.stereonet.plane(p,
                                                     linestyle=line_style,
                                                     linewidth=line_width,
                                                     color=line_color,
                                                     alpha=line_alpha)
                            else:
                                line_rec = GPlane(*plane).normal.downward.tp
                                l = Lin(*line_rec)
                                self.stereonet.line(l,
                                                    marker=marker_style,
                                                    markersize=marker_size,
                                                    color=marker_color,
                                                    alpha=marker_transp)
                            
                if plot_setts["bPlotAxes"]:
                    assert plot_setts["tPlotAxesFormat"] in ["poles", "perpendicular planes"]
                    line_data = get_line_data(structural_values)
                    if not line_data:
                        self.warn(("No line data"))
                    else:
                        for line_rec in line_data:
                            if plot_setts["tPlotAxesFormat"] == "poles":
                                l = Lin(*line_rec)
                                self.stereonet.line(l,
                                                    marker=marker_style,
                                                    markersize=marker_size,
                                                    color=marker_color,
                                                    alpha=marker_transp)
                            else:
                                plane = GAxis(*line_rec).normal_gplane.dda
                                p = Fol(*plane)
                                self.stereonet.plane(p,
                                                     linestyle=line_style,
                                                     linewidth=line_width,
                                                     color=line_color,
                                                     alpha=line_alpha)

            """
            if plot_setts["tStereoplotStatus"] == "new stereonet":
                self.stereonet = StereoNet()
            else:
                if self.stereonet.closed:
                    self.warn("Previous stereonet is closed. Plot in a new one")
                    return
            """
            plot_data_in_stereonet(struc_vals)
            #self.stereonet.show()

        if not self.dLayerSrcParams["LayerSrcData"] and not self.dTextSrcParams["TextSrcData"]:
            self.warn("No data to plot")
            return

        if self.dLayerSrcParams["LayerSrcData"]:
            lGeoStructurData = pt_geoms_attrs(self.dLayerSrcParams["SrcLayer"],
                                              self.dLayerSrcParams["AttidudeFldNames"])
            lStructuralValues = parse_layer_data(self.dLayerSrcParams["InputDataTypes"],
                                                 lGeoStructurData)
        else:
            pass

        dialog = PlotStereonetDlg()
        if dialog.exec_():
            dPlotSettings = dict(tStereoplotStatus=dialog.cmbStereonetFigure.currentText(),
                                 bPlotPlanes=dialog.chkPlanes.isChecked(),
                                 tPlotPlanesFormat=dialog.cmbPlanesType.currentText(),
                                 bPlotPlaneswithRake=dialog.chkPlaneswithRake.isChecked(),
                                 tPlotPlaneswithRakeFormat=dialog.cmbPlaneswithRakeType.currentText(),
                                 bPlotAxes=dialog.chkAxes.isChecked(),
                                 tPlotAxesFormat=dialog.cmbAxesType.currentText())
            plot_dataset(lStructuralValues, dPlotSettings)

    def clear_stereoplot(self):

        self.stereonet.cla()

    def save_figure(self):

        dialog = FigureExportDialog(self.pluginName, self.dExportParams)

        if dialog.exec_():

            try:
                self.dExportParams["expfig_width_inch"] = dialog.qleFigWidthInch.text()
                fig_width_inches = float(self.dExportParams["expfig_width_inch"])
            except:
                self.warn("Error in figure width value")
                return

            try:
                self.dExportParams["expfig_res_dpi"] = dialog.qleFigResolutionDpi.text()
                fig_resolution_dpi = int(self.dExportParams["expfig_res_dpi"])
            except:
                self.warn("Error in figure resolution value")
                return

            try:
                self.dExportParams["expfig_font_size_pts"] = dialog.qleFigFontSizePts.text()
                fig_font_size_pts = float(self.dExportParams["expfig_font_size_pts"])
            except:
                self.warn("Error in font size value")

            try:
                fig_outpath = unicode(dialog.qleFigureOutPath.text())
            except:
                self.warn("Error in figure output path")
                return

            try:
                top_space_value = float(dialog.qsbTopSpaceValue.value())
            except:
                self.warn("Error in figure top space value")
                return

            try:
                left_space_value = float(dialog.qsbLeftSpaceValue.value())
            except:
                self.warn("Error in figure left space value")
                return

            try:
                right_space_value = float(dialog.qsbRightSpaceValue.value())
            except:
                self.warn("Error in figure right space value")
                return

            try:
                bottom_space_value = float(dialog.qsbBottomSpaceValue.value())
            except:
                self.warn("Error in figure bottom space value")
                return

            try:
                blank_width_space = float(dialog.qsbBlankWidthSpaceValue.value())
            except:
                self.warn("Error in figure blank widht space value")
                return

            try:
                blank_height_space = float(dialog.qsbBlankHeightSpaceValue.value())
            except:
                self.warn("Error in figure blank height space value")
                return

        else:

            self.warn("No export figure defined")
            return

        figure = self.stereonet.fig

        fig_current_width, fig_current_height = figure.get_size_inches()
        fig_scale_factor = fig_width_inches / fig_current_width
        figure.set_size_inches(fig_width_inches, fig_scale_factor * fig_current_height)

        for axis in figure.axes:
            for label in (axis.get_xticklabels() + axis.get_yticklabels()):
                label.set_fontsize(fig_font_size_pts)

        figure.subplots_adjust(wspace=blank_width_space, hspace=blank_height_space, left=left_space_value,
                               right=right_space_value, top=top_space_value, bottom=bottom_space_value)

        try:
            figure.savefig(str(fig_outpath), dpi=fig_resolution_dpi)
        except:
            self.warn("Error with image saving")
        else:
            self.info("Image saved")

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



