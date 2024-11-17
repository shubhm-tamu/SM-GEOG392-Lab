# -*- coding: utf-8 -*-

import arcpy
import os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Lab5_Toolbox"
        self.alias = "Lab5_Toolbox"
        self.tools = [Lab5_Tool]

class Lab5_Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Lab5_Tool"
        self.description = "This tool creates a geodatabase, imports CSV data, and performs buffer and clip analysis."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""
        # Parameter 1: GDB Folder
        param_GDB_folder = arcpy.Parameter(
            displayName="GDB Folder",
            name="gdb_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 2: GDB Name
        param_GDB_Name = arcpy.Parameter(
            displayName="GDB Name",
            name="gdb_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 3: Garage CSV File
        param_Garage_CSV_File = arcpy.Parameter(
            displayName="Garage CSV File",
            name="garage_csv_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 4: Garage Layer Name
        param_Garage_Layer_Name = arcpy.Parameter(
            displayName="Garage Layer Name",
            name="garage_layer_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 5: Campus GDB
        param_Campus_GDB = arcpy.Parameter(
            displayName="Campus GDB",
            name="campus_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 6: Selected Garage Name
        param_Selected_Garage_Name = arcpy.Parameter(
            displayName="Selected Garage Name",
            name="selected_garage_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        # Parameter 7: Buffer Radius
        param_Buffer_Radius = arcpy.Parameter(
            displayName="Buffer Radius",
            name="buffer_radius",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input"
        )

        params = [
            param_GDB_folder,
            param_GDB_Name,
            param_Garage_CSV_File,
            param_Garage_Layer_Name,
            param_Campus_GDB,
            param_Selected_Garage_Name,
            param_Buffer_Radius
        ]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Extract user input
        GDB_Folder = parameters[0].valueAsText
        GDB_Name = parameters[1].valueAsText
        Garage_CSV_File = parameters[2].valueAsText
        Garage_Layer_Name = parameters[3].valueAsText
        Campus_GDB = parameters[4].valueAsText
        Selected_Garage_Name = parameters[5].valueAsText
        Buffer_Radius = parameters[6].valueAsText

        # Print user input to the tool messages
        arcpy.AddMessage("User Input:")
        arcpy.AddMessage(f"GDB Folder: {GDB_Folder}")
        arcpy.AddMessage(f"GDB Name: {GDB_Name}")
        arcpy.AddMessage(f"Garage CSV File: {Garage_CSV_File}")
        arcpy.AddMessage(f"Garage Layer Name: {Garage_Layer_Name}")
        arcpy.AddMessage(f"Campus GDB: {Campus_GDB}")
        arcpy.AddMessage(f"Selected Garage Name: {Selected_Garage_Name}")
        arcpy.AddMessage(f"Buffer Radius: {Buffer_Radius}")

        # Construct the full path for the geodatabase
        GDB_Full_Path = os.path.join(GDB_Folder, GDB_Name)

        # Step 1: Create a geodatabase
        if not arcpy.Exists(GDB_Full_Path):
            arcpy.management.CreateFileGDB(GDB_Folder, GDB_Name)
            arcpy.AddMessage(f"Geodatabase created at: {GDB_Full_Path}")
        else:
            arcpy.AddMessage(f"Geodatabase already exists at: {GDB_Full_Path}")

        # Step 2: Import garage CSV into the geodatabase
        try:
            garages_layer = arcpy.management.MakeXYEventLayer(
                Garage_CSV_File, "X", "Y", Garage_Layer_Name
            )
            arcpy.FeatureClassToGeodatabase_conversion(garages_layer, GDB_Full_Path)
            arcpy.AddMessage(f"Garage CSV imported successfully to {GDB_Full_Path}")
        except Exception as e:
            arcpy.AddError(f"Error importing CSV: {e}")
            return

        garages_fc = os.path.join(GDB_Full_Path, Garage_Layer_Name)

        # Step 3: Select the specified garage
        structures = os.path.join(Campus_GDB, "Structures")
        where_clause = f"BldgName = '{Selected_Garage_Name}'"

        with arcpy.da.SearchCursor(structures, ["BldgName"], where_clause=where_clause) as cursor:
            shouldProceed = any(row for row in cursor)

        if shouldProceed:
            # Select the garage feature
            selected_garage = os.path.join(GDB_Full_Path, "selected_garage")
            arcpy.analysis.Select(structures, selected_garage, where_clause)

            # Step 4: Buffer the selected garage
            buffer_output = os.path.join(GDB_Full_Path, "garage_buffer")
            arcpy.analysis.Buffer(selected_garage, buffer_output, Buffer_Radius)
            arcpy.AddMessage(f"Buffer created at: {buffer_output}")

            # Step 5: Clip the buffered area with structures
            clip_output = os.path.join(GDB_Full_Path, "clipped_structures")
            arcpy.analysis.Clip(structures, buffer_output, clip_output)
            arcpy.AddMessage(f"Clip completed. Output saved at: {clip_output}")

            arcpy.AddMessage("Process completed successfully.")
        else:
            arcpy.AddError(f"Garage '{Selected_Garage_Name}' not found in the Structures layer.")

        return