import os

from PyQt5.QtCore import QVariant
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterRasterDestination,
    QgsProcessingException,
    QgsFeature,
    QgsVectorLayer,
    QgsGeometry,
    QgsField,
    QgsPointXY,
    QgsProject,
    QgsCoordinateReferenceSystem,
)
from qgis.PyQt.QtGui import QIcon

import topotoolbox as tt
import numpy as np


class Prominence(QgsProcessingAlgorithm):
    INPUT_RASTER = "INPUT_RASTER"
    USE_HYBRID = "USE_HYBRID"
    TOLERANCE = "TOLERANCE"
    OUTPUT_TYPE = "OUTPUT_TYPE"
    OUTPUT = "OUTPUT"

    def createInstance(self):
        return Prominence()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def name(self):
        return "prominence"

    def displayName(self):
        return self.tr("Prominence")

    def shortHelpString(self):
        return self.tr(
            "calculates the prominence of peaks in a DEM. "
            "The prominence is the minimal amount one would need "
            "to descend from a peak before being able to ascend "
            "to a higher peak. It may take a while to run "
            "for large DEMs. "
            "Increase tolerance to improve runtime."
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
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr("Tolerance for peak detection in meters"),
                type=QgsProcessingParameterNumber.Double,
                minValue=0,
                defaultValue=100,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_HYBRID,
                self.tr("Use the hybrid reconstruction algorithm."),
                defaultValue=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.OUTPUT_TYPE,
                self.tr("Type of output"),
                options=["Raster prominence map", "Vector point layer"],
                defaultValue=1,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT, self.tr("Output location")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )
        tolerance = self.parameterAsDouble(parameters, self.TOLERANCE, context)
        use_hybrid = self.parameterAsBoolean(parameters, self.USE_HYBRID, context)
        output_type = self.parameterAsEnum(parameters, self.OUTPUT_TYPE, context)

        if input_raster is None:
            raise QgsProcessingException("Invalid input raster layer")

        input_path = input_raster.source()
        dem = tt.read_tif(input_path)

        prom, idx = dem.prominence(tolerance=tolerance, use_hybrid=use_hybrid)

        prom_raster = np.full_like(dem.z, np.nan)
        prom_raster[idx[1], idx[0]] = prom

        if output_type == 0:
            # Case: Raster output
            dem.z = prom_raster
            output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
            tt.write_tif(dem, output_path)
            return {self.OUTPUT: output_path}

        else:
            # Case: Vector point layer output
            crs = QgsCoordinateReferenceSystem(dem.georef.to_string())
            layer = QgsVectorLayer(f"Point?crs={crs.authid()}", "Prominence", "memory")
            provider = layer.dataProvider()

            provider.addAttributes([QgsField("prom", QVariant.Double)])
            layer.updateFields()

            features = []
            rows, cols = np.where(~np.isnan(prom_raster))

            for r, c in zip(rows, cols):
                x, y = dem.transform * (c + 0.5, r + 0.5)
                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
                feature.setAttributes([float(prom_raster[r, c])])
                features.append(feature)

            if features:
                provider.addFeatures(features)
                layer.updateExtents()

            QgsProject.instance().addMapLayer(layer)

            return {self.OUTPUT: layer.id()}
