# -*- coding: utf-8 -*-

from builtins import str
from collections import OrderedDict

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.gui import QgsColorButton

from .qgis_utils.qgs import loaded_point_layers


ltInputDataTypes = ("planes", "axes", "planes & axes", "fault planes with slickenline trend, plunge and movement sense", "fault planes with rake")
ltInputPlaneAzimuthTypes = ["dip direction", "strike rhr"]
ltInputPlaneDipTypes = ["dip angle"]
ltInputAxisRakeTypes = ["rake - Aki & Richards, 1980"]
ltInputAxisAzimuthTypes = ["trend"]
ltInputAxisDipTypes = ["plunge"]
ltInputAxisMovSenseTypes = ["mov. sense - N or R"]

tLayerChooseMsg = "choose"
tFieldUndefined = "---"

ltLineStyles = ["solid", "dashed", "dashdot", "dotted"]
ltMarkerStyles = OrderedDict([("circle", "o"), ("square", "s"), ("diamond", "D"), ("triangle", "^")])

ltFileFormats = ["pdf", "png", "svg", "tif"]
liDpiResolutions = [200, 400, 600, 800, 1000, 1200]


class StereoplotInputDlg(QDialog):

    def __init__(self, llyrLoadedPointLayers, parent=None):

        super(StereoplotInputDlg, self).__init__(parent)
        self.llyrLoadedPointLayers = llyrLoadedPointLayers

        layout = QGridLayout()
        self.tabWdgt = QTabWidget()

        self.wdgtLayerInput = self.setup_layer_input_gui()
        self.layerTab = self.tabWdgt.addTab(self.wdgtLayerInput, "Layer")

        self.wdgtTextInput = self.setup_text_input_gui()
        self.textTab = self.tabWdgt.addTab(self.wdgtTextInput, "Text")

        layout.addWidget(self.tabWdgt, 0, 0, 1, 1)

        self.setLayout(layout)

        self.setWindowTitle("Stereoplot input")

    def setup_layer_input_gui(self):

        wdgtLayerInput = QWidget()
        lytLayerInput = QVBoxLayout()

        # input layer

        grpLayer = QGroupBox("Point layer")
        lytLayer = QGridLayout()

        self.cmbInputLayers = QComboBox()
        lytLayer.addWidget(self.cmbInputLayers, 0, 0, 1, 2)

        grpLayer.setLayout(lytLayer)
        lytLayerInput.addWidget(grpLayer)

        # plane values

        grpPlane = QGroupBox("Plane attitudes")
        lytPlane = QGridLayout()

        self.cmbInputLyrPlaneOrAzimType = QComboBox()
        self.cmbInputLyrPlaneOrAzimType.addItems(ltInputPlaneAzimuthTypes)
        lytPlane.addWidget(self.cmbInputLyrPlaneOrAzimType, 0, 0, 1, 1)

        self.cmbInputPlaneAzimSrcFld = QComboBox()
        lytPlane.addWidget(self.cmbInputPlaneAzimSrcFld, 0, 1, 1, 1)

        self.cmbInputPlaneOrientDipType = QComboBox()
        self.cmbInputPlaneOrientDipType.addItems(ltInputPlaneDipTypes)
        lytPlane.addWidget(self.cmbInputPlaneOrientDipType, 1, 0, 1, 1)

        self.cmbInputPlaneDipSrcFld = QComboBox()
        lytPlane.addWidget(self.cmbInputPlaneDipSrcFld, 1, 1, 1, 1)

        grpPlane.setLayout(lytPlane)
        lytLayerInput.addWidget(grpPlane)

        # line values

        grpAxisAttitudes = QGroupBox("Line orientations")
        lytAxisAttitudes = QGridLayout()

        self.cmbInputAxisAzimType = QComboBox()
        self.cmbInputAxisAzimType.addItems(ltInputAxisAzimuthTypes)
        lytAxisAttitudes.addWidget(self.cmbInputAxisAzimType, 0, 0, 1, 1)

        self.cmbInputAxisAzimSrcFld = QComboBox()
        lytAxisAttitudes.addWidget(self.cmbInputAxisAzimSrcFld, 0, 1, 1, 1)

        self.cmbInputAxisDipType = QComboBox()
        self.cmbInputAxisDipType.addItems(ltInputAxisDipTypes)
        lytAxisAttitudes.addWidget(self.cmbInputAxisDipType, 1, 0, 1, 1)

        self.cmbInputAxisDipSrcFld = QComboBox()
        lytAxisAttitudes.addWidget(self.cmbInputAxisDipSrcFld, 1, 1, 1, 1)

        self.cmbInputAxisMovSenseType = QComboBox()
        self.cmbInputAxisMovSenseType.addItems(ltInputAxisMovSenseTypes)
        lytAxisAttitudes.addWidget(self.cmbInputAxisMovSenseType, 2, 0, 1, 1)

        self.cmbInputAxisMovSenseSrcFld = QComboBox()
        lytAxisAttitudes.addWidget(self.cmbInputAxisMovSenseSrcFld, 2, 1, 1, 1)

        self.cmbInputAxisRakeType = QComboBox()
        self.cmbInputAxisRakeType.addItems(ltInputAxisRakeTypes)
        lytAxisAttitudes.addWidget(self.cmbInputAxisRakeType, 3, 0, 1, 1)

        self.cmbInputAxisRakeSrcFld = QComboBox()
        lytAxisAttitudes.addWidget(self.cmbInputAxisRakeSrcFld, 3, 1, 1, 1)

        grpAxisAttitudes.setLayout(lytAxisAttitudes)
        lytLayerInput.addWidget(grpAxisAttitudes)

        self.lStructuralComboxes = [self.cmbInputPlaneAzimSrcFld,
                                    self.cmbInputPlaneDipSrcFld,
                                    self.cmbInputAxisRakeSrcFld,
                                    self.cmbInputAxisAzimSrcFld,
                                    self.cmbInputAxisDipSrcFld,
                                    self.cmbInputAxisMovSenseSrcFld]

        self.refresh_struct_point_lyr_combobox(self.llyrLoadedPointLayers)

        self.cmbInputLayers.currentIndexChanged[int].connect(self.refresh_structural_fields_comboboxes)

        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")

        lytButtons = QHBoxLayout()
        lytButtons.addStretch()
        lytButtons.addWidget(btnOk)
        lytButtons.addWidget(btnCancel)

        lytLayerInput.addLayout(lytButtons)

        wdgtLayerInput.setLayout(lytLayerInput)

        btnOk.clicked.connect(self.accept)
        btnCancel.clicked.connect(self.reject)

        return wdgtLayerInput

    def setup_text_input_gui(self):

        wdgtTextInput = QWidget()
        lytTextInput = QVBoxLayout()

        # input values

        grpInputValues = QGroupBox("Input values")
        lytInputValues = QGridLayout()

        lytInputValues.addWidget(QLabel("Data are"), 0, 0, 1, 1)
        self.cmbInputDataType = QComboBox()
        self.cmbInputDataType.addItems(ltInputDataTypes)
        self.cmbInputDataType.setCurrentIndex(2)
        lytInputValues.addWidget(self.cmbInputDataType, 0, 1, 1, 1)

        lytInputValues.addWidget(QLabel("Plane azimuth refers to"), 1, 0, 1, 1)
        self.cmbInputPlaneOrAzimType = QComboBox()
        self.cmbInputPlaneOrAzimType.addItems(ltInputPlaneAzimuthTypes)
        lytInputValues.addWidget(self.cmbInputPlaneOrAzimType, 1, 1, 1, 1)

        lytInputValues.addWidget(QLabel("Input example for planes and axes: \n220,33,131,1\n145,59,57,9"), 2, 0, 1, 2)
        lytInputValues.addWidget(
            QLabel("Input example for faults with movement sense: \n220,33,222,32,N"), 3, 0, 1, 2)
        lytInputValues.addWidget(QLabel("Input example for faults with rake (Aki and Richards, 1980): \n220,33,122\n145,59,-3"), 4, 0, 1, 2)


        self.plntxtedInputValues = QPlainTextEdit()
        lytInputValues.addWidget(self.plntxtedInputValues, 5, 0, 5, 2)

        grpInputValues.setLayout(lytInputValues)
        lytTextInput.addWidget(grpInputValues)

        # ok/cancel choices

        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")

        btnOk.clicked.connect(self.accept)
        btnCancel.clicked.connect(self.reject)

        lytButtons = QHBoxLayout()
        lytButtons.addStretch()
        lytButtons.addWidget(btnOk)
        lytButtons.addWidget(btnCancel)

        lytTextInput.addLayout(lytButtons)

        wdgtTextInput.setLayout(lytTextInput)

        return wdgtTextInput

    def refresh_struct_point_lyr_combobox(self, llyrLoadedPointLayers):

        self.cmbInputLayers.clear()

        self.cmbInputLayers.addItem(tLayerChooseMsg)
        self.cmbInputLayers.addItems([layer.name() for layer in llyrLoadedPointLayers])

        self.reset_structural_field_comboboxes()

    def reset_structural_field_comboboxes(self):

        for structural_combox in self.lStructuralComboxes:
            structural_combox.clear()
            structural_combox.addItem(tFieldUndefined)

    def refresh_structural_fields_comboboxes(self):

        self.reset_structural_field_comboboxes()

        point_shape_qgis_ndx = self.cmbInputLayers.currentIndex() - 1
        if point_shape_qgis_ndx == -1:
            return

        point_layer = self.llyrLoadedPointLayers[point_shape_qgis_ndx]

        lPointLayerFields = point_layer.dataProvider().fields().toList()

        ltFieldNames = [field.name() for field in lPointLayerFields]

        for structural_combox in self.lStructuralComboxes:
            structural_combox.addItems(ltFieldNames)


