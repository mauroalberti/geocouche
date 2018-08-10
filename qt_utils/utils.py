
from __future__ import division

from builtins import str

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *


def lastUsedDir(plugin_lastDir_QSettStr):
    """
    modified from module RASTERCALC by Barry Rowlingson

    Args:
        plugin_lastDir_QSettStr: string, e.g. "/qProf/lastDir"

    Returns:
        last plugin directory
    """

    settings = QSettings()
    return settings.value(plugin_lastDir_QSettStr, "", type=str)


def setLastUsedDir(plugin_lastDir_QSettStr, lastDir):
    """
    modified from module RASTERCALC by Barry Rowlingson
    """

    path = QFileInfo(lastDir).absolutePath()
    settings = QSettings()
    settings.setValue(plugin_lastDir_QSettStr, str(path))


def new_file_path(parent, show_msg, path, filter_text):

    output_filename, __ = QFileDialog.getSaveFileName(parent,
                                                  show_msg,
                                                  path,
                                                  filter_text)
    if not output_filename:
        return ''
    else:
        return output_filename


def old_file_path(parent, show_msg, filter_extension, filter_text):

    input_filename, __ = QFileDialog.getOpenFileName(parent,
                                                 parent.tr(show_msg),
                                                 filter_extension,
                                                 filter_text)
    if not input_filename:
        return ''
    else:
        return input_filename


# from RedLayers by E. Ferreguti
def create_action(
        icon_path,
        text,
        callback,
        enabled_flag=True,
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

    if object_name is not None:
        action.setObjectName(object_name)

    return action

