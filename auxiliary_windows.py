
from collections import OrderedDict
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import QgsColorButtonV2

from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs

ltInputDataTypes = ("planes", "axes", "planes & axes")
ltInputPlaneAzimuthTypes = ["dip direction", "strike rhr"]
ltInputPlaneDipTypes = ["dip angle"]
ltInputAxisAzimuthTypes = ["trend"]
ltInputAxisDipTypes = ["plunge"]

tLayerChooseMsg = "choose"
tFieldUndefined = "---"

ltLineStyles = ["solid", "dashed", "dashdot", "dotted"]
ltMarkerStyles = OrderedDict([("circle", "o"), ("square", "s"), ("diamond", "D"), ("triangle", "^")])


class StereoplotInputDialog(QDialog):

    def __init__(self, llyrLoadedPointLayers, parent=None):

        super(StereoplotInputDialog, self).__init__(parent)
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
        lytLayerInput = QGridLayout()

        # input layer

        grpLayer = QGroupBox("Point layer storing geological measures")
        lytLayer = QGridLayout()

        self.cmbInputLayers = QComboBox()
        lytLayer.addWidget(self.cmbInputLayers, 0, 0, 1, 2)

        grpLayer.setLayout(lytLayer)
        lytLayerInput.addWidget(grpLayer, 0, 0, 1, 2)

        # plane values

        grpPlane = QGroupBox("Plane attitudes")
        lytPlane = QGridLayout()

        self.cmbInputPlaneOrAzimType = QComboBox()
        self.cmbInputPlaneOrAzimType.addItems(ltInputPlaneAzimuthTypes)
        lytPlane.addWidget(self.cmbInputPlaneOrAzimType, 0, 0, 1, 1)

        self.cmbInputPlaneAzimSrcFld = QComboBox()
        lytPlane.addWidget(self.cmbInputPlaneAzimSrcFld, 0, 1, 1, 1)

        self.cmbInputPlaneOrientDipType = QComboBox()
        self.cmbInputPlaneOrientDipType.addItems(ltInputPlaneDipTypes)
        lytPlane.addWidget(self.cmbInputPlaneOrientDipType, 1, 0, 1, 1)

        self.cmbInputPlaneDipSrcFld = QComboBox()
        lytPlane.addWidget(self.cmbInputPlaneDipSrcFld, 1, 1, 1, 1)

        grpPlane.setLayout(lytPlane)
        lytLayerInput.addWidget(grpPlane, 1, 0, 2, 2)

        # line values

        grpAxisAttitudes = QGroupBox("Axis attitudes")
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

        grpAxisAttitudes.setLayout(lytAxisAttitudes)
        lytLayerInput.addWidget(grpAxisAttitudes, 3, 0, 2, 2)

        self.lStructuralComboxes = [self.cmbInputPlaneAzimSrcFld,
                                    self.cmbInputPlaneDipSrcFld,
                                    self.cmbInputAxisAzimSrcFld,
                                    self.cmbInputAxisDipSrcFld]

        self.refresh_struct_point_lyr_combobox(self.llyrLoadedPointLayers)

        self.cmbInputLayers.currentIndexChanged[int].connect(self.refresh_structural_fields_comboboxes)

        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")

        lytButtons = QHBoxLayout()
        lytButtons.addStretch()
        lytButtons.addWidget(btnOk)
        lytButtons.addWidget(btnCancel)

        lytLayerInput.addLayout(lytButtons, 5, 0, 1, 2)

        wdgtLayerInput.setLayout(lytLayerInput)

        self.connect(btnOk, SIGNAL("clicked()"),
                     self,  SLOT("accept()"))
        self.connect(btnCancel, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

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

        lytInputValues.addWidget(QLabel("Plane azimuth is"), 1, 0, 1, 1)
        self.cmbInputPlaneOrAzimType = QComboBox()
        self.cmbInputPlaneOrAzimType.addItems(ltInputPlaneAzimuthTypes)
        lytInputValues.addWidget(self.cmbInputPlaneOrAzimType, 1, 1, 1, 1)

        lytInputValues.addWidget(QLabel("Input example for planes and axes: \n220,33,131,1\n145,59,57,9"), 2, 0, 1, 2)
        self.plntxtedInputValues = QPlainTextEdit()
        lytInputValues.addWidget(self.plntxtedInputValues, 3, 0, 5, 2)

        grpInputValues.setLayout(lytInputValues)
        lytTextInput.addWidget(grpInputValues)

        # ok/cancel choices

        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")

        self.connect(btnOk, SIGNAL("clicked()"),
                     self, SLOT("accept()"))

        self.connect(btnCancel, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

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


class PlotStyleDialog(QDialog):

    def __init__(self, dPlotStyles, parent=None):

        super(PlotStyleDialog, self).__init__(parent)

        self.dPlotStyles = dPlotStyles

        settings = QSettings("alberese", "geocouche")

        layout = QVBoxLayout()

        # great circle settings

        grpGreatCircles = QGroupBox("Great circles")
        lytGreatCircles = QGridLayout()

        # line color

        lytGreatCircles.addWidget(QLabel("Line color"), 0, 0, 1, 1)
        self.btnLineColor = QgsColorButtonV2()
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
        self.btnPointColor = QgsColorButtonV2()
        point_color = self.dPlotStyles["marker_color"]
        self.btnPointColor.setColor(QColor(point_color))
        lytPoles.addWidget(self.btnPointColor, 0, 1, 1, 1)

        # marker style

        lytPoles.addWidget(QLabel("Marker style"), 0, 2, 1, 1)
        self.cmbPointStyle = QComboBox()
        self.cmbPointStyle.insertItems(0, ltMarkerStyles.keys())
        point_style = self.dPlotStyles["marker_style"]
        point_style_ndx = ltMarkerStyles.keys().index(point_style) if point_style in ltMarkerStyles.keys() else 0
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

        self.connect(btnOk, SIGNAL("clicked()"),
                     self, SLOT("accept()"))
        self.connect(btnCancel, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

        self.setLayout(layout)

        self.setWindowTitle("Plot style")


class PlotStereonetDialog(QDialog):

    def __init__(self, parent=None):

        super(PlotStereonetDialog, self).__init__(parent)

        layout = QVBoxLayout()

        grpPlot = QGroupBox("")

        lytPlot = QGridLayout()

        lytPlot.addWidget(QLabel("Plot in"), 0, 0, 1, 2)

        # stereoplot, new or previous

        self.cmbStereonetFigure = QComboBox()
        self.cmbStereonetFigure.addItems(["new stereonet", "previous stereonet"])
        lytPlot.addWidget(self.cmbStereonetFigure, 0, 2, 1, 1)

        # planes

        self.chkPlanes = QCheckBox("planes")
        self.chkPlanes.setChecked(True)
        lytPlot.addWidget(self.chkPlanes, 1, 0, 1, 1)
        lytPlot.addWidget(QLabel("as"), 1, 1, 1, 1)
        self.cmbPlanesType = QComboBox()
        self.cmbPlanesType.insertItems(0, ["great circles", "normal axes"])
        lytPlot.addWidget(self.cmbPlanesType, 1, 2, 1, 1)

        # axes

        self.chkAxes = QCheckBox("axes")
        self.chkAxes.setChecked(False)
        lytPlot.addWidget(self.chkAxes, 2, 0, 1, 1)
        lytPlot.addWidget(QLabel("as"), 2, 1, 1, 1)
        self.cmbAxesType = QComboBox()
        self.cmbAxesType.insertItems(0, ["poles", "perpendicular planes"])
        lytPlot.addWidget(self.cmbAxesType, 2, 2, 1, 1)

        grpPlot.setLayout(lytPlot)
        layout.addWidget(grpPlot)

        # ok/cancel stuff

        btnOk = QPushButton("&OK")
        btnCancel = QPushButton("Cancel")
        self.connect(btnOk, SIGNAL("clicked()"),
                     self, SLOT("accept()"))
        self.connect(btnCancel, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

        lytButtons = QHBoxLayout()
        lytButtons.addStretch()
        lytButtons.addWidget(btnOk)
        lytButtons.addWidget(btnCancel)

        layout.addLayout(lytButtons)

        # final settings

        self.setLayout(layout)

        self.setWindowTitle("Stereonet plot")

class AnglesSrcPtLyrDia(QDialog):

    def __init__(self, parent=None):

        super(AnglesSrcPtLyrDia, self).__init__(parent)

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

        self.connect(btnOk, SIGNAL("clicked()"),
                     self, SLOT("accept()"))
        self.connect(btnCancel, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

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

        output_filename = QFileDialog.getSaveFileName(self,
                                                      self.tr("Save shapefile"),
                                                      "*.shp",
                                                      "shp (*.shp *.SHP)")
        if not output_filename:
            return
        self.lnedtOutFilename.setText(output_filename)



