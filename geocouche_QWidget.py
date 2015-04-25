# -*- coding: utf-8 -*-


import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import QgsMapLayerRegistry
from geosurf.qgs_tools import loaded_point_layers

       
class geocouche_QWidget( QWidget ):
    
    input_plane_azimuth_types = ["dip dir.", "strike rhr"]
    input_plane_dip_types = ["dip angle"]    

    input_line_azimuth_types = ["trend"]
    input_line_dip_types = ["plunge"] 
    
    
    def __init__( self, canvas, plugin_name ):

        super( geocouche_QWidget, self ).__init__() 
        self.mapcanvas = canvas        
        self.plugin_name = plugin_name           
        self.setup_gui()

                      
    def setup_gui( self ): 

        self.dialog_layout = QVBoxLayout()
        
        self.dialog_layout.addWidget( self.setup_inputdata() )
                                                           
        self.setLayout(self.dialog_layout)            
        self.adjustSize()               
        self.setWindowTitle(self.plugin_name)        
  

    def setup_inputdata(self):
        
        input_QGroupBox = QGroupBox("Input")
        
        layout = QVBoxLayout() 
        
        self.define_point_layer_QPushButton = QPushButton(self.tr("Define point layer"))  
        self.define_point_layer_QPushButton.clicked.connect( self.define_structural_input_params ) 
        layout.addWidget(self.define_point_layer_QPushButton )
        
        input_QGroupBox.setLayout(layout)
        
        return input_QGroupBox
                  

    def define_structural_input_params( self ):
        
        self.structural_input_params = None   

        if len( loaded_point_layers()  ) == 0:
            self.warn( "No available point layers" )
            return            

        dialog = SourcePointLayerDialog()

        if dialog.exec_():
            try:
                structural_input_params = self.get_structural_input_params( dialog )
            except:
                self.warn( "Incorrect definition")
                return 
        else:
            self.warn( "Nothing defined")
            return

        if not self.formally_valid_params( structural_input_params ):
            self.warn( "Invalid parameters")
            return
        else:
            self.info("Input data defined")
        
        self.structural_input_params = structural_input_params


    def formally_valid_params(self, structural_input_params ):
        
        print structural_input_params["plane_azimuth_name_field"]
        print structural_input_params["plane_dip_name_field"]
        print structural_input_params["line_azimuth_name_field"]
        print structural_input_params["line_dip_name_field"]

        
        if structural_input_params["plane_azimuth_name_field"] is not None and \
           structural_input_params["plane_dip_name_field"] is not None:
            return True
        
        if structural_input_params["line_azimuth_name_field"] is not None and \
           structural_input_params["line_dip_name_field"] is not None:
            return True
        
        return False


    def get_structural_input_params(self, dialog ):
        
        point_layer = dialog.point_layer
        
        field_undefined_txt = dialog.field_undefined_txt
        
        plane_azimuth_type_field = dialog.input_plane_orient_azimuth_type_QComboBox.currentText()
        plane_azimuth_name_field = self.parse_field_choice(dialog.input_plane_azimuth_srcfld_QComboBox.currentText(), field_undefined_txt)
            
        plane_dip_type_field = dialog.input_plane_orient_dip_type_QComboBox.currentText()        
        plane_dip_name_field = self.parse_field_choice(dialog.input_plane_dip_srcfld_QComboBox.currentText(), field_undefined_txt)       
                    
        line_azimuth_type_field = dialog.input_line_orient_azimuth_type_QComboBox.currentText()
        line_azimuth_name_field = self.parse_field_choice( dialog.input_line_azimuth_srcfld_QComboBox.currentText(), field_undefined_txt)
                    
        line_dip_type_field = dialog.input_line_orient_dip_type_QComboBox.currentText()        
        line_dip_name_field = self.parse_field_choice( dialog.input_line_dip_srcfld_QComboBox.currentText(), field_undefined_txt)
        
        return dict(point_layer = point_layer,
                    plane_azimuth_type_field = plane_azimuth_type_field,
                    plane_azimuth_name_field = plane_azimuth_name_field,
                    plane_dip_type_field = plane_dip_type_field,
                    plane_dip_name_field = plane_dip_name_field,
                    line_azimuth_type_field = line_azimuth_type_field,
                    line_azimuth_name_field = line_azimuth_name_field,
                    line_dip_type_field = line_dip_type_field,
                    line_dip_name_field = line_dip_name_field)
    

    def parse_field_choice(self, val, choose_message):
        
        if val == choose_message:
            return None
        else:
            return val
        
         
    def open_help_page(self):
        
        import webbrowser
        local_url = os.path.dirname(os.path.realpath(__file__)) + os.sep + "help" + os.sep + "help.html"
        local_url = local_url.replace("\\","/")
        if not webbrowser.open(local_url):
            self.warn("Error with browser.\nOpen manually help/help.html")

        
    def info(self, msg):
        
        QMessageBox.information( self,  self.plugin_name, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self,  self.plugin_name, msg )
        
        
        
class SourcePointLayerDialog( QDialog ):
    
    
    def __init__(self, parent=None):
                
        super( SourcePointLayerDialog, self ).__init__(parent)
        
        self.setup_gui()
        
        
    def setup_gui(self):        
        
        self.layer_choose_msg = "choose"
        self.field_undefined_txt = "---"
 
        layout = QGridLayout()
                        
        # input layer
        
        layer_QGroupBox = QGroupBox("Input point layer")
        layer_QGridLayout = QGridLayout() 
        
        self.input_layers_QComboBox = QComboBox()
        layer_QGridLayout.addWidget(self.input_layers_QComboBox, 0,0,1,2) 
        
        layer_QGroupBox.setLayout(layer_QGridLayout)              
        layout.addWidget(layer_QGroupBox, 0,0,1,2)          

        # plane values
                
        plane_QGroupBox = QGroupBox("Planar orientation source fields")
        plane_QGridLayout = QGridLayout()    

        self.input_plane_orient_azimuth_type_QComboBox = QComboBox()
        self.input_plane_orient_azimuth_type_QComboBox.addItems(geocouche_QWidget.input_plane_azimuth_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_azimuth_type_QComboBox, 0,0,1,1)   
                
        self.input_plane_azimuth_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_azimuth_srcfld_QComboBox, 0,1,1,1)       
 
        self.input_plane_orient_dip_type_QComboBox = QComboBox()
        self.input_plane_orient_dip_type_QComboBox.addItems(geocouche_QWidget.input_plane_dip_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_dip_type_QComboBox, 1,0,1,1) 
        
        self.input_plane_dip_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_dip_srcfld_QComboBox, 1,1,1,1)         

        plane_QGroupBox.setLayout(plane_QGridLayout)              
        layout.addWidget(plane_QGroupBox, 1,0,2,2)
        

        # line values
        
        line_QGroupBox = QGroupBox("Line orientation source fields")
        line_QGridLayout = QGridLayout() 
        
        self.input_line_orient_azimuth_type_QComboBox = QComboBox()
        self.input_line_orient_azimuth_type_QComboBox.addItems(geocouche_QWidget.input_line_azimuth_types)
        line_QGridLayout.addWidget(self.input_line_orient_azimuth_type_QComboBox, 0,0,1,1)   
                
        self.input_line_azimuth_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_azimuth_srcfld_QComboBox, 0,1,1,1)    
        
        self.input_line_orient_dip_type_QComboBox = QComboBox()
        self.input_line_orient_dip_type_QComboBox.addItems(geocouche_QWidget.input_line_dip_types)
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

    
    
        


