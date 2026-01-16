import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterRasterDestination,
    QgsProcessingException,
)
from qgis.PyQt.QtGui import QIcon

import topotoolbox as tt


class Evansslope(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    MODE = "MODE"
    MODIFIED = "MODIFIED"
    OUTPUT = "OUTPUT"

    def createInstance(self):
        return Evansslope()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def name(self):
        return "evansslope"

    def displayName(self):
        return self.tr("Evansslope")

    def shortHelpString(self):
        return self.tr("")

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
                self.MODE,
                "Calculation method",
                options=[
                    "reflect",
                    "constant",
                    "nearest",
                    "mirror",
                    "wrap",
                    "grid-mirror",
                    "grid-constant",
                    "grid-wrap",
                ],
                defaultValue="nearest",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MODIFIED, self.tr(""), defaultValue=False
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(self.OUTPUT, self.tr(""))
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )
        mode = self.parameterAsEnum(parameters, self.MODE, context)
        modified = self.parameterAsBoolean(parameters, self.MODIFIED, context)

        if input_raster is None:
            raise QgsProcessingException("Invalid input raster layer")

        input_path = input_raster.source()
        dem = tt.read_tif(input_path)

        modes = [
            "reflect",
            "constant",
            "nearest",
            "mirror",
            "wrap",
            "grid-mirror",
            "grid-constant",
            "grid-wrap",
        ]
        mode = modes[mode]

        result_dem = dem.evansslope(mode=mode, modified=modified)

        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        tt.write_tif(result_dem, output_path)
        return {self.OUTPUT: output_path}
