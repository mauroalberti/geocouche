# geocouche
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

#from qgis.core import *

from geocouche_QWidget import geocouche_QWidget
import resources



class geocouche_gui( object ):

    # from RedLayers by E. Ferreguti

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=False,
            status_tip=None,
            whats_this=None,
            parent=None,
            object_name=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :param object_name: Optional name to identify objects during customization
        :type object_name: str

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        if callback:
            action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.interface.addPluginToMenu(
                self.plugin_name,
                action)

        if object_name is not None:
            action.setObjectName(object_name)

        self.actions.append(action)

        return action


    def __init__(self, interface):

        self.plugin_name = "geocouche"
        self.interface = interface
        self.main_window = self.interface.mainWindow()
        self.canvas = self.interface.mapCanvas()

        self.actions = []
        

    def initGui(self):

        self.stereoplot_QAction = self.add_action(
            ':/plugins/geocouche/icons/stereoplot.png',
            text = u'Geologic stereoplots',
            callback=self.open_stereoplot_widget,
            parent=self.interface.mainWindow())
        self.is_stereoplot_widget_open = False

        self.angles_QAction = self.add_action(
            ':/plugins/geocouche/icons/angle.svg',
            text=u'Geologic angles',
            callback=self.open_cal_angles_widget,
            parent=self.interface.mainWindow())
        self.is_anglecalc_widget_open = False


    def open_stereoplot_widget(self):
        
        if self.is_stereoplot_widget_open:
            self.warn("Geologic stereoplots already open")
            return

        geocouche_DockWidget = QDockWidget('Stereoplot', self.interface.mainWindow() )
        geocouche_DockWidget.setAttribute(Qt.WA_DeleteOnClose)
        geocouche_DockWidget.setAllowedAreas( Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea )        
        self.geocouche_QWidget = geocouche_QWidget( self.canvas, self.plugin_name )        
        geocouche_DockWidget.setWidget( self.geocouche_QWidget )
        geocouche_DockWidget.destroyed.connect( self.closeEvent )        
        self.interface.addDockWidget( Qt.BottomDockWidgetArea, geocouche_DockWidget )
                
        self.is_stereoplot_widget_open = True


    def open_cal_angles_widget(self):

        if self.is_anglecalc_widget_open:
            self.warn("Geological Angles already open")
            return

        self.info("To implement")

        # TO IMPLEMENT

        self.is_anglecalc_widget_open = True


    def closeEvent(self):
        
        self.is_stereoplot_widget_open = False
        self.is_anglecalc_widget_open = False
                          

    def info(self, msg):
        
        QMessageBox.information( self.interface.mainWindow(),  self.plugin_name, msg )
        
        
    def warn( self, msg):
    
        QMessageBox.warning( self.interface.mainWindow(),  self.plugin_name, msg )
        
                               
    def unload(self):

        #self.interface.removeToolBarIcon(self.stereoplot_QAction)
        self.interface.removePluginMenu( "geocouche", self.stereoplot_QAction)
     
        
               