class PlotStyleDlg(QDialog):

    def __init__(self, dPlotStyles, parent=None):

        super(PlotStyleDlg, self).__init__(parent)

        self.dPlotStyles = dPlotStyles

        settings = QSettings("alberese", "geocouche")

        layout = QVBoxLayout()

        # great circle settings

        grpGreatCircles = QGroupBox("Great circles")
        lytGreatCircles = QGridLayout()

        # line color

        lytGreatCircles.addWidget(QLabel("Line color"), 0, 0, 1, 1)
        self.btnLineColor = QgsColorButton()
        line_color = self.dPlotStyles["line_color"]
        self.btnLineColor.setColor(QColor(line_color))
        lytGreatCircles.addWidget(self.btnLineColor, 0, 1, 1, 1)

        # line style

        lytGreatCircles.addWidget(QLabel("Line style"), 0, 2, 1, 1)
        self.cmbLineStyle = QComboBox()
        self.cmbLineStyle.insertItems(0, ltLineStyles)
        line_style = self.dPlotStyles["line_style"]
        line_style_ndx = ltLineStyles.index(line_style) if line_style in ltLineStyles else 0
        self.cmbLineStyle.setCurrentIndex(line_style_ndx)
        lytGreatCircles.addWidget(self.cmbLineStyle, 0, 3, 1, 1)
    
        # line thickness

        lytGreatCircles.addWidget(QLabel("Line width"), 1, 0, 1, 1)        
        self.cmbLineWidth = QComboBox()
        lnLineThickness = [1, 2, 3, 4, 5, 6]
        ltLineThicknVals = [str(val) + " pt(s)" for val in lnLineThickness]
        self.cmbLineWidth.insertItems(0, ltLineThicknVals)
        line_thickn = self.dPlotStyles["line_width"]
        line_thickn_ndx = ltLineThicknVals.index(line_thickn) if line_thickn in ltLineThicknVals else 0 
        self.cmbLineWidth.setCurrentIndex(line_thickn_ndx)
        lytGreatCircles.addWidget(self.cmbLineWidth, 1, 1, 1, 1)

        # line transparency

        lytGreatCircles.addWidget(QLabel("Line transp."), 1, 2, 1, 1)
        self.cmbLineTransp = QComboBox()        
        lnLineTransparencies = [0, 25, 50, 75]
        ltLineTranspPrcntVals = [str(val) + "%" for val in lnLineTransparencies]
        self.cmbLineTransp.insertItems(0, ltLineTranspPrcntVals)
        line_transp = self.dPlotStyles["line_transp"]
        line_transp_ndx = ltLineTranspPrcntVals.index(line_transp) if line_transp in ltLineTranspPrcntVals else 0 
        self.cmbLineTransp.setCurrentIndex(line_transp_ndx)        
        lytGreatCircles.addWidget(self.cmbLineTransp, 1, 3, 1, 1)

        # set/add to layout

        grpGreatCircles.setLayout(lytGreatCircles)
        layout.addWidget(grpGreatCircles)

        # pole settings

        grpPoles = QGroupBox("Poles")
        lytPoles = QGridLayout()

        # marker color

        lytPoles.addWidget(QLabel("Marker color"), 0, 0, 1, 1)
        self.btnPointColor = QgsColorButton()
        point_color = self.dPlotStyles["marker_color"]
        self.btnPointColor.setColor(QColor(point_color))
        lytPoles.addWidget(self.btnPointColor, 0, 1, 1, 1)

        # marker style

        lytPoles.addWidget(QLabel("Marker style"), 0, 2, 1, 1)
        self.cmbPointStyle = QComboBox()
        self.cmbPointStyle.insertItems(0, list(ltMarkerStyles.keys()))
        point_style = self.dPlotStyles["marker_style"]
        point_style_ndx = list(ltMarkerStyles.keys()).index(point_style) if point_style in list(ltMarkerStyles.keys()) else 0
        self.cmbPointStyle.setCurrentIndex(point_style_ndx)
        lytPoles.addWidget(self.cmbPointStyle, 0, 3, 1, 1)
        
        # marker size

        lytPoles.addWidget(QLabel("Marker size"), 1, 0, 1, 1)
        lnPointSizes = [2, 4, 6, 8, 10, 15, 20]
        self.cmbPointSize = QComboBox()
        ltPointSizeVals = [str(val) + " pt(s)" for val in lnPointSizes]
        self.cmbPointSize.insertItems(0, ltPointSizeVals)
        point_size = self.dPlotStyles["marker_size"]
        point_style_ndx = ltPointSizeVals.index(point_size) if point_size in ltPointSizeVals else 2        
        self.cmbPointSize.setCurrentIndex(point_style_ndx)
        lytPoles.addWidget(self.cmbPointSize, 1, 1, 1, 1)

        # marker transparency

        lytPoles.addWidget(QLabel("Marker transp."), 1, 2, 1, 1)
        lnPointTransparencies = [0, 25, 50, 75]
        self.cmbPointTransp = QComboBox()
        ltPointTranspPrcntVals = [str(val) + "%" for val in lnPointTransparencies]
        self.cmbPointTransp.insertItems(0, ltPointTranspPrcntVals)
        point_transp = self.dPlotStyles["marker_transp"]
        point_transp_ndx = ltPointTranspPrcntVals.index(point_transp) if point_transp in ltPointTranspPrcntVals else 0 
        self.cmbPointTransp.setCurrentIndex(point_transp_ndx)        
        lytPoles.addWidget(self.cmbPointTransp, 1, 3, 1, 1)

        # set/add to layout

        grpPoles.setLayout(lytPoles)
        layout.addWidget(grpPoles)

        # ok/cancel stuff
        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")

        lytButtons = QHBoxLayout()
        lytButtons.addStretch()
        lytButtons.addWidget(btnOk)
        lytButtons.addWidget(btnCancel)

        layout.addLayout(lytButtons)

        btnOk.clicked.connect(self.accept)
        btnCancel.clicked.connect(self.reject)

        self.setLayout(layout)

        self.setWindowTitle("Plot style")


