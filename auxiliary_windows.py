

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs


input_plane_azimuth_types = ["dip dir.", "strike rhr"]
input_plane_dip_types = ["dip angle"]

input_line_azimuth_types = ["trend"]
input_line_dip_types = ["plunge"]






class StereoplotSrcPtLyrDia(QDialog):


    def __init__(self, parent=None):

        super(StereoplotSrcPtLyrDia, self).__init__(parent)

        self.setup_gui()


    def setup_gui(self):

        self.layer_choose_msg = "choose"
        self.field_undefined_txt = "---"

        layout = QGridLayout()

        # input layer

        layer_QGroupBox = QGroupBox("Input point layer")
        layer_QGridLayout = QGridLayout()

        self.input_layers_QComboBox = QComboBox()
        layer_QGridLayout.addWidget(self.input_layers_QComboBox, 0, 0, 1, 2)

        layer_QGroupBox.setLayout(layer_QGridLayout)
        layout.addWidget(layer_QGroupBox, 0, 0, 1, 2)

        # plane values

        plane_QGroupBox = QGroupBox("Planar orientation source fields")
        plane_QGridLayout = QGridLayout()

        self.input_plane_orient_azimuth_type_QComboBox = QComboBox()
        self.input_plane_orient_azimuth_type_QComboBox.addItems(input_plane_azimuth_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_azimuth_type_QComboBox, 0,0,1,1)

        self.input_plane_azimuth_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_azimuth_srcfld_QComboBox, 0,1,1,1)

        self.input_plane_orient_dip_type_QComboBox = QComboBox()
        self.input_plane_orient_dip_type_QComboBox.addItems(input_plane_dip_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_dip_type_QComboBox, 1,0,1,1)

        self.input_plane_dip_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_dip_srcfld_QComboBox, 1,1,1,1)

        plane_QGroupBox.setLayout(plane_QGridLayout)
        layout.addWidget(plane_QGroupBox, 1,0,2,2)


        # line values

        line_QGroupBox = QGroupBox("Line orientation source fields")
        line_QGridLayout = QGridLayout()

        self.input_line_orient_azimuth_type_QComboBox = QComboBox()
        self.input_line_orient_azimuth_type_QComboBox.addItems(input_line_azimuth_types)
        line_QGridLayout.addWidget(self.input_line_orient_azimuth_type_QComboBox, 0,0,1,1)

        self.input_line_azimuth_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_azimuth_srcfld_QComboBox, 0,1,1,1)

        self.input_line_orient_dip_type_QComboBox = QComboBox()
        self.input_line_orient_dip_type_QComboBox.addItems(input_line_dip_types)
        line_QGridLayout.addWidget(self.input_line_orient_dip_type_QComboBox, 1,0,1,1)

        self.input_line_dip_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_dip_srcfld_QComboBox, 1,1,1,1)

        line_QGroupBox.setLayout(line_QGridLayout)
        layout.addWidget(line_QGroupBox, 3,0,2,2)


        self.structural_comboxes = [self.input_plane_azimuth_srcfld_QComboBox,
                                    self.input_plane_dip_srcfld_QComboBox,
                                    self.input_line_azimuth_srcfld_QComboBox,
                                    self.input_line_dip_srcfld_QComboBox ]

        self.refresh_struct_point_lyr_combobox()

        self.input_layers_QComboBox.currentIndexChanged[int].connect (self.refresh_structural_fields_comboboxes )

        okButton = QPushButton("&OK")
        cancelButton = QPushButton("Cancel")

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout( buttonLayout, 5, 0, 1, 2 )

        self.setLayout( layout )

        self.connect(okButton, SIGNAL("clicked()"),
                     self,  SLOT("accept()") )
        self.connect(cancelButton, SIGNAL("clicked()"),
                     self, SLOT("reject()"))

        self.setWindowTitle("Define point structural layer")



    def refresh_struct_point_lyr_combobox(self):

        self.pointLayers = loaded_point_layers()
        self.input_layers_QComboBox.clear()

        self.input_layers_QComboBox.addItem( self.layer_choose_msg )
        self.input_layers_QComboBox.addItems( [ layer.name() for layer in self.pointLayers ] )

        self.reset_structural_field_comboboxes()


    def reset_structural_field_comboboxes(self):

        for structural_combox in self.structural_comboxes:
            structural_combox.clear()
            structural_combox.addItem(self.field_undefined_txt)


    def refresh_structural_fields_comboboxes( self ):

        self.reset_structural_field_comboboxes()

        point_shape_qgis_ndx = self.input_layers_QComboBox.currentIndex() - 1
        if point_shape_qgis_ndx == -1:
            return

        self.point_layer = self.pointLayers[ point_shape_qgis_ndx ]

        point_layer_field_list = self.point_layer.dataProvider().fields().toList( )

        field_names = [field.name() for field in point_layer_field_list]

        for structural_combox in self.structural_comboxes:
            structural_combox.addItems(field_names)


class AnglesSrcPtLyrDia(QDialog):

    def __init__(self, parent=None):

        super(AnglesSrcPtLyrDia, self).__init__(parent)

        self.setup_gui()

    def setup_gui(self):

        self.layer_choose_msg = "choose"
        self.field_undefined_txt = "---"

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
        self.targetatt_dipang_QDSBB.setMaximum(89.9)
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

        self.input_layers_QComboBox.addItem(self.layer_choose_msg)
        self.input_layers_QComboBox.addItems([layer.name() for layer in self.pointLayers])

        self.reset_structural_field_comboboxes()

    def reset_structural_field_comboboxes(self):

        for structural_combox in self.structural_comboxes:
            structural_combox.clear()
            structural_combox.addItem(self.field_undefined_txt)

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



