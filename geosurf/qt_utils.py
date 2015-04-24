
from __future__  import division


import os


from PyQt4.QtCore import QSettings, QFileInfo
from PyQt4.QtGui import QFileDialog


 
def lastUsedDir():
    # from module RASTERCALC by Barry Rowlingson   

    settings = QSettings()
    return settings.value( "/beePen/lastDir", "", type=str )


def setLastUsedDir(lastDir):
    # from module RASTERCALC by Barry Rowlingson
    
    path = QFileInfo( lastDir ).absolutePath()
    settings = QSettings()
    settings.setValue( "/beePen/lastDir", str(path) )
    
 
def new_file_path( parent, show_msg, dir_path, generic_name, filter_text ):
        
    output_filename = QFileDialog.getSaveFileName(parent, 
                                                  show_msg, 
                                                  dir_path + os.sep + generic_name,
                                                  filter_text )        
    if not output_filename: 
        return ''
    else:
        return output_filename 
    
    
def old_file_path( parent, show_msg, filter_extension, filter_text ):
        
    input_filename = QFileDialog.getOpenFileName( parent, 
                                                  parent.tr( show_msg ), 
                                                  filter_extension, 
                                                  filter_text )        
    if not input_filename: 
        return ''
    else:
        return input_filename   
    
        