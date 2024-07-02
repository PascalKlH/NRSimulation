import numpy as np
import plotly.express as px

PARAMETERS = {
    "length": 30,
    "width": 60,
    "row-distance": 10,
    "column-distance": 10,
    "initial-water-layer": 0.5,
    "Plant": "lettuce"
}

class Crop:
    def __init__(self, name):
        self.name = name
        self.cells = []

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

        # Create meshgrid of indices and flatten them to index arrays
        row_grid, col_grid = np.meshgrid(row_indices, col_indices, indexing='ij')
        flat_rows = row_grid.flatten()
        flat_cols = col_grid.flatten()

        # Set plants_layer where plants are planted
        self.plants_layer[flat_rows, flat_cols] = 1

        # Create Crop objects where plants are planted
        crop_names = np.where(self.plants_layer == 1, self.parameters["Plant"], None)
        self.crops_layer = np.vectorize(Crop)(crop_names)

        # Print the name of the crop at each position where plants are planted
        plant_positions = np.argwhere(self.plants_layer == 1)
        for row, col in plant_positions:
            crop_name = self.crops_layer[row, col].name
            print(f"Crop at position ({row}, {col}): {crop_name}")

    def grow_plants(self):
        self.size_layer += self.water_layer * self.plants_layer  # let the plants grow depending on the water availabilities

    def fill_plant_cells(self):
        plant_positions = np.argwhere(self.plants_layer == 1)
        sizes = self.size_layer[plant_positions[:, 0], plant_positions[:, 1]].astype(int)
        
        max_size = sizes.max()
        
        # Create a grid of coordinates
        x, y, z = np.indices((max_size, max_size, max_size))
        
        # Calculate the distances from the center
        center = max_size // 2
        dist_from_center = np.sqrt((x - center) ** 2 + (y - center) ** 2 + (z - center) ** 2)
        
        for (row, col), size in zip(plant_positions, sizes):
            if size > 0:
                plant_cells = np.zeros((size, size, size))
                plant_cells[dist_from_center[:size, :size, :size] <= (size // 2)] = 1
                self.crops_layer[row, col].cells = plant_cells

    def get_plant_info(self, row, col):
        if self.plants_layer[row, col] == 1:  # check if a plant is planted at the given position
            size = self.size_layer[row, col]  # get the size of the plant at the given position
            water_availability = self.water_layer[row, col]  # get the water availability at the given position
            return {"size": size, "water_availability": water_availability}  # create a dictionary with the plant information
        return None

    def visualize_field(self):
        data = np.zeros((self.parameters["length"], self.parameters["width"]))

        for row in range(self.parameters["length"]):
            for col in range(self.parameters["width"]):
                if self.plants_layer[row, col] == 1:
                    crop = self.crops_layer[row, col]
                    if crop and crop.cells.size > 0:
                        # Project the 3D plant cells to 2D by taking the maximum along the z-axis
                        max_projection = crop.cells.max(axis=2)
                        data[row, col] = max_projection.max()

        fig = px.imshow(data, labels=dict(x="x", y="y", color="size"))
        fig.show()


if __name__ == "__main__":
    sim = Simulation(PARAMETERS)
    sim.planting()

    for i in range(10):
        sim.grow_plants()

    sim.fill_plant_cells()

    # Visualize the field using Plotly
    sim.visualize_field()
'''
Größe als farbe, höhe darstellen
Pixel der Pflanzen in einel layer darstellen
Wachstumrichtung der Pflanzen (Konkurenzd er Pflanzen)
kernel zur verschiebung der Boundery, um die konkurenz zu simulieren
'''