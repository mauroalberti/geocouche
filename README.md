# geocouche
a Python plugin for QGis, for plotting and analyzing structural geological measures.

Pre-release version

State
 - only projection of planes is implemented;
 - [2017-01-14] implementation of angle calculation between geological planes - as an aid in testing tool of geoSurfDEM project.
 - [2017-01-22] implemented plot of planes via numeric input; creating a new stereoplot or adding to an existing one; choosing color and transparency for plane plots.
 - [2017-02-11] modifying the interface to accomodate vertical dockwidget with single choice buttons and created branch "new_interfaces"
 - [2017-02-12] implemented memory of last position for two main windows; stereoplot window has functions to be reimplemented, currently they do not work 
 - [2017-02-18] implemented plot type definition
 - [2017-02-19] implemented plot style definition
 - [2017-02-21] implemented stereoplot window definition
 - [2017-02-25] naming convention changed
 - [2017-02-28] restored plot of planes from point layer using user-defined style 
 - [2107-03-05] restored data input from text tab
 - [2017-03-10] implemented plot using chosen line and marker styles
 - [2017-03-11] implemented storage of plot settings
 - [2017-03-12] implemented great circle <-> pole plot switch - STILL TO BE TESTED
 - [2017-03-18] changed plot style management and removed a few minor bugs - help still to be created and pre-release testings to be performed
 - [2017-03-19] created help - to be tested as RC 0.0.2a and merging into Master
 - [2017-03-19] removed bug in angle calculation tool; RC 0.0.2b
 - [2017-03-20] removed bugs in plotting from RHR strike-based inputs; merged new_interface branch into master; RC 0.0.2c
