import numpy as np
from threading import Lock
from datetime import datetime, timedelta
from scipy.ndimage import convolve
import random
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from simapp.models import Plant
from ..models import DataModelInput, DataModelOutput, SimulationIteration, RowDetail, Weather
import time
import csv
import os
from dateutil import parser
from django.core.exceptions import ObjectDoesNotExist

class Crop:
    """
    A class to represent a crop.

    Attributes
    ----------
    name : str
        The name of the crop.
    center : tuple
        The (x, y) coordinates of the center of the crop.
    radius : int
        The radius of the crop.
    parameters : dict
        A dictionary of parameters related to the crop.
    sim : Simulation
        The simulation object that manages the growth and interactions of the crop.
    cells : np.ndarray
        An array representing the cells occupied by the crop.
    boundary : np.ndarray
        An array defining the boundary of the crop's area.
    moves : int
        The number of moves the crop has made during the simulation.
    overlap : float
        The amount of overlap with other plants.
    previous_growth : float
        The growth rate of the crop during the previous time step.

    Methods
    -------
    grow(size_layer, obj_layer, pos_layer)
        Grows the crop based on the provided size layer, object layer, and position layer.
    update_cells_and_boundary()
        Updates the cells and boundary of the crop based on its current center and radius.
    generate_circular_mask(radius)
        Generates a circular mask for the crop area with the specified radius.
    """
    def __init__(self, name, center, parameters, sim):
        """
        Initializes the Crop instance.

        Parameters
        ----------
        name : str
            The name of the crop.
        center : tuple
            The (x, y) coordinates of the center of the crop.
        radius : int
            The radius of the crop.
        parameters : dict
            A dictionary of parameters related to the crop.
        sim : Simulation
            The simulation object managing the crop.
        """
        self.name = name
        self.center = center
        self.radius = 0  # Initial radius is 0
        self.parameters = parameters
        self.sim = sim
        self.size =0
        self.cells = np.zeros(
            (
                self.parameters["W_max"] + self.parameters["max_moves"] + 2,
                self.parameters["W_max"] + self.parameters["max_moves"] + 2,
            ),
            dtype=bool,
        )
        self.boundary = np.zeros(
            (
                self.parameters["W_max"] + self.parameters["max_moves"] + 2,
                self.parameters["W_max"] + self.parameters["max_moves"] + 2,
            ),
            dtype=bool,
        )
        self.moves = 0  # Number of moves
        self.overlap = 1  # Overlap with other plants
        self.previous_growth = 0  # Growth rate of the previous hour

    def grow(self, size_layer, obj_layer, pos_layer, strip):
        """
        Grow the crop based on the size layer, object layer, and position layer.

        Parameters
        ----------
        size_layer : np.ndarray
            An array representing the size information for the growth process.
        obj_layer : np.ndarray
            An array containing information about objects that may affect growth.
        pos_layer : np.ndarray
            An array representing the position information for growth.
        """
        growthrate = self.calculate_growthrate(strip)
        self.add_growthrate_tp_plant(growthrate,size_layer)
        prevous_growth = growthrate.copy()
        self.radius = self.radius + growthrate
        if self.radius > self.parameters["W_max"]:
            self.radius = self.parameters["W_max"]
        rounded_radius = int(np.round(self.radius / 2))
        if rounded_radius != int(np.round(prevous_growth / 2)):
            self.check_overlap(rounded_radius,size_layer,obj_layer,pos_layer)
            self.update_cells()
            self.update_boundary()
        return growthrate, self.overlap
    def calculate_waterfactor(self):
        if self.sim.input_data['useWater']:
            current_time = self.sim.current_date
            current_paticipitation = self.weather_data[current_time.hour][3]
            self.sim.water_layer += current_paticipitation* 0.0001
            self.sim.water_layer[self.sim.water_layer > 2] = 2

            optimal_water = 0.5
            return 1 - abs(current_paticipitation - optimal_water) / optimal_water
        else:
            return 1
    def calculate_tempfactor(self):
        if self.sim.input_data['useTemperature']:
            current_time = self.sim.current_date
            current_temperture = self.weather_data[current_time.hour][2]
            optimal_temp = 20
            #return 1 if the temperture is optimal gradually decrease if the temperture is not optimal 0 if the temperture is -100% if the emperature is +100% of the optimal temperture
            return 1 - abs(current_temperture - optimal_temp) / optimal_temp
        else:
            return 1
    

    def calculate_growthrate(self, strip):
        """
        Calculate the growth rate of the plant based on various environmental and internal factors.
        
        Parameters:
        - strip: The plant strip containing sowing date and other relevant data.

        Returns:
        - float: The calculated growth rate for the plant.
        """
        # Calculate the difference in hours since the sowing date
        current_time = self.sim.current_date

        t_diff_hours = ((current_time - strip.sowing_date).total_seconds() / 3600)
        t_diff_hours = t_diff_hours
        # Calculate environmental impact factors on growth
        water_factor = self.calculate_waterfactor()
        temp_factor = self.calculate_tempfactor()

        # Random factor to introduce natural variation in growth
        random_factor = random.uniform(1, 1.001)

        # Base growth calculation
        growth = 0.00425 *((1-self.overlap)*0.5)# * water_factor * temp_factor * random_factor
        # Detailed growth rate calculation using the logistic growth model modified with environmental factors
        '''
        h = self.parameters["H_max"]
        r = self.parameters["k"]
        m = self.parameters["n"]
        '''
        #diese werte fur den Versuch
        h = 32
        r = 0.0045
        m = 1.421
        x = t_diff_hours
        b= 9
        growth_rate=(h*b*r)/(m-1)*np.exp(-r*x)*(1+b*np.exp(-r*x))**(m/(1-m))
        #get the betrag of the growth rate
        growth_rate = abs(growth_rate*self.sim.stepsize)*self.overlap
        """
        diese Werte dinf bei der Parameterisierung des Modells entstanden
        h = 32
        r = 0.0022
        m = 1.421
        x = t_diff_hours
        b= 11.8
        """
        # Update previous growth and modify the water layer based on the new growth
        self.previous_growth = growth_rate
        self.sim.water_layer[self.center] -= 0.1 * growth_rate

        return growth_rate
    # If the radius is the same as before, we can simply add the growth rate to the circular mask
    def add_growthrate_tp_plant(self,growth_rate,size_layer):
        rounded_radius = int(np.round(self.radius / 2))
        mask = self.generate_circular_mask(rounded_radius)
        crop_mask = np.zeros_like(size_layer, dtype=bool)

        # Check if the mask is within the boundaries of the field
        r_start = int(max(self.center[0] - rounded_radius, 0))
        r_end = int(min(self.center[0] + rounded_radius + 1, size_layer.shape[0]))
        c_start = int(max(self.center[1] - rounded_radius, 0))
        c_end = int(min(self.center[1] + rounded_radius + 1, size_layer.shape[1]))

        # Check if the mask is within the boundaries of the field
        mask_r_start = int(r_start - (self.center[0] - rounded_radius))
        mask_r_end = int(mask_r_start + (r_end - r_start))
        mask_c_start = int(c_start - (self.center[1] - rounded_radius))
        mask_c_end = int(mask_c_start + (c_end - c_start))

        # Add the mask to the crop mask
        crop_mask[r_start:r_end, c_start:c_end] = mask[
            mask_r_start:mask_r_end, mask_c_start:mask_c_end
        ]
        np.add.at(size_layer, np.where(crop_mask), growth_rate)

    def check_overlap(self,rounded_radius,size_layer,obj_layer,pos_layer):
        # Calculate the boundary indices for the area around the crop
        r_min = max(self.center[0] - rounded_radius - 1, 0)
        r_max = min(self.center[0] + rounded_radius + 2, size_layer.shape[0])
        c_min = max(self.center[1] - rounded_radius - 1, 0)
        c_max = min(self.center[1] + rounded_radius + 2, size_layer.shape[1])
        # Create a slice of the size_layer to check for overlap
        snipped_size_layer = size_layer[r_min:r_max, c_min:c_max]
        # Convert all non-zero cells to 1 to create a mask


        mask = np.where(snipped_size_layer > 0, 1, 0)


        # Mittelpunkt der Zellen-Matrix
        center_row = self.cells.shape[0] // 2
        center_col = self.cells.shape[1] // 2

        # Berechnen der Grenzen rund um den Mittelpunkt mit gegebenem Radius
        r_min = max(center_row - rounded_radius - 1, 0)
        r_max = min(center_row + rounded_radius + 2, self.cells.shape[0])
        c_min = max(center_col - rounded_radius - 1, 0)
        c_max = min(center_col + rounded_radius + 2, self.cells.shape[1])
        
        # Ausschneiden des relevanten Teils der Zellen-Matrix
        cells_slice = self.cells[r_min:r_max, c_min:c_max]
        boundary_slice = self.boundary[r_min:r_max, c_min:c_max]


        # Subtract the cells of the current crop to avoid self-interference
        if mask.shape != cells_slice.shape:
            if mask.shape[0] > cells_slice.shape[0] or mask.shape[1] > cells_slice.shape[1]:
                mask = mask[:cells_slice.shape[0], :]
                mask = mask[:, :cells_slice.shape[1]]
            else:
                cells_slice = cells_slice[:mask.shape[0], :mask.shape[1]]
                boundary_slice = boundary_slice[:mask.shape[0], :mask.shape[1]]

        mask -= cells_slice
        mask[mask < 0] = 0

        # Create a corresponding slice from self.boundary
        

        # Add the boundary to the mask
        mask += boundary_slice
        # Check if there is any overlap with other plants
        if np.any(mask > 1):
            # Calculate total and relative overlap
            total_overlap = np.sum(mask > 1)
            relative_overlap = total_overlap / np.sum(self.boundary) if np.sum(self.boundary) > 0 else 0
            maxoverlap = 0.07
            self.overlap = max(0, min(1, 1 - (relative_overlap / maxoverlap)))
            if self.moves < self.parameters["max_moves"]:
                pass
                #self.move_plant(mask,size_layer,obj_layer,pos_layer)
        else:
            self.overlap = 1  # Reset overlap if no interference

    def move_plant(self, mask, size_layer, obj_layer, pos_layer):

        interference_indices = np.where(mask > 1)
        interference_points = np.column_stack(interference_indices)
        center_point = np.array(self.center)

        if interference_points.size == 0:
            return

        # Initialize a zero vector for the movement
        total_vector = np.zeros(2)

        # Accumulate all repulsion vectors
        for point in interference_points:
            direction_vector = center_point - point
            distance = np.linalg.norm(direction_vector)
            if distance > 0:  # Avoid division by zero
                normalized_vector = direction_vector / distance
                # Optionally weight the vector by 1/distance or another function
                weighted_vector = normalized_vector / distance
                total_vector += weighted_vector

        # Normalize the total movement vector
        norm = np.linalg.norm(total_vector)
        if norm == 0:
            return

        # Determine the final movement steps
        movement_vector = np.round(total_vector / norm).astype(int)
        new_center_x, new_center_y = center_point + movement_vector
            # Check if the new position is within the boundaries of the field
        if (
            0 <= new_center_x < size_layer.shape[0]
            and 0 <= new_center_y < size_layer.shape[1]
        ):
            center_x, center_y = self.center
            self.center = (
                new_center_x,
                new_center_y,
            )  # update the cenetr of the crop
            pos_layer[center_x, center_y] = (
                False  # delete the old position of the crop in the pos_layer
            )
            pos_layer[new_center_x, new_center_y] = (
                True  # update the position of the crop in the pos_layer
            )
            obj_layer[center_x, center_y] = (
                None  # delete the old object of the crop in the obj_layer
            )
            obj_layer[new_center_x, new_center_y] = (
                self  # update the object of the crop in the obj_layer
            )
            self.moves += 1

            # Update cells and boundary to avoid self-interference
        else:
            return



    def update_cells(self):
            """
            Update the cells and boundary of the crop based on the current center and radius

            """
            rounded_radius = int(np.round(self.radius / 2))
            mask = self.generate_circular_mask(rounded_radius)
            # Reset the cells and boundary
            r_start = max(self.cells.shape[0] // 2 - mask.shape[0] // 2, 0)
            r_end = min(r_start + mask.shape[0], self.cells.shape[0])
            c_start = max(self.cells.shape[1] // 2 - mask.shape[1] // 2, 0)
            c_end = min(c_start + mask.shape[1], self.cells.shape[1])
            # Check if the mask is within the boundaries of the field
            mask_r_start = 0 if r_start >= 0 else -r_start
            mask_r_end = (
                mask.shape[0]
                if r_end <= self.cells.shape[0]
                else mask.shape[0] - (r_end - self.cells.shape[0])
            )
            mask_c_start = 0 if c_start >= 0 else -c_start
            mask_c_end = (
                mask.shape[1]
                if c_end <= self.cells.shape[1]
                else mask.shape[1] - (c_end - self.cells.shape[1])
            )
            # Add the mask to the cells

            self.cells[r_start:r_end, c_start:c_end] = mask[
                mask_r_start:mask_r_end, mask_c_start:mask_c_end
            ]

    def update_boundary(self):
            rounded_radius = int(np.round(self.radius / 2))
            # Update the boundary using a convolution
            self.boundary = (
                convolve(
                    self.cells,
                    np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]),
                    mode="constant",
                    cval=0.0,
                )
                ^ self.cells
            )
            # Ensure r_min, r_max, c_min, c_max are within valid range
            r_min = int(max(self.center[0] - rounded_radius - 1, 0))
            r_max = int(min(self.center[0] + rounded_radius + 2, self.sim.boundary_layer.shape[0])
            )
            c_min = int(max(self.center[1] - rounded_radius - 1, 0))
            c_max = int(min(self.center[1] + rounded_radius + 2, self.sim.boundary_layer.shape[1])
            )

            # Check if the boundary expands outside the array
            if (
                r_min == 0
                or r_max == self.sim.boundary_layer.shape[0]
                or c_min == 0
                or c_max == self.sim.boundary_layer.shape[1]
            ):
                return

            # Create a slice of the boundary array to assign
            start_index = max(self.parameters["W_max"] // 2 - rounded_radius - 1, 0)
            end_index = min(self.parameters["W_max"] // 2 + rounded_radius + 2, self.parameters["W_max"])

            # Use the safe indices to slice the array
            new_boundary_slice = self.boundary[start_index:end_index, start_index:end_index]
            boundary =self.sim.boundary_layer[r_min:r_max, c_min:c_max]
            if boundary.shape > new_boundary_slice.shape:
                boundary = boundary[:new_boundary_slice.shape[0], :new_boundary_slice.shape[1]]
            # Add the new boundary slice to the existing boundary_layer
            boundary += new_boundary_slice.astype(
                int
            )
    


    @staticmethod
    def generate_circular_mask(radius):
        """
        Generate a circular mask with the given radius. The mask is a boolean
        array that is True within the circle defined by the given radius and
        False outside.

        Parameters
        ----------
        radius : int
            The radius of the circle for which to create the mask.

        Returns
        -------
        np.ndarray
            A boolean array with shape (2*radius+1, 2*radius+1) representing the circular mask.

        Example
        -------
        >>> radius = 3
        >>> mask = Strip.generate_circular_mask(radius)
        >>> print(mask.astype(int))
        [[0 0 0 1 0 0 0]
         [0 0 1 1 1 0 0]
         [0 1 1 1 1 1 0]
         [1 1 1 1 1 1 1]
         [0 1 1 1 1 1 0]
         [0 0 1 1 1 0 0]
         [0 0 0 1 0 0 0]]
        """
        y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
        mask = x**2 + y**2 <= radius**2
        return mask



class Strip:
    def __init__(
        self,
        strip_width,
        plantType,
        plantingType,
        rowSpacing,
        sim,
        index,
        harvesttype="max_Yield",
        num_sets=1,
    ):
        self.num_sets = num_sets
        self.current_set = 0
        self.index = index
        self.width = strip_width
        self.plantType = plantType
        self.plantingType = plantingType
        self.harvesttype = harvesttype
        self.rowSpacing = rowSpacing
        self.start = sum(
            [sim.input_data["rows"][i]["stripWidth"] for i in range(index)]
        )
        self.num_plants = 0  # Will be calculated during planting
        self.sowing_date = sim.current_date
        self.sim = sim
        # Tracking previous sizes for the stability check (initiate with None)
        self.previous_sizes = [None] * 5  # List to track the last 5 size changes
        self.plant_parameters = Strip.get_plant_parameters(self.plantType)
    def get_plant_parameters(plant_name):
        try:
            plant = Plant.objects.get(name=plant_name)
            return {
                "name": str(plant.name),
                "W_max": int(plant.W_max),
                "H_max": int(plant.H_max),
                "k": float(plant.k),
                "n": int(plant.n),
                "b": int(plant.b),
                "max_moves": int(plant.max_moves),
                "Yield": float(plant.Yield),
                "size_per_plant": float(plant.size_per_plant),
                "row-distance": int(plant.row_distance),
                "column-distance": int(plant.column_distance),
                "planting_cost": float(plant.planting_cost),
                "revenue": float(plant.revenue),
            }
        except Plant.DoesNotExist:
            print(f"Plant {plant_name} not found in the database.")
            return None

    def planting(self, sim):
        strip_parameters = {
            "rowLength": sim.input_data["rowLength"],
            "rowDistance": self.rowSpacing,
            "columnDistance": self.width,
        }
        if self.plantingType == "grid":
            self._grid_planting(
                strip_parameters,
                self.start,
                self.start + self.width,
                self.plant_parameters,
                sim,
            )
        elif self.plantingType == "alternating":
            self._alternating_planting(
                strip_parameters,
                self.start,
                self.start + self.width,
                self.plant_parameters,
                sim,
            )
        elif self.plantingType == "random":
            self._random_planting(
                strip_parameters,
                self.start,
                self.start + self.width,
                self.plant_parameters,
                sim,
            )
        else:
            self._empty_planting()
        self.sowing_date = sim.current_date
    def apply_planting(self, row_indices, col_indices, plant_parameters, sim):
        # Ensure that rows and columns are used consistently with the dimensions of the layers
        # meshgrid outputs first the row indices then the column indices
        col_grid, row_grid = np.meshgrid(col_indices, row_indices, indexing="ij")

        # Set crop positions to True in your crop position layer
        sim.crops_pos_layer[row_grid, col_grid] = True

        # Create crop objects using vectorize properly over the grid
        create_crop = np.vectorize(lambda r, c: Crop(self.plantType, (r, c), plant_parameters, sim))
        crops = create_crop(row_grid, col_grid)

        # Place crop objects in the crops_obj_layer
        sim.crops_obj_layer[row_grid, col_grid] = crops

        # Set initial sizes in the crop_size_layer
        sim.crop_size_layer[row_grid, col_grid] = 0.001

        # Count the number of plants actually planted
        self.num_plants = np.size(row_grid)

        return row_grid, col_grid




    def _grid_planting(self, strip_parameters, start_col, end_col, plant_parameters, sim):
        plant_distance = strip_parameters["rowDistance"]  # Space between plants
        row_length = strip_parameters["rowLength"]  # Length of the row

        # Calculate offsets
        offset = 40 // 2

        # Adjust indices to ensure plants are not on the edges
        row_start = offset
        row_end = row_length - offset
        col_start = start_col + offset
        col_end = end_col - offset

        # Generate grid indices with adjusted bounds
        row_indices = np.arange(row_start, row_end, plant_distance)
        col_indices = np.arange(col_start, col_end, 40)

        # Pass row and column indices in the correct order
        self.apply_planting(row_indices, col_indices, plant_parameters, sim)



    def _empty_planting():
        pass

    def _alternating_planting(self, strip_parameters, start_col, end_col, plant_parameters, sim):
        """
        Plant the crops in an alternating pattern, avoiding edges
        """
        plant_distance = strip_parameters["rowDistance"]
        row_length = strip_parameters["rowLength"]

        # Use half the plant distance as offset to avoid planting at the edges
        offset = plant_distance // 2
        row_start = offset
        row_end = row_length - offset
        col_start = start_col + offset
        col_end = end_col - offset

        # Create grid indices for odd and even rows
        row_indices = np.arange(row_start, row_end, plant_distance)
        col_indices_odd = np.arange(col_start, col_end, plant_distance)
        col_indices_even = col_indices_odd + plant_distance // 2

        # Clip the indices to stay within bounds
        col_indices_even = col_indices_even[col_indices_even < col_end]
        col_indices_odd = col_indices_odd[col_indices_odd < col_end]

        # Create masks for alternating rows
        row_grid_odd = row_indices[::2]
        row_grid_even = row_indices[1::2]



        # Apply planting to odd and even rows
        self.apply_planting(row_grid_odd, col_indices_odd, plant_parameters, sim)
        self.apply_planting(row_grid_even, col_indices_even, plant_parameters, sim)


    def _random_planting(self,strip_parameters, start_col, end_col, plant_parameters, sim):
        """
        Plant the crops in a random pattern
        """
        num_plants = int(
            (strip_parameters["rowLength"] * (end_col - start_col) )/(strip_parameters["rowDistance"]*40)

        )
        offset = 40 // 2
        row_start = offset
        row_end = strip_parameters["rowLength"] - offset
        col_start = start_col + offset
        col_end = end_col - offset
        print(num_plants)
        # Calculate the adjusted grid dimensions based on offsets
        adjusted_row_length = row_end - row_start
        adjusted_col_length = col_end - col_start

        # Determine the number of plants to place
        print(f"Placing {num_plants} plants in strip {self.index}.")
        # Randomly select positions within the adjusted bounds
        total_positions = adjusted_row_length * adjusted_col_length
        plant_positions = np.random.choice(total_positions, num_plants, replace=False)
        row_indices, col_indices = np.unravel_index(
            plant_positions, (adjusted_row_length, adjusted_col_length)
        )
        row_indices, col_indices = np.unravel_index(
                plant_positions, (adjusted_row_length, adjusted_col_length)
            )
        row_indices += row_start
        col_indices += col_start
        print
        # Set crop positions to True in your crop position layer
        sim.crops_pos_layer[row_indices, col_indices] = True

        # Create crop objects using vectorize properly over the grid
        create_crop = np.vectorize(lambda r, c: Crop(self.plantType, (r, c), plant_parameters, sim))
        crops = create_crop(row_indices, col_indices)

        # Place crop objects in the crops_obj_layer
        sim.crops_obj_layer[row_indices, col_indices] = crops

        # Set initial sizes in the crop_size_layer
        sim.crop_size_layer[row_indices, col_indices] = 0.001

        # Count the number of plants actually planted
        self.num_plants = np.size(row_indices)

    def harvesting(self, sim):
        # startr harvesting 10 days after planting
        if (sim.current_date - self.sowing_date).days < 10:
            return
        harvesting_type = self.harvesttype
        strip = sim.crop_size_layer[:, self.start : self.start + self.width]
        plant_sizes = strip[strip > 0]

        if harvesting_type == "max_Yield":
            # Calculate the average size in the strip (crop size precision at 0.001)
            # get all sizes of the sizelayer in the strip where the value is not 0
            current_average_size = np.mean(plant_sizes)
            rounded_current_size = round(current_average_size, 3)

            # Shift previous sizes and store the current one
            self.previous_sizes.pop(0)  # Remove the oldest entry
            self.previous_sizes.append(rounded_current_size)  # Add the latest size
            # Check if all the last 5 sizes are equal (stable growth)
            if self.previous_sizes.count(rounded_current_size) == 5:
                print(f"Strip {self.index} has reached stable growth. Harvesting...")
                # Move the harvested plants to the harvested plants array
                sim.harvested_plants[:, self.start : self.start + self.width] = strip
                # Clear the harvested plants from the crop_size_layer
                sim.crop_size_layer[:, self.start : self.start + self.width+2] = 0
                # clear the crops from the crop_obj_layer
                sim.crops_obj_layer[:, self.start : self.start + self.width] = None
                # clear the crops from the crop_pos_layer
                sim.crops_pos_layer[:, self.start : self.start + self.width] = False
                self.current_set += 1
                # replant the strip if num of sets is not reached
                if self.current_set < self.num_sets:
                    self.planting(sim)
                    self.previous_sizes = [None] * 5
                    self.num_plants = 0
                    print(f"Strip {self.index} replanted.")
                else:
                    if np.sum(sim.crop_size_layer) == 0:
                        sim.finish = True
                        print("All sets harvested. Simulation finished")
                    else:
                        print("Not All sets harvested. not Simulation finished")

        elif harvesting_type == "max_quality":
            pass
            if np.mean(np.sum(strip) / self.num_plants) > 7000:
                # cut out harvested palnts and paste them on the corresponding position in the harvested_plants array
                sim.harvested_plants[:, self.start : self.start + self.width] = strip
                # set the harvested plants to 0 in the crop_size_layer
                sim.crop_size_layer[:, self.start : self.start + self.width] = 0
            self.current_set += 1
            if self.current_set < self.num_sets:
                self.planting(sim)
                self.previous_sizes = [None] * 5
        elif harvesting_type == "earliest":
            pass
            self.current_set += 1
        else:
            print("Invalid harvesting type. Simulation finished.")
            if self.current_set < self.num_sets:
                self.planting(sim)
                # reset previous sizes
                self.previous_sizes = [None] * 5

            # Check if all strips have been harvested
            if np.sum(sim.crop_size_layer) == 0:
                print("All strips harvested. Simulation finished.")
                sim.finish = True


class Simulation:
    """
    A class to simulate crop growth and management in a specified area.

    Attributes
    ----------
    input_data : dict
        A dictionary containing input parameters for the simulation.
    total_width : int
        The total width of the simulation area based on strip widths.
    water_layer : np.ndarray
        A layer representing water levels across the simulation area.
    crop_size_layer : np.ndarray
        A layer representing the size of crops at each position.
    crops_pos_layer : np.ndarray
        A boolean layer indicating the positions occupied by crops.
    crops_obj_layer : np.ndarray
        A layer storing crop objects at each position.
    boundary_layer : np.ndarray
        A layer representing the boundary of the crops.
    weeds_size_layer : np.ndarray
        A layer representing the size of weeds at each position.
    weeds_obj_layer : np.ndarray
        A layer storing weed objects at each position.
    weeds_pos_layer : np.ndarray
        A boolean layer indicating the positions occupied by weeds.
    lock : Lock
        A lock to manage concurrent access to shared resources.
    date : str
        The start date of the simulation.
    current_date : datetime
        The current date in the simulation.
    df : pd.DataFrame
        A DataFrame to store simulation data over time.
    stepsize : int
        The time step size for the simulation.

    Methods
    -------
    planting()
        Initiates the planting process based on the input data.
    harvesting()
        Checks if crops are ready for harvest based on their size.
    grow_weeds()
        Grows the weeds in the simulation area using parallel processing.
    grow_plants()
        Grows the crops in the simulation area using parallel processing.
    run_simulation()
        Executes the simulation loop for crop and weed growth.
    record_data(date, size, growth_rate, water_level, overlap, size_layer, boundary, weed_size_layer)
        Records the current state of the simulation into the DataFrame.
    """
    def __init__(self, input_data, weather_data):
        """
        Initializes the Simulation instance with the provided input data.

        Parameters
        ----------
        input_data : dict
            A dictionary containing parameters such as row length, start date, and step size.
        """
        self.weather_data=weather_data
        self.input_data=input_data
        length = int(self.input_data["rowLength"])
        self.total_width = int(sum(row["stripWidth"] for row in self.input_data["rows"]))
        self.water_layer = np.full((length, self.total_width), 0.5, dtype=float)
        self.crop_size_layer = np.zeros((length, self.total_width+2), dtype=float)
        self.crops_pos_layer = np.zeros((length, self.total_width), dtype=bool)
        self.crops_obj_layer = np.full((length, self.total_width), None, dtype=object)
        self.boundary_layer = np.zeros((length, self.total_width), dtype=int)
        self.weeds_size_layer = np.zeros((length, self.total_width), dtype=float)
        self.weeds_obj_layer = np.full((length, self.total_width), None, dtype=object)
        self.weeds_pos_layer = np.zeros((length, self.total_width), dtype=bool)
        self.lock = Lock()
        self.finish = False
        self.current_date = datetime.strptime(
            self.input_data["startDate"] + ":00:00:00", "%Y-%m-%d:%H:%M:%S"
        )
        self.stepsize = int(self.input_data["stepSize"])
        self.strips = np.array([Strip(
                    strip["stripWidth"],
                    strip["plantType"],
                    strip["plantingType"],
                    strip["rowSpacing"],
                    self,
                    index,
                )  
                for index, strip in enumerate(self.input_data["rows"])
            ]
        )
        self.harvested_plants = np.zeros((length, self.total_width), dtype=float)
    
  
    def grow_weeds(self, strip):
        """
        Grows the weeds in parallel using multiple threads or processes to speed up the simulation.
        Weeds are grown based on the current weed positions and sizes.
        """
        with self.lock:
            # Extract weeds that are present in the weeds_layer

            weeds = self.weeds_obj_layer[self.weeds_pos_layer]
            if len(weeds) > 0:
                weed_list = np.ravel(weeds)
                np.random.shuffle(weed_list)

                def grow_subset(subset):
                    for weed in subset:
                        weed.grow(
                            self.weeds_size_layer,
                            self.weeds_obj_layer,
                            self.weeds_pos_layer,
                            strip,
                        )

                num_cores = cpu_count()
                weed_subsets = np.array_split(weed_list, num_cores)
                with ThreadPoolExecutor(max_workers=num_cores) as executor:
                    futures = [
                        executor.submit(grow_subset, subset) for subset in weed_subsets
                    ]
                    for future in futures:
                        future.result()
            weed_x = np.random.randint(0, self.crop_size_layer.shape[0], 1)
            weed_y = np.random.randint(0, self.crop_size_layer.shape[1] - 2, 1)
            size_at_spot = self.crop_size_layer[weed_x, weed_y]
            random = np.random.uniform(0, (24 + size_at_spot) / self.stepsize, 1)
            if random <= 0.2:
                weed_parameters = Strip.get_plant_parameters("weed")
                self.weeds_pos_layer[weed_x, weed_y] = True
                self.weeds_obj_layer[weed_x, weed_y] = Crop(
                    "weed", (weed_x, weed_y), weed_parameters, self
                )

    def grow_plants(self, strip):
        """
        Grows the crops in parallel using multiple threads or processes to speed up the simulation.
        Plants are grown based on their current positions and sizes.
        """

        with self.lock:
            # Extract crops that are present in the plants_layer
            crops = self.crops_obj_layer[self.crops_pos_layer]
            crop_list = np.ravel(crops)  # Flatten the array
            np.random.shuffle(crop_list)  # Shuffle the crop list

            # Function to grow plants in a specific subset
            def grow_subset(subset):
                subset_growthrate = 0
                subset_overlap = 0
                for crop in subset:
                    crop_growthrate, crop_overlap = crop.grow(
                        self.crop_size_layer,
                        self.crops_obj_layer,
                        self.crops_pos_layer,
                        strip,
                    )
                    subset_growthrate += crop_growthrate
                    subset_overlap += crop_overlap
                return subset_growthrate, subset_overlap

            # Split the crop list into approximately equal subsets
            num_cores = cpu_count()
            crop_subsets = np.array_split(crop_list, num_cores)

            # Execute the grow_subset function in parallel
            growthrate = 0
            overlap = 0
            with ThreadPoolExecutor(max_workers=num_cores) as executor:
                futures = [executor.submit(grow_subset, subset) for subset in crop_subsets]
                for future in futures:
                    thread_growthrate, thread_overlap = future.result()  # Collect results from each subset
                    growthrate += thread_growthrate
                    overlap += thread_overlap

            return growthrate, overlap


    def run_simulation(self,iteration_instance):
        """
        Executes the simulation loop for crop and weed growth.
        Continuously updates the simulation state until a specdified end date is reached.
        Records the state of the simulation in a DataFrame for later analysis.
        """

        for strip in self.strips:
            strip.planting(self)
        #while not self.finish:
        while self.current_date < datetime.strptime(self.input_data["startDate"] + ":00:00:00", "%Y-%m-%d:%H:%M:%S") + timedelta(days=53):

            total_growthrate = 0
            total_overlap = 0
            start_time = time.time()
            for strip in self.strips:
                growthrate,overlap = self.grow_plants(strip)
                total_growthrate += growthrate
                total_overlap += overlap
                if self.input_data["allowWeedgrowth"]:
                    self.grow_weeds(strip)          
            end_time = time.time()
            time_needed = end_time - start_time
            self.record_data(time_needed,iteration_instance,total_growthrate,total_overlap,)
            self.current_date += timedelta(hours=self.stepsize)

         #   for strip in self.strips:
          #    strip.harvesting(self)
        print("Simulation finished.")



    def record_data(self,time_needed,iteration_instance,total_growthrate,total_overlap):
        index_where = np.where(self.crops_pos_layer > 0)  
        yields = np.sum(self.crop_size_layer[index_where])*11
        num_plants = np.sum(self.crops_pos_layer)
        profit = yields *self.strips[0].plant_parameters["revenue"]*0.001-0.05*self.strips[0].num_plants
        #self.strips[0].plant_parameters["planting_cost"]
        data = {

            "date": self.current_date,
            "yield": yields,
            "growth": total_growthrate,
            "water": np.sum(self.water_layer),
            "overlap": num_plants-total_overlap,
            "map": self.crop_size_layer.tolist(),
            "boundary": self.boundary_layer.tolist(),
            "weed": self.weeds_size_layer.tolist(),
            "time_needed": time_needed,
            "profit": profit,
            "temperature": self.weather_data[self.current_date]["temperature"],
            "rain": self.weather_data[self.current_date]["rain"],
            "num_plants": num_plants,

        }
        output_instance = DataModelOutput(
            iteration=iteration_instance
        )
        output_instance.set_data(data)
        output_instance.save()
        """
        # CSV file path (same directory as this script)
        csv_file_path = os.path.join(os.path.dirname(__file__), '6.csv')

        # Check if file exists to write headers
        file_exists = os.path.isfile(csv_file_path)

        # Open the file in append mode
        with open(csv_file_path, mode='a', newline='') as file:
            fieldnames = ['date', 'yield', 'growth']
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')

            # Write the header only if the file is newly created
            if not file_exists:
                writer.writeheader()

            # Prepare data with the decimal change
            def format_decimal(value):
                if isinstance(value, float):
                    return f"{value:.2f}".replace('.', ',')
                return value

            # Write data row with formatted decimals
            writer.writerow({
                'date': data['date'],
                'yield': format_decimal(data['yield']),
                'growth': format_decimal(data['growth'])
            })
            """



def main(input_data):
    """
    Entry point for running simulations with given input data, considering testing mode adjustments.
    """
    print(input_data)
    input_instance = save_initial_data(input_data)
    weather_data = fetch_weather_data()

    if input_data["testingMode"]:
        print("Running simulation in testing mode.")
        handle_testing_mode(input_data, input_instance, weather_data)
    else:
        print("Running standard simulation.")
        run_standard_simulation(input_data, input_instance, weather_data)
    #return the simulation name
    return input_instance.simName

def save_initial_data(input_data):
    """
    Save the initial data into the DataModelInput model and create RowDetail entries for each row.
    
    Parameters
    ----------
    input_data : dict
        A dictionary containing the data to be saved.

    Returns
    -------
    DataModelInput
        The created DataModelInput instance.
    """
    # Create the DataModelInput instance
    input_instance = DataModelInput(
        startDate=input_data.get('startDate'),
        stepSize=input_data.get('stepSize'),
        rowLength=input_data.get('rowLength'),
        testingMode=input_data.get('testingMode'),
        simName=input_data.get('simName')
    )
    
    # Handle testing data
    testing_data = input_data.get('testingData', {})
    if testing_data and input_instance.testingMode:
        input_instance.testingKey, input_instance.testingValue = next(iter(testing_data.items()), (None, None))
        if isinstance(input_instance.testingValue, dict):
            input_instance.testingValue = -99  # or handle accordingly
    else:
        input_instance.testingKey = None
        input_instance.testingValue = None
    
    # Save the DataModelInput instance to the database
    input_instance.save()
    
    # Save each row's details into RowDetail model
    for row in input_data.get('rows', []):
        row_instance = RowDetail(
            plantType=row.get('plantType'),
            plantingType=row.get('plantingType'),
            stripWidth=row.get('stripWidth'),
            rowSpacing=row.get('rowSpacing'),
            numSets=row.get('numSets'),
            input_data=input_instance  # Linking the RowDetail to the DataModelInput
        )
        row_instance.save()

    return input_instance




def fetch_weather_data():
    try:
        # Fetch weather data as a QuerySet of dictionaries
        weather_data = Weather.objects.values('date', 'rain', 'temperature')
        weather_data_dict = {}

        for data in weather_data:
            try:
                if data["date"] not in [None, 'NaT', '']:
                    # More flexible parsing that handles a variety of date formats
                    data['date'] = parser.parse(data["date"])
                else:
                    continue  # Skip entries with no valid date
            except ValueError:
                print(f"Skipping invalid date format: {data['date']}")
                continue  # Skip entries with unparseable dates

            weather_data_dict[data['date']] = data

        return weather_data_dict
    except ObjectDoesNotExist:
        print("Weather data not found in the database.")
        return None



def handle_testing_mode(input_data, input_instance, weather_data):
    """
    Handles variations for testing mode simulations.
    """
    if "rows" in input_data["testingData"]:
        handle_row_variations(input_data, input_instance, weather_data)
    else:
        handle_parameter_variations(input_data, input_instance, weather_data)

def handle_row_variations(input_data, input_instance, weather_data):
    """
    Processes each row variation for testing mode.
    """
    for row_index, row in enumerate(input_data['rows']):
        modified_input_data = create_modified_input_data(input_data, row_index)
        iteration_instance = create_iteration_instance(input_instance, row_index, -99)
        run_simulation(modified_input_data, weather_data, iteration_instance)
    print("All row variations processed.")
def handle_parameter_variations(input_data, input_instance, weather_data):
    """
    Processes parameter variations for testing mode.
    """
    testing_key, testing_value = next(iter(input_data["testingData"].items()))
    if testing_key  in input_data["rows"][0]:
        start_value, end_value = sorted([input_data.get(testing_key, input_data["rows"][0][testing_key]), testing_value])
    else:
        start_value, end_value = sorted([input_data.get(testing_key, -99), testing_value])
    
    for param_value in range(start_value, end_value + 1):
        modified_input_data = modify_input_data_for_parameter(input_data, testing_key, param_value)
        iteration_instance = create_iteration_instance(input_instance, param_value, param_value)
        run_simulation(modified_input_data, weather_data, iteration_instance)
    print("All variations processed.")
def run_standard_simulation(input_data, input_instance, weather_data):
    """
    Runs a standard simulation when not in testing mode.
    """

    iteration_instance = create_iteration_instance(input_instance, index=1, param_value=-99)
    run_simulation(input_data, weather_data, iteration_instance)

def modify_input_data_for_parameter(input_data, key, value):
    """
    Returns a modified copy of input_data with the specified parameter changed.
    """
    modified_input_data = input_data.copy()
    if key in modified_input_data:
        modified_input_data[key] = value
    else:
        modified_input_data["rows"][0][key] = value
    return modified_input_data
def create_modified_input_data(original_data, row_index):
    """
    Creates a modified version of the input data that includes only the specified row,
    suitable for handling variations during testing mode.
    """
    modified_data = original_data.copy()  # Deep copy to avoid altering the original data
    selected_row = original_data['rows'][row_index]
    modified_data['rows'] = [selected_row]  # Replace the rows list with only the selected row
    return modified_data


def create_iteration_instance(input_instance, index, param_value):
    """
    Creates a new SimulationIteration instance.
    """
    return SimulationIteration.objects.create(
        input=input_instance,
        iteration_index=index,
        param_value=param_value
    )

def run_simulation(input_data, weather_data, iteration_instance):
    """
    Initializes and runs the simulation.
    """
    sim = Simulation(input_data, weather_data)
    sim.run_simulation(iteration_instance)
