import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from threading import Thread, Lock
import time
from datetime import datetime, timedelta
from scipy.ndimage import convolve
from plotly.subplots import make_subplots
import random
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count



PARAMETERS = {
    "length": 100,                      # length of the field
    "width": 100,                       # width of the field
    "row-distance": 30,                 # Distance between rows in cm
    "column-distance": 30,              # Distance between columns in cm
    "initial-water-layer": 1,           # Initial water layer in mm
    "Plant": "lettuce",                 # Name of the plant
    "start_date": datetime(2022, 1, 1), # Start date of the simulation
    "end_date": datetime(2022, 7, 1),   # End date of the simulation
    "W_max": 30,                        # Maximum Width in cm
    "H_max": 30,                        # Maximum height in cm
    "k": 0.001,                         # Growth rate
    "n": 2,                             # Shape parameter
    "max_moves": 5,                     # Maximum number of moves
    "Yield": 0.8,                       # Yield in kg
    "size_per_plant": 7068.3,           # Size per plant in cm^2
    "pattern": "alternating",                # Planting pattern(grid, alternating, random)

}

class Crop:
    def __init__(self, name, center, parameters, sim):
        self.name = name
        self.center = center
        self.radius = 0  # Initial radius is 0
        self.parameters = parameters
        self.sim = sim
        self.cells = np.zeros((self.parameters["W_max"] + 1, self.parameters["W_max"] + 1), dtype=bool)
        self.boundary = np.zeros((self.parameters["W_max"] + 3, self.parameters["W_max"] + 3), dtype=bool)
        self.moves = 0 # Number of moves
        self.overlap = 0 # Overlap with other plants
        self.pervious_growth = 0 # Growth rate of the previous hour

    def grow(self):
        current_time = self.sim.current_date
        t_diff_hours = (current_time - self.parameters["start_date"]).total_seconds() / 3600.0
        growth= self.parameters["k"] * (1 - self.overlap)* random.uniform(0.9, 1.1)
        growth_rate = self.parameters["H_max"] * self.parameters["n"] * (1 - np.exp(-growth * t_diff_hours))**(self.parameters["n"] - 1) * self.parameters["k"] * np.exp(-self.parameters["k"] * t_diff_hours)
        self.pervious_growth = growth_rate
        rounded_radius_before_growth = int(np.round(self.radius / 2))
        self.radius += growth_rate 
        rounded_radius = int(np.round(self.radius / 2))
        sim.water_layer[self.center] -= 0.1*growth_rate
        # If the radius is the same as before, we can simply add the growth rate to the circular mask
        if rounded_radius == rounded_radius_before_growth:
            mask = self.generate_circular_mask(rounded_radius)
            crop_mask = np.zeros_like(self.sim.size_layer, dtype=bool)
            
            r_start = max(self.center[0] - rounded_radius, 0)
            r_end = min(self.center[0] + rounded_radius + 1, self.sim.size_layer.shape[0])
            c_start = max(self.center[1] - rounded_radius, 0)
            c_end = min(self.center[1] + rounded_radius + 1, self.sim.size_layer.shape[1])
            
            mask_r_start = r_start - (self.center[0] - rounded_radius)
            mask_r_end = mask_r_start + (r_end - r_start)
            mask_c_start = c_start - (self.center[1] - rounded_radius)
            mask_c_end = mask_c_start + (c_end - c_start)
            
            crop_mask[r_start:r_end, c_start:c_end] = mask[mask_r_start:mask_r_end, mask_c_start:mask_c_end]
            np.add.at(self.sim.size_layer, np.where(crop_mask), growth_rate)
            return
        #move the plant if the max is not reached
        if self.moves < self.parameters["max_moves"]:
            r_min, r_max = self.center[0] - rounded_radius - 1, self.center[0] + rounded_radius + 2
            c_min, c_max = self.center[1] - rounded_radius - 1, self.center[1] + rounded_radius + 2
            # Check if the new position is within the boundaries of the field
            if 0 <= r_min < self.sim.size_layer.shape[0] and 0 <= r_max <= self.sim.size_layer.shape[0] and \
            0 <= c_min < self.sim.size_layer.shape[1] and 0 <= c_max <= self.sim.size_layer.shape[1]:

                snipped_size_layer = self.sim.size_layer[r_min:r_max, c_min:c_max]
                mask = np.where(snipped_size_layer > 0, 1, 0)
                
                snipped_cells = self.cells[
                    self.parameters["W_max"] // 2 - rounded_radius - 1:self.parameters["W_max"] // 2 + rounded_radius + 2,
                    self.parameters["W_max"] // 2 - rounded_radius - 1:self.parameters["W_max"] // 2 + rounded_radius + 2
                ]
                mask -= snipped_cells
                mask += self.boundary[
                    self.parameters["W_max"] // 2 - rounded_radius - 1:self.parameters["W_max"] // 2 + rounded_radius + 2,
                    self.parameters["W_max"] // 2 - rounded_radius - 1:self.parameters["W_max"] // 2 + rounded_radius + 2
                ]
   
                # Check if there is any overlap with other plants
                if np.any(mask > 1):
                    total_overlap = np.sum(mask > 1)
                    relative_overlap = total_overlap  / np.sum(self.boundary)
                    self.overlap = relative_overlap
                    coords_interference = np.where(mask > 1)
                    interference_centroid_x = np.mean(coords_interference[0])
                    interference_centroid_y = np.mean(coords_interference[1])
                    center_x, center_y = self.center

                    # Calculate the direction vector
                    direction_x = interference_centroid_x - center_x
                    direction_y = interference_centroid_y - center_y
                    norm = np.sqrt(direction_x**2 + direction_y**2)
                    # Normalize the direction vector
                    if norm != 0:
                        direction_x /= norm
                        direction_y /= norm

                    movement_x = int(round(-direction_x))
                    movement_y = int(round(-direction_y))
                    # Check if the movement is non-zero
                    if movement_x != 0 or movement_y != 0:
                        new_center_x, new_center_y = center_x + movement_x, center_y + movement_y

                        # Check if the new position is within the boundaries of the field
                        if 0 <= new_center_x < self.sim.size_layer.shape[0] and 0 <= new_center_y < self.sim.size_layer.shape[1]:
                            self.center = (new_center_x, new_center_y)
                            self.sim.plants_layer[center_x, center_y] = False
                            self.sim.plants_layer[new_center_x, new_center_y] = True
                            self.sim.crops_layer[center_x, center_y] = None
                            self.sim.crops_layer[new_center_x, new_center_y] = self
                            self.moves += 1

                            # Update cells and boundary to avoid self-interference
                            self.update_cells_and_boundary()

        mask = self.generate_circular_mask(rounded_radius)
        crop_mask = np.zeros_like(self.sim.size_layer, dtype=bool)
        
        r_start = max(self.center[0] - rounded_radius, 0)
        r_end = min(self.center[0] + rounded_radius + 1, self.sim.size_layer.shape[0])
        c_start = max(self.center[1] - rounded_radius, 0)
        c_end = min(self.center[1] + rounded_radius + 1, self.sim.size_layer.shape[1])
        
        mask_r_start = r_start - (self.center[0] - rounded_radius)
        mask_r_end = mask_r_start + (r_end - r_start)
        mask_c_start = c_start - (self.center[1] - rounded_radius)
        mask_c_end = mask_c_start + (c_end - c_start)
        
        crop_mask[r_start:r_end, c_start:c_end] = mask[mask_r_start:mask_r_end, mask_c_start:mask_c_end]
        np.add.at(self.sim.size_layer, np.where(crop_mask), growth_rate)
        # Update the cells and boundary
        if self.radius == 0:
            self.cells[self.parameters["W_max"] // 2, self.parameters["W_max"] // 2] = 1
        else:
            self.update_cells_and_boundary()

    def update_cells_and_boundary(self):
        '''
        Update the cells and boundary of the crop based on the current center and radius
        '''
        rounded_radius = int(np.round(self.radius / 2))
        mask = self.generate_circular_mask(rounded_radius)
        
        r_start = max(self.parameters["W_max"] // 2 - mask.shape[0] // 2, 0)
        r_end = min(r_start + mask.shape[0], self.cells.shape[0])
        c_start = max(self.parameters["W_max"] // 2 - mask.shape[1] // 2, 0)
        c_end = min(c_start + mask.shape[1], self.cells.shape[1])

        mask_r_start = 0 if r_start >= 0 else -r_start
        mask_r_end = mask.shape[0] if r_end <= self.cells.shape[0] else mask.shape[0] - (r_end - self.cells.shape[0])
        mask_c_start = 0 if c_start >= 0 else -c_start
        mask_c_end = mask.shape[1] if c_end <= self.cells.shape[1] else mask.shape[1] - (c_end - self.cells.shape[1])
        self.cells[r_start:r_end, c_start:c_end] = mask[mask_r_start:mask_r_end, mask_c_start:mask_c_end]
        self.boundary = convolve(self.cells, np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]), mode='constant', cval=0.0) ^ self.cells

    @staticmethod
    def generate_circular_mask(radius):
        '''
        Generate a circular mask with the given radius
        '''
        y, x = np.ogrid[-radius: radius + 1, -radius: radius + 1]
        mask = x**2 + y**2 <= radius**2
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
        self.df = pd.DataFrame(columns=["Date", "Yield", "Growth", "Water", "Overlap"])

    def planting(self, pattern=PARAMETERS["pattern"], num_plants=100):
        if pattern == 'grid':
            self._grid_planting()
        elif pattern == 'alternating':
            self._alternating_planting()
        elif pattern == 'random':
            self._random_planting(num_plants)

    def _grid_planting(self):
        '''
        Plant the crops in a grid pattern
        '''
        half_row_dist = self.parameters["W_max"] // 2
        half_col_dist = self.parameters["W_max"] // 2

        row_indices = np.arange(half_row_dist, self.parameters["length"] - half_row_dist, self.parameters["row-distance"])
        col_indices = np.arange(half_col_dist, self.parameters["width"] - half_col_dist, self.parameters["column-distance"])

        row_grid, col_grid = np.meshgrid(row_indices, col_indices, indexing='ij')
        self.plants_layer[row_grid, col_grid] = True

        crop_array = np.array([Crop(self.parameters["Plant"], (r, c), self.parameters, self) for r in row_indices for c in col_indices])
        self.crops_layer[row_grid, col_grid] = crop_array.reshape(row_grid.shape)

    def _alternating_planting(self):
        '''
        Plant the crops in an alternating pattern
        '''
        half_row_dist = self.parameters["W_max"] // 3
        half_col_dist = self.parameters["W_max"] // 3

        row_indices = np.arange(half_row_dist, self.parameters["length"] - half_row_dist, self.parameters["row-distance"])
        col_indices = np.arange(half_col_dist, self.parameters["width"] - half_col_dist, self.parameters["column-distance"])

        col_grid_odd = col_indices
        col_grid_even = col_indices + self.parameters["column-distance"] // 2
        col_grid_even = col_grid_even[col_grid_even < self.parameters["width"]]

        row_grid_odd = row_indices[::2]
        row_grid_even = row_indices[1::2]

        row_grid_odd, col_grid_odd = np.meshgrid(row_grid_odd, col_grid_odd, indexing='ij')
        row_grid_even, col_grid_even = np.meshgrid(row_grid_even, col_grid_even, indexing='ij')

        row_grid = np.concatenate((row_grid_odd.flatten(), row_grid_even.flatten()))
        col_grid = np.concatenate((col_grid_odd.flatten(), col_grid_even.flatten()))

        self.plants_layer[row_grid, col_grid] = True

        crop_array = np.array([Crop(self.parameters["Plant"], (r, c), self.parameters, self) for r, c in zip(row_grid, col_grid)])
        self.crops_layer[row_grid, col_grid] = crop_array

    def _random_planting(self, num_plants):
        '''
        Plant the crops in a random pattern
        '''
        total_cells = self.parameters["length"] * self.parameters["width"]
        all_positions = np.arange(total_cells)
        plant_positions = np.random.choice(all_positions, num_plants, replace=False)

        row_indices, col_indices = np.unravel_index(plant_positions, (self.parameters["length"], self.parameters["width"]))

        self.plants_layer[row_indices, col_indices] = True

        crop_array = np.array([Crop(self.parameters["Plant"], (r, c), self.parameters, self) for r, c in zip(row_indices, col_indices)])
        self.crops_layer[row_indices, col_indices] = crop_array
    def grow_plants(self):
        '''
        Grow the plants in parallel using multiple threads or processes to speed up the simulation
        '''
        with self.lock:
            # Extract crops that are present in the plants_layer
            crops = self.crops_layer[self.plants_layer]
            crop_list = np.ravel(crops)  # Flatten the array
            np.random.shuffle(crop_list)  # Shuffle the crop list

            # Function to grow plants in a specific subset
            def grow_subset(subset):
                for crop in subset:
                    crop.grow()

            # Split the crop list into approximately equal subsets
            num_cores = cpu_count()
            crop_subsets = np.array_split(crop_list, num_cores)

            # Execute the grow_subset function in parallel
            with ThreadPoolExecutor(max_workers=num_cores) as executor:
                futures = [executor.submit(grow_subset, subset) for subset in crop_subsets]
                for future in futures:
                    future.result()  # Wait for all threads to complete

            self.plot_update_flag = True

    def run_simulation(self):
        yield_per_size = self.parameters["Yield"] / self.parameters["size_per_plant"]
        
        # Start a timer to keep track of the simulation performance
        start_time = time.time()
        
        while self.current_date < self.parameters["end_date"]:
            self.grow_plants()
            self.current_date += timedelta(hours=1)
            #save all data in a dataframe as well as the date
            sum_grrowthrate = np.sum(self.crops_layer[r,c].pervious_growth for r in range(self.parameters["length"]) for c in range(self.parameters["width"]) if self.crops_layer[r,c] is not None)
            sum_overlap = np.sum(self.crops_layer[r,c].overlap for r in range(self.parameters["length"]) for c in range(self.parameters["width"]) if self.crops_layer[r,c] is not None)                 
            self.record_data(self.current_date, np.sum(self.size_layer), sum_grrowthrate,np.sum(self.water_layer),sum_overlap)        #save the dataframe in a csv file, called "data.csv"
        self.df.to_csv("data.csv")


        # Sum the size layer to get the total size of the plants and save it together with the current date
        sum_size = np.sum(self.size_layer)
        sum_yield = sum_size * yield_per_size
        print(f"Total size of the plants on {self.current_date}: {sum_yield}")
        
        # End the timer and print the time taken to run the simulation
        end_time = time.time()
        
        # Calculate the time per plant
        time_per_plant = (end_time - start_time) / np.sum(self.plants_layer)
        
        # Then divide by the number of days
        time_per_plant /= (self.parameters["end_date"] - self.parameters["start_date"]).days
        print(f"Time taken to run the simulation, per day and plant: {time_per_plant:.6f} seconds")

        

    def record_data(self, date, yield_value, growth_value,water_value,overlap_value):
        new_row = pd.DataFrame({"Date": [date], "Yield": [yield_value], "Growth": [growth_value], "Water": [water_value], "Overlap": [overlap_value]})
        self.df = pd.concat([self.df, new_row], ignore_index=True)


if __name__ == "__main__":
    sim = Simulation(PARAMETERS)
    sim.planting()
    sim.run_simulation()
