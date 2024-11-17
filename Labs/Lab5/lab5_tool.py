import arcpy
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
arcpy.env.workspace = BASE_DIR
arcpy.env.overwriteOutput = True

print("Please input the following parameters:\n")
GDB_Folder = input("Enter the path for the GDB Folder (e.g., '***/Labs/Lab5'): ")
GDB_Name = input("Enter the GDB Name (e.g., 'Lab5.gdb'): ")
Garage_CSV_File = input("Enter the path for the Garage CSV File (e.g., '***/Labs/Lab5/garages.csv'): ")
Garage_Layer_Name = input("Enter the Garage Layer Name (e.g., 'garages'): ")
Campus_GDB = input("Enter the path for the Campus GDB (e.g., '***/Labs/Lab5/Campus.gdb'): ")
Selected_Garage_Name = input("Enter the name of the garage to select (e.g., 'Northside Parking Garage'): ")
Buffer_Radius = input("Enter the Buffer Radius (e.g., '150 meters'): ")

#create gdb
GDB_Full_Path = os.path.join(GDB_Folder, GDB_Name)
if not arcpy.Exists(GDB_Full_Path):
    arcpy.management.CreateFileGDB(GDB_Folder, GDB_Name)
    print(f"Geodatabase created at: {GDB_Full_Path}")
else:
    print(f"Geodatabase already exists at: {GDB_Full_Path}")

#import garage csv
try:
    garages_layer = arcpy.management.MakeXYEventLayer(
        Garage_CSV_File, "X", "Y", Garage_Layer_Name, spatial_reference=4326
    )
    arcpy.FeatureClassToGeodatabase_conversion(garages_layer, GDB_Full_Path)
    print(f"Garage CSV imported successfully to {GDB_Full_Path}")
except Exception as e:
    print(f"Error importing CSV: {e}")

garages_fc = os.path.join(GDB_Full_Path, Garage_Layer_Name)
structures = os.path.join(Campus_GDB, "Structures")
where_clause = f"BldgName = '{Selected_Garage_Name}'"
with arcpy.da.SearchCursor(structures, ["BldgName"], where_clause=where_clause) as cursor:
    shouldProceed = any(row for row in cursor)

if shouldProceed:
    # Select the garage into a new feature class
    selected_garage_layer_name = "selected_garage"
    selected_garage = arcpy.analysis.Select(
        structures, os.path.join(GDB_Full_Path, selected_garage_layer_name), where_clause
    )

    print(f"Selected garage: {Selected_Garage_Name}")

    # Buffer the selected garage
    buffer_output = os.path.join(GDB_Full_Path, "garage_buffer")
    arcpy.analysis.Buffer(selected_garage, buffer_output, Buffer_Radius)
    print(f"Buffer created at: {buffer_output}")

    # Clip the buffered area with structures
    clip_output = os.path.join(GDB_Full_Path, "clipped_structures")
    arcpy.analysis.Clip(structures, buffer_output, clip_output)
    print(f"Clip completed. Output saved at: {clip_output}")

    print("Process completed successfully.")
else:
    print(f"Garage '{Selected_Garage_Name}' not found.")