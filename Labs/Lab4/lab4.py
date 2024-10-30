import arcpy
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DB_PATH = "E:\\Documents\\GISProgramming\\SM-GEOG392-Lab\\Labs\\Lab4\\data\\Campus.gdb"
CSV_PATH = "E:\\Documents\\GISProgramming\\SM-GEOG392-Lab\\Labs\\Lab4\\data\\garages.csv"
OUTPUT_DB_PATH = "E:\\Documents\\GISProgramming\\SM-GEOG392-Lab\\Labs\\Lab4\\data\\output.gdb"

arcpy.env.workspace = INPUT_DB_PATH

# Layers that need to be kept
layers_to_keep = ["GaragePoints", "LandUse", "Structures", "Trees"]

# List all feature classes
feature_classes = arcpy.ListFeatureClasses()

# Delete feature classes that are not in layers_to_keep
for fc in feature_classes:
    if fc not in layers_to_keep:
        arcpy.management.Delete(fc)

# Create output GDB if it doesn't exist
if not os.path.exists(OUTPUT_DB_PATH):
    arcpy.management.CreateFileGDB(os.path.dirname(OUTPUT_DB_PATH), os.path.basename(OUTPUT_DB_PATH))

# Load CSV file as point feature class into the input GDB
garage_points_output = "in_memory/GaragePoints"
# Import CSV as a point feature class using X and Y fields with a specified spatial reference
arcpy.management.XYTableToPoint(
    CSV_PATH, 
    garage_points_output, 
    x_field="X", 
    y_field="Y", 
)
# Print spatial references before re-projection
print("Before Re-Projection...")
print(f"garages layer spatial reference: {arcpy.Describe(garage_points_output).spatialReference.name}.")
print(f"Structures layer spatial reference: {arcpy.Describe('Structures').spatialReference.name}.")

# Re-project
target_ref = arcpy.SpatialReference(4326)  

structures_projected = arcpy.management.Project("Structures", "in_memory/Structures_Projected", target_ref)

# Print spatial references after re-projection
print("After Re-Projection...")
print(f"garages layer spatial reference: {arcpy.Describe(garage_points_output).spatialReference.name}.")
print(f"re-projected Structures layer spatial reference: {arcpy.Describe(structures_projected).spatialReference.name}.")

# Buffer analysis
radiumStr = "150 Meters"
garages_buffered = arcpy.analysis.Buffer(garage_points_output, "in_memory/garages_buffered", radiumStr)

# Intersect analysis
intersection_result = arcpy.analysis.Intersect([garages_buffered, structures_projected], "in_memory/intersection")

layers_to_copy = {garage_points_output: "garages", "Structures": "Structure", garages_buffered: "garages_buffered", intersection_result: "intersection"}

for source_layer, output_name in layers_to_copy.items():
    output_path = os.path.join(OUTPUT_DB_PATH, output_name)
    
    if arcpy.Exists(output_path):
        arcpy.management.Delete(output_path)
    
    arcpy.management.CopyFeatures(source_layer, output_path)

print("Feature layers have been successfully exported to the output GDB.")