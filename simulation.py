import random
import pandas as pd
from datetime import datetime, timedelta
import json
import threading
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
import mplcursors

############################################################################################################
# This file contains the classes and functions that are used to simulate the growth of plants in the field #
############################################################################################################


class Farm:
    def __init__(self, name):
        self.name = name
        self.fields = []

    def start_simulation(self, start_date, end_date):
        for field in self.fields:
            field.plant_plants()
            ############################################################################################################
            field.fig, field.ax = plt.subplots()  # Create the plot outside the loop
            field.ax.set_title(f"Field {field.name}, date: {start_date}")
            ## Brown, Green, Orange, Yellow
            cmap = ListedColormap(["#994c00", "#008000", "#FFA500", "#FFFF00"])
            field.im = field.ax.imshow(
                np.zeros((len(field.plants), len(field.plants[0]))),
                cmap=cmap,
                interpolation="nearest",
                vmin=0,
                vmax=3,
            )
            plt.colorbar(
                field.im,
                ticks=[0, 1, 2, 3],
                label="Plant Type",
                format=plt.FuncFormatter(
                    lambda val, loc: ["Empty", "Crop", "Fieldvetch", "Jacobsragwort",""][
                        int(val)
                    ]
                ),
            )
            field.ax.grid(True, which="major", color="black", linewidth=0.5)
            field.ax.set_xticks(np.arange(0, len(field.plants[0]), 1), minor=False)
            field.ax.set_yticks(np.arange(0, len(field.plants), 1), minor=False)
            # add axis labels rotated by 90 degrees starting from 0 to the length of the field
            field.ax.set_xticklabels(
                np.arange(0, len(field.plants[0]), 1), rotation=90, fontsize=6
            )
            field.ax.set_yticklabels(
                np.arange(0, len(field.plants), 1), rotation=0, fontsize=6
            )

            plt.ion()  # Turn on interactive mode

            ############################################################################################################

        hour_step = timedelta(hours=1)
        current_date = start_date
        while current_date <= end_date:
            date = current_date.strftime("%Y-%m-%d %H:00:00")
            debug_print("#############################################")
            debug_print(f"Simulation at {date}")
            debug_print("#############################################")
            current_date += hour_step

    def query_weather_data_by_date(csv_file, query_date):
        steanm_pressure = query_specific_value_by_date(
            csv_file, query_date, "Dampfdruck in hPa"
        )
        wet_temperature = query_specific_value_by_date(
            csv_file, query_date, "Feuchttemperatur in °C"
        )
        global_radiation = query_specific_value_by_date(
            csv_file, query_date, "Globalstrahlung in J/cm²"
        )
        air_temperature = query_specific_value_by_date(
            csv_file, query_date, "Lufttemperatur in °C"
        )
        wind_speed = query_specific_value_by_date(
            csv_file, query_date, "Windstärke in km/h"
        )
        rain = query_specific_value_by_date(csv_file, query_date, "Niederschlag in mm")
        weather_data = [
            query_date,
            steanm_pressure,
            wet_temperature,
            global_radiation,
            air_temperature,
            wind_speed,
            rain,
        ]
        return weather_data

            for field in self.fields:
                field.simulate(
                    query_weather_data_by_date("transformed_weather_data.csv", date),
                    field,
                )
                field.weeding(current_date)
        input("Press Enter to close the simulation")

    def farm_to_json_async(
        self,
    ):
        thread = threading.Thread(target=self._farm_to_json)
        thread.start()

    def _farm_to_json(self):
        with open("farm.json", "w") as file:
            json.dump(self.to_dict(), file, indent=4)


