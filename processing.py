
from apsg import *



def plot_stereonet(plane_data, line_data):
    
    s = StereoNet()
             
    if plane_data is not None:
        for plane in plane_data:
            p = Fol(*plane)
            s.plane(p, linewidth=1.0, color='r')

    if line_data is not None:
        for line_rec in line_data:            
            l = Lin(*line_rec)
            s.line(l)
                   
    s.show() 