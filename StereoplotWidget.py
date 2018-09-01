# -*- coding: utf-8 -*-

"""
/***************************************************************************
 geocouche - plugin for Quantum GIS

 geologic stereoplots
-------------------

    Begin                : 2015.04.18
    Copyright            : (C) 2015-2018 by Mauro Alberti
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

import os

from builtins import str
from builtins import map

from .apsg import StereoNet, Lin as aLin, Fol as aFol, Fault as aFault

from .auxiliary_windows import *
from .pygsf.orientations.orientations import Plane as GPlane, Axis as GAxis
from .qgis_utils.qgs import pt_geoms_attrs
from .mpl_utils.save_figure import FigureExportDlg
from .fault_utils.utils import rake_to_apsg_movsense, movsense_to_apsg_movsense
from .fault_utils.errors import RakeInputException


class StereoplotWidget(QWidget):

    window_closed = pyqtSignal()

    def __init__(self, canvas, plugin_name, settings_name):

        super(StereoplotWidget, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.mapCanvas = canvas

        self.pluginName = plugin_name
        self.settingsName = settings_name

        # settings stored for geocouche plugin

        settings = QSettings(self.settingsName, self.pluginName)

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
                                  SrcLayer=None,
                                  AttidudeFldNames=[],
                                  InputDataTypes=[])

    def reset_text_src_data(self):

        self.dTxtSrcParams = dict(TextSrcData=False,
                                  GestructuralData=[])

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

        self.pshHelp = QPushButton(self.tr("Help"))
        self.pshHelp.clicked.connect(self.open_help)
        self.layout.addWidget(self.pshHelp)

        self.setLayout(self.layout)
        self.setWindowTitle("{} - stereonet".format(self.pluginName))
        self.adjustSize()

    def open_help(self):

        dialog = HelpDialog(self.pluginName)
        dialog.exec_()

    def define_input(self):

        def extract_input_types():

            def parse_field_choice(val, choose_message):

                if val == choose_message:
                    return ''
                else:
                    return val

            dInputLayerParams = dict()

            try:

                dInputLayerParams["pln_azimuth_type"] = dialog.cmbInputLyrPlaneOrAzimType.currentText()
                dInputLayerParams["pln_azimuth_name_field"] = parse_field_choice(dialog.cmbInputPlaneAzimSrcFld.currentText(),
                                                                                    tFieldUndefined)

                dInputLayerParams["pln_dip_type"] = dialog.cmbInputPlaneOrientDipType.currentText()
                dInputLayerParams["pln_dip_name_field"] = parse_field_choice(dialog.cmbInputPlaneDipSrcFld.currentText(),
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

                dInputLayerParams["ln_rake_type"] = dialog.cmbInputAxisRakeType.currentText()
                dInputLayerParams["ln_rake_name_field"] = parse_field_choice(dialog.cmbInputAxisRakeSrcFld.currentText(),
                                                                              tFieldUndefined)

            except:

                self.warn("Incorrect input field definitions")
                return

            return dInputLayerParams

        def is_valid_layer_input_type(dInputLayerParams):

            if dInputLayerParams["pln_azimuth_name_field"] is not None and \
                            dInputLayerParams["pln_dip_name_field"] is not None:
                return True
            elif dInputLayerParams["ln_azimuth_name_field"] is not None and \
                            dInputLayerParams["ln_dip_name_field"] is not None:
                return True
            else:
                return False

        def actual_layer_inputs_types(dInputParams):

            # define type for planar data

            bIsPlaneDefined = True if dInputParams["pln_azimuth_name_field"] and dInputParams[
                "pln_dip_name_field"] else False

            if bIsPlaneDefined:
                tPlaneAzimType = "dip_dir" if dInputParams["pln_azimuth_type"] == "dip direction" else "strike_rhr"
                tPlaneDipType = "dip"
            else:
                tPlaneAzimType = None
                tPlaneDipType = None

            # define type for linear data

            bIsLnTrndPlngDefined = True if dInputParams["ln_azimuth_name_field"] and dInputParams[
                "ln_dip_name_field"] else False
            bIsLnMovSnsDefined = True if bIsLnTrndPlngDefined and dInputParams["ln_movsen_name_field"] else False
            bIsLnRkDefined = True if bIsPlaneDefined and dInputParams["ln_rake_name_field"] else False

            if bIsLnTrndPlngDefined:
                tLineAzimType = "trend"
                tLineDipType = "plunge"
            else:
                tLineAzimType = None
                tLineDipType = None

            if bIsLnMovSnsDefined:
                tLineMovSenseType = "movement_sense"
            else:
                tLineMovSenseType = None

            if bIsLnRkDefined:
                tLineRakeType = "rake"
            else:
                tLineRakeType = None

            return dict(has_plane_data=bIsPlaneDefined,
                        pln_az_type=tPlaneAzimType,
                        pln_dip_type=tPlaneDipType,
                        has_line_trpl_data=bIsLnTrndPlngDefined,
                        ln_az_type=tLineAzimType,
                        ln_dip_type=tLineDipType,
                        has_ln_ms_data=bIsLnMovSnsDefined,
                        ln_ms_type=tLineMovSenseType,
                        has_rake_data=bIsLnRkDefined,
                        ln_rake_type=tLineRakeType)

        def orientations_from_text(data_type, azimuth_type, text, sep=','):

            def extract_values(row):

                def parse_plane_dirdir(az_raw):

                    if azimuth_type == "strike rhr":
                        dip_dir = az_raw + 90.0
                    else:
                        dip_dir = az_raw

                    return dip_dir % 360.0

                def parse_fault_mov_sense(raw_values):

                    azim, dip_ang, lin_trend, lin_plunge = list(map(float, raw_values[:4]))
                    mov_sense = str(raw_values[4])

                    return azim, dip_ang, lin_trend, lin_plunge, mov_sense

                record_dict = dict()
                try:
                    raw_values = row.split(sep)
                    if data_type == "planes":
                        azim, dip_ang = list(map(float, raw_values))
                        record_dict["pln_dipdir"] = parse_plane_dirdir(azim)
                        record_dict["pln_dipang"] = dip_ang
                    elif data_type == "axes":
                        trend, plunge = list(map(float, raw_values))
                        record_dict["ln_tr"] = trend
                        record_dict["ln_pl"] = plunge
                    elif data_type == "planes & axes":
                        azim, dip_ang, trend, plunge = list(map(float, raw_values))
                        record_dict["pln_dipdir"] = parse_plane_dirdir(azim)
                        record_dict["pln_dipang"] = dip_ang
                        record_dict["ln_tr"] = trend
                        record_dict["ln_pl"] = plunge
                    elif data_type == "fault planes with slickenline trend, plunge and movement sense":
                        azim, dip_ang, slick_tr, slick_pl, mov_sense = parse_fault_mov_sense(raw_values)
                        record_dict["pln_dipdir"] = parse_plane_dirdir(azim)
                        record_dict["pln_dipang"] = dip_ang
                        record_dict["ln_tr"] = slick_tr
                        record_dict["ln_pl"] = slick_pl
                        record_dict["ln_ms"] = mov_sense
                    elif data_type == "fault planes with rake":
                        azim, dip_ang, rake = list(map(float, raw_values))
                        record_dict["pln_dipdir"] = parse_plane_dirdir(azim)
                        record_dict["pln_dipang"] = dip_ang
                        record_dict["ln_rk"] = rake
                    else:
                        raise Exception("Unimplemented input type")
                except:
                    self.warn("Check input values")

                return record_dict

            if text is None or text == '':
                return False, "No value available"
            rows = text.split("\n")
            if len(rows) == 0:
                return False, "No value available"
            else:
                geostructural_data = []
                for row in rows:
                    if row:
                        data_row = extract_values(row)
                        if not data_row:
                            return False, "Error with input"
                        else:
                            geostructural_data.append(data_row)

            if geostructural_data:
                return True, geostructural_data
            else:
                return False, "No extracted data"


        llyrLoadedPointLayers = loaded_point_layers()
        dialog = StereoplotInputDlg(llyrLoadedPointLayers)
        if dialog.exec_():

            if dialog.tabWdgt.currentIndex() == 0:  # layer as input

                self.reset_text_src_data()  # discard text-derived data

                # check that input layer is defined
                try:
                    lyrInputLayer = llyrLoadedPointLayers[dialog.cmbInputLayers.currentIndex() - 1]
                except:
                    self.warn("Incorrect point layer choice")
                    return

                # extract input type definitions
                dInputLayerParams = extract_input_types()
                if not is_valid_layer_input_type(dInputLayerParams):
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

                self.dLyrSrcParams["LayerSrcData"] = True
                self.dLyrSrcParams["SrcLayer"] = lyrInputLayer
                self.dLyrSrcParams["AttidudeFldNames"] = ltAttitudeFldNms
                self.dLyrSrcParams["InputDataTypes"] = actual_layer_inputs_types(dInputLayerParams)

            elif dialog.tabWdgt.currentIndex() == 1:  # text as input

                self.reset_layer_src_data()  # discard layer-derived data

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
                    self.dTxtSrcParams["GestructuralData"] = tResult

            else:  # unknown choice

                self.reset_text_src_data()  # discard text-derived data
                self.reset_layer_src_data()  # discard layer-derived data

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

            def parse_azimuth(azimuth):

                if az_type == "dip_dir":
                    offset = 0.0
                elif az_type == "strike_rhr":
                    offset = 90.0
                else:
                    raise Exception("Invalid azimuth data type")

                return (float(azimuth) + offset) % 360.0

            # create list of text holders for data to extract

            data_types_to_extract = [("x", float), ("y", float)]
            if input_data_types["has_plane_data"]:
                az_type = input_data_types["pln_az_type"]
                data_types_to_extract += [("pln_dipdir", parse_azimuth), ("pln_dipang", float)]
            if input_data_types["has_line_trpl_data"]:
                data_types_to_extract += [("ln_tr", float), ("ln_pl", float)]
            if input_data_types["has_ln_ms_data"]:
                data_types_to_extract.append(("ln_ms", str))
            if input_data_types["has_rake_data"]:
                data_types_to_extract.append(("ln_rk", float))

            # extract and parse raw data

            lSrcStructuralVals = []
            for rec in structural_data:
                dRecord = dict()
                for ndx, (key, func) in enumerate(data_types_to_extract):
                    dRecord[key] = func(rec[ndx])
                lSrcStructuralVals.append(dRecord)

            return lSrcStructuralVals

        def plot_dataset(structural_values, plot_setts):

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

            def downaxis_from_rake(dipdir, dipang, rk):

                return GPlane(dipdir, dipang).rakeToDirect(float(rk)).downward().d

            def get_plane_data(struct_vals):

                plane_data = []
                for row in struct_vals:
                    if not ("pln_dipdir" in row and "pln_dipang" in row):
                        continue
                    else:
                        plane_data.append([row["pln_dipdir"], row["pln_dipang"]])

                return plane_data

            def get_line_data(struct_vals):

                line_data = []
                for row in struct_vals:
                    if not (("ln_tr" in row and "ln_pl" in row) or
                            ("pln_dipdir" in row and "pln_dipang" in row and "ln_rk" in row)):
                        continue
                    else:
                        if "pln_dipdir" in row and "pln_dipang" in row and "ln_rk" in row:
                            lin_tr, lin_pl = downaxis_from_rake(row["pln_dipdir"], row["pln_dipang"], row["ln_rk"])
                        elif "ln_tr" in row and "ln_pl" in row:
                            lin_tr, lin_pl = row["ln_tr"], row["ln_pl"]
                        else:
                            continue
                        line_data.append([lin_tr, lin_pl])

                return line_data

            def get_fault_slikenline_data(struct_vals):

                fault_slickenline_data = []
                for row in struct_vals:
                    if "pln_dipdir" in row and "pln_dipang" in row:
                        dip_dir = row["pln_dipdir"]
                        dip_ang = row["pln_dipang"]
                        if "ln_rk" in row:
                            rake = row["ln_rk"]
                            lin_tr, lin_pl = downaxis_from_rake(dip_dir, dip_ang, rake)
                            try:
                                sense = rake_to_apsg_movsense(rake)
                            except RakeInputException as e:
                                self.warn(e)
                                return []
                        elif "ln_tr" in row and "ln_pl" in row and "ln_ms" in row:
                            lin_tr, lin_pl = row["ln_tr"], row["ln_pl"]
                            mov_sense = row["ln_ms"].upper()
                            if mov_sense == "":
                                continue
                            else:
                                try:
                                    sense = movsense_to_apsg_movsense(mov_sense)
                                except:
                                    self.warn("Unrecognized movement type")
                                    return []
                        else:
                            continue
                        fault_slickenline_data.append((dip_dir, dip_ang, lin_tr, lin_pl, sense))
                    else:
                        continue

                if not fault_slickenline_data:
                    self.warn("No fault-slickenline data extracted")

                return fault_slickenline_data

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
                            p = aFol(*plane)
                            self.stereonet.plane(p,
                                                 linestyle=line_style,
                                                 linewidth=line_width,
                                                 color=line_color,
                                                 alpha=line_alpha)
                        elif plot_setts["tPlotPlanesFormat"] == "normal axes":
                            line_rec = GPlane(*plane).normDirect().d
                            l = aLin(*line_rec)
                            self.stereonet.line(l,
                                                marker=marker_style,
                                                markersize=marker_size,
                                                color=marker_color,
                                                alpha=marker_transp)
                        else:
                            raise Exception("Not yet implemented")

            if plot_setts["bPlotPlaneswithRake"]:
                flt_slik_data = get_fault_slikenline_data(structural_values)
                if not flt_slik_data:
                    self.warn(("No fault-slickenline data"))
                else:
                    for flt_slick in flt_slik_data:
                        dip_dir, dip_ang, lin_tr, lin_pl, sense = flt_slick
                        flt = aFault(dip_dir, dip_ang, lin_tr, lin_pl, sense)
                        if plot_setts["tPlotPlaneswithRakeFormat"] == "faults with skickenlines":
                            self.stereonet.fault(flt,
                                                 linestyle=line_style,
                                                 linewidth=line_width,
                                                 color=line_color,
                                                 alpha=line_alpha)
                        elif plot_setts["tPlotPlaneswithRakeFormat"] == "T-L diagrams":
                            self.stereonet.hoeppner(flt,
                                                     linestyle=line_style,
                                                     linewidth=line_width,
                                                     color=line_color,
                                                     alpha=line_alpha)
                        else:
                            raise Exception("Not yet implemented")

            if plot_setts["bPlotAxes"]:
                line_data = get_line_data(structural_values)
                if not line_data:
                    self.warn(("No line data"))
                else:
                    for line_rec in line_data:
                        if plot_setts["tPlotAxesFormat"] == "poles":
                            l = aLin(*line_rec)
                            self.stereonet.line(l,
                                                marker=marker_style,
                                                markersize=marker_size,
                                                color=marker_color,
                                                alpha=marker_transp)
                        elif plot_setts["tPlotAxesFormat"] == "perpendicular planes":
                            plane = GAxis(*line_rec).normal_gplane.dda
                            p = aFol(*plane)
                            self.stereonet.plane(p,
                                                 linestyle=line_style,
                                                 linewidth=line_width,
                                                 color=line_color,
                                                 alpha=line_alpha)
                        else:
                            raise Exception("Not yet implemented")

        if not (self.dLyrSrcParams["LayerSrcData"] or self.dTxtSrcParams["TextSrcData"]):
            self.warn("No data to plot")
            return
        elif self.dLyrSrcParams["LayerSrcData"] and self.dTxtSrcParams["TextSrcData"]:
            raise Exception("Debug: both layer and text sources defined")
        else:
            pass

        if self.dLyrSrcParams["LayerSrcData"]:
            lGeoStructurData = pt_geoms_attrs(self.dLyrSrcParams["SrcLayer"],
                                              self.dLyrSrcParams["AttidudeFldNames"])
            lStructuralValues = parse_layer_data(self.dLyrSrcParams["InputDataTypes"],
                                                 lGeoStructurData)
        elif self.dTxtSrcParams["TextSrcData"]:
            lStructuralValues = self.dTxtSrcParams["GestructuralData"]
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
                fig_outpath = str(dialog.qleFigureOutPath.text())
            except:
                self.warn("Error in figure output path")
                return
        else:
            self.warn("No export figure defined")
            return

        try:
            self.stereonet.fig.savefig(str(fig_outpath), dpi=fig_resolution_dpi)
            success, msg = True, "Image saved"
        except Exception as e:
            success, msg = False, "Exception with image saving: {}".format(e)

        if success:
            self.info(msg)
        else:
            self.warn(msg)

    def info(self, msg):

        QMessageBox.information(self, self.pluginName, msg)

    def warn(self, msg):

        QMessageBox.warning(self, self.pluginName, msg)

    def update_style_settings(self):

        settings = QSettings(self.settingsName, self.pluginName)
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

        settings = QSettings(self.settingsName, self.pluginName)
        settings.setValue("StereoplotWidget/size", self.size())
        settings.setValue("StereoplotWidget/position", self.pos())

        self.window_closed.emit()


class HelpDialog(QDialog):

    def __init__(self, plugin_name, parent=None):
        super(HelpDialog, self).__init__(parent)

        layout = QVBoxLayout()

        # About section

        helpTextBrwsr = QTextBrowser(self)

        url_path = "file:///{}/help/help_stereonet.html".format(os.path.dirname(__file__))
        helpTextBrwsr.setSource(QUrl(url_path))
        helpTextBrwsr.setSearchPaths(['{}/help'.format(os.path.dirname(__file__))])
        helpTextBrwsr.setMinimumSize(700, 600)
        layout.addWidget(helpTextBrwsr)

        self.setLayout(layout)

        self.setWindowTitle("{} - stereonet help".format(plugin_name))





