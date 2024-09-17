import numpy as np
import pandas as pd
from threading import Lock
import time
from datetime import datetime, timedelta
from scipy.ndimage import convolve
import random
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

class Crop:
    def __init__(self, name, center, parameters, sim):
        self.name = name
        self.center = center
        self.radius = 0  # Initial radius is 0
        self.parameters = parameters
        self.sim = sim
        self.cells = np.zeros((self.parameters["W_max"] + self.parameters["max_moves"], self.parameters["W_max"] + self.parameters["max_moves"]), dtype=bool) 
        self.boundary = np.zeros((self.parameters["W_max"] + 3, self.parameters["W_max"] + 3), dtype=bool) 
        self.moves = 0 # Number of moves
        self.overlap = 0 # Overlap with other plants
        self.previous_growth = 0 # Growth rate of the previous hour

    def grow(self,size_layer,obj_layer,pos_layer):
        current_time = self.sim.current_date
        t_diff_hours = (current_time - datetime.strptime(self.sim.date, '%Y-%m-%d:%H:%M:%S')).total_seconds() / (3600.0)
        growth= self.parameters["k"] * (1 - self.overlap)* random.uniform(0.9, 1.1)
        growth_rate = self.parameters["H_max"] * self.parameters["n"] * (1 - np.exp(-growth * t_diff_hours))**(self.parameters["n"] - 1) * self.parameters["k"] * np.exp(-self.parameters["k"] * t_diff_hours)*self.sim.stepsize
        self.previous_growth = growth_rate
        rounded_radius_before_growth = int(np.round(self.radius / 2))
        self.radius += growth_rate 
        rounded_radius = int(np.round(self.radius / 2))
        self.sim.water_layer[self.center] -= 0.1*growth_rate
        # If the radius is the same as before, we can simply add the growth rate to the circular mask
        if rounded_radius == rounded_radius_before_growth:
            mask = self.generate_circular_mask(rounded_radius)
            crop_mask = np.zeros_like(size_layer, dtype=bool)

            # Check if the mask is within the boundaries of the field
            r_start =int(max(self.center[0] - rounded_radius, 0))
            r_end = int(min(self.center[0] + rounded_radius + 1, size_layer.shape[0]))
            c_start = int(max(self.center[1] - rounded_radius, 0))
            c_end = int(min(self.center[1] + rounded_radius + 1, size_layer.shape[1]))

            # Check if the mask is within the boundaries of the field
            mask_r_start = int(r_start - (self.center[0] - rounded_radius))
            mask_r_end = int(mask_r_start + (r_end - r_start))
            mask_c_start = int(c_start - (self.center[1] - rounded_radius))
            mask_c_end = int(mask_c_start + (c_end - c_start))

            # Add the mask to the crop mask
            crop_mask[r_start:r_end, c_start:c_end] = mask[mask_r_start:mask_r_end, mask_c_start:mask_c_end]
            np.add.at(size_layer, np.where(crop_mask), growth_rate)
            return
        #move the plant if the max is not reached
        if self.moves < self.parameters["max_moves"]:
            
            r_min, r_max = int(self.center[0] - rounded_radius - 1), int(self.center[0] + rounded_radius + 2)
            c_min, c_max = int(self.center[1] - rounded_radius - 1), int(self.center[1] + rounded_radius + 2)
            # Check if the new position is within the boundaries of the field
            if 0 <= r_min < size_layer.shape[0] and 0 <= r_max <= size_layer.shape[0] and \
            0 <= c_min < size_layer.shape[1] and 0 <= c_max <= size_layer.shape[1]:
                # Create a slice of the size_layer to check for overlap
                #snpi the crop out of the size_layer to get just the crop
                snipped_size_layer = size_layer[r_min:r_max, c_min:c_max]
                mask = np.where(snipped_size_layer > 0, 1, 0)
                # Create a slice of the crop mask to check for overlap
                snipped_cells = self.cells[
                    self.parameters["W_max"] // 2 - rounded_radius - 1:self.parameters["W_max"] // 2 + rounded_radius + 2,
                    self.parameters["W_max"] // 2 - rounded_radius - 1:self.parameters["W_max"] // 2 + rounded_radius + 2
                ]
                # Subtract the cells of the current crop to avoid self-interference
                mask -= snipped_cells
                # Add the mask to the crop mask
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
                    # Round the direction to the nearest integer
                    movement_x = round(int(-direction_x))
                    movement_y = round(int(-direction_y))
                    # Check if the movement is non-zero
                    if movement_x != 0 or movement_y != 0:
                        # Calculate the new center position
                        new_center_x, new_center_y = center_x + movement_x, center_y + movement_y

                        # Check if the new position is within the boundaries of the field
                        if 0 <= new_center_x < size_layer.shape[0] and 0 <= new_center_y < size_layer.shape[1]:
                            self.center = (new_center_x, new_center_y)      #update the cenetr of the crop
                            pos_layer[center_x, center_y] = False           #delete the old position of the crop in the pos_layer
                            pos_layer[new_center_x, new_center_y] = True    #update the position of the crop in the pos_layer
                            obj_layer[center_x, center_y] = None            #delete the old object of the crop in the obj_layer
                            obj_layer[new_center_x, new_center_y] = self    #update the object of the crop in the obj_layer
                            self.moves += 1

                            # Update cells and boundary to avoid self-interference
                            self.update_cells_and_boundary()
        # create a mask of the current plant
        mask = self.generate_circular_mask(rounded_radius)
        #create an empty array of the size of the field to add the current plant on the right position to it
        crop_mask = np.zeros_like(size_layer, dtype=bool)
        # Check if the plant is within the boundaries of the field
        r_start = int(max(self.center[0] - rounded_radius, 0))
        r_end = int(min(self.center[0] + rounded_radius + 1, size_layer.shape[0]))
        c_start = int(max(self.center[1] - rounded_radius, 0))
        c_end = int(min(self.center[1] + rounded_radius + 1, size_layer.shape[1]))
        # Check if the mask is within the boundaries of the field
        mask_r_start = int(r_start - (self.center[0] - rounded_radius))
        mask_r_end = int(mask_r_start + (r_end - r_start))
        mask_c_start = int(c_start - (self.center[1] - rounded_radius))
        mask_c_end = int(mask_c_start + (c_end - c_start))
        #apply the mask to the crop mask array to get the current plant on the right position
        crop_mask[r_start:r_end, c_start:c_end] = mask[mask_r_start:mask_r_end, mask_c_start:mask_c_end]
        #add the current growthrate to the new fields of the plant
        np.add.at(size_layer, np.where(crop_mask), growth_rate)
        # Update the cells and boundary
        if self.radius == 0:
            #set the inital cell of the plant to 1
            self.cells[self.parameters["W_max"] // 2, self.parameters["W_max"] // 2] = 1
        else:
            self.update_cells_and_boundary()

    def update_cells_and_boundary(self):
        '''
        Update the cells and boundary of the crop based on the current center and radius

        '''
        #print("before")
        #print(self.cells)
        rounded_radius = int(np.round(self.radius / 2))
        mask = self.generate_circular_mask(rounded_radius)
        # Reset the cells and boundary
        r_start = max(self.parameters["W_max"] // 2 - mask.shape[0] // 2, 0)
        r_end = min(r_start + mask.shape[0], self.cells.shape[0])
        c_start = max(self.parameters["W_max"] // 2 - mask.shape[1] // 2, 0)
        c_end = min(c_start + mask.shape[1], self.cells.shape[1])
        # Check if the mask is within the boundaries of the field
        mask_r_start = 0 if r_start >= 0 else -r_start
        mask_r_end = mask.shape[0] if r_end <= self.cells.shape[0] else mask.shape[0] - (r_end - self.cells.shape[0])
        mask_c_start = 0 if c_start >= 0 else -c_start
        mask_c_end = mask.shape[1] if c_end <= self.cells.shape[1] else mask.shape[1] - (c_end - self.cells.shape[1])
        # Add the mask to the cells
        self.cells[r_start:r_end, c_start:c_end] = mask[mask_r_start:mask_r_end, mask_c_start:mask_c_end]
        # Update the boundary using a convolution
        self.boundary = convolve(self.cells, np.array([[0, 1, 0],
                                                       [1, 0, 1],
                                                       [0, 1, 0]]),
                                                                     mode='constant', cval=0.0) ^ self.cells


       # Ensure r_min, r_max, c_min, c_max are within valid range
        r_min = int(max(self.center[0] - rounded_radius - 1, 0))
        r_max = int(min(self.center[0] + rounded_radius + 2, self.sim.boundary_layer.shape[0]))
        c_min = int(max(self.center[1] - rounded_radius - 1, 0))
        c_max = int(min(self.center[1] + rounded_radius + 2, self.sim.boundary_layer.shape[1]))

        # Check if the boundary expands outside the array
        if r_min == 0 or r_max == self.sim.boundary_layer.shape[0] or c_min == 0 or c_max == self.sim.boundary_layer.shape[1]:
            return

        # Create a slice of the boundary array to assign
        new_boundary_slice = self.boundary[
            self.parameters["W_max"] // 2 - rounded_radius - 1:self.parameters["W_max"] // 2 + rounded_radius + 2,
            self.parameters["W_max"] // 2 - rounded_radius - 1:self.parameters["W_max"] // 2 + rounded_radius + 2
        ]

        # Add the new boundary slice to the existing boundary_layer
        self.sim.boundary_layer[r_min:r_max, c_min:c_max] += new_boundary_slice.astype(int)
        #print("after")
        #print(self.cells)




    @staticmethod
    def generate_circular_mask(radius):
        '''
        Generate a circular mask with the given radius.
        '''
        y, x = np.ogrid[-radius: radius + 1, -radius: radius + 1]
        mask = x**2 + y**2 <= radius**2
        return mask


class Simulation:
    def __init__(self, input_data):
        length = int(input_data["rowLength"])
        self.input_data = input_data
        self.total_width = int(sum(row['stripWidth'] for row in input_data['rows']))
        self.water_layer = np.full((length, self.total_width), 0.5, dtype=float)
        self.crop_size_layer = np.zeros((length, self.total_width), dtype=float)
        self.crops_pos_layer = np.zeros((length, self.total_width), dtype=bool)
        self.crops_obj_layer = np.full((length, self.total_width), None, dtype=object)
        self.boundary_layer = np.zeros((length, self.total_width), dtype=int)
        self.weeds_size_layer = np.zeros((length, self.total_width), dtype=float)
        self.weeds_obj_layer = np.full((length, self.total_width),None, dtype=object)
        self.weeds_pos_layer = np.zeros((length, self.total_width), dtype=bool)
        self.lock = Lock()
        #add hours to the current date
        self.date= input_data["startDate"]+":00:00:00"
        self.current_date = datetime.strptime(self.date, '%Y-%m-%d:%H:%M:%S')
        self.running = True
        self.plot_update_flag = False
        self.df = pd.DataFrame(columns=["Date","Yield", "Growth", "Water", "Overlap","Map","Boundary","Weed"])
        self.stepsize= int(input_data["stepSize"])

    def planting(self):
        current_col = 0
        plant_parameters_map = {
            'lettuce': lettuce,
            'cabbage': cabbage,
            'spinach': spinach,
        }
        for row in self.input_data['rows']:
            strip_width = row['stripWidth']
            start_col = current_col
            end_col = current_col + strip_width
            plant_parameters = plant_parameters_map.get(row['plantType'], None)
            if plant_parameters is None:
                raise ValueError(f"Unknown plant type: {row['plantType']}")

            strip_parameters = {
                "plantType": plant_parameters,
                "plantingType": row['plantingType'],
                "rowDistance": row['rowSpacing'],
                "columnDistance": strip_width,
                "rowLength": self.input_data['rowLength'],
            }

            if strip_parameters["plantingType"] == 'grid':
                self._grid_planting(strip_parameters, start_col, end_col,row,plant_parameters)
            elif strip_parameters["plantingType"] == 'alternating':
                self._alternating_planting(strip_parameters, start_col, end_col,row,plant_parameters)
            elif strip_parameters["plantingType"] == 'random':
                self._random_planting(strip_parameters, start_col, end_col, row,plant_parameters)
            elif strip_parameters["plantingType"] == 'empty':
                self._empty_planting()
            current_col += strip_width
    def _empty_planting(self):     
        pass
    def _grid_planting(self, strip_parameters, start_col, end_col,row,plantparameters):
        plant_distance = strip_parameters["rowDistance"]###Space between plants
        row_length = strip_parameters["rowLength"]  ###länge der Reihe

        # Calculate offsets
        offset = plant_distance // 2
 

        # Adjust indices to ensure plants are not on the edges
        row_start = offset
        row_end = row_length - offset
        col_start = start_col + offset
        col_end = end_col - offset

        # Generate grid indices with adjusted bounds
        row_indices = np.arange(row_start, row_end, plant_distance)
        col_indices = np.arange(col_start, col_end, plant_distance)

        row_grid, col_grid = np.meshgrid(row_indices, col_indices, indexing='ij')

        self.crops_pos_layer[row_grid, col_grid] = True
        crop_array = np.array([Crop(row["plantType"], (r, c), plantparameters, self)
                            for r in row_indices for c in col_indices])
        self.crops_obj_layer[row_grid, col_grid] = crop_array.reshape(row_grid.shape)

    def _alternating_planting(self, strip_parameters, start_col, end_col,row,plant_parameters):
        '''
        Plant the crops in an alternating pattern
        '''
        row_distance = strip_parameters["rowDistance"]
        column_distance = strip_parameters["columnDistance"]
        row_length = strip_parameters["rowLength"]

        half_row_dist = row_distance // 3
        # Create grid indices for odd and even rows
        row_indices = np.arange(half_row_dist, row_length, row_distance)
        col_indices_odd = np.arange(start_col, end_col, column_distance)
        col_indices_even = col_indices_odd + column_distance // 2

        # Clip the indices to stay within bounds
        col_indices_even = col_indices_even[col_indices_even < end_col]

        # Create masks for alternating rows
        row_grid_odd = row_indices[::2]
        row_grid_even = row_indices[1::2]

        # Apply planting
        row_grid_odd, col_grid_odd = np.meshgrid(row_grid_odd, col_indices_odd, indexing='ij')
        row_grid_even, col_grid_even = np.meshgrid(row_grid_even, col_indices_even, indexing='ij')

        # Place plants
        self.crops_pos_layer[row_grid_odd, col_grid_odd] = True
        self.crops_pos_layer[row_grid_even, col_grid_even] = True

        # Vectorized crop placement
        self.crops_obj_layer[row_grid_odd, col_grid_odd] = np.vectorize(lambda r, c: Crop(row['plantType'], (r, c), plant_parameters, self))(row_grid_odd, col_grid_odd)
        self.crops_obj_layer[row_grid_even, col_grid_even] = np.vectorize(lambda r, c: Crop(row['plantType'], (r, c), plant_parameters, self))(row_grid_even, col_grid_even)


    def _random_planting(self, strip_parameters, start_col, end_col,row,plant_parameters):
        '''
        Plant the crops in a random pattern
        '''
        num_plants = int(strip_parameters['columnDistance'] * strip_parameters["rowLength"] / strip_parameters['rowDistance'])
        total_positions = strip_parameters["rowLength"] * (end_col - start_col)
        
        # Randomly select positions within the strip
        plant_positions = np.random.choice(total_positions, num_plants, replace=False)
        row_indices, col_indices = np.unravel_index(plant_positions, (strip_parameters["rowLength"], end_col - start_col))
        col_indices += start_col  # Adjust column indices based on the strip's starting position

        # Place plants
        self.crops_pos_layer[row_indices, col_indices] = True
        self.crops_obj_layer[row_indices, col_indices] = np.vectorize(lambda r, c: Crop(row['plantType'], (r, c), plant_parameters, self))(row_indices, col_indices)

    def grow_weeds(self):
        '''
        Grow the weeds in parallel using multiple threads or processes to speed up the simulation
        '''
        with self.lock:
            # Extract weeds that are present in the weeds_layer

            weeds = self.weeds_obj_layer[self.weeds_pos_layer] 
            if len(weeds) > 0:
                
                weed_list = np.ravel(weeds)
                np.random.shuffle(weed_list)
                def grow_subset(subset):
                    for weed in subset:
                        weed.grow(self.weeds_size_layer,self.weeds_obj_layer,self.weeds_pos_layer)
                num_cores = cpu_count()
                weed_subsets = np.array_split(weed_list, num_cores)
                with ThreadPoolExecutor(max_workers=num_cores) as executor:
                    futures = [executor.submit(grow_subset, subset) for subset in weed_subsets]
                    for future in futures:
                        future.result()
            weed_x = np.random.randint(0, self.crop_size_layer.shape[0], 1)
            weed_y = np.random.randint(0, self.crop_size_layer.shape[1], 1)
            size_at_spot = self.crop_size_layer[weed_x, weed_y]
            random = np.random.uniform(0, (24+size_at_spot)/self.stepsize, 1)
            if random <=0.2:
                self.weeds_pos_layer[weed_x, weed_y] = True
                self.weeds_obj_layer[weed_x, weed_y] = Crop("weed", (weed_x, weed_y),weed, self)




#

    def grow_plants(self):
        '''
        Grow the plants in parallel using multiple threads or processes to speed up the simulation
        '''
        #rainfall = weather_data[0][7]
        #self.water_layer += rainfall

        with self.lock:
            # Extract crops that are present in the plants_layer
            crops = self.crops_obj_layer[self.crops_pos_layer]
            crop_list = np.ravel(crops)  # Flatten the array
            np.random.shuffle(crop_list)  # Shuffle the crop list

            # Function to grow plants in a specific subset
            def grow_subset(subset):
                for crop in subset:
                    crop.grow(self.crop_size_layer,self.crops_obj_layer,self.crops_pos_layer)

            # Split the crop list into approximately equal subsets
            num_cores = cpu_count()
            crop_subsets = np.array_split(crop_list, num_cores)

            # Execute the grow_subset function in parallel
            with ThreadPoolExecutor(max_workers=num_cores) as executor:
                futures = [executor.submit(grow_subset, subset) for subset in crop_subsets]
                for future in futures:
                    future.result()  # Wait for all threads to complete



    def run_simulation(self):

        yield_per_size = 0.8 / 7068.3
        
        # Start a timer to keep track of the simulation performance
        start_time = time.time()
        
        while self.current_date < datetime.strptime("2022-12-02:00:00:00", '%Y-%m-%d:%H:%M:%S'):
            self.grow_plants()
            self.grow_weeds()
            self.plot_update_flag = True
            # Save all data in a dataframe as well as the date
            sum_growthrate = sum(self.crops_obj_layer[r, c].previous_growth for r in range(self.input_data["rowLength"]) for c in range(self.total_width) if self.crops_obj_layer[r, c] is not None)
            sum_overlap = sum(self.crops_obj_layer[r, c].overlap for r in range(self.input_data["rowLength"]) for c in range(self.total_width) if self.crops_obj_layer[r, c] is not None)
            # Convert size_layer to a list
            crop_size_layer_list = self.crop_size_layer.tolist()
            weed_size_layer_list = self.weeds_size_layer.tolist()
            #take the boundary out of the crop object and and place it on the field where it belongs, use the plants layer to determine where the plants are to create a boundary_layer
            boundary_list = self.boundary_layer.tolist()

            
            self.record_data(self.current_date, np.sum(self.crop_size_layer), sum_growthrate, np.sum(self.water_layer), sum_overlap, crop_size_layer_list,boundary_list,weed_size_layer_list)        
            self.current_date += timedelta(hours=self.stepsize)

        # Sum the size layer to get the total size of the plants and save it together with the current date
        sum_size = np.sum(self.crop_size_layer)
        sum_yield = sum_size * yield_per_size
        print(f"Total yield: {sum_yield:.2f}")
        
        # End the timer and print the time taken to run the simulation
        end_time = time.time()
        
        # Calculate the time per plant
        time_per_plant = (end_time - start_time) / np.sum(self.crops_pos_layer)
        date= self.input_data["startDate"]+":00:00:00"
        start_date = datetime.strptime(date, '%Y-%m-%d:%H:%M:%S')
        # Then divide by the number of days
        time_per_plant /= (datetime.strptime("2022-12-02:00:00:00", '%Y-%m-%d:%H:%M:%S') - start_date).days
        print(f"Time taken to run the simulation, per day and plant: {time_per_plant:.6f} seconds")


        

    def record_data(self, date, size, growth_rate, water_level, overlap, size_layer,boundary,weed_size_layer):
        new_row = pd.DataFrame([[date, size, growth_rate, water_level, overlap, size_layer,boundary,weed_size_layer]], columns=self.df.columns)
        self.df = pd.concat([self.df, new_row], ignore_index=True)




def main(input_data):
    sim = Simulation(input_data)
    sim.planting()
    sim.run_simulation()
    # Convert the DataFrame columns to lists for serialization
    data = {
        "time": sim.df["Date"].tolist(),
        "yield": sim.df["Yield"].tolist(),
        "growth": sim.df["Growth"].tolist(),
        "water": sim.df["Water"].tolist(),
        "overlap": sim.df["Overlap"].tolist(),
        "map": sim.df["Map"].tolist(),
        "boundary": sim.df["Boundary"].tolist(),
        "weed": sim.df["Weed"].tolist(),
    }
    #save the last instance of the simulation in the db
    index_of_last_instance = len(sim.df)-1
    last_instance = sim.df.iloc[index_of_last_instance]
    return data, last_instance

lettuce = {
        "name": "lettuce",
        "W_max": 30,
        "H_max": 30,
        "k": 0.001,
        "n": 2,
        "max_moves": 5,
        "Yield": 0.8,
        "size_per_plant": 7068.3,
        "row-distance": 30,
        "column-distance": 30,
    }
cabbage = {
        "name": "cabbage",
        "W_max": 60,
        "H_max": 40,
        "k": 0.0005,
        "n": 2,
        "max_moves": 5,
        "Yield": 1.6,
        "size_per_plant": 9000.3,
        "row-distance": 60,
        "column-distance": 40,
    }
spinach = {
        "name": "spinach",
        "W_max": 20,
        "H_max": 30,
        "k": 0.002,
        "n": 2,
        "max_moves": 5,
        "Yield": 0.4,
        "size_per_plant": 5068.3,
        "row-distance": 20,
        "column-distance": 30,
    }
weed = {
        "name": "weed",
        "W_max": 30,
        "H_max": 30,
        "k": 0.001,
        "n": 2,
        "max_moves": 5,
        "Yield": 0.8,
        "size_per_plant": 7068.3,
        "row-distance": 30,
        "column-distance": 30,
    }
        

#if __name__ == "__main__":
#    main()