import os

from qgis.core import (
    QgsProcessingProvider,
    QgsApplication,
)
from qgis.PyQt.QtGui import QIcon

from .algorithms.fillsinks import Fillsinks
from .algorithms.excesstopgraphy import Excesstopography
from .algorithms.gradient8 import Gradient8
from .algorithms.curvature import Curvature
from .algorithms.evansslope import Evansslope
from .algorithms.stream_network_raster import StreamNetworkRaster
from .algorithms.prominence import Prominence
from .algorithms.zscore import ZScore
from .algorithms.stream_network_vector import StreamNetworkVector
from .algorithms.flow_accumulation import FlowAccumulation
from .algorithms.drainage_basins import DrainageBasins


class TopoToolboxProvider(QgsProcessingProvider):
    def __init__(self):
        super().__init__()

    def loadAlgorithms(self):
        self.addAlgorithm(Fillsinks())
        self.addAlgorithm(Excesstopography())
        self.addAlgorithm(Gradient8())
        self.addAlgorithm(Curvature())
        self.addAlgorithm(Evansslope())
        self.addAlgorithm(Prominence())
        self.addAlgorithm(ZScore())
        self.addAlgorithm(StreamNetworkRaster())
        self.addAlgorithm(StreamNetworkVector())
        self.addAlgorithm(FlowAccumulation())
        self.addAlgorithm(DrainageBasins())

    def id(self):
        return "topotoolbox"

    def name(self):
        return "TopoToolbox"

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "icons", "logo.png"))


class TopoToolboxPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initProcessing(self):
        self.provider = TopoToolboxProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
