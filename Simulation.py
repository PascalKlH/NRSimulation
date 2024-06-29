import numpy as np
import plotly.graph_objects as go


PARAMETERS = {
    "length": 10,
    "width": 20,
    "row-distance": 2,
    "column-distance": 3,
    "initial-water-layer": 0.5,
    "Plant": "lettuce"
}

class Crop:
    def __init__(self,name):
        self.name = name
        self.cells = []
class Simulation:
    def __init__(self, parameters):
        self.parameters = parameters  # initializing the parameters
        self.size_layer = np.zeros((self.parameters["length"], self.parameters["width"]))  # create a grid for the plant sizes
        self.water_layer = np.full((self.parameters["length"], self.parameters["width"]), self.parameters["initial-water-layer"])  # create a grid for the water availabilities
        self.plants_layer = np.zeros((self.parameters["length"], self.parameters["width"]))  # create a grid for the plants
        self.crops_layer = np.full((self.parameters["length"], self.parameters["width"]),None,object)  # create a grid for the crops
        
    
    def planting(self):
            row_indices = np.arange(0, self.parameters["length"], self.parameters["row-distance"])
            col_indices = np.arange(0, self.parameters["width"], self.parameters["column-distance"])
            
            # Create meshgrid of indices
            row_grid, col_grid = np.meshgrid(row_indices, col_indices, indexing='ij')
            
            # Set plants_layer where plants are planted
            self.plants_layer[row_grid, col_grid] = 1
            
            # Create Crop objects where plants are planted
            crop_names = np.where(self.plants_layer == 1, self.parameters["Plant"], None)
            self.crops_layer = np.vectorize(Crop)(crop_names)
            
            # Print the name of the crop at each position where plants are planted
            plant_positions = np.argwhere(self.plants_layer == 1)
            for row, col in plant_positions:
                crop_name = self.crops_layer[row, col].name
                print(f"Crop at position ({row}, {col}): {crop_name}")
    
    def grow_plants(self):
        self.size_layer += self.water_layer*self.plants_layer #let the plants grow depending on the water availabilities


    def get_plant_info(self, row, col):
        if self.plants_layer[row, col] == 1: # check if a plant is planted at the given position
            size = self.size_layer[row,col] #get the size of the plant at the given position
            water_availability = self.water_layer[row, col] #get the water availability at the given position
            return {"size": size, "water_availability": water_availability} #create a dictionary with the plant information
        return None


if __name__ == "__main__":
    sim = Simulation(PARAMETERS)
    sim.planting()
    for i in range(10):
        sim.grow_plants()
        
        if (i + 1) % 100 == 0: 
            print(f"Iteration {i + 1}")
            for row in range(0, sim.parameters["length"], PARAMETERS["row-distance"]):
                for col in range(0, sim.parameters["width"], PARAMETERS["column-distance"]):
                    plant_info = sim.get_plant_info(row, col)
                    if plant_info:
                        print(f"Pflanze an Position ({row}, {col}): {plant_info}")
"""
Raeumliches wachstum in 3D mit numpy
Hoehenwachstum wird durch Pflanyenspeyifische Wahrscheinlichkeiten bestimmt, sodass Pflanzen in unterschiedlicher weise in die Hoehe wachsen
Um die aussenkante der Pflanze wird ein layer erstellt,in der die Pflanze wachsen koennte
Abbildung von Konkurenz: Wenn in einem moeglichen Kaestchen schon eine Pflanze ist, kann dort keine weitere Pflanze wachsen
Die Anzahl der Flaechen wird abhaengig von den schon vorhandenen Quadrate erstellt.
"""
def create_sphere_in_array(array, center, radius):
    x0, y0, z0 = center
    length, width, height = array.shape
    for x in range(length):
        for y in range(width):
            for z in range(height):
                if np.sqrt((x - x0)**2 + (y - y0)**2 + (z - z0)**2) <= radius:
                    array[x, y, z] = 1
    return array

