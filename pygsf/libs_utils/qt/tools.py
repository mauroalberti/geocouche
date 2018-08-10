# -*- coding: utf-8 -*-


from typing import List, Tuple

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QComboBox, QMessageBox


def info(parent, header, msg):
    """
    Displays an information window.

    :param parent:
    :param header:
    :param msg:
    :return:
    """
    
    QMessageBox.information(parent, header, msg)


def warn(parent, header, msg):
    """
    Displays a warning window.

    :param parent:
    :param header:
    :param msg:
    :return:
    """

    QMessageBox.warning(parent, header, msg)


def error(parent, header, msg):
    """
    Displays an error window.

    :param parent:
    :param header:
    :param msg:
    :return:
    """

    QMessageBox.error(parent, header, msg)
    
    
def update_ComboBox(combobox: QComboBox, init_text: str, texts: List[str]):
    """
    Updates a combo box content using a list of strings.

    :param combobox: the combobox to be updated
    :param init_text: the initial updated combo box element
    :param texts: the list of the texts used to fill the combo box
    :return:
    """

    combobox.clear()

    if len(texts) == 0:
        return

    if init_text:
        combobox.addItem(init_text)

    combobox.addItems(texts)


def qcolor2rgbmpl(qcolor: QColor) -> Tuple[float, float, float]:
    """
    Calculates the red, green and blue components of the given QColor instance.

    :param qcolor: the input QColor instance
    :type qcolor: QColor
    :return: the triplet of the three RGB color values
    :type: a tuple of three floats
    """

    red = qcolor.red() / 255.0
    green = qcolor.green() / 255.0
    blue = qcolor.blue() / 255.0

    return red, green, blue

