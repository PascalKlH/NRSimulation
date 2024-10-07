import numpy as np
import pandas as pd
from threading import Lock
from datetime import datetime, timedelta
from scipy.ndimage import convolve
import random
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from simapp.models import Plant

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
        self.overlap = 0  # Overlap with other plants
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
        current_time = self.sim.current_date
        t_diff_hours = (current_time - strip.sowing_date).total_seconds() / (3600.0)
        growth = self.parameters["k"] * (1 - self.overlap) * random.uniform(0.9, 1.1)
        # TODO: make the function more readable
        growth_rate = (
            self.parameters["H_max"]
            * self.parameters["n"]
            * (1 - np.exp(-growth * t_diff_hours)) ** (self.parameters["n"] - 1)
            * self.parameters["k"]
            * np.exp(-self.parameters["k"] * t_diff_hours)
            * self.sim.stepsize
        )

        self.previous_growth = growth_rate
        rounded_radius_before_growth = int(np.round(self.radius / 2))
        ##################
        self.radius += growth_rate
        if self.radius > self.parameters["H_max"]:
            self.radius = self.parameters["H_max"]
        ####################
        rounded_radius = int(np.round(self.radius / 2))
        self.sim.water_layer[self.center] -= 0.1 * growth_rate
        # If the radius is the same as before, we can simply add the growth rate to the circular mask
        if rounded_radius == rounded_radius_before_growth:
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
            return
        # move the plant if the max is not reached
        if self.moves < self.parameters["max_moves"]:
            r_min, r_max = (
                int(self.center[0] - rounded_radius - 1),
                int(self.center[0] + rounded_radius + 2),
            )
            c_min, c_max = (
                int(self.center[1] - rounded_radius - 1),
                int(self.center[1] + rounded_radius + 2),
            )
            # Check if the new position is within the boundaries of the field
            if (
                0 <= r_min < size_layer.shape[0]
                and 0 <= r_max <= size_layer.shape[0]
                and 0 <= c_min < size_layer.shape[1]
                and 0 <= c_max <= size_layer.shape[1]
            ):
                # Create a slice of the size_layer to check for overlap
                # snpi the crop out of the size_layer to get just the crop
                snipped_size_layer = size_layer[r_min:r_max, c_min:c_max]
                mask = np.where(snipped_size_layer > 0, 1, 0)
                # Create a slice of the crop mask to check for overlap
                snipped_cells = self.cells[
                    self.parameters["W_max"] // 2
                    - rounded_radius
                    - 1 : self.parameters["W_max"] // 2 + rounded_radius + 2,
                    self.parameters["W_max"] // 2
                    - rounded_radius
                    - 1 : self.parameters["W_max"] // 2 + rounded_radius + 2,
                ]
                # Subtract the cells of the current crop to avoid self-interference
                mask -= snipped_cells
                # Add the mask to the crop mask
                mask += self.boundary[
                    self.parameters["W_max"] // 2
                    - rounded_radius
                    - 1 : self.parameters["W_max"] // 2 + rounded_radius + 2,
                    self.parameters["W_max"] // 2
                    - rounded_radius
                    - 1 : self.parameters["W_max"] // 2 + rounded_radius + 2,
                ]

                # Check if there is any overlap with other plants
                if np.any(mask > 1):
                    total_overlap = np.sum(mask > 1)
                    relative_overlap = total_overlap / np.sum(self.boundary)
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
                        new_center_x, new_center_y = (
                            center_x + movement_x,
                            center_y + movement_y,
                        )

                        # Check if the new position is within the boundaries of the field
                        if (
                            0 <= new_center_x < size_layer.shape[0]
                            and 0 <= new_center_y < size_layer.shape[1]
                        ):
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
                            self.update_cells_and_boundary()
        # create a mask of the current plant
        mask = self.generate_circular_mask(rounded_radius)
        # create an empty array of the size of the field to add the current plant on the right position to it
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
        # apply the mask to the crop mask array to get the current plant on the right position
        crop_mask[r_start:r_end, c_start:c_end] = mask[
            mask_r_start:mask_r_end, mask_c_start:mask_c_end
        ]
        # add the current growthrate to the new fields of the plant
        np.add.at(size_layer, np.where(crop_mask), growth_rate)
        # Update the cells and boundary
        if self.radius == 0:
            # set the inital cell of the plant to 1
            self.cells[self.parameters["W_max"] // 2, self.parameters["W_max"] // 2] = 1
        else:
            self.update_cells_and_boundary()

    def update_cells_and_boundary(self):
        """
        Update the cells and boundary of the crop based on the current center and radius

        """
        rounded_radius = int(np.round(self.radius / 2))
        mask = self.generate_circular_mask(rounded_radius)
        # Reset the cells and boundary
        r_start = max(self.parameters["W_max"] // 2 - mask.shape[0] // 2, 0)
        r_end = min(r_start + mask.shape[0], self.cells.shape[0])
        c_start = max(self.parameters["W_max"] // 2 - mask.shape[1] // 2, 0)
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
        r_max = int(
            min(self.center[0] + rounded_radius + 2, self.sim.boundary_layer.shape[0])
        )
        c_min = int(max(self.center[1] - rounded_radius - 1, 0))
        c_max = int(
            min(self.center[1] + rounded_radius + 2, self.sim.boundary_layer.shape[1])
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
        new_boundary_slice = self.boundary[
            self.parameters["W_max"] // 2 - rounded_radius - 1 : self.parameters[
                "W_max"
            ]
            // 2
            + rounded_radius
            + 2,
            self.parameters["W_max"] // 2 - rounded_radius - 1 : self.parameters[
                "W_max"
            ]
            // 2
            + rounded_radius
            + 2,
        ]

        # Add the new boundary slice to the existing boundary_layer
        self.sim.boundary_layer[r_min:r_max, c_min:c_max] += new_boundary_slice.astype(
            int
        )

    @staticmethod
    def generate_circular_mask(radius):
        """
        Generate a circular mask with the given radius.

        Parameters
        ----------
        radius : int
            The radius of the circular mask to be generated.

        Returns
        -------
        np.ndarray
            A boolean array representing the circular mask.
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

    def get_plant_parameters(plant_name):
        try:
            plant = Plant.objects.get(name=plant_name)
            return {
                "name": plant.name,
                "W_max": int(plant.W_max),
                "H_max": int(plant.H_max),
                "k": float(plant.k),
                "n": int(plant.n),
                "max_moves": int(plant.max_moves),
                "Yield": float(plant.Yield),
                "size_per_plant": float(plant.size_per_plant),
                "row-distance": int(plant.row_distance),
                "column-distance": int(plant.column_distance),
            }
        except Plant.DoesNotExist:
            print(f"Plant {plant_name} not found in the database.")
            return None

    def planting(self, sim):
        plant_parameters = Strip.get_plant_parameters(self.plantType)
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
                plant_parameters,
                sim,
            )
        elif self.plantingType == "alternating":
            self._alternating_planting(
                strip_parameters,
                self.start,
                self.start + self.width,
                self.index,
                plant_parameters,
                sim,
            )
        elif self.plantingType == "random":
            self._random_planting(
                strip_parameters,
                self.start,
                self.start + self.width,
                self.index,
                plant_parameters,
                sim,
            )
        else:
            self._empty_planting()
        self.sowing_date = sim.current_date

    def _grid_planting(
        self, strip_parameters, start_col, end_col, plant_parameters, sim
    ):
        plant_distance = strip_parameters["rowDistance"]  # Space between plants
        row_length = strip_parameters["rowLength"]  # Length of the row

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

        row_grid, col_grid = np.meshgrid(row_indices, col_indices, indexing="ij")

        # Set crop positions to True in your crop position layer
        sim.crops_pos_layer[row_grid, col_grid] = True

        # Create crop objects and place them in the crops_obj_layer
        crop_array = np.array(
            [
                Crop(self.plantType, (r, c), plant_parameters, sim)
                for r in row_indices
                for c in col_indices
            ]
        )

        sim.crops_obj_layer[row_grid, col_grid] = crop_array.reshape(row_grid.shape)
        sim.crop_size_layer[row_grid, col_grid] = 0.001

        # Count the number of plants actually planted
        self.num_plants = len(crop_array)

    def _empty_planting():
        pass

    def _alternating_planting(
        strip_parameters, start_col, end_col, row, plant_parameters, sim
    ):
        """
        Plant the crops in an alternating pattern
        """
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
        row_grid_odd, col_grid_odd = np.meshgrid(
            row_grid_odd, col_indices_odd, indexing="ij"
        )
        row_grid_even, col_grid_even = np.meshgrid(
            row_grid_even, col_indices_even, indexing="ij"
        )

        # Place plants
        sim.crops_pos_layer[row_grid_odd, col_grid_odd] = True
        sim.crops_pos_layer[row_grid_even, col_grid_even] = True

        # Vectorized crop placement
        sim.crops_obj_layer[row_grid_odd, col_grid_odd] = np.vectorize(
            lambda r, c: Crop(row["plantType"], (r, c), plant_parameters, sim)
        )(row_grid_odd, col_grid_odd)
        sim.crops_obj_layer[row_grid_even, col_grid_even] = np.vectorize(
            lambda r, c: Crop(row["plantType"], (r, c), plant_parameters, sim)
        )(row_grid_even, col_grid_even)

    def _random_planting(
        strip_parameters, start_col, end_col, row, plant_parameters, sim
    ):
        """
        Plant the crops in a random pattern
        """
        num_plants = int(
            strip_parameters["columnDistance"]
            * strip_parameters["rowLength"]
            / strip_parameters["rowDistance"]
        )
        total_positions = strip_parameters["rowLength"] * (end_col - start_col)

        # Randomly select positions within the strip
        plant_positions = np.random.choice(total_positions, num_plants, replace=False)
        row_indices, col_indices = np.unravel_index(
            plant_positions, (strip_parameters["rowLength"], end_col - start_col)
        )
        col_indices += (
            start_col  # Adjust column indices based on the strip's starting position
        )

        # Place plants
        sim.crops_pos_layer[row_indices, col_indices] = True
        sim.crops_obj_layer[row_indices, col_indices] = np.vectorize(
            lambda r, c: Crop(row["plantType"], (r, c), plant_parameters, sim)
        )(row_indices, col_indices)

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
                sim.crop_size_layer[:, self.start : self.start + self.width] = 0
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
                    # prinz out the planted plant objects and thier attributes

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
            if self.current_set < self.num_sets:
                self.planting(sim)
                # reset previous sizes
                self.previous_sizes = [None] * 5
        else:
            print("Unknown harvesting type. No harvesting performed.")
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
    def __init__(self, input_data):
        """
        Initializes the Simulation instance with the provided input data.

        Parameters
        ----------
        input_data : dict
            A dictionary containing parameters such as row length, start date, and step size.
        """
        self.input_data=input_data
        self.iterate_to = None
        length = int(self.input_data["rowLength"])
        self.total_width = int(sum(row["stripWidth"] for row in self.input_data["rows"]))
        self.water_layer = np.full((length, self.total_width), 0.5, dtype=float)
        self.crop_size_layer = np.zeros((length, self.total_width), dtype=float)
        self.crops_pos_layer = np.zeros((length, self.total_width), dtype=bool)
        self.crops_obj_layer = np.full((length, self.total_width), None, dtype=object)
        self.boundary_layer = np.zeros((length, self.total_width), dtype=int)
        self.weeds_size_layer = np.zeros((length, self.total_width), dtype=float)
        self.weeds_obj_layer = np.full((length, self.total_width), None, dtype=object)
        self.weeds_pos_layer = np.zeros((length, self.total_width), dtype=bool)
        self.lock = Lock()
        self.finish = False
        # add hours to the current date
        self.current_date = datetime.strptime(
            self.input_data["startDate"] + ":00:00:00", "%Y-%m-%d:%H:%M:%S"
        )
        self.df = pd.DataFrame(
            columns=[
                "date",
                "yield",
                "growth",
                "water",
                "overlap",
                "map",
                "boundary",
                "weed",
            ]
        )
        self.stepsize = int(self.input_data["stepSize"])
        # creatt a 1d array depending of the number of strips
        self.strips = np.array(
            [
                Strip(
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

                num_cores = 1  # cpu_count()
                weed_subsets = np.array_split(weed_list, num_cores)
                with ThreadPoolExecutor(max_workers=num_cores) as executor:
                    futures = [
                        executor.submit(grow_subset, subset) for subset in weed_subsets
                    ]
                    for future in futures:
                        future.result()
            weed_x = np.random.randint(0, self.crop_size_layer.shape[0], 1)
            weed_y = np.random.randint(0, self.crop_size_layer.shape[1], 1)
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
        # rainfall = weather_data[0][7]
        # self.water_layer += rainfall

        with self.lock:
            # Extract crops that are present in the plants_layer
            crops = self.crops_obj_layer[self.crops_pos_layer]
            crop_list = np.ravel(crops)  # Flatten the array
            np.random.shuffle(crop_list)  # Shuffle the crop list

            # Function to grow plants in a specific subset
            def grow_subset(subset):
                for crop in subset:
                    crop.grow(
                        self.crop_size_layer,
                        self.crops_obj_layer,
                        self.crops_pos_layer,
                        strip,
                    )

            # Split the crop list into approximately equal subsets
            num_cores = cpu_count()
            crop_subsets = np.array_split(crop_list, num_cores)

            # Execute the grow_subset function in parallel
            with ThreadPoolExecutor(max_workers=num_cores) as executor:
                futures = [
                    executor.submit(grow_subset, subset) for subset in crop_subsets
                ]
                for future in futures:
                    future.result()  # Wait for all threads to complete

    def run_simulation(self):
        """
        Executes the simulation loop for crop and weed growth.
        Continuously updates the simulation state until a specified end date is reached.
        Records the state of the simulation in a DataFrame for later analysis.
        """
        for strip in self.strips:
            strip.planting(self)
        while not self.finish:
            for strip in self.strips:
                self.grow_plants(strip)
                self.grow_weeds(strip)
            # Save all data in a dataframe as well as the date
            sum_growthrate = sum(
                self.crops_obj_layer[r, c].previous_growth
                for r in range(self.input_data["rowLength"])
                for c in range(self.total_width)
                if self.crops_obj_layer[r, c] is not None
            )
            sum_overlap = sum(
                self.crops_obj_layer[r, c].overlap
                for r in range(self.input_data["rowLength"])
                for c in range(self.total_width)
                if self.crops_obj_layer[r, c] is not None
            )
            # Convert size_layer to a list
            crop_size_layer_list = self.crop_size_layer.tolist()
            weed_size_layer_list = self.weeds_size_layer.tolist()
            # take the boundary out of the crop object and and place it on the field where it belongs, use the plants layer to determine where the plants are to create a boundary_layer
            boundary_list = self.boundary_layer.tolist()
            self.record_data(
                self.current_date,
                np.sum(self.crop_size_layer),
                sum_growthrate,
                np.sum(self.water_layer),
                sum_overlap,
                crop_size_layer_list,
                boundary_list,
                weed_size_layer_list,
            )
            self.current_date += timedelta(hours=self.stepsize)
            for strip in self.strips:
                strip.harvesting(self)
        data = {
            "time": self.df["date"].tolist(),
            "yield": self.df["yield"].tolist(),
            "growth": self.df["growth"].tolist(),
            "water": self.df["water"].tolist(),
            "overlap": self.df["overlap"].tolist(),
            "map": self.df["map"].tolist(),
            "boundary": self.df["boundary"].tolist(),
            "weed": self.df["weed"].tolist(),
        }
        index_of_last_instance = len(self.df) - 1
        last_instance = self.df.iloc[index_of_last_instance]
        return data, last_instance

    def record_data(
        self,
        date,
        size,
        growth_rate,
        water_level,
        overlap,
        size_layer,
        boundary,
        weed_size_layer,
    ):
        """
        Records the current state of the simulation into the DataFrame.

        Parameters
        ----------
        date : str
            The current date of the simulation.
        size : float
            The total size of the crops.
        growth_rate : float
            The sum of the growth rates of the crops.
        water_level : float
            The total water level in the simulation area.
        overlap : float
            The sum of overlaps for the crops.
        size_layer : list
            A list representing the size of crops at each position.
        boundary : list
            A list representing the boundary of the crops.
        weed_size_layer : list
            A list representing the size of weeds at each position.
        """
        new_row = pd.DataFrame(
            [
                [
                    str(date),
                    size,
                    growth_rate,
                    water_level,
                    overlap,
                    size_layer,
                    boundary,
                    weed_size_layer,
                ]
            ],
            columns=self.df.columns,
        )
        self.df = pd.concat([self.df, new_row], ignore_index=True)


def main(input_data):
    """
    {'startDate': '2022-09-30',
    'numIterations': 1,
    'stepSize': 1,
    'rowLength': 31,
    'rows': [{
        'plantType': 'lettuce',
        'plantingType': 'grid',
        'stripWidth': 30,
        'rowSpacing': 15}]}
    """
    # Initialize a variable to hold any second values that are not -1
    if isinstance(input_data["startDate"], list):
        second_values = {}
        # Helper function to handle the values
        def process_value(key, value):
            # Check if the value is a list
            if isinstance(value, list):
                if isinstance(value[0], dict):
                    return value[0]
                first_value = value[0]
                second_value = value[1]
                # If the second value is not -1, store it for further use
                if second_value != -1:
                    second_values[key] = second_value
                return first_value  # Return the first value from the list
            return value  # Return the value as it is if it's not a list
        # Process each key-value pair in input_data
        usable_input_data = {}
        for key, value in input_data.items():
            if isinstance(value[0], dict):  # If it's a nested structure like 'rows'
                usable_input_data[key] = []
                for sub_value in value:
                    processed_row = {k: process_value(k, v) for k, v in sub_value.items()}
                    usable_input_data[key].append(processed_row)
            else:
                usable_input_data[key] = process_value(key, value)

        key, second_value = next(iter(second_values.items()))  # Extract the key and second value
        print(input_data)
        #if the first value is not found in inpurdata check in rows
        if key not in input_data:
            for row in input_data["rows"]:
                if key in row:
                    first_value = row[key][0]
                    break
        else:
            first_value = input_data[key][0]

        all_data = []
        all_last_instances = []

        # Run simulations for the range of param_values
        for param_value in range(first_value, second_value + 1):
            usable_input_data[key] = param_value
            sim = Simulation(usable_input_data)
            data, last_instance = sim.run_simulation()
            
            # Dynamically replace the key name
            all_data.append({
                key: param_value,  # Replace 'param_value' with the fitting key dynamically
                "data": data,
            })
            all_last_instances.append({
                key: param_value,  # Replace 'param_value' with the fitting key dynamically
                "last_instance": last_instance,
            })
            print(f"Simulation for {key}={param_value} completed.")
        
        print("All simulations completed.")
        return all_data, all_last_instances, usable_input_data

    else:
        # If no lists are found, run a single simulation
        sim = Simulation(input_data)
        data, last_instance = sim.run_simulation()
        usable_input_data = input_data

    return data, last_instance, usable_input_data