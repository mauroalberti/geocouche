

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import QgsColorButtonV2

from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs


ltInputPlaneAzimuthTypes = ["dip dir.", "strike rhr"]
ltInputPlaneDipTypes = ["dip angle"]

ltInputLineAzimuthTypes = ["trend"]
ltInputLineDipTypes = ["plunge"]

tLayerChooseMsg = "choose"
tFieldUndefined = "---"


class StereoplotInputDialog(QDialog):



    def __init__(self, llyrLoadedPointLayers, parent=None):

        super(StereoplotInputDialog, self).__init__(parent)
        self.llyrLoadedPointLayers = llyrLoadedPointLayers

        layout = QGridLayout()
        tabWdgt = QTabWidget()

        self.wdgtLayerInput = self.setup_layer_input_gui()
        self.layerTab = tabWdgt.addTab(self.wdgtLayerInput, "Layer")

        self.wdgtTextInput = self.setup_text_input_gui()
        self.textTab = tabWdgt.addTab(self.wdgtTextInput, "Text")

        layout.addWidget(tabWdgt, 0, 0, 1, 1)

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

        self.cmbInputLineOrientAzimType = QComboBox()
        self.cmbInputLineOrientAzimType.addItems(ltInputLineAzimuthTypes)
        lytAxisAttitudes.addWidget(self.cmbInputLineOrientAzimType, 0, 0, 1, 1)

        self.cmbInputLineAzimSrcFld = QComboBox()
        lytAxisAttitudes.addWidget(self.cmbInputLineAzimSrcFld, 0, 1, 1, 1)

        self.cmbInputLineOrientDipType = QComboBox()
        self.cmbInputLineOrientDipType.addItems(ltInputLineDipTypes)
        lytAxisAttitudes.addWidget(self.cmbInputLineOrientDipType, 1, 0, 1, 1)

        self.cmbInputLineDipSrcFld = QComboBox()
        lytAxisAttitudes.addWidget(self.cmbInputLineDipSrcFld, 1, 1, 1, 1)

        grpAxisAttitudes.setLayout(lytAxisAttitudes)
        lytLayerInput.addWidget(grpAxisAttitudes, 3, 0, 2, 2)

        self.lStructuralComboxes = [self.cmbInputPlaneAzimSrcFld,
                                    self.cmbInputPlaneDipSrcFld,
                                    self.cmbInputLineAzimSrcFld,
                                    self.cmbInputLineDipSrcFld]

        self.refresh_struct_point_lyr_combobox(self.llyrLoadedPointLayers)

        self.cmbInputLayers.currentIndexChanged[int].connect (self.refresh_structural_fields_comboboxes)

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

        lytInputValues.addWidget(QLabel("Type of azimuth"), 0, 0, 1, 1)
        self.cmbInputPlaneOrAzimType = QComboBox()
        self.cmbInputPlaneOrAzimType.addItems(ltInputPlaneAzimuthTypes)
        lytInputValues.addWidget(self.cmbInputPlaneOrAzimType, 0, 1, 1, 1)

        lytInputValues.addWidget(QLabel("Input is: azimuth, dip angle\ne.g.\n220,33\n145,59"), 1, 0, 1, 2)
        self.plntxtedInputValues = QPlainTextEdit()
        lytInputValues.addWidget(self.plntxtedInputValues, 2, 0, 5, 2)

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

    def __init__(self, parent=None):

        super(PlotStyleDialog, self).__init__(parent)

        self.tColorRGBA = '255,0,0,255'

        layout = QVBoxLayout()

        # great circle settings

        grpGreatCircles = QGroupBox("Great circles")
        lytGreatCircles = QHBoxLayout()

        # line color

        lytGreatCircles.addWidget(QLabel("Line color"))
        red, green, blue, alpha = map(int, self.tColorRGBA.split(","))
        self.btnLineColor = QgsColorButtonV2()
        self.btnLineColor.setColor(QColor(red, green, blue, alpha))
        lytGreatCircles.addWidget(self.btnLineColor)

        # line thickness

        lytGreatCircles.addWidget(QLabel("Line width"))
        lnLineThickness = [1, 2, 3, 4]
        self.cmbLineThickn = QComboBox()
        self.ltLineThicknVals = [str(val) + " pt(s)" for val in lnLineThickness]
        self.cmbLineThickn.insertItems(0, self.ltLineThicknVals)
        lytGreatCircles.addWidget(self.cmbLineThickn)

        # line transparency

        lytGreatCircles.addWidget(QLabel("Line transp."))
        lnLineTransparencies = [0, 25, 50, 75]
        self.cmbLineTransp = QComboBox()
        self.ltLineTranspPrcntVals = [str(val) + "%" for val in lnLineTransparencies]
        self.cmbLineTransp.insertItems(0, self.ltLineTranspPrcntVals)
        # self.transparency_QComboBox.currentIndexChanged['QString'].connect(self.update_color_transparency)
        lytGreatCircles.addWidget(self.cmbLineTransp)

        # set/add to layout

        grpGreatCircles.setLayout(lytGreatCircles)
        layout.addWidget(grpGreatCircles)

        # pole settings

        grpPoles = QGroupBox("Poles")
        lytPoles = QHBoxLayout()

        # pole color

        lytPoles.addWidget(QLabel("Point color"))
        red, green, blue, alpha = map(int, self.tColorRGBA.split(","))
        self.btnPointColor = QgsColorButtonV2()
        self.btnPointColor.setColor(QColor(red, green, blue, alpha))
        lytPoles.addWidget(self.btnPointColor)

        # point size

        lytPoles.addWidget(QLabel("Point size   "))
        lnPointSizes = [1, 2, 3, 4, 5]
        self.cmbPointSize = QComboBox()
        self.ltPointSizeVals = [str(val) + " pt(s)" for val in lnPointSizes]
        self.cmbPointSize.insertItems(0, self.ltPointSizeVals)
        lytPoles.addWidget(self.cmbPointSize)

        # point transparency

        lytPoles.addWidget(QLabel("Point transp."))
        lnPointTransparencies = [0, 25, 50, 75]
        self.cmbPointTransp = QComboBox()
        self.ltPointTranspPrcntVals = [str(val) + "%" for val in lnPointTransparencies]
        self.cmbPointTransp.insertItems(0, self.ltPointTranspPrcntVals)
        lytPoles.addWidget(self.cmbPointTransp)

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
        self.cmbStereonetFigure.addItems(["new stereoplot", "previous stereoplot"])
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


