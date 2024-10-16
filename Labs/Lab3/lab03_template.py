import os
import geopandas as gpd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

class CensusTract:
    def __init__(self, geoid, population, aland, geometry):
        self.geoid = geoid
        self.population = population
        self.aland = aland  # land area in square meters
        self.geometry = geometry
    
    def calculate_population_density(self):
        # Calculate the area in square kilometers if the CRS is in meters
        area_km2 = self.aland / 1e6  # Convert land area from square meters to square kilometers
        population_density = self.population / area_km2 if area_km2 > 0 else 0
        return population_density

if __name__ == "__main__":
    # Read data
    file_path = os.path.join(DATA_DIR, 'data.geojson')
    gdf = gpd.read_file('data/data.geojson')

    # Preview data
    print(gdf.head())
    print(gdf.columns)
    print(gdf.shape)
    print(gdf.dtypes)

    def calculate_pop_density(row):
        tract = CensusTract(row['GeoId'], row['Pop'], row['ALAND'], row['geometry'])
        return tract.calculate_population_density()

    # using apply function
    gdf['Pop_Den_new'] = gdf.apply(calculate_pop_density, axis=1)

    # printing the updated data with population density
    print(gdf.head())