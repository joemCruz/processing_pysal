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

class Markov(GeoAlgorithm):

    INPUT = 'INPUT'
    FIELD_START = 'FIELD_START'
    FIELD_END = 'FIELD_END'
    FIELD_JUMPS = 'FIELD_JUMPS'
    CONTIGUITY = 'CONTIGUITY'
    MARKOV_T = 'MARKOV_T'
    TRANSITIONS = 'TRANSITIONS'
    MAP_OUTPUT = 'MAP_OUTPUT'

    def defineCharacteristics(self):
        self.name = "Markov"
        self.group = 'Spatial Dynamics'

        ##input=vector
        ##field=field input
        ##contiguity=selection queen;rook
        ##i=output number 

        self.addParameter(ParameterVector(self.INPUT,
            self.tr('Input Layer'), [ParameterVector.VECTOR_TYPE_POLYGON]))
        #Added Markov parameter
        self.addParameter(ParameterSelection(self.MARKOV_T,
            self.tr('Markov Type'), ['Classic', 'Spatial', 'LISA']))
        #Beginning and end field parameters to read
        self.addParameter(ParameterTableField(self.FIELD_START,
            self.tr('Starting Field'), self.INPUT))
        self.addParameter(ParameterTableField(self.FIELD_END,
            self.tr('Ending Field'), self.INPUT))
        self.addParameter(ParameterSelection(self.FIELD_JUMPS,
            self.tr('Fields to Jump'), ['1','2','3','4','5']))
        
        self.addParameter(ParameterSelection(self.CONTIGUITY,
            self.tr('Contiguity'), ['Queen','Rook']))

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
        # given, appended field.
        # using fields.append(...) i.e:
        fields.append(QgsField('MARKOV_RES', QVariant.Int))

        field_names = [field.name() for field in fields]
        # Retrieve the index values for the fields
        # Use these as the starting and stopping points

        start_index = field_names.index(field_s)
        end_index = field_names.index(field_e)
        print field_names[start_index], field_names[end_index]

        jumps = self.getParameterValue(self.FIELD_JUMPS)
        contiguity = self.getParameterValue(self.CONTIGUITY)
        markov_type = self.getParameterValue(self.MARKOV_T)

        # String placeholder using the parameter MARKOV_T
        mt = ''
        if markov_type == 0:
            mt = 'Classic'
        elif markov_type == 1:
            mt = 'Spatial'
        else:
            mt = 'LISA'

        # Taking care of the spatial weights for Spatial and LISA
        if mt != 'Classic': # Not Classic Markov
            if contiguity == 0: # 0 for queen
                print 'INFO: {0} Markov using queen contiguity'.format(mt)
                w = pysal.queen_from_shapefile(filename)
            else: # 1 for rook
                print 'INFO: {0} Markov using rook contiguity'.format(mt)
                w = pysal.rook_from_shapefile(filename)

        # Setting up the data for Markov chaining using quintiles
        f = pysal.open(filename.replace('.shp','.dbf'))
        header = f.header
        start_index = header.index(field_s)
        end_index = header.index(field_e)
        variables = [header[i] for i in range(start_index, end_index+1)]
        pci = np.array([f.by_col[v] for v in variables])
        q5 = np.array([pysal.Quantiles(y).yb for y in pci]).transpose()
        pci = pci.astype(float)
        print pci.shape
        print q5.shape


        # Performin the Markov chain analysis
        if markov_type == 0: # Classic Markov
            m = pysal.Markov(q5)
        elif markov_type == 1: # Spatial Markov
            m = pysal.Spatial_Markov(pci, w, fixed = True, k = 5,
                variable_name = 'spatialMarkovVar')
        else: # LISA Markov
            m = pysal.LISA_Markov(pci, w, 100)
            
        print m.transitions

        # Endpoint data, for now, this is depicted in the final map
        # Takes the first value of a geometry and the last value then
        # finds the difference between the two.
        i = 0
        quants_ends_difs = []
        for q in q5:
            #print (q)
            dif = q[-1] - q[0]
            if dif > 0:
                quants_ends_difs.append(2)
            elif dif < 0:
                quants_ends_difs.append(0)
            else: # dif == 0
                quants_ends_difs.append(1)
        print quants_ends_difs

        
        # Handling Map Output
        """
        writer = self.getOutputFromName(self.MAP_OUTPUT).getVectorWriter(fields, provider.geometryType(), layer.crs())
        outFeat = QgsFeature()
        i = 0
        for inFeat in processing.features(layer):
            inGeom = inFeat.geometry()
            outFeat.setGeometry(inGeom)
            attribs = inFeat.attribute()
            attribs.append(int(quants_ends_difs[i]))
            outFeat.setAttributes(attribs)
            writer.addFeature(outFeat)
            i += 1

        del writer

            
        out_layer = dataobjects.getObjectFromUri(self.getOutputValue(self.MAP_OUTPUT))
        """
        writer = self.getOutputFromName(self.MAP_OUTPUT).getVectorWriter(
            fields, provider.geometryType(), layer.crs() )
        outFeat = QgsFeature()
        i = 0
        for inFeat in processing.features(layer):
            inGeom = inFeat.geometry()
            outFeat.setGeometry(inGeom)
            attrs = inFeat.attributes()
            attrs.append(int(quants_ends_difs[i]))
            outFeat.setAttributes(attrs)
            writer.addFeature(outFeat)
            i+=1

        del writer

        out_layer = dataobjects.getObjectFromUri(self.getOutputValue(
         self.MAP_OUTPUT))


        
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
        expression = "MARKOV_RES"
        renderer = QgsCategorizedSymbolRendererV2(expression,
                                                  categories)
        out_layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(out_layer)
        iface.mapCanvas().refresh()
        iface.legendInterface().refreshLayerSymbology(out_layer)
        iface.mapCanvas().refresh()
