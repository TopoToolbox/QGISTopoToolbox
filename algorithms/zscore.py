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


class ZScore(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    OUTPUT = "OUTPUT"

    def createInstance(self):
        return ZScore()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def name(self):
        return "zscore"

    def displayName(self):
        return self.tr("zscore")

    def shortHelpString(self):
        return self.tr(
            "Returns the z-score for each element of GridObject "
            "such that all values are centered to have mean 0 and "
            "scaled to have standard deviation 1."
        )

    def icon(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "icons", "logo.png")
        return QIcon(icon_path)

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_RASTER, self.tr("Input DEM"))
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT, self.tr("Output Z-Score raster")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )

        if input_raster is None:
            raise QgsProcessingException("Invalid input raster layer")

        input_path = input_raster.source()
        dem = tt.read_tif(input_path)

        zscore_dem = dem.zscore()

        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        tt.write_tif(zscore_dem, output_path)
        return {self.OUTPUT: output_path}
