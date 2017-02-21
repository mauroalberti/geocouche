

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import QgsColorButtonV2

from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs


input_plane_azimuth_types = ["dip dir.", "strike rhr"]
input_plane_dip_types = ["dip angle"]

input_line_azimuth_types = ["trend"]
input_line_dip_types = ["plunge"]

layer_choose_msg = "choose"
field_undefined_txt = "---"


class StereoplotInputDialog(QDialog):

    def __init__(self, parent=None):

        super(StereoplotInputDialog, self).__init__(parent)

        layout = QGridLayout()

        tabWidget = QTabWidget()

        self.layer_input_QW = self.setup_layer_input_gui()
        self.layer_tab = tabWidget.addTab(self.layer_input_QW, "Layer")

        self.text_input_QW = self.setup_text_input_gui()
        self.text_tab = tabWidget.addTab(self.text_input_QW, "Text")

        layout.addWidget(tabWidget, 0, 0, 1, 1)

        self.setLayout(layout)

        self.setWindowTitle("Stereoplot input")

    def setup_layer_input_gui(self):

        layer_input_widget = QWidget()
        layer_input_layout = QGridLayout()

        # input layer

        layer_QGroupBox = QGroupBox("Point layer storing geological measures")
        layer_QGridLayout = QGridLayout()

        self.input_layers_QComboBox = QComboBox()
        layer_QGridLayout.addWidget(self.input_layers_QComboBox, 0, 0, 1, 2)

        layer_QGroupBox.setLayout(layer_QGridLayout)
        layer_input_layout.addWidget(layer_QGroupBox, 0, 0, 1, 2)

        # plane values

        plane_QGroupBox = QGroupBox("Plane attitudes")
        plane_QGridLayout = QGridLayout()

        self.input_plane_orient_azimuth_type_QComboBox = QComboBox()
        self.input_plane_orient_azimuth_type_QComboBox.addItems(input_plane_azimuth_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_azimuth_type_QComboBox, 0, 0, 1, 1)

        self.input_plane_azimuth_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_azimuth_srcfld_QComboBox, 0, 1, 1, 1)

        self.input_plane_orient_dip_type_QComboBox = QComboBox()
        self.input_plane_orient_dip_type_QComboBox.addItems(input_plane_dip_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_dip_type_QComboBox, 1, 0, 1, 1)

        self.input_plane_dip_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_dip_srcfld_QComboBox, 1, 1, 1, 1)

        plane_QGroupBox.setLayout(plane_QGridLayout)
        layer_input_layout.addWidget(plane_QGroupBox, 1, 0, 2, 2)

        # line values

        line_QGroupBox = QGroupBox("Axis attitudes")
        line_QGridLayout = QGridLayout()

        self.input_line_orient_azimuth_type_QComboBox = QComboBox()
        self.input_line_orient_azimuth_type_QComboBox.addItems(input_line_azimuth_types)
        line_QGridLayout.addWidget(self.input_line_orient_azimuth_type_QComboBox, 0, 0, 1, 1)

        self.input_line_azimuth_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_azimuth_srcfld_QComboBox, 0, 1, 1, 1)

        self.input_line_orient_dip_type_QComboBox = QComboBox()
        self.input_line_orient_dip_type_QComboBox.addItems(input_line_dip_types)
        line_QGridLayout.addWidget(self.input_line_orient_dip_type_QComboBox, 1, 0, 1, 1)

        self.input_line_dip_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_dip_srcfld_QComboBox, 1, 1, 1, 1)

        line_QGroupBox.setLayout(line_QGridLayout)
        layer_input_layout.addWidget(line_QGroupBox, 3, 0, 2, 2)

        self.structural_comboxes = [self.input_plane_azimuth_srcfld_QComboBox,
                                    self.input_plane_dip_srcfld_QComboBox,
                                    self.input_line_azimuth_srcfld_QComboBox,
                                    self.input_line_dip_srcfld_QComboBox]

        self.refresh_struct_point_lyr_combobox()

        self.input_layers_QComboBox.currentIndexChanged[int].connect (self.refresh_structural_fields_comboboxes)

        okButton = QPushButton("&OK")
        cancelButton = QPushButton("Cancel")

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        layer_input_layout.addLayout(buttonLayout, 5, 0, 1, 2)

        layer_input_widget.setLayout(layer_input_layout)

        self.connect(okButton, SIGNAL("clicked()"),
                     self,  SLOT("accept()"))
        self.connect(cancelButton, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

        return layer_input_widget

    def setup_text_input_gui(self):

        text_input_widget = QWidget()

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

        text_input_widget.setLayout(text_input_layout)

        return text_input_widget

    def refresh_struct_point_lyr_combobox(self):

        self.pointLayers = loaded_point_layers()
        self.input_layers_QComboBox.clear()

        self.input_layers_QComboBox.addItem(layer_choose_msg)
        self.input_layers_QComboBox.addItems([layer.name() for layer in self.pointLayers])

        self.reset_structural_field_comboboxes()

    def reset_structural_field_comboboxes(self):

        for structural_combox in self.structural_comboxes:
            structural_combox.clear()
            structural_combox.addItem(field_undefined_txt)

    def refresh_structural_fields_comboboxes(self):

        self.reset_structural_field_comboboxes()

        point_shape_qgis_ndx = self.input_layers_QComboBox.currentIndex() - 1
        if point_shape_qgis_ndx == -1:
            return

        self.point_layer = self.pointLayers[point_shape_qgis_ndx]

        point_layer_field_list = self.point_layer.dataProvider().fields().toList()

        field_names = [field.name() for field in point_layer_field_list]

        for structural_combox in self.structural_comboxes:
            structural_combox.addItems(field_names)


class PlotStyleDialog(QDialog):

    def __init__(self, parent=None):

        super(PlotStyleDialog, self).__init__(parent)

        self.color_name = '255,0,0,255'

        layout = QVBoxLayout()

        # great circle settings

        greatcircles_QGroupBox = QGroupBox("Great circles")
        greatcircles_layout = QHBoxLayout()

        # line color

        greatcircles_layout.addWidget(QLabel("Line color"))
        red, green, blue, alpha = map(int, self.color_name.split(","))
        self.line_color_QgsColorButtonV2 = QgsColorButtonV2()
        self.line_color_QgsColorButtonV2.setColor(QColor(red, green, blue, alpha))
        greatcircles_layout.addWidget(self.line_color_QgsColorButtonV2)

        # line thickness

        greatcircles_layout.addWidget(QLabel("Line width"))
        line_thickness = [1, 2, 3, 4]
        self.line_thickn_QComboBox = QComboBox()
        self.line_thickn_vals = [str(val) + " pt(s)" for val in line_thickness]
        self.line_thickn_QComboBox.insertItems(0, self.line_thickn_vals)
        greatcircles_layout.addWidget(self.line_thickn_QComboBox)

        # line transparency

        greatcircles_layout.addWidget(QLabel("Line transp."))
        line_transparencies = [0, 25, 50, 75]
        self.line_transp_QComboBox = QComboBox()
        self.line_transp_percent_vals = [str(val) + "%" for val in line_transparencies]
        self.line_transp_QComboBox.insertItems(0, self.line_transp_percent_vals)
        # self.transparency_QComboBox.currentIndexChanged['QString'].connect(self.update_color_transparency)
        greatcircles_layout.addWidget(self.line_transp_QComboBox)

        # set/add to layout

        greatcircles_QGroupBox.setLayout(greatcircles_layout)
        layout.addWidget(greatcircles_QGroupBox)

        # pole settings

        poles_QGroupBox = QGroupBox("Poles")
        poles_layout = QHBoxLayout()

        # pole color

        poles_layout.addWidget(QLabel("Point color"))
        red, green, blue, alpha = map(int, self.color_name.split(","))
        self.point_color_QgsColorButtonV2 = QgsColorButtonV2()
        self.point_color_QgsColorButtonV2.setColor(QColor(red, green, blue, alpha))
        poles_layout.addWidget(self.point_color_QgsColorButtonV2)

        # point size

        poles_layout.addWidget(QLabel("Point size   "))
        point_sizes = [1, 2, 3, 4, 5]
        self.point_size_QComboBox = QComboBox()
        self.point_size_vals = [str(val) + " pt(s)" for val in point_sizes]
        self.point_size_QComboBox.insertItems(0, self.point_size_vals)
        poles_layout.addWidget(self.point_size_QComboBox)

        # point transparency

        poles_layout.addWidget(QLabel("Point transp."))
        point_transparencies = [0, 25, 50, 75]
        self.point_transp_QComboBox = QComboBox()
        self.point_transp_percent_vals = [str(val) + "%" for val in point_transparencies]
        self.point_transp_QComboBox.insertItems(0, self.point_transp_percent_vals)
        poles_layout.addWidget(self.point_transp_QComboBox)

        # set/add to layout

        poles_QGroupBox.setLayout(poles_layout)
        layout.addWidget(poles_QGroupBox)

        # ok/cancel stuff
        okButton = QPushButton("&OK")
        cancelButton = QPushButton("Cancel")

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout(buttonLayout)

        self.connect(okButton, SIGNAL("clicked()"),
                     self, SLOT("accept()"))
        self.connect(cancelButton, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

        self.setLayout(layout)

        self.setWindowTitle("Plot style")


class PlotStereonetDialog(QDialog):

    def __init__(self, parent=None):

        super(PlotStereonetDialog, self).__init__(parent)

        layout = QVBoxLayout()

        plot_QGroupBox = QGroupBox("")

        plot_layout = QGridLayout()

        plot_layout.addWidget(QLabel("Plot in"), 0, 0, 1, 2)

        self.stereonet_window_QComboBox = QComboBox()
        self.stereonet_window_QComboBox.addItems(["new stereoplot", "previous stereoplot"])
        plot_layout.addWidget(self.stereonet_window_QComboBox, 0, 2, 1, 1)

        self.planes_QCheckBox = QCheckBox("planes")
        self.planes_QCheckBox.setChecked(True)
        plot_layout.addWidget(self.planes_QCheckBox, 1, 0, 1, 1)

        plot_layout.addWidget(QLabel("as"), 1, 1, 1, 1)

        self.planes_type_QComboBox = QComboBox()
        self.planes_type_QComboBox.insertItems(0, ["great circles", "normal axes"])
        plot_layout.addWidget(self.planes_type_QComboBox, 1, 2, 1, 1)

        self.axes_QCheckBox = QCheckBox("axes")
        self.axes_QCheckBox.setChecked(False)
        plot_layout.addWidget(self.axes_QCheckBox, 2, 0, 1, 1)

        plot_layout.addWidget(QLabel("as"), 2, 1, 1, 1)

        self.axes_type_QComboBox = QComboBox()
        self.axes_type_QComboBox.insertItems(0, ["poles", "perpendicular planes"])
        plot_layout.addWidget(self.axes_type_QComboBox, 2, 2, 1, 1)

        plot_QGroupBox.setLayout(plot_layout)

        layout.addWidget(plot_QGroupBox)

        # ok/cancel stuff

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

        layout.addLayout(buttonLayout)

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

        layer_QGroupBox = QGroupBox("Input point layer")
        layer_QGridLayout = QGridLayout()

        self.input_layers_QComboBox = QComboBox()
        layer_QGridLayout.addWidget(self.input_layers_QComboBox, 0, 0, 1, 2)

        layer_QGroupBox.setLayout(layer_QGridLayout)
        layout.addWidget(layer_QGroupBox)

        # plane values

        plane_QGroupBox = QGroupBox("Planar orientation source fields")
        plane_QGridLayout = QGridLayout()

        self.input_plane_orient_azimuth_type_QComboBox = QComboBox()
        self.input_plane_orient_azimuth_type_QComboBox.addItems(input_plane_azimuth_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_azimuth_type_QComboBox, 0, 0, 1, 1)

        self.input_plane_azimuth_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_azimuth_srcfld_QComboBox, 0, 1, 1, 1)

        self.input_plane_orient_dip_type_QComboBox = QComboBox()
        self.input_plane_orient_dip_type_QComboBox.addItems(input_plane_dip_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_dip_type_QComboBox, 1, 0, 1, 1)

        self.input_plane_dip_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_dip_srcfld_QComboBox, 1, 1, 1, 1)

        self.structural_comboxes = [self.input_plane_azimuth_srcfld_QComboBox,
                                    self.input_plane_dip_srcfld_QComboBox]

        self.refresh_struct_point_lyr_combobox()

        self.input_layers_QComboBox.currentIndexChanged[int].connect(self.refresh_structural_fields_comboboxes)

        plane_QGroupBox.setLayout(plane_QGridLayout)
        layout.addWidget(plane_QGroupBox)

        # target attitude

        tplane_QGroupBox = QGroupBox("Target plane")
        tplane_QGridLayout = QGridLayout()

        tplane_QGridLayout.addWidget(QLabel("Dip dir."), 0, 0, 1, 1)

        self.targetatt_dipdir_QDSB = QDoubleSpinBox()
        self.targetatt_dipdir_QDSB.setMinimum(0.0)
        self.targetatt_dipdir_QDSB.setMaximum(359.9)
        self.targetatt_dipdir_QDSB.setDecimals(1)
        tplane_QGridLayout.addWidget(self.targetatt_dipdir_QDSB, 0, 1, 1, 1)

        tplane_QGridLayout.addWidget(QLabel("Dip angle"), 0, 2, 1, 1)

        self.targetatt_dipang_QDSBB = QDoubleSpinBox()
        self.targetatt_dipang_QDSBB.setMinimum(0.0)
        self.targetatt_dipang_QDSBB.setMaximum(90.0)
        self.targetatt_dipang_QDSBB.setDecimals(1)
        tplane_QGridLayout.addWidget(self.targetatt_dipang_QDSBB, 0, 3, 1, 1)

        tplane_QGroupBox.setLayout(tplane_QGridLayout)
        layout.addWidget(tplane_QGroupBox)

        # output layer

        outlayer_QGroupBox = QGroupBox("Output point layer")
        outlayer_QGridLayout = QGridLayout()

        self.out_filename_QLEdit = QLineEdit()
        outlayer_QGridLayout.addWidget(self.out_filename_QLEdit, 0, 0, 1, 1)

        self.out_filename_browse_QPushButton = QPushButton(".....")
        self.out_filename_browse_QPushButton.clicked.connect(self.selectOutputVectorFile)
        outlayer_QGridLayout.addWidget(self.out_filename_browse_QPushButton, 0, 1, 1, 1)

        outlayer_QGroupBox.setLayout(outlayer_QGridLayout)
        layout.addWidget(outlayer_QGroupBox)

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

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

        self.setWindowTitle("Define point structural layer")

    def refresh_struct_point_lyr_combobox(self):

        self.pointLayers = loaded_point_layers()
        self.input_layers_QComboBox.clear()

        self.input_layers_QComboBox.addItem(layer_choose_msg)
        self.input_layers_QComboBox.addItems([layer.name() for layer in self.pointLayers])

        self.reset_structural_field_comboboxes()

    def reset_structural_field_comboboxes(self):

        for structural_combox in self.structural_comboxes:
            structural_combox.clear()
            structural_combox.addItem(field_undefined_txt)

    def refresh_structural_fields_comboboxes(self):

        self.reset_structural_field_comboboxes()

        point_shape_qgis_ndx = self.input_layers_QComboBox.currentIndex() - 1
        if point_shape_qgis_ndx == -1:
            return

        self.point_layer = self.pointLayers[point_shape_qgis_ndx]

        point_layer_field_list = self.point_layer.dataProvider().fields().toList()

        field_names = [field.name() for field in point_layer_field_list]

        for structural_combox in self.structural_comboxes:
            structural_combox.addItems(field_names)

    def selectOutputVectorFile(self):

        output_filename = QFileDialog.getSaveFileName(self,
                                                      self.tr("Save shapefile"),
                                                      "*.shp",
                                                      "shp (*.shp *.SHP)")
        if not output_filename:
            return
        self.out_filename_QLEdit.setText(output_filename)



