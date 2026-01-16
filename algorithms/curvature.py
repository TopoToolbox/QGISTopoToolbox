import os

# pylint: disable=import-error
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


class Curvature(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    CTYPE = "CTYPE"
    MEANFILT = "MEANFILT"
    OUTPUT = "OUTPUT"

    def createInstance(self):
        return Curvature()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def name(self):
        return "curvature"

    def displayName(self):
        return self.tr("Curvature")

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
                self.CTYPE,
                "Calculation method",
                options=["profc", "planc", "tangc", "meanc", "total"],
                defaultValue="tangent",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MEANFILT, self.tr(""), defaultValue=False
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(self.OUTPUT, self.tr(""))
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )
        meanfilt = self.parameterAsBoolean(parameters, self.MEANFILT, context)
        ctype = self.parameterAsEnum(parameters, self.CTYPE, context)

        if input_raster is None:
            raise QgsProcessingException("Invalid input raster layer")

        input_path = input_raster.source()
        dem = tt.read_tif(input_path)

        if ctype == 0:
            ctype = "profc"
        elif ctype == 1:
            ctype = "planc"
        elif ctype == 2:
            ctype = "tangc"
        elif ctype == 3:
            ctype = "meanc"
        else:
            ctype = "total"

        result_dem = dem.curvature(ctype=ctype, meanfilt=meanfilt)

        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        tt.write_tif(result_dem, output_path)
        return {self.OUTPUT: output_path}
