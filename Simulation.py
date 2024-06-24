import numpy as np

PARAMETERS = {
    "length": 100,
    "width": 200,
    "row-distance": 2,
    "column-distance": 3,
    "initial-water-layer": 0.5,
}

class Simulation:
    def __init__(self, parameters):
        self.parameters = parameters
        self.num_rows = self.parameters["length"] // self.parameters["row-distance"]
        self.num_cols = self.parameters["width"] // self.parameters["column-distance"]
        self.size_layer = np.zeros((self.num_rows, self.num_cols))
        self.water_layer = np.random.rand(self.parameters["length"], self.parameters["width"]) * self.parameters["initial-water-layer"]
        self.plants_layer = np.zeros((self.parameters["length"], self.parameters["width"]))
        
        self.planting()
    
    def planting(self):
        # Calculate indices in reduced grid
        row_indices = np.arange(0, self.num_rows) * self.parameters["row-distance"]
        col_indices = np.arange(0, self.num_cols) * self.parameters["column-distance"]
        row_grid, col_grid = np.meshgrid(row_indices, col_indices, indexing='ij')
        
        # Set plant locations in original layer
        self.plants_layer[row_grid, col_grid] = 1
        
        # Set initial size for planted positions
    
    def grow_plants(self):
        # Get indices of plant positions
        plant_indices = np.where(self.plants_layer == 1)
        water_availabilities = self.water_layer[plant_indices]
        
        # Update plant sizes based on water availability
        self.size_layer[plant_indices[0] // self.parameters["row-distance"], plant_indices[1] // self.parameters["column-distance"]] += 1 * water_availabilities



    def get_plant_info(self, row, col):
        # Calculate indices based on row and column distances
        row_idx = row // self.parameters["row-distance"]
        col_idx = col // self.parameters["column-distance"]
        
        # Check bounds for reduced grid
        if row_idx < self.num_rows and col_idx < self.num_cols:
            size = self.size_layer[row_idx, col_idx]
            # Calculate original indices for water_layer
            orig_row_idx = row_idx * self.parameters["row-distance"]
            orig_col_idx = col_idx * self.parameters["column-distance"]
            if orig_row_idx < self.parameters["length"] and orig_col_idx < self.parameters["width"]:
                water_availability = self.water_layer[orig_row_idx, orig_col_idx]
                return {"size": size, "water_availability": water_availability}
        return None
    
if __name__ == "__main__":
    sim = Simulation(PARAMETERS)
    
    for i in range(1000):
        sim.grow_plants()
        
        # Print plant information at specified intervals
        if (i + 1) % 100 == 0:  # Print every 100 iterations
            print(f"Iteration {i + 1}")
            for row in range(0, sim.parameters["length"], PARAMETERS["row-distance"]):
                for col in range(0, sim.parameters["width"], PARAMETERS["column-distance"]):
                    plant_info = sim.get_plant_info(row, col)
                    if plant_info:
                        print(f"Pflanze an Position ({row}, {col}): {plant_info}")
