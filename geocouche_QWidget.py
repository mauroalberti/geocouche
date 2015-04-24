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
        self.define_point_layer_QPushButton.clicked.connect( self.define_point_layer ) 
        layout.addWidget(self.define_point_layer_QPushButton )
        
        input_QGroupBox.setLayout(layout)
        
        return input_QGroupBox
                  

    def define_point_layer( self ):        

        current_point_layers = loaded_point_layers()   

        if len( current_point_layers ) == 0:
            self.warn( "No available point layers" )
            return            

        dialog = SourcePointLayerDialog( current_point_layers )

        if dialog.exec_():
            structural_input_params = self.get_structural_input_params( dialog )
        else:
            self.warn( "No defined point layer" )
            return


    def get_structural_input_params(self, dialog ):
        
        """
        selected_dems = []
        selected_dem_colors = [] 
        for dem_qgis_ndx in range( dialog.listDEMs_treeWidget.topLevelItemCount () ):
            curr_DEM_item = dialog.listDEMs_treeWidget.topLevelItem ( dem_qgis_ndx ) 
            if curr_DEM_item.checkState ( 0 ) == 2:
                selected_dems.append( dialog.singleband_raster_layers_in_project[ dem_qgis_ndx ] )
                selected_dem_colors.append( dialog.listDEMs_treeWidget.itemWidget( curr_DEM_item, 1 ).currentText() )  
         
        return selected_dems, selected_dem_colors
        """
    
        return None
    
  
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
    
    def __init__(self, current_point_layers, parent=None):
                
        super( SourcePointLayerDialog, self ).__init__(parent)
        
        self.choose_message = "choose"
        
        self.current_point_layers = current_point_layers
 
        layout = QGridLayout()
                        

        layout.addWidget(QLabel("Layer (point)"), 0,0,1,1)
        
        self.input_layers_QComboBox = QComboBox()
        layout.addWidget(self.input_layers_QComboBox, 0,1,1,1)   

        # plane values
                
        plane_QGroupBox = QGroupBox("Planar orientation")
        plane_QGridLayout = QGridLayout()    

        self.input_plane_orient_azimuth_type_QComboBox = QComboBox()
        self.input_plane_orient_azimuth_type_QComboBox.addItems(geocouche_QWidget.input_plane_azimuth_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_azimuth_type_QComboBox, 0,0,1,1)   
                
        self.input_plane_orient_azimuth_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_orient_azimuth_srcfld_QComboBox, 0,1,1,1)       
 
        self.input_plane_orient_dip_type_QComboBox = QComboBox()
        self.input_plane_orient_dip_type_QComboBox.addItems(geocouche_QWidget.input_plane_dip_types)
        plane_QGridLayout.addWidget(self.input_plane_orient_dip_type_QComboBox, 1,0,1,1) 
        
        self.input_plane_orient_dip_srcfld_QComboBox = QComboBox()
        plane_QGridLayout.addWidget(self.input_plane_orient_dip_srcfld_QComboBox, 1,1,1,1)         

        plane_QGroupBox.setLayout(plane_QGridLayout)              
        layout.addWidget(plane_QGroupBox, 1,0,2,2)
        

        # line values
        
        line_QGroupBox = QGroupBox("Line orientation")
        line_QGridLayout = QGridLayout() 
        
        self.input_line_orient_azimuth_type_QComboBox = QComboBox()
        self.input_line_orient_azimuth_type_QComboBox.addItems(geocouche_QWidget.input_line_azimuth_types)
        line_QGridLayout.addWidget(self.input_line_orient_azimuth_type_QComboBox, 0,0,1,1)   
                
        self.input_line_orient_azimuth_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_orient_azimuth_srcfld_QComboBox, 0,1,1,1)    
        
        self.input_line_orient_dip_type_QComboBox = QComboBox()
        self.input_line_orient_dip_type_QComboBox.addItems(geocouche_QWidget.input_line_dip_types)
        line_QGridLayout.addWidget(self.input_line_orient_dip_type_QComboBox, 1,0,1,1) 
        
        self.input_line_orient_dip_srcfld_QComboBox = QComboBox()
        line_QGridLayout.addWidget(self.input_line_orient_dip_srcfld_QComboBox, 1,1,1,1)         
 
        line_QGroupBox.setLayout(line_QGridLayout)              
        layout.addWidget(line_QGroupBox, 3,0,2,2)
         
 
        self.structural_comboxes = [self.input_plane_orient_azimuth_srcfld_QComboBox,
                                    self.input_plane_orient_dip_srcfld_QComboBox,
                                    self.input_line_orient_azimuth_srcfld_QComboBox,
                                    self.input_line_orient_dip_srcfld_QComboBox ]                
                
        self.refresh_struct_point_lyr_combobox()

                        
        # self.refresh_structural_fields_comboboxes( )
        
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
        
        # self.current_structural_point_layer = 
        self.pointLayers = loaded_point_layers()
        self.input_layers_QComboBox.clear()        
        
        self.input_layers_QComboBox.addItem( self.choose_message )
        self.input_layers_QComboBox.addItems( [ layer.name() for layer in self.pointLayers ] ) 
        
        self.reset_structural_field_comboboxes()
         
         
    def reset_structural_field_comboboxes(self):        
        
        for structural_combox in self.structural_comboxes:
            structural_combox.clear()
            structural_combox.addItem("---")
            
                     
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

    
    
        


