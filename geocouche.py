"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import webbrowser

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import resources

from .StereoplotWidget import StereoplotWidget
from .AnglesWidget import AnglesWidget


class Geocouche(object):

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
                self.tPluginName,
                action)

        if object_name is not None:
            action.setObjectName(object_name)

        self.actions.append(action)

        return action

    def __init__(self, interface):

        self.tPluginName = "geocouche"
        self.interface = interface
        self.main_window = self.interface.mainWindow()
        self.canvas = self.interface.mapCanvas()

        self.actions = []

    def initGui(self):

        self.actStereoplot = self.add_action(
            ':/plugins/geocouche/icons/stereoplot.png',
            text='Geologic stereonets',
            callback=self.open_stereoplot_widget,
            parent=self.interface.mainWindow())
        self.bStereoplotWidgetOpen = False

        self.actAngles = self.add_action(
            ':/plugins/geocouche/icons/angle.svg',
            text='Geologic angles',
            callback=self.open_cal_angles_widget,
            parent=self.interface.mainWindow())
        self.bAnglesWidgetOpen = False

        self.actHelp = self.add_action(
            ':/plugins/geocouche/icons/help.ico',
            text='Help',
            callback=self.open_html_help,
            parent=self.interface.mainWindow())

    def open_stereoplot_widget(self):
        
        if self.bStereoplotWidgetOpen:
            self.warn("Geologic stereonets already open")
            return

        dwgtStereoplotDockWidget = QDockWidget(self.tPluginName, self.interface.mainWindow())
        dwgtStereoplotDockWidget.setAttribute(Qt.WA_DeleteOnClose)
        dwgtStereoplotDockWidget.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)

        self.wdgtStereoplot = StereoplotWidget(self.canvas, self.tPluginName)
        dwgtStereoplotDockWidget.setWidget(self.wdgtStereoplot)
        dwgtStereoplotDockWidget.destroyed.connect(self.stereoplot_off)
        self.interface.addDockWidget(Qt.BottomDockWidgetArea, dwgtStereoplotDockWidget)

        #self.wdgtStereoplot.window_closed.connect(self.stereoplot_off)
        """
        settings = QSettings("alberese", "geocouche")
        if settings.contains("StereoplotWidget/size") and settings.contains("StereoplotWidget/position"):
            size = settings.value("StereoplotWidget/size", None)
            pos = settings.value("StereoplotWidget/position", None)
            self.wdgtStereoplot.resize(size)
            self.wdgtStereoplot.move(pos)
            self.wdgtStereoplot.show()
        else:
            self.wdgtStereoplot.show()
        """


        self.bStereoplotWidgetOpen = True

    def open_cal_angles_widget(self):

        if self.bAnglesWidgetOpen:
            self.warn("Geological Angles already open")
            return

        self.wdgtAngles = AnglesWidget(self.canvas, self.tPluginName)
        self.wdgtAngles.sgnWindowClosed.connect(self.angles_off)

        settings = QSettings("alberese", "geocouche")
        if settings.contains("AnglesWidget/size") and settings.contains("AnglesWidget/position"):
            size = settings.value("AnglesWidget/size", None)
            pos = settings.value("AnglesWidget/position", None)
            self.wdgtAngles.resize(size)
            self.wdgtAngles.move(pos)
            self.wdgtAngles.show()
        else:
            self.wdgtAngles.show()

        self.bAnglesWidgetOpen = True

    def open_html_help(self):

        webbrowser.open('{}/help/geocouche.html'.format(os.path.dirname(__file__)), new=True)

    def stereoplot_off(self):

        self.bStereoplotWidgetOpen = False

    def angles_off(self):

        self.bAnglesWidgetOpen = False

    def info(self, msg):
        
        QMessageBox.information(self.interface.mainWindow(), self.tPluginName, msg)

    def warn(self, msg):
    
        QMessageBox.warning(self.interface.mainWindow(), self.tPluginName, msg)

    def unload(self):

        self.interface.removePluginMenu("geocouche", self.actStereoplot)