class Field:
    def __init__(self, name, length, width, crop, proportion, waterlevel, soiltype):
        self.name = name
        self.length = length  # length of the field in meters
        self.width = width  # width of the field in meters
        self.crop = crop  # crop that is planted on the field
        self.proportion = (
            proportion  # proportion of the field that is planted with the crop
        )
        self.plants = []  # list of plants on the field
        self.harvested_plants = []  # list of harvested plants
        self.waterlevel = waterlevel  # waterlevel in the soil All one Field has one waterlevel which is the same for all plants
        self.soiltype = soiltype  # soiltype of the field
        debug_print(
            f'Crop: {crop.plant["name"]}, Proportion: {proportion}, Waterlevel: {waterlevel}, Soiltype: {soiltype.name}'
        )

    def plant_plants(self):
        debug_print("##########PLANTING##########")
        for i in range(self.length):
            row = []
            for j in range(self.width):
                if (i % self.crop.plant["row_distance"] == 0 or i == 0) and (
                    j % self.crop.plant["plant_distance"] == 0 or j == 0
                ):
                    if random.random() < self.proportion:
                        plant = Crop(self.crop.plant, i, j)
                        row.append(plant)
                        debug_print(
                            f' {self.crop.plant["name"]} at x:{plant.x_coordinate}, y:{plant.y_coordinate}'
                        )
                    else:
                        plant = Crop({"name": "Empty"}, i, j)
                        row.append(plant)
                        debug_print(
                            f" Empty at x:{plant.x_coordinate}, y:{plant.y_coordinate}"
                        )
                else:
                    plant = Crop({"name": "Empty"}, i, j)
                    row.append(plant)
                    debug_print(
                        f" Empty at x:{plant.x_coordinate}, y:{plant.y_coordinate}"
                    )
            self.plants.append(row)
        debug_print("###########################")




    def weeding(self, date):
        intervall = 2
        if date.day % intervall == 0:
            if date.hour == 0:
                for row in self.plants:
                    for plant in row:
                        if any(plant.plant["name"] == weed.plant["name"] for weed in weed_list):
                            if random.randint(0, 100) < 10 * plant.bbch:
                                plant.plant = {"name": "Empty"}
                                plant.bbch = 0
                                debug_print(
                                    f'Weeded{plant.plant["name"]} at x:{plant.x_coordinate}, y:{plant.y_coordinate}'
                                )

    def simulate(self, weatherdata, field):
        field.weeding(weatherdata[0])
        for row in self.plants:
            for plant_in_row in row:
                if plant_in_row.plant["name"] == "Empty":
                    debug_print(
                        f"Empty{plant_in_row.plant} at x:{plant_in_row.x_coordinate}, y:{plant_in_row.y_coordinate}"
                    )
                    plant_in_row = plant_in_row.weed_germination(weatherdata[0])
                else:
                    debug_print(
                        f"Plant at x:{plant_in_row.x_coordinate}, y:{plant_in_row.y_coordinate}, crop: {plant_in_row.plant['name']}, with BBCH: {round(plant_in_row.bbch,2)}, Waterlevel: {self.waterlevel}, Soiltype: {self.soiltype.name}"
                    )
                    soil_water = plant_in_row.grow(weatherdata, field)
                    self.waterlevel = soil_water

        debug_print("###########################")
        for row in self.plants:
            for plant_in_row in row:
                if plant_in_row.plant in Crop_list:
                    debug_print(
                        f"Plant at x:{plant_in_row.x_coordinate}, y:{plant_in_row.y_coordinate}, crop: {self.crop.plant['name']}, with BBCH: {round(plant_in_row.bbch,2)}, Waterlevel: {self.waterlevel}, Soiltype: {self.soiltype.name}"
                    )
                elif plant_in_row.plant in weed_list:
                    debug_print(
                        f"Weed at x:{plant_in_row.x_coordinate}, y:{plant_in_row.y_coordinate}, : {plant_in_row.bbch}, Waterlevel: {self.waterlevel}, Soiltype: {self.soiltype.name}"
                    )
                elif plant_in_row.plant == "Empty":
                    debug_print(
                        f"{plant_in_row.plant} at x:{plant_in_row.x_coordinate}, y:{plant_in_row.y_coordinate}"
                    )
                else:
                    debug_print("Error: Unknown plant type")
        debug_print("###########################")
        # Update the plot
        if datetime.strptime(weatherdata[0], "%Y-%m-%d %H:%M:%S").hour % 1 == 0:
            plants_data = self.plot_plants_on_field(weatherdata[0])
            self.im.set_data(plants_data)
            plt.pause(0.01)
            return self.plants

    ### Plot the plants on the field
    def plot_plants_on_field(self, date):
        data = np.zeros((len(self.plants), len(self.plants[0])))
        # create a heading with the current date
        self.ax.set_title(f"Field {self.name},date: {date}")
        for i in range(len(self.plants)):
            for j in range(len(self.plants[0])):
                plant = self.plants[i][j]
                if plant.plant["name"] != "Empty":
                    radius = plant.calculate_radius_from_bbch() - 1
                    start_x = max(0, i - radius)
                    end_x = min(len(self.plants), i + radius + 1)
                    start_y = max(0, j - radius)
                    end_y = min(len(self.plants[0]), j + radius + 1)
                    for x in range(start_x, end_x):
                        for y in range(start_y, end_y):
                            if (x - i) ** 2 + (y - j) ** 2 <= radius**2:
                                data[x][y] = (
                                    1
                                    if plant.plant["name"] == "Carrot"
                                    else 2
                                    if plant.plant["name"] == "Field Vetch"
                                    else 3
                                )
        return data



