from processing.core.AlgorithmProvider import AlgorithmProvider
from moran import Moran
from moranrate import MoranRate
from moranlocal import MoranLocal
from moranlocalrate import MoranLocalRate
from glocal import GLocal
from dtheil import TheilDSim
from neighborsetLIMA import NeighborSetLIMA
from neighborhoodsetLIMA import NeighborhoodSetLIMA

#from markov import Markov
from markovClassic import MarkovClassic
from markovLISA import MarkovLISA
from markovSpatial import MarkovSpatial

class pysalProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)

        self.activate = False

        self.alglist = [Moran(),MoranRate(),
                        MoranLocal(),MoranLocalRate(),
                        GLocal(),
                        TheilDSim(),
                        NeighborSetLIMA(),NeighborhoodSetLIMA(),
                        #Markov(),
                        MarkovClassic(),MarkovLISA(),MarkovSpatial()]
        for alg in self.alglist:
            alg.provider = self

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)

    def unload(self):
        AlgorithmProvider.unload(self)

    def getName(self):
        return 'pysal'

    def getDescription(self):
        return 'PySAL'

    def _loadAlgorithms(self):
        self.algs = self.alglist
