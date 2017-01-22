
from apsg import *



def plot_new_stereonet(plane_data, line_data, color_name, transparency):
    
    stereoplot = StereoNet()
             
    if plane_data is not None:
        for plane in plane_data:
            p = Fol(*plane)
            stereoplot.plane(p, linewidth=1.0, color=color_name, alpha=transparency)

    if line_data is not None:
        for line_rec in line_data:            
            l = Lin(*line_rec)
            stereoplot.line(l)

    return stereoplot


def add_to_stereonet(stereoplot, plane_data, line_data, color_name, transparency):

    if plane_data is not None:
        for plane in plane_data:
            p = Fol(*plane)
            stereoplot.plane(p, linewidth=1.0, color=color_name, alpha=transparency)

    if line_data is not None:
        for line_rec in line_data:
            l = Lin(*line_rec)
            stereoplot.line(l)