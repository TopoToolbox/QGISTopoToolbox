import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterRasterDestination,
    QgsProcessingException,
)
from qgis.PyQt.QtGui import QIcon

import topotoolbox as tt


class Excesstopography(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    METHOD = "METHOD"
    THRESHOLD = "THRESHOLD"
    OUTPUT = "OUTPUT"

    def createInstance(self):
        return Excesstopography()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def name(self):
        return "Excesstopography"

    def displayName(self):
        return self.tr("Excesstopography")

    def shortHelpString(self):
        return self.tr("Compute the two-dimensional excess topography.")

    def icon(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "icons", "logo.png")
        return QIcon(icon_path)

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_RASTER, self.tr("Input DEM"))
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                "Calculation method",
                options=["fsm2d", "fmm2d"],
                defaultValue="fsm2d",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.THRESHOLD,
                "Threshold for excess topography calculation",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.2,
                minValue=0.0,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(self.OUTPUT, self.tr(""))
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )
        threshold = self.parameterAsDouble(parameters, self.THRESHOLD, context)
        method = self.parameterAsEnum(parameters, self.METHOD, context)

        if input_raster is None:
            raise QgsProcessingException("Invalid input raster layer")

        input_path = input_raster.source()
        dem = tt.read_tif(input_path)

        if method == 0:
            method = "fsm2d"
        else:
            method = "fmm2d"

        result_dem = dem.excesstopography(threshold=threshold, method=method)

        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        tt.write_tif(result_dem, output_path)
        return {self.OUTPUT: output_path}
