import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import webbrowser
from threading import Thread, Lock
import time
from datetime import datetime, timedelta
from scipy.ndimage import convolve

PARAMETERS = {
    "length": 600,
    "width": 60,
    "row-distance": 30,
    "column-distance": 30,
    "initial-water-layer": 1,
    "Plant": "lettuce",
    "start_date": datetime(2022, 1, 1),
    "end_date": datetime(2022, 12, 31),
    "W_max": 30,  # Maximum Width in cm
    "H_max": 30,  # Maximum height in cm
    "k": 0.1,  # Growth rate
    "n": 2  # Shape parameter
}

class Crop:
    def __init__(self, name, center):
        self.name = name
        self.center = center  # Store the center of the plant
        self.cells = np.array([center])
        self.boundary_cells = np.array([center])

    def update_cells(self, new_cells):
        self.cells = np.vstack([self.cells, new_cells])
        self.update_boundary()

    def update_boundary(self):
        crop_size_layer = np.zeros_like(sim.size_layer)
        crop_size_layer[self.cells[:, 0], self.cells[:, 1]] = 1

        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])

        neighbors = convolve(crop_size_layer, kernel, mode='constant', cval=0)
        boundary_mask = (neighbors > 0) & (crop_size_layer == 0)

        boundary_cells_indices = np.argwhere(boundary_mask)
        self.boundary_cells = boundary_cells_indices

    def grow(self):
        if len(self.cells) == 1:
            if sim.water_layer[self.cells[0, 0], self.cells[0, 1]] >= 0.9:
                r, c = self.center
                mask = self.generate_circular_mask(1)
                new_cells = np.argwhere(mask) + [r - 1, c - 1]
                new_cells = new_cells[
                    (new_cells[:, 0] >= 0) & (new_cells[:, 0] < sim.size_layer.shape[0]) & 
                    (new_cells[:, 1] >= 0) & (new_cells[:, 1] < sim.size_layer.shape[1])
                ]
                new_cells = np.unique(new_cells, axis=0)
                sim.size_layer[new_cells[:, 0], new_cells[:, 1]] = 0.1
                self.update_cells(new_cells)
        else:
            if not self.boundary_cells.size:
                return

            current_time = sim.current_date
            t_diff_hours = (current_time - PARAMETERS["start_date"]).total_seconds() / 3600.0

            growth_rate = PARAMETERS["H_max"] * PARAMETERS["n"] * (1 - np.exp(-PARAMETERS["k"] * t_diff_hours))**(PARAMETERS["n"] - 1) * PARAMETERS["k"] * np.exp(-PARAMETERS["k"] * t_diff_hours)
            sim.size_layer[self.cells[:, 0], self.cells[:, 1]] += growth_rate
            
            self.update_boundary()
            boundary_cells_indices = self.boundary_cells

            if not boundary_cells_indices.size:
                return

            plant_width = np.max(self.cells[:, 1]) - np.min(self.cells[:, 1]) + 1
            if plant_width >= PARAMETERS["W_max"]:
                return

            average_size = np.mean(sim.size_layer[self.cells[:, 0], self.cells[:, 1]])
            if average_size > 0.9:
                new_boundary_cells = []
                for r, c in boundary_cells_indices:
                    mask = self.generate_circular_mask(1)
                    new_cells = np.argwhere(mask) + [r - 1, c - 1]
                    new_cells = new_cells[
                        (new_cells[:, 0] >= 0) & (new_cells[:, 0] < sim.size_layer.shape[0]) & 
                        (new_cells[:, 1] >= 0) & (new_cells[:, 1] < sim.size_layer.shape[1])
                    ]
                    new_cells = np.unique(new_cells, axis=0)
                    new_cells = self.avoid_interference(new_cells)
                    sim.size_layer[new_cells[:, 0], new_cells[:, 1]] = 0.1
                    new_boundary_cells.extend(new_cells)
                self.update_cells(np.array(new_boundary_cells))

    def avoid_interference(self, new_cells):
        adjusted_cells = []
        for r, c in new_cells:
            if sim.crops_layer[r, c] is None:
                adjusted_cells.append([r, c])
            else:
                # Adjust cells to avoid interference
                adjusted_r, adjusted_c = self.adjust_growth_cell(r, c)
                if 0 <= adjusted_r < sim.size_layer.shape[0] and 0 <= adjusted_c < sim.size_layer.shape[1]:
                    adjusted_cells.append([adjusted_r, adjusted_c])
        
        return np.array(adjusted_cells)

    def adjust_growth_cell(self, r, c):
        # Adjust the position of the new cell to avoid overlap based on the direction
        if c < self.center[1]:  # If interference is on the left, grow right
            return r, c + 1
        elif c > self.center[1]:  # If interference is on the right, grow left
            return r, c - 1
        elif r < self.center[0]:  # If interference is above, grow down
            return r + 1, c
        else:  # If interference is below, grow up
            return r - 1, c

    @staticmethod
    def generate_circular_mask(radius):
        diameter = 2 * radius + 1
        center = radius
        y, x = np.ogrid[:diameter, :diameter]
        mask = (x - center) ** 2 + (y - center) ** 2 <= radius ** 2
        return mask

