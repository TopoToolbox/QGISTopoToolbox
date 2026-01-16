import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterVectorDestination,
    QgsProcessingException,
    QgsProcessing,
)
from qgis.PyQt.QtGui import QIcon

import topotoolbox as tt


class StreamNetwork(QgsProcessingAlgorithm):

    INPUT_RASTER = "INPUT_RASTER"
    THRESHOLD = "THRESHOLD"
    UNITS = "UNITS"
    OUTPUT = "OUTPUT"

    def createInstance(self):
        return StreamNetwork()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def name(self):
        return "Stream Network"

    def displayName(self):
        return self.tr("Stream Network")

    def shortHelpString(self):
        return self.tr(
            "Extracts a stream network using TopoToolbox FlowObject and "
            "StreamObject. Threshold can be int/float or 2D matrix. "
            "Units must be one of: pixels, mapunits, m2, km2."
        )

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
            QgsProcessingParameterNumber(
                self.THRESHOLD,
                self.tr("Threshold (0 = auto threshold)"),
                QgsProcessingParameterNumber.Double,
                defaultValue=1000.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.UNITS,
                self.tr("Units"),
                options=["pixels", "mapunits", "m2", "km2"],
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr("Output Stream Network"),
                type=QgsProcessing.TypeVectorLine,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )
        if input_raster is None:
            raise QgsProcessingException("Invalid input raster layer")

        threshold = self.parameterAsDouble(parameters, self.THRESHOLD, context)
        units = ["pixels", "mapunits", "m2", "km2"][
            self.parameterAsEnum(parameters, self.UNITS, context)
        ]

        input_path = input_raster.source()
        dem = tt.read_tif(input_path)

        fd = tt.FlowObject(dem)
        s = tt.StreamObject(flow=fd, units=units, threshold=threshold)

        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        s.to_shapefile(output_path)

        return {self.OUTPUT: output_path}
