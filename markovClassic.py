#markovClassic.py

import pysal 
import numpy as np
import processing 
from processing.tools.vector import VectorWriter
from qgis.core import *
from PyQt4.QtCore import *
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import *
from processing.core.outputs import *
from processing.tools import dataobjects
from PyQt4 import QtGui
from qgis.utils import iface

class MarkovClassic(GeoAlgorithm):

    INPUT = 'INPUT'
    FIELD_START = 'FIELD_START'
    FIELD_END = 'FIELD_END'
    FIELD_JUMPS = 'FIELD_JUMPS'
    TRANSITIONS = 'TRANSITIONS'
    ANALYSIS_T = 'ANALYSIS_T'
    MAP_OUTPUT = 'MAP_OUTPUT'
    
    def defineCharacteristics(self):
        self.name = "Classic Markov"
        self.group = 'Spatial Dynamics'

        ##input=vector
        ##field=field input
        ##contiguity=selection queen;rook
        ##i=output number 

        self.addParameter(ParameterVector(self.INPUT,
            self.tr('Input Layer'), [ParameterVector.VECTOR_TYPE_POLYGON]))
        self.addParameter(ParameterSelection(self.ANALYSIS_T,
            self.tr('Analysis Type'), ['End Point', 'Majority Moves']))
        # Beginning and end field parameters to read
        self.addParameter(ParameterTableField(self.FIELD_START,
            self.tr('Starting Field'), self.INPUT))
        self.addParameter(ParameterTableField(self.FIELD_END,
            self.tr('Ending Field'), self.INPUT))
        self.addParameter(ParameterSelection(self.FIELD_JUMPS,
            self.tr('Fields to Jump'), ['1','2','3','4','5']))

        #Outputs
        self.addOutput(OutputNumber(self.TRANSITIONS, self.tr('transitions')))
        self.addOutput(OutputVector(self.MAP_OUTPUT, self.tr('Markov Result')))
        
    def processAlgorithm(self, progress):
        field_s = self.getParameterValue(self.FIELD_START)
        field_s = field_s[0:10] # try to handle Shapefile field length limit
        field_e = self.getParameterValue(self.FIELD_END)
        field_e = field_e[0:10]
        
        filename = self.getParameterValue(self.INPUT)
        layer = dataobjects.getObjectFromUri(filename)
        filename = dataobjects.exportVectorLayer(layer)
        provider = layer.dataProvider()
        fields = provider.fields()
        # Can append new data to the fields variable. This will
        # be used later to enter newly calculated data into the
        # given, appended field. Using fields.append(...) i.e:

        # Adds the field MARKOV_RES to the end of the list of fields.
        # This field will be used to add a new layer to the QGIS canvas.
        fields.append(QgsField('MARKOV_RES', QVariant.Int))
        field_names = [field.name() for field in fields]
        
        # Retrieve the index values for the fields
        # Use these as the starting and stopping points
        start_index = field_names.index(field_s)
        end_index = field_names.index(field_e)
        print ("Field Range: {0} : {1}".format(field_names[start_index], field_names[end_index]))
        print (self.getParameterValue(self.FIELD_JUMPS))
        jumps = int(self.getParameterValue(self.FIELD_JUMPS)) + 1
        print ("Fields Read:")
        for i in range(start_index, end_index+1, jumps):
            print (field_names[i])

        analysis_type = self.getParameterValue(self.ANALYSIS_T)

        # Setting up the data for Markov chaining using quintiles
        f = pysal.open(filename.replace('.shp','.dbf'))
        header = f.header
        start_index = header.index(field_s)
        end_index = header.index(field_e)
        variables = [header[i] for i in range(start_index, end_index+1, jumps)]
        pci = np.array([f.by_col[v] for v in variables])
        q5 = np.array([pysal.Quantiles(y).yb for y in pci]).transpose()
        pci = pci.astype(float)
        #print pci.shape
        #print q5.shape


        # Performing the Markov chain analysis
        m = pysal.Markov(q5)
        print ("INFO: Classic Markov")
        print ("INFO: Transitions:\n {0}".format(m.transitions))
        print ("INFO: Steady State Matrix:\n {0}".format(m.steady_state))
        print ("INFO: P-Matrix:\n {0}".format(m.p))