class Simulation:
    def __init__(self, parameters):
        self.parameters = parameters
        self.size_layer = np.zeros((self.parameters["length"], self.parameters["width"]))
        self.water_layer = np.full((self.parameters["length"], self.parameters["width"]), self.parameters["initial-water-layer"])
        self.plants_layer = np.zeros((self.parameters["length"], self.parameters["width"]), dtype=bool)
        self.crops_layer = np.full((self.parameters["length"], self.parameters["width"]), None, dtype=object)
        self.lock = Lock()
        self.current_date = self.parameters["start_date"]
        self.running = True
        self.plot_update_flag = False

    def planting(self):
        half_row_dist = self.parameters["row-distance"] // 2
        half_col_dist = self.parameters["column-distance"] // 2

        row_indices = np.arange(half_row_dist, self.parameters["length"] - half_row_dist, self.parameters["row-distance"])
        col_indices = np.arange(half_col_dist, self.parameters["width"] - half_col_dist, self.parameters["column-distance"])

        row_grid, col_grid = np.meshgrid(row_indices, col_indices, indexing='ij')
        row_grid_flat = row_grid.flatten()
        col_grid_flat = col_grid.flatten()

        self.plants_layer[row_grid_flat, col_grid_flat] = True

        for r, c in zip(row_grid_flat, col_grid_flat):
            center = (r, c)
            self.crops_layer[r, c] = Crop(self.parameters["Plant"], center)
            self.crops_layer[r, c].update_cells(np.array([[r, c]]))

    def grow_plants(self):
        with self.lock:
            unique_crops = set(self.crops_layer[self.plants_layer].flat)
            for crop in unique_crops:
                if crop is not None:
                    crop.grow()

            self.plot_update_flag = True

    def run_simulation(self):
        while self.current_date < self.parameters["end_date"]:
            self.grow_plants()
            self.current_date += timedelta(hours=1)
            self.plot_update_flag = True
            time.sleep(1)

def create_app(sim):
    app = Dash(__name__)

    colorscale = [
        [0.0, 'rgb(150,75,0)'],# Brown for the soil
        [0.1, 'rgb(190,255,128)'],# light green for the small plants
        [1.0, 'rgb(21,128,0)']   # Dark green for the big plants
    ]

    fig = go.Figure(data=go.Heatmap(z=sim.size_layer, colorscale=colorscale, zmin=0, zmax=np.max(sim.size_layer)))
    fig.update_layout(title=str(sim.current_date), xaxis_title='Width', yaxis_title='Length')
    fig.update_layout(width=2000, height=2000)

    app.layout = html.Div([
        dcc.Graph(id='heatmap', figure=fig),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,
            n_intervals=0
        )
    ])

    @app.callback(
        Output('heatmap', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_heatmap(n):
        if sim.plot_update_flag:
            with sim.lock:
                fig.data[0].z = sim.size_layer.copy()
                fig.data[0].zmax = np.max(sim.size_layer)
                fig.update_layout(title=str(sim.current_date))
                sim.plot_update_flag = False
        return fig

    return app

if __name__ == "__main__":
    sim = Simulation(PARAMETERS)
    sim.planting()

    app = create_app(sim)

    def run_server():
        #webbrowser.open_new('http://127.0.0.1:8050/')
        app.run_server(debug=True, use_reloader=False)

    server_thread = Thread(target=run_server)
    server_thread.start()

    sim.run_simulation()