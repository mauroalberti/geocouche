# geoStereo
#
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------




from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from geocouche_QWidget import geocouche_QWidget
import resources



class geocouche_gui( object ):
    

    def __init__(self, interface):

        self.interface = interface
        self.main_window = self.interface.mainWindow()
        self.canvas = self.interface.mapCanvas()        

        self.plugin_name = "geocouche"
        

    def initGui(self):
        
        self.geocouche_QAction = QAction(QIcon(":/plugins/geocouche/icon.png"), "geocouche", self.interface.mainWindow())
        self.geocouche_QAction.setWhatsThis( "Geologic stereoplots" ) 
        self.geocouche_QAction.triggered.connect( self.open_geocouche_widget )
        self.interface.addPluginToMenu("geocouche", self.geocouche_QAction)
        self.interface.addToolBarIcon(self.geocouche_QAction)

        self.is_geocouche_widget_open = False
                
        
    def open_geocouche_widget(self):
        
        if self.is_geocouche_widget_open:
            self.warn("geocouche is already open")
            return

        geocouche_DockWidget = QDockWidget( 'geocouche', self.interface.mainWindow() )        
        geocouche_DockWidget.setAttribute(Qt.WA_DeleteOnClose)
        geocouche_DockWidget.setAllowedAreas( Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea )        
        self.geocouche_QWidget = geocouche_QWidget( self.canvas, self.plugin_name )        
        geocouche_DockWidget.setWidget( self.geocouche_QWidget )
        geocouche_DockWidget.destroyed.connect( self.closeEvent )        
        self.interface.addDockWidget( Qt.BottomDockWidgetArea, geocouche_DockWidget )
                
        self.is_geocouche_widget_open = True
        

    def closeEvent(self):
        
        self.is_geocouche_widget_open = False
        
                          

    def info(self, msg):
        
        QMessageBox.information( self.interface.mainWindow(),  self.plugin_name, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self.interface.mainWindow(),  self.plugin_name, msg )
        
                               
    def unload(self):

        self.interface.removeToolBarIcon(self.geocouche_QAction)        
        self.interface.removePluginMenu( "geocouche", self.geocouche_QAction )
     
        
               

