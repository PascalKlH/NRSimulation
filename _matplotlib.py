import numpy as np
PARAMETERS = {
    "length": 50,
    "width": 100,
    "row-distance": 10,
    "column-distance": 10,
    "initial-water-layer": 0.5,
    "Plant": "lettuce"
}

class Crop:
    def __init__(self, name):
        self.name = name
        self.cells = []
        self.boundery = []

class Simulation:
    def __init__(self, parameters):
        self.parameters = parameters  # initializing the parameters
        self.size_layer = np.zeros((self.parameters["length"], self.parameters["width"]))  # create a grid for the plant sizes
        self.water_layer = np.full((self.parameters["length"], self.parameters["width"]), self.parameters["initial-water-layer"])  # create a grid for the water availabilities
        self.plants_layer = np.zeros((self.parameters["length"], self.parameters["width"]))  # create a grid for the plants
        self.crops_layer = np.full((self.parameters["length"], self.parameters["width"]), None, object)  # create a grid for the crops

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

    def grow_plants(self):
        self.size_layer += self.water_layer * self.plants_layer  # let the plants grow depending on the water availabilities
        

    def get_plant_info(self, row, col):
        if self.plants_layer[row, col] == 1:  # check if a plant is planted at the given position
            size = self.size_layer[row, col]  # get the size of the plant at the given position
            water_availability = self.water_layer[row, col]  # get the water availability at the given position
            return {"size": size, "water_availability": water_availability}  # create a dictionary with the plant information
        return None
    
if __name__ == "__main__":
    sim = Simulation(PARAMETERS)
    sim.planting()
    for i in range(10):
        sim.grow_plants()
   

   