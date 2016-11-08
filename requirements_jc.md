# Requirements Analysis Document
## PySAL-QGIS Integration
## Joseph Cruz

### 1. Introduction
  1. Purpose
    * PySAL-QGIS Integration intends to allow the integration of certain portions of the PySAL library within the GIS system, QGIS.
    * This project focuses on the addition of the Spatial Dynamics: Markov based methods to the PySAL-QGIS integration toolkit.
  2. Scope
    
    Users of the software QGIS.
  3. Objectives and success metrics 
    * PySAL and QGIS can be considered successfully integrated when the Markov based methods can be accessed and utilized within QGIS with readable and meaningful results.
      * With successfully read data within QGIS, this data can be analyzed by PySAL's Markov based methods.
      * Additional data columns are added to the existing data within QGIS that will depict the result of one of the Markov based methods.
      * A map is produced that accurately reflects the results calculated above.
    * The interface that allows a QGIS user to use the Markov based methods within PySAL allows the user to use the three forms of Markov based analysis located within the library. i.e. Classic Markov, Spatial Markov, and LISA Markov
  4. Definitions, terms
  
    GUI := Graphical User Interface
  5. References
    * "Discover QGIS." Discover QGIS. QGIS, n.d. Web. 25 Oct. 2016. [QGIS](http://www.qgis.org/en/site/about/index.html)
    * PySAL Developers. "PySAL." PySAL — Python Spatial Analysis Library. PySAL Developers, 2014. Web. 25 Oct. 2016. [PySAL](http://pysal.readthedocs.io/en/latest/index.html)
    * Graser, Anita. "Anitagraser/QGIS-Processing-tools." GitHub. GitHub, 23 Apr. 2015. Web. 07 Nov. 2016. [PySAL-QGIS Integration](https://github.com/anitagraser/QGIS-Processing-tools/wiki/PySAL-Integration)
  6. Overview
  
  This project focuses on combining the strengths of PySAL and QGIS using the PySAL-QGIS Integration library. Inherently, PySAL is a library of spatial analytics methods, developed in Python, of which QGIS lacks in some areas. QGIS, on the other hand, has a ready to use GUI. For example, QGIS lacks the ability to analyze data using any form of Markov chaining, however, PySAL contains methods to do just that. PySAL, as of this moment, lacks the ability to display its own maps whereas QGIS can. By combining the functionality of the two, a user will be able to analyze a geospatial problem and draw a map without having to use QGIS and PySAL or some other set of libraries separately, as PySAL analysis will be handled within the QGIS environment.
  
### 2. Current System
  1. Description of existing project
  
  PySAL is an open source library of spatial analysis functions written in Python intended to support the development of high level applications. PySAL is open source under the BSD License. [PySAL](http://pysal.readthedocs.io/en/latest/index.html)
  
  QGIS is a user friendly Open Source Geographic Information System (GIS) licensed under the GNU General Public License. [QGIS](http://www.qgis.org/en/site/about/index.html)
  
  PySAL - QGIS integration is a developing project that intends to mesh the functionalities of PySAL's analytics with QGIS' ability to display maps. "We are currently writing scripts which add PySAL functionality to (QGIS) Processing." [QGIS-PySAL Integration](https://github.com/anitagraser/QGIS-Processing-tools/wiki/PySAL-Integration)
  2. How does the project extend existing work
  
  The project extends the functionality inherent within PySAL onto the QGIS platform. This allows for functions not found within QGIS, but found within PySAL, to be used in QGIS' GUI. This further extends the work done in PySAL-QGIS integration by adding additional libraries from PySAL, in this case, the spatial dynamics Markov based methods.
  3. What tasks does the new system support
  
  The interoperability between PySAL and QGIS will result in the Markov based methods, based in PySAL, to be usable as analytic methods on data within QGIS. QGIS will display the results of these analyses.

  
### 3. System Proposal
####Overview

This system will provide the necessary integration between PySAL and QGIS with the addition of PySAL's Markov based methods. These methods will be usable within QGIS in the manner that QGIS will read data and PySAL will perform the Markov based analytics and return a result to the QGIS GUI.

2. Functional Requirements
  1. Features to be implemented
    * The modules will be done in Python 2.7 since QGIS does not support Python 3.
    * PySAL-QGIS integration is a module that will be modifiable.
      * The actual code will be well-commented.
    * Markov based methods within PySAL's spatial dynamics library will be given the ability to interact with QGIS.
    * A toolkit for QGIS will be developed:
      * The input layer will be selectable from the current layers loaded within the QGIS project
      * The desired field to be used in the Markov based methods will be selectable from the layer's database
      * A drop down menu in the QGIS toolkit will list the three forms of Markov based methods (Classic Markov, Spatial Markov, and LISA Markov) will be included.
        * From this drop down menu, only one method will be selectable at a time.
        * (If individual tools is preferred then three individual tools will be constructed instead of one with a drop down menu.)
      * If the Markov based method is either Spatial Markov or LISA Markov, the contiguity will need to be specified. Rook will be considered the defualt. The spatial weights matrix based on contiguity will be calculated.
      * An output file containing the results of the Markov based method analysis can be created, otherwise, a temporary file is instead created.
      * A new output layer is displayed on the current QGIS project GUI reflecting the results of the selected Markov based method.
  2. Mock-ups (sketches) of features
3. Nonfunctional Requirements
  1. Useability:
    PySAL-QGIS interoperability will be available only on Linux and Mac OS. These methods are readily usable granted the user can install the PySAL-QGIS Intgration library properly and add it to their QGIS processing toolkit. After this initial hump, the tool will be easy to use.
  2. Reliability:
    Considering the number of operations required for spatial and LISA Markov methods, issues may arise when file sizes become large.
  3. Performance:
    Considering the number of operations required for spatial and LISA Markov methods, issues may arise when file sizes become large. This entails the calculation of spatial weights matrices for all polygons within the system which requires a considerable amount of memory and may result in slowing the system.
  4. Supportability:
    The software will be readily editable and readable given a new developer understands how PySAL interfaces with QGIS.
  5. Implementation:
    Both modules will be built utilizing Python 2.7
  6. Interface:
    PySAL-QGIS Integration will be handled with QGIS' toolkit handling software. The GUI is displayed on QGIS and is handled by the interfacing elements within PySAL-QGIS Integration.
  7. Packaging:
    PySAL-QGIS Integration will be a stand-alone package. It will need to be manually added to QGIS for the time being.
  8. Licensing:
    BSD
            
### 4. Project Management
1. Schedule
  1. November 11: Choose proper way to show the results of the Markov based methods
  2. November 18: Have the Classic Markov method working. This includes calculating the statistics along with producing a new layer in QGIS.
  3. November 23: Have the Spatial and LISA Markov methods working. This includes calculating the statistics, accounting for both rook and queen contiguity, and producing a new layer in QGIS.
  4. November 26: Complete testing. Ensure all functional requirements are fulfilled.
  5. November 28: Begin making presentation.
  6. December 6 : Presentation
2. Repository
  1. URL: [https://github.com/joemCruz/processing_pysal/tree/test]