#----------------------------------------------------------------------
# Analysis Types

        # Endpoint data
        # Takes the first value of a geometry and the last value then
        # finds the difference between the two.
        analysis_result = []
        if analysis_type == 0:
            print ("Analysis Type: Endpoints")
            for q in q5:
                #print (q)
                dif = q[-1] - q[0]
                if dif > 0:
                    analysis_result.append(2)
                elif dif < 0:
                    analysis_result.append(0)
                else: # dif == 0
                    analysis_result.append(1)
        # Majority Moves
        # Finds the number of up, down or stationary moves of a geo-
        # metry and shows the majority number of types of moves it
        # makes.
        elif analysis_type == 1:
            print ("Analysis Type: Majority Moves")
            for q in q5:
                up = 0
                stay = 0
                down = 0
                for j in range(len(q)-1):
                    move = q[j+1] - q[j]
                    if move > 0: #upwards moves
                        up += 1
                    elif move == 0: #stationary moves
                        stay += 1
                    elif move < 0: #downards moves
                        down += 1

                if max(up, stay, down) == up:
                    analysis_result.append(2)
                if max(up, stay, down) == stay:
                    analysis_result.append(1)
                if max(up, stay, down) == down:
                    analysis_result.append(0)
                    
#--------------------------------------------------------------------- 
# Handling Map Output
        # Taken directly from Local Moran's I: moranlocal.py with some
        # changes to fit the Markov module.
        writer = self.getOutputFromName(self.MAP_OUTPUT).getVectorWriter(
            fields, provider.geometryType(), layer.crs() )
        outFeat = QgsFeature()
        i = 0
        for inFeat in processing.features(layer):
            inGeom = inFeat.geometry()
            outFeat.setGeometry(inGeom)
            attrs = inFeat.attributes()
            # This requires the field to be added above and for the
            # new field to be empty. This is additonally appending
            # the analysis result calculate above.
            attrs.append(int(analysis_result[i]))
            outFeat.setAttributes(attrs)
            writer.addFeature(outFeat)
            i+=1

        del writer

        out_layer = dataobjects.getObjectFromUri(self.getOutputValue(
         self.MAP_OUTPUT))


        # Classes defined for map output
        # End Point:
        #  Decreasing: The region's final quantile value is lower than its
        #              initial value.
        #  Stationary: The region's final quintile value is the same as
        #              its initial value.
        #  Increasing: The region's final quantile value is greater than
        #              its initial value.
        # Majority Moves:
        #  Decreasing: The region has a majority of downward moves.
        #  Stationary: The region remains stationary for a majority of "moves"
        #  Increasing: The region has a majority of upward moves.
        classes = [0,1,2]
        labels = ["Decreasing", "Stationary", "Increasing"]
        #          Brown         White         Blue
        colors = ["#D8B365"   , "#F5F5F5"   , "#5AB4AC"]

        quads = {}
        for i in classes:
            quads[i] = (colors[i], labels[i])

        categories = []
        for quad, (color, label) in quads.items():
            symbol = QgsSymbolV2.defaultSymbol(out_layer.geometryType())
            symbol.setColor(QtGui.QColor(color))
            category = QgsRendererCategoryV2(quad, symbol, label)
            categories.append(category)

        # 'expression' is the name of the field that will used
        # to generate the map.
        # Line 70 above.
        expression = "MARKOV_RES"
        renderer = QgsCategorizedSymbolRendererV2(expression,
                                                  categories)
        out_layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(out_layer)
        iface.mapCanvas().refresh()
        iface.legendInterface().refreshLayerSymbology(out_layer)
        iface.mapCanvas().refresh()