class PlotStereonetDlg(QDialog):

    def __init__(self, parent=None):

        super(PlotStereonetDlg, self).__init__(parent)

        layout = QVBoxLayout()

        grpPlot = QGroupBox("")

        lytPlot = QGridLayout()

        lytPlot.addWidget(QLabel("Plot"), 0, 0, 1, 2)

        # planes

        self.chkPlanes = QCheckBox("planes")
        self.chkPlanes.setChecked(True)
        lytPlot.addWidget(self.chkPlanes, 1, 0, 1, 1)
        lytPlot.addWidget(QLabel("as"), 1, 1, 1, 1)
        self.cmbPlanesType = QComboBox()
        self.cmbPlanesType.insertItems(0, ["great circles", "normal axes"])
        lytPlot.addWidget(self.cmbPlanesType, 1, 2, 1, 1)

        # lines

        self.chkAxes = QCheckBox("lines")
        self.chkAxes.setChecked(False)
        lytPlot.addWidget(self.chkAxes, 2, 0, 1, 1)
        lytPlot.addWidget(QLabel("as"), 2, 1, 1, 1)
        self.cmbAxesType = QComboBox()
        self.cmbAxesType.insertItems(0, ["poles", "perpendicular planes"])
        lytPlot.addWidget(self.cmbAxesType, 2, 2, 1, 1)

        # planes and lines

        self.chkPlaneswithRake = QCheckBox("planes and lines")
        self.chkPlaneswithRake.setChecked(False)
        lytPlot.addWidget(self.chkPlaneswithRake, 3, 0, 1, 1)
        lytPlot.addWidget(QLabel("as"), 3, 1, 1, 1)
        self.cmbPlaneswithRakeType = QComboBox()
        self.cmbPlaneswithRakeType.insertItems(0, ["faults with skickenlines", "T-L diagrams"])
        lytPlot.addWidget(self.cmbPlaneswithRakeType, 3, 2, 1, 1)

        grpPlot.setLayout(lytPlot)
        layout.addWidget(grpPlot)

        # ok/cancel stuff

        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")

        btnOk.clicked.connect(self.accept)
        btnCancel.clicked.connect(self.reject)

        lytButtons = QHBoxLayout()
        lytButtons.addStretch()
        lytButtons.addWidget(btnOk)
        lytButtons.addWidget(btnCancel)

        layout.addLayout(lytButtons)

        # final settings

        self.setLayout(layout)

        self.setWindowTitle("Stereonet plot")


