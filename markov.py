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

class Markov(GeoAlgorithm):

    INPUT = 'INPUT'
    FIELD_START = 'FIELD_START'
    FIELD_END = 'FIELD_END'
    CONTIGUITY = 'CONTIGUITY'
    MARKOV_T = 'MARKOV_T'
    TRANSITIONS = 'TRANSITIONS'

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
        
        self.addParameter(ParameterSelection(self.CONTIGUITY,
            self.tr('Contiguity'), ["Queen","Rook"]))

        self.addOutput(OutputNumber(self.TRANSITIONS, self.tr('transitions')))
        
    def processAlgorithm(self, progress):
        field_s = self.getParameterValue(self.FIELD_START)
        field_s = field_s[0:10] # try to handle Shapefile field length limit
        field_e = self.getParameterValue(self.FIELD_END)
        # pci = np.array([f.by_col[str(y)] for y in range(1929,2010)])
        # q5 = np.array([pysal.Quantiles(y).yb for y in pci]).transpose()
        # m = Markov(q5)
        filename = self.getParameterValue(self.INPUT)
        layer = dataobjects.getObjectFromUri(filename)
        filename = dataobjects.exportVectorLayer(layer)        
        
        contiguity = self.getParameterValue(self.CONTIGUITY)
        markov_type = self.getParameterValue(self.MARKOV_T)

        
        """
        if markov_type != 0: # Not Classic Markov
            if contiguity == 0: # queen
                print 'INFO: {0} Markov using queen contiguity'.format(markov_type)
                w = pysal.queen_from_shapefile(filename)
            else: # 1 for rook
                print 'INFO: {0} Markov using rook contiguity'.format(markov_type)
                w = pysal.rook_from_shapefile(filename)
        """
        #for now, this will be only the south
        f = pysal.open(filename.replace('.shp','.dbf'))

        ## hr are columns 9-12 in south
        pci = np.array(f).transpose()[9:13]
        pci = pci.astype(float)
        quants = np.array([pysal.Quantiles(pci).yb for y in pci])
        print quants
        ##
        #quants = np.array(f.by_col[str(field)])
        m = pysal.Markov(quants)
        print (m.transitions)
        self.setOutputValue(self.TRANSITIONS, m.transitions)
        
        print "Transitions: %f" % (m.transitions)
        """
        print "INFO: Moran's I values range from -1 (indicating perfect dispersion) to +1 (perfect correlation). Values close to -1/(n-1) indicate a random spatial pattern."
        print "p_norm: %f" % (m.p_norm)
        print "p_rand: %f" % (m.p_rand)
        print "p_sim: %f" % (m.p_sim)
        print "INFO: p values smaller than 0.05 indicate spatial autocorrelation that is significant at the 5% level."
        print "z_norm: %f" % (m.z_norm)
        print "z_rand: %f" % (m.z_rand)
        print "z_sim: %f" % (m.z_sim)
        print "INFO: z values greater than 1.96 or smaller than -1.96 indicate spatial autocorrelation that is significant at the 5% level."
        """
