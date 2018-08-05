"""
/***************************************************************************
 geocouche - plugin for Quantum GIS

 geologic stereoplots
-------------------

    Begin                : 2015.04.18
    Copyright            : (C) 2015-2018 by Mauro Alberti
    Email                : alberti dot m65 at gmail dot com
        
 ***************************************************************************/

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

from .geocouche import Geocouche


def classFactory(iface):

    return Geocouche(iface)



