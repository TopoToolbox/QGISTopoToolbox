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


class Gradient8(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    UNIT = "UNIT"
    MULTIPROCESSING = "MULTIPROCESSING"
    OUTPUT = "OUTPUT"

    def createInstance(self):
        return Gradient8()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def name(self):
        return "gradient8"

    def displayName(self):
        return self.tr("Gradient8")

    def shortHelpString(self):
        return self.tr(
            "Compute the gradient of a digital elevation model "
            "using an 8-direction algorithm."
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
            QgsProcessingParameterEnum(
                self.UNIT,
                "Calculation method",
                options=["tangent", "radians", "degrees", "sine", "percent"],
                defaultValue="tangent",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MULTIPROCESSING,
                self.tr("Threshold for excess topography calculation"),
                defaultValue=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(self.OUTPUT, self.tr(""))
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )
        multiprocessing = self.parameterAsBoolean(
            parameters, self.MULTIPROCESSING, context
        )
        unit = self.parameterAsEnum(parameters, self.UNIT, context)

        if input_raster is None:
            raise QgsProcessingException("Invalid input raster layer")

        input_path = input_raster.source()
        dem = tt.read_tif(input_path)

        if unit == 0:
            unit = "tsngent"
        elif unit == 1:
            unit = "radians"
        elif unit == 2:
            unit = "degrees"
        elif unit == 3:
            unit = "sine"
        else:
            unit = "percent"

        result_dem = dem.gradient8(unit=unit, multiprocessing=multiprocessing)

        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        tt.write_tif(result_dem, output_path)
        return {self.OUTPUT: output_path}
