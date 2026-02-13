import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterRasterDestination,
    QgsProcessingException,
)
from qgis.PyQt.QtGui import QIcon

import topotoolbox as tt


class DrainageBasins(QgsProcessingAlgorithm):

    INPUT_RASTER = "INPUT_RASTER"
    OUTPUT = "OUTPUT"

    def createInstance(self):
        return DrainageBasins()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def group(self):
        return "Flow Object"

    def groupId(self):
        return "flow_object"

    def name(self):
        return "drainage_basins"

    def displayName(self):
        return self.tr("Drainage Basins")

    def shortHelpString(self):
        return self.tr("Delineate drainage basins from a flow network.")

    def icon(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "icons", "logo.png")
        return QIcon(icon_path)

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER, self.tr("Input DEM raster")
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT, self.tr("Drainage Basins")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )
        if input_raster is None:
            raise QgsProcessingException("Invalid input raster layer")

        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        input_path = input_raster.source()
        dem = tt.read_tif(input_path)
        fd = tt.FlowObject(dem)
        basins = fd.drainagebasins().shufflelabel()
        tt.write_tif(basins, output_path)

        return {self.OUTPUT: output_path}
