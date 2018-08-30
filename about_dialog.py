# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *

    
class about_Dialog(QDialog):

    def __init__(self):

        super(about_Dialog, self).__init__() 
                            
        self.setup_gui()
        
    def setup_gui(self):

        dialog_layout = QVBoxLayout()
        
        htmlText = """
        <h3>geocouche - release 2.0.1</h3>
        Created by M. Alberti (alberti.m65@gmail.com).
        <br /><br /><a href="https://github.com/mauroalberti/geocouche">https://github.com/mauroalberti/geocouche</a>
        <br /><br />Stereonet plotting and processing of geological structures.  
        <br /><br />Licensed under the terms of GNU GPL 3.
        """ 
               
        aboutQTextBrowser = QTextBrowser(self)
        aboutQTextBrowser.insertHtml(htmlText)
        aboutQTextBrowser.setMinimumSize(400, 200)
        dialog_layout.addWidget(aboutQTextBrowser)

        self.setLayout(dialog_layout)

        self.setWindowTitle('geocouche about')


