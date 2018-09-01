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

from __future__ import absolute_import

from builtins import object
import os
import webbrowser

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from . import resources

from .qt_utils.utils import *

from .StereoplotWidget import StereoplotWidget
from .AnglesWidget import AnglesWidget
from .about_dialog import about_Dialog

_plugin_name_ = "geocouche"
_settings_name_ = "alberese"


class Geocouche(object):

    def __init__(self, interface):

        self.tPluginName = _plugin_name_
        self.tSettingsName = _settings_name_

        self.interface = interface
        self.main_window = self.interface.mainWindow()
        self.canvas = self.interface.mapCanvas()

        self.actions = []

    def initGui(self):

        self.actStereoplot = create_action(
            icon_path=':/plugins/geocouche/icons/stereoplot.png',
            text='Geologic stereonets',
            callback=self.open_stereoplot_widget,
            parent=self.interface.mainWindow())
        self.bStereoplotWidgetOpen = False
        self.interface.addPluginToMenu(
            self.tPluginName,
            self.actStereoplot)
        self.actions.append(self.actStereoplot)

        self.actAngles = create_action(
            icon_path=':/plugins/geocouche/icons/angle.svg',
            text='Geologic angles',
            callback=self.open_cal_angles_widget,
            parent=self.interface.mainWindow())
        self.bAnglesWidgetOpen = False
        self.interface.addPluginToMenu(
            self.tPluginName,
            self.actAngles)
        self.actions.append(self.actAngles)

        self.actAbout = create_action(
            icon_path=':/plugins/geocouche/icons/about.png',
            text='About',
            callback=self.run_about,
            parent=self.interface.mainWindow())
        self.interface.addPluginToMenu(
            self.tPluginName,
            self.actAbout)
        self.actions.append(self.actAbout)

    def open_stereoplot_widget(self):

        if self.bStereoplotWidgetOpen:
            self.warn("Geologic stereonets already open")
            return

        dwgtStereoplotDockWidget = QDockWidget(
            "{} - stereonet".format(self.tPluginName),
            self.interface.mainWindow())
        dwgtStereoplotDockWidget.setAttribute(Qt.WA_DeleteOnClose)
        dwgtStereoplotDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.wdgtStereoplot = StereoplotWidget(self.canvas, self.tPluginName, self.tSettingsName)
        dwgtStereoplotDockWidget.setWidget(self.wdgtStereoplot)
        dwgtStereoplotDockWidget.destroyed.connect(self.stereoplot_off)
        self.interface.addDockWidget(Qt.RightDockWidgetArea, dwgtStereoplotDockWidget)

        self.bStereoplotWidgetOpen = True

    def open_cal_angles_widget(self):

        if self.bAnglesWidgetOpen:
            self.warn("Geological Angles already open")
            return

        self.wdgtAngles = AnglesWidget(self.canvas, self.tPluginName)
        self.wdgtAngles.sgnWindowClosed.connect(self.angles_off)

        settings = QSettings(self.tSettingsName, self.tPluginName)
        if settings.contains("AnglesWidget/size") and settings.contains("AnglesWidget/position"):
            size = settings.value("AnglesWidget/size", None)
            pos = settings.value("AnglesWidget/position", None)
            self.wdgtAngles.resize(size)
            self.wdgtAngles.move(pos)
            self.wdgtAngles.show()
        else:
            self.wdgtAngles.show()

        self.bAnglesWidgetOpen = True

    def run_about(self):

        about_dlg = about_Dialog()
        about_dlg.show()
        about_dlg.exec_()

    def stereoplot_off(self):

        self.bStereoplotWidgetOpen = False

    def angles_off(self):

        self.bAnglesWidgetOpen = False

    def info(self, msg):
        
        QMessageBox.information(self.interface.mainWindow(), self.tPluginName, msg)

    def warn(self, msg):
    
        QMessageBox.warning(self.interface.mainWindow(), self.tPluginName, msg)

    def unload(self):

        self.interface.removePluginMenu(self.tPluginName, self.actStereoplot)
        self.interface.removePluginMenu(self.tPluginName, self.actAngles)
        self.interface.removePluginMenu(self.tPluginName, self.actAbout)


