import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterVectorDestination,
    QgsProcessingException,
    QgsProcessing,
    QgsVectorLayer,
    edit,
)
from qgis.PyQt.QtGui import QIcon

import topotoolbox as tt


class StreamNetworkVector(QgsProcessingAlgorithm):

    INPUT_RASTER = "INPUT_RASTER"
    THRESHOLD = "THRESHOLD"
    UNITS = "UNITS"
    OUTPUT = "OUTPUT"
    HALF_SHIFT = "HALF_SHIFT"

    def createInstance(self):
        return StreamNetworkVector()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)
    
    def group(self):
        return 'Stream Object'

    def groupId(self):
        return 'stream_object'

    def name(self):
        return "streamnetworkvector"

    def displayName(self):
        return self.tr("Stream Network (Vector)")

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
                self.tr("Threshold (0 = auto threshold of 1000)"),
                QgsProcessingParameterNumber.Double,
                defaultValue=1000.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.UNITS,
                self.tr("Units (default: pixels)"),
                options=["pixels", "mapunits", "m2", "km2"],
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr("Output Stream Network (Vector)"),
                type=QgsProcessing.TypeVectorLine,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.HALF_SHIFT,
                self.tr(
                    "Apply half-cell shift to output vector layer. If disabled, "
                    "streams vertexes will fall on cell corners of input dem."
                    " (i.e. shifts by cellsize/2 to the right and down)."
                ),
                defaultValue=True,
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

        half_shift = self.parameterAsBool(parameters, self.HALF_SHIFT, context)

        if half_shift:
            layer = QgsVectorLayer(output_path, "streams", "ogr")
            cell = dem.cellsize

            with edit(layer):
                for f in layer.getFeatures():
                    geom = f.geometry()
                    geom.translate(cell / 2, -cell / 2)
                    f.setGeometry(geom)
                    layer.updateFeature(f)

        return {self.OUTPUT: output_path}
