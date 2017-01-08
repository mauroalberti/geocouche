# -*- coding: utf-8 -*-


import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from qgis.core import QgsMapLayerRegistry
from geosurf.qgs_tools import loaded_point_layers, pt_geoms_attrs

from processing import plot_stereonet

       
class geocouche_QWidget( QWidget ):
    
    
    input_plane_azimuth_types = ["dip dir.", "strike rhr"]
    input_plane_dip_types = ["dip angle"]    

    input_line_azimuth_types = ["trend"]
    input_line_dip_types = ["plunge"] 
    
    
    def __init__( self, canvas, plugin_name ):

        super( geocouche_QWidget, self ).__init__() 
        self.mapcanvas = canvas        
        self.plugin_name = plugin_name

        self.point_layer = None
        self.structural_input_params = None

        self.setup_gui()

                      
    def setup_gui( self ): 

        self.dialog_layout = QHBoxLayout()
        
        self.dialog_layout.addWidget( self.setup_inputdata() )
        self.dialog_layout.addWidget( self.setup_processing() )        
                                                           
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
  
  
    def setup_processing(self):
        
        processing_QGroupBox = QGroupBox("Processing")
        
        layout = QGridLayout()

        self.plot_stereonet_QPushButton = QPushButton(self.tr("Plot stereonet"))          
        self.plot_stereonet_QPushButton.clicked.connect( self.process_geodata )         
        layout.addWidget(self.plot_stereonet_QPushButton, 0, 0, 1, 1 )

        processing_QGroupBox.setLayout(layout)
        
        return processing_QGroupBox
    

    def define_structural_input_params( self ):
        
        self.structural_input_params = None   

        if len( loaded_point_layers()  ) == 0:
            self.warn( "No available point layers" )
            return            

        dialog = SourcePointLayerDialog()

        if dialog.exec_():
            try:
                point_layer, structural_input_params = self.get_structural_input_params( dialog )
            except:
                self.warn( "Incorrect definition")
                return 
        else:
            self.warn( "Nothing defined")
            return

        if not self.formally_valid_params( structural_input_params ):
            self.warn( "Invalid/incomplete parameters")
            return
        else:
            self.info("Input data defined")
        
        self.point_layer = point_layer
        self.structural_input_params = structural_input_params


    def formally_valid_params(self, structural_input_params ):

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
        
        plane_azimuth_type = dialog.input_plane_orient_azimuth_type_QComboBox.currentText()
        plane_azimuth_name_field = self.parse_field_choice(dialog.input_plane_azimuth_srcfld_QComboBox.currentText(), field_undefined_txt)
            
        plane_dip_type = dialog.input_plane_orient_dip_type_QComboBox.currentText()        
        plane_dip_name_field = self.parse_field_choice(dialog.input_plane_dip_srcfld_QComboBox.currentText(), field_undefined_txt)       
                    
        line_azimuth_type = dialog.input_line_orient_azimuth_type_QComboBox.currentText()
        line_azimuth_name_field = self.parse_field_choice( dialog.input_line_azimuth_srcfld_QComboBox.currentText(), field_undefined_txt)
                    
        line_dip_type = dialog.input_line_orient_dip_type_QComboBox.currentText()        
        line_dip_name_field = self.parse_field_choice( dialog.input_line_dip_srcfld_QComboBox.currentText(), field_undefined_txt)
        
        return point_layer, dict(plane_azimuth_type = plane_azimuth_type,
                                plane_azimuth_name_field = plane_azimuth_name_field,
                                plane_dip_type = plane_dip_type,
                                plane_dip_name_field = plane_dip_name_field,
                                line_azimuth_type = line_azimuth_type,
                                line_azimuth_name_field = line_azimuth_name_field,
                                line_dip_type = line_dip_type,
                                line_dip_name_field = line_dip_name_field)
    

    def parse_field_choice(self, val, choose_message):
        
        if val == choose_message:
            return None
        else:
            return val


    def get_actual_field_names(self):
        
        actual_field_names = []
        
        usable_fields = [self.structural_input_params["plane_azimuth_name_field"],
                         self.structural_input_params["plane_dip_name_field"],
                         self.structural_input_params["line_azimuth_name_field"],
                         self.structural_input_params["line_dip_name_field"] ]
        
        for usable_fld in usable_fields:
            if usable_fld is not None:
                actual_field_names.append(usable_fld)

        return actual_field_names


    def get_actual_data_type(self):
        
        # define type for planar data
        if self.structural_input_params["plane_azimuth_name_field"] is not None and \
           self.structural_input_params["plane_dip_name_field"] is not None:            
            planar_data = True
            if self.structural_input_params["plane_azimuth_type"] ==  "dip dir.":
                planar_az_type = "dip_dir"
            elif self.structural_input_params["plane_azimuth_type"] ==  "strike rhr":
                planar_az_type = "strike_rhr"
            planar_dip_type = "dip"
        else:
            planar_data = False
            planar_az_type = None
            planar_dip_type = None
 
        # define type for linear data            
        if self.structural_input_params["line_azimuth_name_field"] is not None and \
           self.structural_input_params["line_dip_name_field"] is not None:            
            linear_data = True
            linear_az_type = "trend"
            linear_dip_type = "plunge"  
        else:
            linear_data = False
            linear_az_type = None
            linear_dip_type = None
                   
        
        return dict(planar_data = planar_data,
                    planar_az_type = planar_az_type,
                    planar_dip_type = planar_dip_type,
                    linear_data = linear_data,
                    linear_az_type = linear_az_type,
                    linear_dip_type = linear_dip_type)
        
        
    def process_geodata(self):

        # check definition of input point layer
        if self.point_layer is None or \
           self.structural_input_params is None:
            self.warn(str("Input point layer/parameters not defined"))
            return

        # get used field names in the point attribute table 
        self.actual_field_names = self.get_actual_field_names()
        
        # get input data presence and type
        self.actual_data_type = self.get_actual_data_type()

        structural_data = pt_geoms_attrs(self.point_layer, self.actual_field_names)
        
        input_data_types = self.get_actual_data_type()
           
        try:  
            _, plane_orientations, lineament_orientations = self.parse_geodata(input_data_types, structural_data)  
        except Exception, msg:
            self.warn(str(msg))
            return
        
        plot_stereonet(plane_orientations, lineament_orientations)
         

    def parse_geodata(self, input_data_types, structural_data):
        
        xy_vals = [(float(rec[0]), float(rec[1])) for rec in structural_data]
        
        try:
            if input_data_types["planar_data"]:            
                if input_data_types["planar_az_type"] == "dip_dir":
                    dipdir_vals = [ float(rec[2]) for rec in structural_data]
                elif input_data_types["planar_az_type"] == "strike_rhr":
                    dipdir_raw_vals = [ float(rec[2]) + 90.0 for rec in structural_data]
                    dipdir_vals = [ val if val < 360.0 else val - 360.0 for val in dipdir_raw_vals ]
                dipangle_vals = [ float(rec[3]) for rec in structural_data]
                plane_vals = zip(dipdir_vals, dipangle_vals)
                line_data_ndx_start = 4            
            else:
                plane_vals = None
                line_data_ndx_start = 2
        except:
            raise Exception, "Error in planar data"
             
        try:   
            if input_data_types["linear_data"]:
                line_vals = [ (float(rec[line_data_ndx_start]), float(rec[line_data_ndx_start + 1])) for rec in structural_data]
            else:
                line_vals = None     
        except:
            raise Exception, "Error in linear data"
                    
        return xy_vals, plane_vals, line_vals
    
                  
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

    
    
        