class SaveFigureDlg(QDialog):

    def __init__(self, dFigureParams, parent=None):

        super(SaveFigureDlg, self).__init__(parent)

        self.dFigureParams = dFigureParams

        layout = QVBoxLayout()

        # output format settings

        grpFormatSettings = QGroupBox("Output format")
        lytFormatSettings = QGridLayout()

        # format

        lytFormatSettings.addWidget(QLabel("File format"), 0, 0, 1, 1)
        self.cmbFileFormat = QComboBox()
        self.cmbFileFormat.insertItems(0, ltFileFormats)
        sFileFormat = self.dPlotStyles["file_format"]
        iCurrFileFrmtNdx = ltFileFormats.index(sFileFormat) if sFileFormat in ltFileFormats else 0
        self.cmbFileFormat.setCurrentIndex(iCurrFileFrmtNdx)
        lytFormatSettings.addWidget(self.cmbFileFormat, 0, 1, 1, 1)

        # dpi (for rasters)

        lytFormatSettings.addWidget(QLabel("Dpi (for rasters"), 1, 0, 1, 1)
        self.cmbDpiResolution = QComboBox()
        self.cmbDpiResolution.insertItems(0, liDpiResolutions)
        iCurrDpiResolution = self.dPlotStyles["dpi_resolution"]
        iCurrDpiResolNdx = ltFileFormats.index(iCurrDpiResolution) if iCurrDpiResolution in ltFileFormats else 0
        self.cmbDpiResolution.setCurrentIndex(iCurrDpiResolNdx)
        lytFormatSettings.addWidget(self.cmbDpiResolution, 1, 1, 1, 1)

        # set/add to layout

        grpFormatSettings.setLayout(lytFormatSettings)
        layout.addWidget(grpFormatSettings)

        # output file path

        grpPoles = QGroupBox("Poles")
        lytPoles = QGridLayout()

        # marker color

        lytPoles.addWidget(QLabel("Marker color"), 0, 0, 1, 1)
        self.btnPointColor = QgsColorButton()
        point_color = self.dPlotStyles["marker_color"]
        self.btnPointColor.setColor(QColor(point_color))
        lytPoles.addWidget(self.btnPointColor, 0, 1, 1, 1)

        # marker style

        lytPoles.addWidget(QLabel("Marker style"), 0, 2, 1, 1)
        self.cmbPointStyle = QComboBox()
        self.cmbPointStyle.insertItems(0, list(ltMarkerStyles.keys()))
        point_style = self.dPlotStyles["marker_style"]
        point_style_ndx = list(ltMarkerStyles.keys()).index(point_style) if point_style in list(ltMarkerStyles.keys()) else 0
        self.cmbPointStyle.setCurrentIndex(point_style_ndx)
        lytPoles.addWidget(self.cmbPointStyle, 0, 3, 1, 1)

        # marker size

        lytPoles.addWidget(QLabel("Marker size"), 1, 0, 1, 1)
        lnPointSizes = [2, 4, 6, 8, 10, 15, 20]
        self.cmbPointSize = QComboBox()
        ltPointSizeVals = [str(val) + " pt(s)" for val in lnPointSizes]
        self.cmbPointSize.insertItems(0, ltPointSizeVals)
        point_size = self.dPlotStyles["marker_size"]
        point_style_ndx = ltPointSizeVals.index(point_size) if point_size in ltPointSizeVals else 2
        self.cmbPointSize.setCurrentIndex(point_style_ndx)
        lytPoles.addWidget(self.cmbPointSize, 1, 1, 1, 1)

        # marker transparency

        lytPoles.addWidget(QLabel("Marker transp."), 1, 2, 1, 1)
        lnPointTransparencies = [0, 25, 50, 75]
        self.cmbPointTransp = QComboBox()
        ltPointTranspPrcntVals = [str(val) + "%" for val in lnPointTransparencies]
        self.cmbPointTransp.insertItems(0, ltPointTranspPrcntVals)
        point_transp = self.dPlotStyles["marker_transp"]
        point_transp_ndx = ltPointTranspPrcntVals.index(point_transp) if point_transp in ltPointTranspPrcntVals else 0
        self.cmbPointTransp.setCurrentIndex(point_transp_ndx)
        lytPoles.addWidget(self.cmbPointTransp, 1, 3, 1, 1)

        # set/add to layout

        grpPoles.setLayout(lytPoles)
        layout.addWidget(grpPoles)

        # ok/cancel stuff
        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")

        lytButtons = QHBoxLayout()
        lytButtons.addStretch()
        lytButtons.addWidget(btnOk)
        lytButtons.addWidget(btnCancel)

        layout.addLayout(lytButtons)

        btnOk.clicked.connect(self.accept)
        btnCancel.clicked.connect(self.reject)

        self.setLayout(layout)

        self.setWindowTitle("Plot style")


