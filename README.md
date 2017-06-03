# geocouche
geocouche is a GGIS plugin for processing geological meso-structures, based on the module apsg by Ondrej Lexa. 


Currently, it can:
 - plot data from layers or texts in stereonets
 - calculate the angles between planes stored in a layer and a reference plane

These two tools are available from the QGIS plugin interface.

![alt text](/help/ims/screenshot_01.png "geocouche interface")

*Fig. 1. geocouche interface.*


Geological stereonets
------------------------------------

It allows to produce stereonets depicting geological plane and axis attitudes (Fig. 2). There are three steps:

+ Choice of input data
+ Definition of plot style
+ Data plotting

![alt text](/help/ims/geocouche_bl_total.png "Stereonet interface")

*Fig. 2. Stereonet interface.*

**Choice of input data**

It is possible to use input data from data stored in a point layer (Layer tab, Fig. 3) or to use text input (Text tab, Fig. 4).


**Input from point layer**

When using a point layer (already loaded in the TOC), plane and/or axis attitudes are defined via the fields storing their values (Fig. 3). If there is a selection, onmly selected features will be used.

Depending if you want to plot planes, lines/axis of faults with slickenlines, you have to define accordingly the source fields for the various data type: for instance, for faults and slickenlines, you have to define plane dip direction and dip angle, and rake or (line trend, dip and movement sense).

Remember that rake information takes precedence over (shadows) line trend/dip and optional movement sense, even if you want just to plot data as planes and lines, not just as faults with slickenlines. 


![alt text](/help/ims/geocouche_bl_input_layer.png "Input from point layer interface")

*Fig. 3. Input from point layer interface.*

To plot faults, the movement sense or the fault rake must be also defined. Since the current (incorporated) version of apsg do not explicitly support pure transcurrent faults, pure left- or right-lateral movements are not treated, in the present plugin version.

The movement sense may assume two values: "N" for normal faults, and "R" for reverse faults.

The other option to define faults is by defining a field storing the rake values.
The rake should follow the Aki and Richards (1980) convention:

0° < rakes < 180° -> reverse movements

0° > rakes > -180° -> normal movements


When using rakes, slickenline trend and plunge does not need to be explicited.
Moreover, when defined, rake values take priority above any defined trend-plunge and movement sense values (if present). 


**Input from text**

The input can be inserted into a text window (Fig. 4), defining if data consist of:

+ planes
+ axes
+ planes and axes
+ fault planes with slickenline trend, plunge and movement sense values
+ fault planes with rake values

Another option to take care of for plane data, is whether orientations are expressed using dip direction or RHR strike.

![alt text](/help/ims/geocouche_bl_input_text.png "Input from text interface")

*Fig. 4. Input from text interface.*


**Plot style**

Styles can be defined for both great circles and poles: color, width/size, line/marker style, and transparency (Fig. 5).
Settings are stored in memory and are reused in subsequent sessions.

![alt text](/help/ims/geocouche_bl_plot_style.png "Plot style interface")

*Fig. 5. Plot style interface.*

**Stereonet plotting**

Plots can use a new or a pre-existing stereonet plot. Previous plots can be erased by using the button Clear stereonet (see Fig. 2).

Plane can be plotted as great circles or as plane normals, axes as poles or as normal great circles, faults with slickenlines as great circles with arrows or alternatvely as T-L diagrams (Fig. 6). 

![alt text](/help/ims/geocouche_bl_plot_choices.png "Stereonet plot interface")

*Fig. 6. Stereonet plot interface.*

An example of stereonet is shown in Fig. 7.

![alt text](/help/ims/stereonet_06.png "Stereonet example")

*Fig. 7. Stereonet example.*


Geological angles
------------------------------------

This tool allows to calculate the angles (as degrees) between a reference plane and the (eventually selected) features in a point layer (Fig. 8).

It can be applied to determine the degree of misalignement between a reference (for instance, regional) measure and local geological measures.

![alt text](/help/ims/angles_01.png "Geological angles calculation interface")

*Fig. 8. Geological angles calculation interface.*

The user has to define the two fields storing the azimuth (dip direction or RHR strike) and the dip angle of each feature, the attitude of the reference plane, and the name of the output shapefile with a new field storing the calculated angle (Fig. 9).


![alt text](/help/ims/angles_02.png "Definition of parameters for angle calculation")

*Fig. 9. Definition of parameters for angle calculation.*