"""
class StereoplotSrcValuesDia(QDialog):

    def __init__(self, parent=None):
        super(StereoplotSrcValuesDia, self).__init__(parent)

        self.setup_text_input_gui()

    def setup_text_input_gui(self):

        self.layer_choose_msg = "choose"
        self.field_undefined_txt = "---"

        text_input_layout = QVBoxLayout()

        # input values

        values_QGroupBox = QGroupBox("Input values")
        values_QGridLayout = QGridLayout()

        values_QGridLayout.addWidget(QLabel("Type of azimuth"), 0, 0, 1, 1)
        self.input_plane_orient_azimuth_type_QComboBox = QComboBox()
        self.input_plane_orient_azimuth_type_QComboBox.addItems(input_plane_azimuth_types)
        values_QGridLayout.addWidget(self.input_plane_orient_azimuth_type_QComboBox, 0, 1, 1, 1)

        values_QGridLayout.addWidget(QLabel("Input is: azimuth, dip angle\ne.g.\n220,33\n145,59"), 1, 0, 1, 2)
        self.input_values_QPlainTextEdit = QPlainTextEdit()
        values_QGridLayout.addWidget(self.input_values_QPlainTextEdit, 2, 0, 5, 2)

        values_QGroupBox.setLayout(values_QGridLayout)
        text_input_layout.addWidget(values_QGroupBox)

        # ok/cancel choices

        okButton = QPushButton("&OK")
        cancelButton = QPushButton("Cancel")

        self.connect(okButton, SIGNAL("clicked()"),
                     self, SLOT("accept()"))

        self.connect(cancelButton, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        text_input_layout.addLayout(buttonLayout)

        self.setLayout(text_input_layout)

        self.setWindowTitle("Define plane attitude values")
"""

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