class Crop:
    def __init__(self, plant, x_coordinate=-1, y_coordinate=-1):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.plant = plant  ####plant beinhaltet die Spezifischen Parameter der Pflanze, sollte jeder parameter in einem eigenen Attribut gespeichert werden?
        self.bbch = 0
        self.pests = {}
        self.illnesses = {}

    ### Function to simulate the growth of the plant
    def grow(self, weatherdata, field):
        plant_factor = self.plant["growth_speed"]
        # self.check_pests()
        # self.check_illnesses()

        wed_factor = self.check_weed_impact(field)
        wtr_factor, soil_water = self.check_waterlevel(
            weatherdata, field.waterlevel, field.soiltype
        )
        tmp_factor = self.check_temperature(weatherdata[4])
        # self.check_fertilization()
        self.bbch += (
            plant_factor * wtr_factor * tmp_factor * wed_factor * random.random()
        )
        self.check_harvest()
        self.check_overgrowth(field)

        return soil_water


    ### Function to simulate the germination of a weed
    def weed_germination(self, timestring):
        timestring = str(timestring)
        date_obj = datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S")
        start_of_year = datetime(date_obj.year, 1, 1)
        date = (date_obj - start_of_year).days + 1
        for weed in weed_list:
            if True:  # weed.plant.get('earliest_appearance') <= date <= weed.plant.get('latest_appearance'):
                if random.randint(0, 50000) == 1:
                    self.germination_date = date
                    # debug_print(f'{emptyplant} at x:{self.x_coordinate}, y:{self.y_coordinate}')
                    # Deleting the plant object
                    # debug_print(f'{plant} at x:{self.x_coordinate}, y:{self.y_coordinate}')
                    self.plant = weed.plant
                    debug_print(
                        f"{weed.plant['name']} germinated at x:{self.x_coordinate}, y:{self.y_coordinate}"
                    )
        return self

    ### Function to check if the plant is overgrown
    def check_overgrowth(self, field):
        # Get index of current field
        field_index = farm.fields.index(field)
        radius = self.calculate_radius_from_bbch()
        # Check all plants in the radius if they are overgrown in a circle around the plant
        for i in range(self.x_coordinate - radius, self.x_coordinate + radius):
            for j in range(self.y_coordinate - radius, self.y_coordinate + radius):
                if 0 <= i < len(farm.fields[field_index].plants) and 0 <= j < len(
                    farm.fields[field_index].plants[0]
                ):
                    if (
                        farm.fields[field_index].plants[i][j].plant["name"] != "Empty"
                        and (i - self.x_coordinate) ** 2 + (j - self.y_coordinate) ** 2
                        <= radius**2
                    ):
                        # Check if the crop is fully under the plant
                        if (
                            radius
                            < Crop.calculate_radius_from_bbch(
                                farm.fields[field_index].plants[i][j]
                            )
                            and random.randint(0, 100) < 50
                        ):
                            old_plant = self.plant["name"]
                            self.plant = {"name": "Empty"}
                            self.bbch = 0
                            debug_print(
                                f"{old_plant}, overgrown at x:{self.x_coordinate}, y:{self.y_coordinate}, by {farm.fields[field_index].plants[i][j].plant['name']} at x:{i}, y:{j}"
                            )

    def check_harvest(self, harvested_plants=[]):
        if not self.plant["is_weed"]:
            if self.bbch >= self.plant["harvest_at"]:
                self.plant = {"name": "Empty"}
                self.bbch = 0
                debug_print(
                    f"Harvested at x:{self.x_coordinate}, y:{self.y_coordinate}"
                )
                harvested_plants.append(self)

    def calculate_radius_from_bbch(self):
        bbch = self.bbch
        stage1 = self.plant["stage1"]
        stage2 = self.plant["stage2"]
        stage3 = self.plant["stage3"]
        stage4 = self.plant["stage4"]

        if bbch <= stage1["BBCH"]:
            fct = bbch / stage1["BBCH"]
            radius = fct * stage1["radius"]
        elif bbch <= stage2["BBCH"]:
            fct = (bbch - stage1["BBCH"]) / (stage2["BBCH"] - stage1["BBCH"])
            radius = stage1["radius"] + fct * (stage2["radius"] - stage1["radius"])
        elif bbch <= stage3["BBCH"]:
            fct = (bbch - stage2["BBCH"]) / (stage3["BBCH"] - stage2["BBCH"])
            radius = stage2["radius"] + fct * (stage3["radius"] - stage2["radius"])
        elif bbch <= stage4["BBCH"]:
            fct = (bbch - stage3["BBCH"]) / (stage4["BBCH"] - stage3["BBCH"])
            radius = stage3["radius"] + fct * (stage4["radius"] - stage3["radius"])
        else:
            # If bbch is greater than stage4["BBCH"], the radius raises with the same rate as stage4["radius"]
            radius = stage4["radius"] + (bbch - stage4["BBCH"])
        radius = int(radius + 0.5)
        if radius < 1:
            radius = 1
        return radius

    ### Function to check if the plant is surrounded by weeds
    def check_weed_impact(self, field):
        # Check if the plant is surrounded by weeds
        field_index = farm.fields.index(field)
        total_overlap = 0
        xcoord = self.x_coordinate
        ycoord = self.y_coordinate
        radius = self.calculate_radius_from_bbch()
        length = farm.fields[field_index].length
        width = farm.fields[field_index].width

        for i in range(xcoord - radius * 2, xcoord + radius * 2):
            for j in range(ycoord - radius * 2, ycoord + radius * 2):
                if 0 <= i < length and 0 <= j < width:
                    # Check if the found plant overlaps with the current plant
                    if (
                        farm.fields[field_index].plants[i][j].plant["name"] != "Empty"
                        and (i - xcoord) ** 2 + (j - ycoord) ** 2 <= radius**2
                    ):
                        if not (i == xcoord and j == ycoord):
                            # Calculate the overlapping area
                            plant_radius = (
                                farm.fields[field_index]
                                .plants[i][j]
                                .calculate_radius_from_bbch()
                            )
                            overlap_radius = (
                                radius
                                + plant_radius
                                - ((i - xcoord) ** 2 + (j - ycoord) ** 2) ** 0.5
                            )
                            if overlap_radius > 0:
                                # Increment the total overlap
                                total_overlap += overlap_radius
        # Calculate the weed factor
        weed_fct = 1 - (total_overlap / radius)
        if weed_fct < 0:
            weed_fct = 0
        debug_print(f"weed_fct: {weed_fct}")
        return weed_fct


    ### Function to check if the has the required temperature
    def check_temperature(self, temp):  # is the temperature in the optimal range
        min_temp = self.plant["min_growth_temperature"]
        max_temp = self.plant["max_growth_temperature"]
        optimal_temp = self.plant["optimal_growth_temperature"]
        if temp == optimal_temp:
            factor = 1
        elif temp >= max_temp:
            factor = 0
        elif temp <= min_temp:
            factor = 0
        else:
            factor = (temp - min_temp) / (max_temp - min_temp)
        return factor

    def check_waterlevel(self, weatherdata, field, soil_thickness=30):
        # Extract date and convert it to datetime object
        date = str(weatherdata[0])
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

        # Determine irrigation amount based on the current hour and irrigation frequency
        if date_obj.hour % datainput["irrigation_frequency"] == 0:
            irrigation = (
                datainput["irrigation_amount"] * datainput["irrigation_duration"]
            )
        else:
            irrigation = 0

        # Extract and convert weather data values
        steam_pressure = weatherdata[1] * 0.1  # Convert hPa to kPa
        wet_temperature = weatherdata[2]  # in °C
        global_radiation = weatherdata[3] * 0.1  # Convert J/cm² to MJ/m²
        air_temperature = weatherdata[4]  # in °C
        wind_speed = weatherdata[5]  # in m/s
        Kc_Value = self.get_kc_value()  # Crop coefficient
        rain = weatherdata[6]  # in mm

        # Calculate Evapotranspiration using a simplified formula
        Evapotranspiration = (
            0.480
            * (steam_pressure / wet_temperature)
            * (global_radiation + 0.066)
            * (900 / (air_temperature + 273))
            * wind_speed
        ) / ((steam_pressure / wet_temperature) + 0.066 * (1 + 0.34 * wind_speed))

        # Calculate water usage
        waterusage = Evapotranspiration * Kc_Value

        # Debug print statements for tracing values

        # Update water level
        # units mm            mm         mm/h     mm/h         mm/h
        waterlevel = field.waterlevel + rain + irrigation - waterusage

        # Check if water level exceeds field capacity (FC) or permanent wilting point (PWP)
        if waterlevel > soil_thickness * field.soiltype.FK / 10:
            waterlevel = (
                soil_thickness * field.soiltype.FK / 10
            )  # Set water level to max
        elif waterlevel < soil_thickness * field.soiltype.PWP / 10:
            waterlevel = (
                soil_thickness * field.soiltype.PWP / 10
            )  # Set water level to min

        # Calculate the factor based on optimal water level
        optimal_water = self.plant["optimal_water"]
        FK = field.soiltype.FK / 10 * soil_thickness
        PWP = field.soiltype.PWP / 10 * soil_thickness

        if waterlevel == optimal_water:
            factor = 1
        elif waterlevel >= FK:
            factor = 0
        elif waterlevel <= PWP:
            factor = 0
        else:
            factor = (waterlevel - PWP) / (FK - PWP)

        # Update field water level
        field.waterlevel = waterlevel
        return factor

    def get_kc_value(self):
        if self.bbch <= self.plant["stage1"]["BBCH"]:
            return self.plant["stage1"]["Kc"]
        elif self.bbch <= self.plant["stage2"]["BBCH"]:
            return self.plant["stage2"]["Kc"]
        elif self.bbch <= self.plant["stage3"]["BBCH"]:
            return self.plant["stage3"]["Kc"]
        elif self.bbch <= self.plant["stage4"]["BBCH"]:
            return self.plant["stage4"]["Kc"]
        else:
            print(f"Error: Unknown BBCH value, at Plant: {self.plant['name']}")
            return 0