class AnglesSrcPtLyrDlg(QDialog):

    def __init__(self, parent=None):

        super(AnglesSrcPtLyrDlg, self).__init__(parent)

        self.tFieldUndefined = tFieldUndefined

        self.setup_gui()

    def setup_gui(self):

        layout = QVBoxLayout()

        # input layer

        grpLayer = QGroupBox("Input point layer")
        lytLayer = QGridLayout()

        self.cmbInputLayers = QComboBox()
        lytLayer.addWidget(self.cmbInputLayers, 0, 0, 1, 2)

        grpLayer.setLayout(lytLayer)
        layout.addWidget(grpLayer)

        # plane values

        grpPlane = QGroupBox("Planar orientation source fields")
        lytPlane = QGridLayout()

        self.cmbInputPlaneOrientAzimType = QComboBox()
        self.cmbInputPlaneOrientAzimType.addItems(ltInputPlaneAzimuthTypes)
        lytPlane.addWidget(self.cmbInputPlaneOrientAzimType, 0, 0, 1, 1)

        self.cmbInputPlaneAzimSrcFld = QComboBox()
        lytPlane.addWidget(self.cmbInputPlaneAzimSrcFld, 0, 1, 1, 1)

        self.cmbInputPlaneOrientDipType = QComboBox()
        self.cmbInputPlaneOrientDipType.addItems(ltInputPlaneDipTypes)
        lytPlane.addWidget(self.cmbInputPlaneOrientDipType, 1, 0, 1, 1)

        self.cmbInputPlaneDipSrcFld = QComboBox()
        lytPlane.addWidget(self.cmbInputPlaneDipSrcFld, 1, 1, 1, 1)

        self.lStructuralComboxes = [self.cmbInputPlaneAzimSrcFld,
                                    self.cmbInputPlaneDipSrcFld]

        self.refresh_struct_point_lyr_combobox()

        self.cmbInputLayers.currentIndexChanged[int].connect(self.refresh_structural_fields_comboboxes)

        grpPlane.setLayout(lytPlane)
        layout.addWidget(grpPlane)

        # target attitude

        grpTargetPlane = QGroupBox("Target plane")
        lytTargetPlane = QGridLayout()

        lytTargetPlane.addWidget(QLabel("Dip dir."), 0, 0, 1, 1)

        self.spnTargetAttDipDir = QDoubleSpinBox()
        self.spnTargetAttDipDir.setMinimum(0.0)
        self.spnTargetAttDipDir.setMaximum(359.9)
        self.spnTargetAttDipDir.setDecimals(1)
        lytTargetPlane.addWidget(self.spnTargetAttDipDir, 0, 1, 1, 1)

        lytTargetPlane.addWidget(QLabel("Dip angle"), 0, 2, 1, 1)

        self.spnTargetAttDipAng = QDoubleSpinBox()
        self.spnTargetAttDipAng.setMinimum(0.0)
        self.spnTargetAttDipAng.setMaximum(90.0)
        self.spnTargetAttDipAng.setDecimals(1)
        lytTargetPlane.addWidget(self.spnTargetAttDipAng, 0, 3, 1, 1)

        grpTargetPlane.setLayout(lytTargetPlane)
        layout.addWidget(grpTargetPlane)

        # output layer

        grpOutLayer = QGroupBox("Output point layer")
        lytOutLayer = QGridLayout()

        self.lnedtOutFilename = QLineEdit()
        lytOutLayer.addWidget(self.lnedtOutFilename, 0, 0, 1, 1)

        self.pshOutFilenameBrowse = QPushButton(".....")
        self.pshOutFilenameBrowse.clicked.connect(self.selectOutputVectorFile)
        lytOutLayer.addWidget(self.pshOutFilenameBrowse, 0, 1, 1, 1)

        grpOutLayer.setLayout(lytOutLayer)
        layout.addWidget(grpOutLayer)

        # ok/cancel choices

        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")

        btnOk.clicked.connect(self.accept)
        btnCancel.clicked.connect(self.reject)

        lytButtons = QHBoxLayout()
        lytButtons.addStretch()
        lytButtons.addWidget(btnOk)
        lytButtons.addWidget(btnCancel)

        layout.addLayout(lytButtons)

        self.setLayout(layout)

        self.setWindowTitle("Define point structural layer")

    def refresh_struct_point_lyr_combobox(self):

        self.pointLayers = loaded_point_layers()
        self.cmbInputLayers.clear()

        self.cmbInputLayers.addItem(tLayerChooseMsg)
        self.cmbInputLayers.addItems([layer.name() for layer in self.pointLayers])

        self.reset_structural_field_comboboxes()

    def reset_structural_field_comboboxes(self):

        for structural_combox in self.lStructuralComboxes:
            structural_combox.clear()
            structural_combox.addItem(tFieldUndefined)

    def refresh_structural_fields_comboboxes(self):

        self.reset_structural_field_comboboxes()

        point_shape_qgis_ndx = self.cmbInputLayers.currentIndex() - 1
        if point_shape_qgis_ndx == -1:
            return

        self.point_layer = self.pointLayers[point_shape_qgis_ndx]

        point_layer_field_list = self.point_layer.dataProvider().fields().toList()

        field_names = [field.name() for field in point_layer_field_list]

        for structural_combox in self.lStructuralComboxes:
            structural_combox.addItems(field_names)

    def selectOutputVectorFile(self):

        output_filename, __ = QFileDialog.getSaveFileName(self,
                                                      self.tr("Save shapefile"),
                                                      "*.shp",
                                                      "shp (*.shp *.SHP)")
        if not output_filename:
            return
        self.lnedtOutFilename.setText(output_filename)



