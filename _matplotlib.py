import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from threading import Timer
import webbrowser

PARAMETERS = {
    "length": 2000,
    "width": 2000,
    "row-distance": 20,
    "column-distance": 20,
    "initial-water-layer": 1,
    "Plant": "lettuce"
}

class Crop:
    def __init__(self, name):
        self.name = name
        self.cells = np.zeros((1, 1))
        self.boundary = np.zeros((1, 1))

    def grow_to_sides(self):
        rows, cols = self.cells.shape
        new_cells = np.zeros((rows + 2, cols + 2))
        new_boundary = np.zeros((rows + 2, cols + 2))
        
        new_cells[1:-1, 1:-1] = self.cells
        new_boundary[1:-1, 1:-1] = self.boundary

        self.cells = new_cells
        self.boundary = new_boundary

    @staticmethod
    def generate_circular_mask(size):
        center = size // 2
        y, x = np.ogrid[:size, :size]
        mask = (x - center) ** 2 + (y - center) ** 2 <= (center) ** 2
        return mask

class Simulation:
    def __init__(self, parameters):
        self.parameters = parameters
        self.size_layer = np.zeros((self.parameters["length"], self.parameters["width"]))
        self.water_layer = np.full((self.parameters["length"], self.parameters["width"]), self.parameters["initial-water-layer"])
        self.plants_layer = np.zeros((self.parameters["length"], self.parameters["width"]), dtype=bool)
        self.crops_layer = np.full((self.parameters["length"], self.parameters["width"]), None, dtype=object)
        self.iteration = 0

        self.app = Dash(__name__)
        self.app.layout = html.Div([
            html.H1("Plant Growth Simulation"),
            dcc.Graph(id="heatmap-graph"),
            dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
        ])

        self.planting()
        self.app.callback(Output('heatmap-graph', 'figure'), [Input('interval-component', 'n_intervals')])(self.animate_growth)

    def planting(self):
        row_indices = np.arange(0, self.parameters["length"], self.parameters["row-distance"])
        col_indices = np.arange(0, self.parameters["width"], self.parameters["column-distance"])

        # Create meshgrid of indices
        row_grid, col_grid = np.meshgrid(row_indices, col_indices, indexing='ij')

        # Flatten the meshgrid indices for proper broadcasting
        row_grid_flat = row_grid.flatten()
        col_grid_flat = col_grid.flatten()

        # Set plants_layer where plants are planted
        self.plants_layer[row_grid_flat, col_grid_flat] = True

        # Create Crop objects where plants are planted
        crop_names = np.full_like(self.plants_layer, None, dtype=object)
        crop_names[self.plants_layer] = self.parameters["Plant"]

        # Vectorize the creation of Crop objects
        crop_objects = np.vectorize(Crop)(crop_names[self.plants_layer])

        # Assign the Crop objects to the crops_layer
        self.crops_layer[row_grid_flat, col_grid_flat] = crop_objects

    def animate_growth(self, n):
        mean_size = int(np.mean(self.size_layer[self.plants_layer]))
        mask_size = mean_size * 2 + 1
        mask = Crop.generate_circular_mask(mask_size).astype(bool)

        crop_center_coords = np.argwhere(self.plants_layer)
        crop_center_rows, crop_center_cols = crop_center_coords[:, 0], crop_center_coords[:, 1]

        for r, c in zip(crop_center_rows, crop_center_cols):
            rs, re = max(0, r - mean_size), min(self.parameters["length"], r + mean_size + 1)
            cs, ce = max(0, c - mean_size), min(self.parameters["width"], c + mean_size + 1)

            mask_rs, mask_re = max(0, mean_size - r), mask_size - max(0, r + mean_size + 1 - self.parameters["length"])
            mask_cs, mask_ce = max(0, mean_size - c), mask_size - max(0, c + mean_size + 1 - self.parameters["width"])

            self.size_layer[rs:re, cs:ce] += mask[mask_rs:mask_re, mask_cs:mask_ce] * self.water_layer[r, c]

        colorscale = [
            [0.0, 'rgb(150,75,0)'],  #Brown for 0 values
            [0.1, 'rgb(0,255,0)'],   #Lighter green for smaller values
            [1.0, 'rgb(0,100,0)']    #Darker green for larger values
        ]

        fig = go.Figure(data=go.Heatmap(z=self.size_layer, colorscale=colorscale, zmin=0, zmax=np.max(self.size_layer)))
        #Format the plot in a square shape
        fig.update_layout(width=1000, height=1000)

        return fig

    def run(self):
        def open_browser():
            webbrowser.open_new('http://127.0.0.1:8050/')

        Timer(1, open_browser).start()
        self.app.run_server(debug=True)

if __name__ == "__main__":
    sim = Simulation(PARAMETERS)
    sim.run()
