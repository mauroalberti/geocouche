"""
/***************************************************************************
 geoStereoplot - plugin for Quantum GIS

 geologic stereoplots
                              -------------------
        begin                : 2015.04.18

        
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


from geocouche_gui import geocouche_gui


def classFactory(iface):    
    # create qgSurf_gui class   
    return geocouche_gui(iface)