class SoilType:
    def __init__(self, name, nKF, FK, PWP, category):
        self.name = name  # Name of the soil
        self.nKF = nKF  # useabel Field capacity in mm  bzw.  L/m²
        self.FK = FK  # Field capacity in mm (soil is full of water the ovrflow is lost)
        self.PWP = (
            PWP  # Permanent wilting point in mm(plant cant extract water anymore)
        )
        self.categorie = category


def query_specific_value_by_date(csv_file, query_date, column_name):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        df["Date"] = pd.to_datetime(df["Date"])

        # Query the specific value
        queried_row = df.loc[df["Date"] == query_date]
        specific_value = queried_row[column_name].values[0]
        return specific_value
    except FileNotFoundError:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"File {csv_file} not found.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return None
    except IndexError:
        return None


############################################################################################################
# Chracteristics of the plants and the soil
############################################################################################################
carrotCharakteristics = {
    "name": "Carrot",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": False,
    "needs_irrigation": True,
    "optimal_soil": "Sand",
    "growth_speed": 10,  ##0.0291666, #bbch per hour
    "harvest_at": 49,  # BBCH to harvest
    "max_temperature": 25,
    "min_temperature": -15,
    "earliest_sowing_time": 30,
    "latest_sowing_time": 100,
    "min_growth_temperature": 4,
    "max_growth_temperature": 30,
    "optimal_growth_temperature": 20,
    "optimal_water": 40,
    "row_distance": 10,
    "plant_distance": 10,
    "optimal_ph": 6,
}
cut_lettuceCharakteristics = {
    "name": "Cut Lettuce",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65},
    "is_weed": False,
    "needs_irrigation": True,
    "optimal_soil": "Sand",
    "max_temperature": 25,
    "min_temperature": -15,
    "earliest_sowing_time": 30,
    "latest_sowing_time": 100,
    "min_growth_temperature": 4,
    "max_growth_temperature": 30,
    "optimal_growth_temperature": 20,
    "row_distance": 15,
    "plant_distance": 3,
    "optimal_ph": 6,
}
FrenchherbCharacteristics = {  ##Franzosenkraut
    "name": "French Herb",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
JacobsragwortCharacteristics = {  ##Jakobs-Greiskraut
    "name": "Jacobsragwort",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_water": 30,
    "optimal_soil": "sand",
    "growth_speed": 1.5,  # 0.021666, #bbch per hour
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
thistleCharacteristics = {  ##Distel
    "name": "Thistle",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
CouchGrassCharacteristics = {  ##Quecke
    "name": "Couch Grass",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
ChickweedCharacteristics = {  ##Voegelmiere
    "name": "Chick weed",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}

ReportCharacteristics = {  ##Melde
    "name": "Report",
    "stage1": {"Kc": 0.3, "depth": 30, "BBCH": 9, "radius": 0.5},
    "stage2": {"Kc": 0.6, "depth": 30, "BBCH": 15, "radius": 4},
    "stage3": {"Kc": 0.8, "depth": 60, "BBCH": 43, "radius": 10},
    "stage4": {"Kc": 1.0, "depth": 60, "BBCH": 65, "radius": 15},
    "is_weed": True,
    "impact": "Bad",
    "optimal_soil": "sand",
    "growth_speed": 1.2,  # 0.0391666, #bbch per hour
    "optimal_water": 45,
    "optimal_ph": 6,
    "max_high": 80,  # cm
    "max_width": 15,  # Radius des Beschatteten Bereichs
    "waterusage": 0.125,  # mm/Stunde
    "earliest_appearance": "03-01",
    "latest_appearance": "11-30",
    "growth_period": 75,  # days
    "optimal_growth_temperature": 20,
    "min_growth_temperature": 5,
    "max_growth_temperature": 30,
}
################################################################################################################
# Crops
carrot = Crop(carrotCharakteristics)
cut_lettuce = Crop(cut_lettuceCharakteristics)
# Weeds
Couchgrass = Crop(CouchGrassCharacteristics)
Thistle = Crop(thistleCharacteristics)
Frenchherb = Crop(FrenchherbCharacteristics)
Chickweed = Crop(ChickweedCharacteristics)
Jacobsragwort = Crop(JacobsragwortCharacteristics)
Report = Crop(ReportCharacteristics)
weed_list = [Frenchherb, Jacobsragwort, Thistle, Couchgrass, Chickweed, Report]
Crop_list = ["Carrot", "cut_lettuce"]
# Soil
sand = SoilType("Sand", 9, 15, 1, "light")
slightly_loamy_sand = SoilType("Slightly Loamy Sand", 13, 15, 1, "light")
strong_loamy_sand = SoilType("Strong Loamy Sand", 16, 15, 1, "medium")
sandy_loam = SoilType("Sandy Loam", 19, 40, 10, "medium")
silty_clay = SoilType("Silty Clay", 22, 40, 10, "medium")
clayey_loam = SoilType("Clayey Loam", 17, 40, 10, "heavy")
clay = SoilType("Clay", 14, 60, 25, "heavy")
peat = SoilType("Peat", 30, 60, 25, "heavy")
# Pests
aphids = {
    "name": "Aphids",
    "period": "04-01:11-01",
    "majorperiod": "01-05;30-06",
    "impact": 3,
    "EndangeredCrop": "RedCabage",
    "min_temperature": 10,
    "max_temperature": 35,
}
thrips = {
    "name": "Thrips",
    "period": "06-10:08-31",
    "majorperiod": "15.07-15.08",
    "impact": 3,
    "EndangeredCrop": "WhiteCabage",
    "min_temperature": 10,
    "max_temperature": 35,
}
CabbageWhiteButterfly = {
    "name": "Cabbage White Butterfly",
    "period": "05-01:09-15",
    "majorperiod": "01.06-31.07",
    "impact": 2,
    "min_temperature": 10,
    "max_temperature": 35,
}
Cabbagefly = {
    "name":"Cabbagefly",
    "period":"15.04-15.05",
    "period":"15.06-15.10",
    "majorperiod":"15.04-15.05",
    "impact":3,

}
# Illnesses
Bacterialsoftrot = {
    "name":"Bacterial soft rot",
    "period":"",
    "impact":2,
}
Leafspot = {
    "name":"Leaf spot",
    "period":"",
    "impact":1,
}
# Falscher Mehltau
Mildew = {
    "name":" Mildew",
    "period":"01.05-01.10",
    "majorperiod":"01.05-01.08",
    "impact":2,
}
# Kohlhernie
Clubroot = {
    "name":"Clubroot",
    "period":"01.05-01.10",
    "majorperiod":"01.05-01.08",
    "impact":3,
}
# Ringfleckenkrankheit
RingSpotDisease = {
    "name":" Ring spot disease",
    "period":"01.05-01.10",
    "majorperiod":"01.05-01.08",
    "impact":3,
}
############################################################################################################
# Input data
############################################################################################################
datainput = {
    "Farmname": "MyFarm",
    "Fieldname": "Field_001",
    "length": 50,
    "width": 50,
    "crop": carrot,
    "cropproportion": 1,
    "soiltype": silty_clay,
    "groundthickness": 30,
    "startdate": "2023-05-30 00:00:00",
    "enddate": "2023-10-30 00:00:00",
    "debugmode": False,
    "irrigation_amount": 2,  # mm/m²*h
    "irrigation_frequency": 3,  # 1 times evry 7 hours
    "irrigation_duration": 2,  # h
    "beginning_waterlevel": 40,
    "number_of_fields": 1,
}
############################################################################################################
# Simulation
############################################################################################################


Farm.start_simulation()
