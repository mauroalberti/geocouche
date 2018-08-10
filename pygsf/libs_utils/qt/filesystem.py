# -*- coding: utf-8 -*-


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


def lastUsedDir(module_nm):
    """
    Gets the last used directory for the given module.
    Modified from module RASTERCALC by Barry Rowlingson.

    :param module_nm: the current module name
    :type module_nm: string
    :return: the name of the last used directory
    :rtype: string
    """

    settings = QSettings()
    return settings.value(
        "/{}/lastDir".format(module_nm),
        "",
        type=str)


def setLastUsedDir(module_nm, lastDir):
    """
    Stores in the module QSettings the path of the last used directory.
    Modified from module RASTERCALC by Barry Rowlingson.

    :param module_nm: the current module name
    :type module_nm: string
    :param lastDir: the last used directory
    :type lastDir: string

    :return: None
    """

    path = QFileInfo(lastDir).absolutePath()
    settings = QSettings()
    settings.setValue(
        "/{}/lastDir".format(module_nm),
        str(path))


def update_directory_key(settings: QSettings, settings_dir_key, fileName):
    """
    Updates the value of a QSetting key with the path of a file.
    Modified from module RASTERCALC by Barry Rowlingson.

    :param settings:
    :param settings_dir_key:
    :param fileName:
    :return:
    """

    path = QFileInfo(fileName).absolutePath()
    settings.setValue(settings_dir_key,
                      str(path))


def new_file_path(parent, show_msg, path, filter_text):
    """
    Defines the path of a new file.

    :param parent:
    :param show_msg:
    :param path:
    :param filter_text:
    :return:
    """

    output_filename = QFileDialog.getSaveFileName(parent,
                                                  show_msg,
                                                  path,
                                                  filter_text)
    if not output_filename:
        return ''
    else:
        return output_filename


def old_file_path(parent, show_msg, filter_extension, filter_text):
    """
    Defines the path of a pre-existing file.

    :param parent:
    :param show_msg:
    :param filter_extension:
    :param filter_text:
    :return:
    """

    input_filename = QFileDialog.getOpenFileName(parent,
                                                 parent.tr(show_msg),
                                                 filter_extension,
                                                 filter_text)
    if not input_filename:
        return ''
    else:
        return input_filename

