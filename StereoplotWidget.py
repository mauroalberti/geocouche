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
from .mpl_utils.save_figure import FigureExportDlg


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

        self.dLyrSrcParams = dict(LayerSrcData=False,
                                  GeoStructurData=[],
                                  InputDataTypes=[])

    def reset_text_src_data(self):

        self.dTxtSrcParams = dict(TextSrcData=False,
                                  PlaneOrientations=[],
                                  AxisOrientations=[],
                                  FaultRakeOrientations=[])

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
                return ''
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

        def layer_inputs_types(dInputParams):

            # define type for planar data

            bIsPlaneDefined = True if dInputParams["pln_azimuth_name_field"] and dInputParams["pln_dip_name_field"] else False

            if bIsPlaneDefined:
                pln_az_type = "dip_dir" if dInputParams["pln_azimuth_type"] == "dip direction" else "strike_rhr"
                pln_dip_type = "dip"
            else:
                pln_az_type = None
                pln_dip_type = None

            # define type for linear data

            bIsLnTrndPlngDefined = True if dInputParams["ln_azimuth_name_field"] and dInputParams["ln_dip_name_field"] else False
            bIsLnMovSnsDefined = True if dInputParams["ln_movsen_name_field"] else False
            bIsLnRkDefined = True if bIsPlaneDefined and not bIsLnTrndPlngDefined and dInputParams["ln_rake_name_field"] else False

            if (dInputParams["ln_azimuth_name_field"] is not None and \
                    dInputParams["ln_dip_name_field"] is not None) or \
                    dInputParams["ln_rake_name_field"] is not None:
                line_data = True
                ln_az_type = "trend"
                ln_dip_type = "plunge"
                if dInputParams["ln_movsen_name_field"] is not None:
                    ln_ms_value = True
                    ln_ms_type = "movement_sense"
                else:
                    ln_ms_value = False
                    ln_ms_type = None
                if dInputParams["ln_rake_name_field"] is not None:
                    ln_rake_value = True
                    ln_rake_type = "rake"
                else:
                    ln_rake_value = False
                    ln_rake_type = None
            else:
                line_data = False
                ln_az_type = None
                ln_dip_type = None
                ln_ms_value = False
                ln_ms_type = None
                ln_rake_value = False
                ln_rake_type = None

            return dict(plane_data=bIsPlaneDefined,
                        pln_az_type=pln_az_type,
                        pln_dip_type=pln_dip_type,
                        pln_rake_type=ln_rake_type,
                        ln_rake_value=ln_rake_value,
                        line_data=line_data,
                        ln_az_type=ln_az_type,
                        ln_dip_type=ln_dip_type,
                        ln_ms_type=ln_ms_type,
                        ln_ms_value=ln_ms_value)

        def orientations_from_text(data_type, azimuth_type, text, sep=','):

            def extract_values(row):

                def parse_plane_dirdir(az_raw):
                    if azimuth_type == "strike rhr":
                        dip_dir = az_raw + 90.0
                    else:
                        dip_dir = az_raw
                    return dip_dir % 360.0

                raw_values = row.split(sep)
                if data_type == "planes":
                    azim, dip_ang = map(float, raw_values)
                    planes.append([parse_plane_dirdir(azim), dip_ang])
                elif data_type == "axes":
                    trend, plunge = map(float, raw_values)
                    axes.append([trend, plunge])
                elif data_type == "planes & axes":
                    azim, dip_ang, trend, plunge = map(float, raw_values)
                    planes.append([parse_plane_dirdir(azim), dip_ang])
                    axes.append([trend, plunge])
                elif data_type == "fault planes with rake":
                    azim, dip_ang, rake = map(float, raw_values)
                    dip_dir = parse_plane_dirdir(azim)
                    planes.append([dip_dir, dip_ang])
                    slick_tr, slick_pl = GPlane(dip_dir, dip_ang).rake_to_gv(rake).downward.tp
                    axes.append([slick_tr, slick_pl])
                    faults.append([dip_dir, dip_ang, rake, slick_tr, slick_pl])

            if text is None or text == '':
                return False, "No value available"

            rows = text.split("\n")
            if len(rows) == 0:
                return False, "No value available"

            planes = []
            axes = []
            faults = []
            try:
                map(extract_values, rows)
                return True, (planes, axes, faults)
            except:
                return False, "Error in input values"

        llyrLoadedPointLayers = loaded_point_layers()
        dialog = StereoplotInputDlg(llyrLoadedPointLayers)
        if dialog.exec_():
            # layer as input
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

                    dInputLayerParams["pln_rake_type"] = dialog.cmbInputAxisRakeType.currentText()
                    dInputLayerParams["ln_rake_name_field"] = parse_field_choice(dialog.cmbInputAxisRakeSrcFld.currentText(),
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
                                    dInputLayerParams["ln_azimuth_name_field"],
                                    dInputLayerParams["ln_dip_name_field"],
                                    dInputLayerParams["ln_movsen_name_field"],
                                    dInputLayerParams["ln_rake_name_field"],]

                # set input data presence and type

                self.dLyrSrcParams = dict(LayerSrcData=True,
                                          SrcLayer=lyrInputLayer,
                                          AttidudeFldNames=ltAttitudeFldNms,
                                          InputDataTypes=layer_inputs_types(dInputLayerParams))
                self.reset_text_src_data()  # discard text-derived data

            # text as input
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
                    self.dTxtSrcParams["TextSrcData"] = True
                    self.dTxtSrcParams["PlaneOrientations"] = tResult[0]
                    self.dTxtSrcParams["AxisOrientations"] = tResult[1]
                    self.dTxtSrcParams["FaultRakeOrientations"] = tResult[2]
                    self.reset_layer_src_data()  # discard layer-derived data
            else:
                self.warn("Error with input data choice")
                return
    
            self.info("Input data defined")

    def define_style(self):

        def extract_user_styles():

            self.dPlotStyles["line_color"] = dialog.btnLineColor.color().name()
            self.dPlotStyles["line_style"] = dialog.cmbLineStyle.currentText()
            self.dPlotStyles["line_width"] = dialog.cmbLineWidth.currentText()
            self.dPlotStyles["line_transp"] = dialog.cmbLineTransp.currentText()

            self.dPlotStyles["marker_color"] = dialog.btnPointColor.color().name()
            self.dPlotStyles["marker_style"] = dialog.cmbPointStyle.currentText()
            self.dPlotStyles["marker_size"] = dialog.cmbPointSize.currentText()
            self.dPlotStyles["marker_transp"] = dialog.cmbPointTransp.currentText()

        dialog = PlotStyleDlg(self.dPlotStyles)

        if dialog.exec_():

            extract_user_styles()
            self.update_style_settings()

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

            # create list of text holders for data to extract

            data_types_to_extract = [("x", float), ("y", float)]
            if input_data_types["plane_data"]:
                data_types_to_extract += [("pln_dipdir", parse_azimuth), ("pln_dipang", float)]
            if input_data_types["line_data"]:
                data_types_to_extract += [("ln_tr", float), ("ln_pl", float)]
                if input_data_types["ln_ms_type"]:
                    data_types_to_extract.append(("ln_ms", str))
                if input_data_types["ln_rake_value"]:
                    data_types_to_extract.append(("ln_rk", float))

            # extract and parse raw data

            lSrcStructuralVals = []
            for rec in structural_data:
                dRecord = dict()
                for ndx, (key, func) in enumerate(data_types_to_extract):
                    dRecord[key] = func(rec[ndx])
                lSrcStructuralVals.append(dRecord)

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

                def get_fault_slikenline_data(struct_vals):

                    def parse_rake(dipdir, dipang, rk):

                        gv = GPlane(dipdir, dipang).rake_to_gv(float(rk)).downward
                        return gv.tp

                    for row in struct_vals:
                        if not "pln_dipdir" in row or not "pln_dipang" in row or not "ln_rk" in row:
                            return None
                        else:
                            continue

                    vals = []
                    for row in struct_vals:
                        dip_dir = row["pln_dipdir"]
                        dip_ang = row["pln_dipang"]
                        rake = row["ln_rk"]
                        lin_tr, lin_pl = parse_rake(dip_dir, dip_ang, rake)
                        vals.append((dip_dir, dip_ang, rake, lin_tr, lin_pl))

                    return vals

                def get_line_data(struct_vals):

                    for row in struct_vals:
                        if not "ln_tr" in row or not "ln_pl" in row:
                            return None
                        else:
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
                        self.warn("No plane data")
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

                if plot_setts["bPlotPlaneswithRake"]:
                    assert plot_setts["tPlotPlaneswithRakeFormat"] in ["faults with skickenlines", "P-T axes", "T-L diagrams"]
                    flt_slik_data = get_fault_slikenline_data(structural_values)
                    if not flt_slik_data:
                        self.warn(("No fault-slickenline data"))
                    else:
                        if plot_setts["tPlotPlaneswithRakeFormat"] != "faults with skickenlines":
                            self.warn("{} not yet implemented".format(plot_setts["tPlotPlaneswithRakeFormat"]))
                        else:
                            for flt_slick in flt_slik_data:
                                dip_dir, dip_ang, rake, lin_tr, lin_pl = flt_slick
                                if rake > 0:  # reverse faults according to Aki & Richards, 1980 convention
                                    sense = 1
                                else: # normal faults according to Aki & Richards, 1980 convention
                                    sense = -1
                                flt = Fault(dip_dir, dip_ang, lin_tr, lin_pl, sense)
                                if plot_setts["tPlotPlaneswithRakeFormat"] == "faults with skickenlines":
                                    self.stereonet.fault(flt,
                                                         linestyle=line_style,
                                                         linewidth=line_width,
                                                         color=line_color,
                                                         alpha=line_alpha)
                                else:
                                    raise Exception("Not yet implemented")

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

            plot_data_in_stereonet(struc_vals)

        if not self.dLyrSrcParams["LayerSrcData"] and not self.dTxtSrcParams["TextSrcData"]:
            self.warn("No data to plot")
            return

        if self.dLyrSrcParams["LayerSrcData"]:
            lGeoStructurData = pt_geoms_attrs(self.dLyrSrcParams["SrcLayer"],
                                              self.dLyrSrcParams["AttidudeFldNames"])
            lStructuralValues = parse_layer_data(self.dLyrSrcParams["InputDataTypes"],
                                                 lGeoStructurData)
        elif self.dLyrSrcParams["LayerSrcData"]:
            pass
        else:
            raise Exception("Unknown data type source")

        dialog = PlotStereonetDlg()
        if dialog.exec_():
            dPlotSettings = dict(bPlotPlanes=dialog.chkPlanes.isChecked(),
                                 tPlotPlanesFormat=dialog.cmbPlanesType.currentText(),
                                 bPlotPlaneswithRake=dialog.chkPlaneswithRake.isChecked(),
                                 tPlotPlaneswithRakeFormat=dialog.cmbPlaneswithRakeType.currentText(),
                                 bPlotAxes=dialog.chkAxes.isChecked(),
                                 tPlotAxesFormat=dialog.cmbAxesType.currentText())
            plot_dataset(lStructuralValues, dPlotSettings)

    def clear_stereoplot(self):

        self.stereonet.cla()

    def save_figure(self):

        dialog = FigureExportDlg(self.pluginName, self.dExportParams)

        if dialog.exec_():
            try:
                self.dExportParams["expfig_res_dpi"] = dialog.qleFigResolutionDpi.text()
                fig_resolution_dpi = int(self.dExportParams["expfig_res_dpi"])
            except:
                self.warn("Error in figure resolution value")
                return

            try:
                fig_outpath = unicode(dialog.qleFigureOutPath.text())
            except:
                self.warn("Error in figure output path")
                return
        else:
            self.warn("No export figure defined")
            return

        try:
            self.stereonet.fig.savefig(str(fig_outpath), dpi=fig_resolution_dpi)
            success, msg, func = True, "Image saved", self.info
        except Exception as e:
            success, msg, func = False, "Exception with image saving: {}".format(e.message), self.warn
        finally:
            func(msg)

    def info(self, msg):

        QMessageBox.information(self, self.pluginName, msg)

    def warn(self, msg):

        QMessageBox.warning(self, self.pluginName, msg)

    def update_style_settings(self):

        settings = QSettings("alberese", "geocouche")
        settings.setValue("StereoplotWidget/line_color", self.dPlotStyles["line_color"])
        settings.setValue("StereoplotWidget/line_style", self.dPlotStyles["line_style"])
        settings.setValue("StereoplotWidget/line_width", self.dPlotStyles["line_width"])
        settings.setValue("StereoplotWidget/line_transp", self.dPlotStyles["line_transp"])

        settings.setValue("StereoplotWidget/marker_color", self.dPlotStyles["marker_color"])
        settings.setValue("StereoplotWidget/marker_style", self.dPlotStyles["marker_style"])
        settings.setValue("StereoplotWidget/marker_size", self.dPlotStyles["marker_size"])
        settings.setValue("StereoplotWidget/point_transp", self.dPlotStyles["marker_transp"])

    def closeEvent(self, event):

        # todo: define if this function it's reached or not, and how to change in negative case

        settings = QSettings("alberese", "geocouche")
        settings.setValue("StereoplotWidget/size", self.size())
        settings.setValue("StereoplotWidget/position", self.pos())

        self.window_closed.emit()



