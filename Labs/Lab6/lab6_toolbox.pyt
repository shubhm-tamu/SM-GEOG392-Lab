# -*- coding: utf-8 -*-

import arcpy
import time

class Toolbox(object):
    def __init__(self):
        self.label = "Lab6_Toolbox"
        self.alias = "Lab6_Toolbox"
        self.tools = [Lab6_Tool]


class Lab6_Tool(object):
    def __init__(self):
        self.label = "Lab6_Tool"
        self.description = "Apply renderers and progressor to layers in ArcGIS Pro"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param_proj_path = arcpy.Parameter(
            displayName="Project File Path",
            name="proj_path",
            datatype="DEFile",
            parameterType="Required",
            direction="Input",
        )
        param_layer_name = arcpy.Parameter(
            displayName="Layer Name",
            name="layer_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        param_output_path = arcpy.Parameter(
            displayName="Output Project File Path",
            name="output_path",
            datatype="DEFile",
            parameterType="Optional",
            direction="Output",
        )
        return [param_proj_path, param_layer_name, param_output_path]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        """The source code of the tool"""
        readTime = 3
        start = 0
        max = 100
        step = 25

        arcpy.SetProgressor("step", "Initializing tool...", start, max, step)
        arcpy.AddMessage("Init tool...")

        # User input
        aprxFilePath = parameters[0].valueAsText
        outputPath = parameters[2].valueAsText if parameters[2].value else aprxFilePath.replace(".aprx", "_updated.aprx")

        project = arcpy.mp.ArcGISProject(aprxFilePath)
        layers = project.listMaps('Map')[0].listLayers()

        for layer in layers:
            if layer.isFeatureLayer:
                symbology = layer.symbology

                # Update progress
                arcpy.SetProgressorPosition(start + step)
                arcpy.SetProgressorLabel("Checking layer: {}".format(layer.name))
                arcpy.AddMessage(f"Processing layer: {layer.name}")
                time.sleep(readTime)

                if hasattr(symbology, 'renderer') and layer.name == 'Structures':
                    # UniqueValueRenderer for Structures
                    symbology.updateRenderer('UniqueValueRenderer')
                    symbology.renderer.fields = ["Type"]
                    layer.symbology = symbology

                    # Update progress
                    arcpy.SetProgressorPosition(start + 2 * step)
                    arcpy.SetProgressorLabel("Applying UniqueValueRenderer to Structures")
                    arcpy.AddMessage("Applied UniqueValueRenderer to Structures.")
                    time.sleep(readTime)

                elif hasattr(symbology, 'renderer') and layer.name == 'Trees':
                    # GraduatedColorsRenderer for Trees
                    symbology.updateRenderer('GraduatedColorsRenderer')
                    symbology.renderer.classificationField = "Shape_Area"
                    symbology.renderer.breakCount = 5
                    symbology.renderer.colorRamp = project.listColorRamps("Oranges (5 Classes)")[0]
                    layer.symbology = symbology

                    # Update progress
                    arcpy.SetProgressorPosition(start + 3 * step)
                    arcpy.SetProgressorLabel("Applying GraduatedColorsRenderer to Trees")
                    arcpy.AddMessage("Applied GraduatedColorsRenderer to Trees.")
                    time.sleep(readTime)

        # Save updated project
        project.saveACopy(outputPath)
        arcpy.SetProgressorPosition(max)
        arcpy.SetProgressorLabel("Saving project...")
        arcpy.AddMessage(f"Project saved at {outputPath}")
        time.sleep(readTime)

        return