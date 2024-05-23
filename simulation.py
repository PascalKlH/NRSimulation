import random
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

############################################################################################################
# This file contains the classes and functions that are used to simulate the growth of plants in the field #
############################################################################################################


class Farm:
    def __init__(self, name):
        self.name = name
        self.fields = []

    def start_simulation(self, start_date, end_date):
        for field in self.fields:
            field.plant_plants(start_date)
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
                    csv_file, query_date, "Globalstrahlung in J/m²"
                )
                air_temperature = query_specific_value_by_date(
                    csv_file, query_date, "Lufttemperatur in °C"
                )
                wind_speed = query_specific_value_by_date(
                    csv_file, query_date, "Windstärke in km/h"
                )
                rain = query_specific_value_by_date(
                    csv_file, query_date, "Niederschlag in mm"
                )
                weather_data = [
                    date,
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
                #End Simulation if all plants are harvested
                if all(plant.plant in Crop_list for row in field.plants for cell in row for plant in cell):
                    input("All plants are harvested")
                    print(field.harvested_plants)
                    break
        input("Press Enter to close the simulation")

    def create_field(self, name, length, width, crop, proportion, waterlevel, soiltype):
        field = Field(name, length, width, crop, proportion, waterlevel, soiltype)
        self.fields.append(field)


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

    def plant_plants(self, start_date):
        debug_print("##########PLANTING##########")
        self.plants = []  # Initialize or clear the field grid
        for i in range(self.length):
            row = []
            debug_print(f"Row {i}")
            for j in range(self.width):
                cell = []
                if (i % self.crop.plant["row_distance"] == 0 or i == 0) and (j % self.crop.plant["plant_distance"] == 0 or j == 0):
                    if random.random() < self.proportion:
                        plant = Crop(self.crop.plant, i, j, start_date)
                        cell.append(plant)
                        debug_print(f'{self.crop.plant["name"]} at x:{plant.x_coordinate}, y:{plant.y_coordinate}')
                    else:
                        plant = Crop({"name": "Empty"}, i, j)
                        cell.append(plant)
                        debug_print(f" Empty at x:{plant.x_coordinate}, y:{plant.y_coordinate}")
                else:
                    plant = Crop({"name": "Empty"}, i, j)
                    cell.append(plant)
                    debug_print(f" Empty at x:{plant.x_coordinate}, y:{plant.y_coordinate}")
                row.append(cell)  # Append the cell to the row
            self.plants.append(row)  # Append the row to the field grid
        debug_print("###########################")




    def weeding(self, date):
        intervall = 10
        if date.day % intervall == 0:
            if date.hour == 0:
                for row in self.plants:
                    for cell in row:
                        for plant in cell:
                            if any(plant.plant["name"] == weed.plant["name"] for weed in weed_list):
                                if random.randint(0, 100) < 10 * plant.bbch:
                                    # Weeding logic
                                    radius = plant.calculate_radius_from_bbch()
                                    for i in range(plant.x_coordinate - radius, plant.x_coordinate + radius + 1):
                                        for j in range(plant.y_coordinate - radius, plant.y_coordinate + radius + 1):
                                            if 0 <= i < len(self.plants) and 0 <= j < len(self.plants[0]):
                                                for weeded_plant in self.plants[i][j]:
                                                    if weeded_plant.x_coordinate == plant.x_coordinate and weeded_plant.y_coordinate == plant.y_coordinate:
                                                        weeded_plant.plant = {"name": "Empty"}
                                                        weeded_plant.bbch = 0
                                                        weeded_plant.harvested_yields = 0
                                                        weeded_plant.illnesses = []
                                                        weeded_plant.pests = {}
                                                        weeded_plant.sowing_date = -1
                                                        debug_print(
                                                            f'Weeded {plant.plant["name"]} at x:{plant.x_coordinate}, y:{plant.y_coordinate}'
                                                        )
                                                        break  # Exit loop after updating the plant

    def simulate(self, weatherdata, field):
        for row in self.plants:
            for cell in row:
                for plant_in_cell in cell:
                    if plant_in_cell.plant["name"] == "Empty":
                        debug_print(
                            f"Empty{plant_in_cell.plant} at x:{plant_in_cell.x_coordinate}, y:{plant_in_cell.y_coordinate}"
                        )
                        plant_in_cell = plant_in_cell.weed_germination(weatherdata[0])
                    elif plant_in_cell.plant["name"] != "Empty":
                        debug_print(
                            f"Plant at x:{plant_in_cell.x_coordinate}, y:{plant_in_cell.y_coordinate}, crop: {plant_in_cell.plant['name']}, with BBCH: {round(plant_in_cell.bbch,2)}, Waterlevel: {self.waterlevel}, Soiltype: {self.soiltype.name}"
                        )
                        soil_water = plant_in_cell.grow(weatherdata, field)
                        self.waterlevel = soil_water
                    else:
                        print(f"Error: Unknown plant type at x:{plant_in_cell.x_coordinate}, y:{plant_in_cell.y_coordinate}")


        debug_print("###########################")
        # Update the plot if the hour is 23
        if datetime.strptime(weatherdata[0], "%Y-%m-%d %H:%M:%S").hour % 23 == 0:
            plants_data = self.plot_plants_on_field(weatherdata[0])
            self.im.set_data(plants_data)
            plt.pause(0.01)
        return self.plants

    def plot_plants_on_field(self, date):
            data = np.zeros((len(self.plants), len(self.plants[0])))
            # Create a heading with the current date
            self.ax.set_title(f"Field {self.name}, date: {date}")
            for i in range(len(self.plants)):
                for j in range(len(self.plants[0])):
                    # Check each plant in the list at position [i][j]
                    for plant in self.plants[i][j]:
                        if plant.plant["name"] != "Empty":
                            if plant.plant["name"] == "Carrot":
                                data[i][j] = 1
                            elif plant.plant["name"] == "Field Vetch":
                                data[i][j] = 2
                            else:
                                data[i][j] = 3
                            break  # If there's at least one non-empty plant, break the inner loop
            return data



class Crop:
    def __init__(self, plant, x_coordinate=-1, y_coordinate=-1,sow_date =-1):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.plant = plant  ####plant beinhaltet die Spezifischen Parameter der Pflanze, sollte jeder parameter in einem eigenen Attribut gespeichert werden?
        self.bbch = 0
        self.pests = {}
        self.illnesses = []
        self.sowing_date = sow_date
        havested_yields = 0

    ### Function to simulate the growth of the plant
    def grow(self, weatherdata, field):
            plant_factor = self.plant["growth_speed"]
            self.check_pests(weatherdata)
            self.check_illnesses(weatherdata, field)

            wed_factor = self.check_weed_impact(field)
            wtr_factor, soil_water = self.check_waterlevel(weatherdata, field.waterlevel, field.soiltype)
            tmp_factor = self.check_temperature(weatherdata[4])
            self.bbch += plant_factor * wtr_factor * tmp_factor * wed_factor * random.random()
            
            self.check_harvest(weatherdata[0], field)
            if self.plant["name"] != "Empty":
                self.check_overgrowth(field)
            
            if self.plant["name"] != "Empty":
                # Fill the Grid with the plant in the radius of the plant in a circular shape
                radius = self.calculate_radius_from_bbch() - 1
                for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
                    for j in range(self.y_coordinate - radius, self.y_coordinate + radius + 1):
                        if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                            if (i, j) != (self.x_coordinate, self.y_coordinate):
                                if (i - self.x_coordinate) ** 2 + (j - self.y_coordinate) ** 2 <= radius ** 2:
                                    # Make sure not to duplicate plants
                                    if self not in field.plants[i][j]:
                                        field.plants[i][j].append(self)
            return soil_water


    ### Function to simulate the germination of a weed
    def weed_germination(self, timestring):
        timestring = str(timestring)
        date_obj = datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S")
        date_str = timestring.split()[0]  # Extract date part from weather data
        date = datetime.strptime(date_str, "%Y-%m-%d")
        month_day = (date.month, date.day)
        #reconert month_day into datetime object to compare with the start and end date               
        month_day = datetime.strptime(str(month_day[0]) + "-" + str(month_day[1]), "%m-%d")
        if random.randint(0, 50000) == 1:
            for weed in weed_list:
                if datetime.strptime(weed.plant['earliest_appearance'],"%m-%d") <=month_day <=  datetime.strptime(weed.plant['latest_appearance'],"%m-%d"):


                    # debug_print(f'{emptyplant} at x:{self.x_coordinate}, y:{self.y_coordinate}')
                    # Deleting the plant object
                    # debug_print(f'{plant} at x:{self.x_coordinate}, y:{self.y_coordinate}')
                    self.plant = weed.plant
                    debug_print(
                        f"{weed.plant['name']} germinated at x:{self.x_coordinate}, y:{self.y_coordinate}"
                    )
        return self
    def check_pests(self,weatherdata,field):
        if len(self.pests) == 0:
            
            possible_pests = []

            for pest in pest_list:
                #convert daterange string into start and end date string: 15.04-15.05 -> 15.04 and 15.05, than convert into datetime object to compare with the weatherdata
                start_date_str, end_date_str = pest["period"].split(":")
                start_date = datetime.strptime(start_date_str, "%m-%d")
                end_date = datetime.strptime(end_date_str, "%m-%d")
                #calculate the temperature factor if between the min and max temperature factor =1, if below min temperature factor = 0, if above max
                max_temperature = pest["max_temperature"]
                min_temperature= pest["min_temperature"]
                current_temperature = weatherdata[4]
                # Calculate the difference (range) between max and min temperatures
                temperature_range = max_temperature - min_temperature
                if current_temperature < min_temperature:
                    # Below min_temperature, calculate the factor linearly
                    temperature_factor = max(0, 1 - (min_temperature - current_temperature) / temperature_range)
                elif current_temperature > max_temperature:
                    # Above max_temperature, calculate the factor linearly
                    temperature_factor = max(0, 1 - (current_temperature - max_temperature) / temperature_range)
                else:
                    # Within the range
                    temperature_factor = 1
                # Extract month and day from weather data
                date_str = weatherdata[0].split()[0]  # Extract date part from weather data
                date = datetime.strptime(date_str, "%Y-%m-%d")
                month_day = (date.month, date.day)
                #reconert month_day into datetime object to compare with the start and end date
                month_day = datetime.strptime(str(month_day[0]) + "-" + str(month_day[1]), "%m-%d")

                if start_date <= month_day <= end_date:
                    if pest["min_temperature"] <= weatherdata[4] <= pest["max_temperature"]:
                        possible_pests.append(pest)
            if len(possible_pests) == 0:
                pass
            else:
                pest = random.choice(possible_pests)
                if random.randint(0, 100000) < weatherdata[5]*temperature_factor:
                    self.pest.append(pest["name"])
                    debug_print(
                        f"Illness {pest['name']} at x:{self.x_coordinate}, y:{self.y_coordinate}"
                    )
        else:
            print(self.pests)
            #check for all overlaping plants
            radius = self.calculate_radius_from_bbch()
            for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
                for j in range(self.y_coordinate - radius, self.y_coordinate + radius + 1):
                    if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                        for plant in field.plants[i][j]:
                            if plant!= self:
                                if plant.plant["name"] != "Empty":
                                    if random.randint(0, 1000) < weatherdata[5]:
                                        field.plants[plant.x_coordinate][plant.y_coordinate][0].pests.append(self.pests)
                                        input("T")
                                        for pest in field.plants[plant.x_coordinate][plant.y_coordinate][0].pests:
                                            debug_print(
                                                f"Illness {pest} at x:{plant.x_coordinate}, y:{plant.y_coordinate}"
                                            )

        
    def check_illnesses(self, weatherdata,field):
        if len(self.illnesses) == 0:
            
            possible_illnesses = []

            for illness in illness_list:
                #convert daterange string into start and end date string: 15.04-15.05 -> 15.04 and 15.05, than convert into datetime object to compare with the weatherdata
                start_date_str, end_date_str = illness["period"].split(":")
                start_date = datetime.strptime(start_date_str, "%m-%d")
                end_date = datetime.strptime(end_date_str, "%m-%d")
                #calculate the temperature factor if between the min and max temperature factor =1, if below min temperature factor = 0, if above max
                max_temperature = illness["max_temperature"]
                min_temperature= illness["min_temperature"]
                current_temperature = weatherdata[4]
                # Calculate the difference (range) between max and min temperatures
                temperature_range = max_temperature - min_temperature
                if current_temperature < min_temperature:
                    # Below min_temperature, calculate the factor linearly
                    temperature_factor = max(0, 1 - (min_temperature - current_temperature) / temperature_range)
                elif current_temperature > max_temperature:
                    # Above max_temperature, calculate the factor linearly
                    temperature_factor = max(0, 1 - (current_temperature - max_temperature) / temperature_range)
                else:
                    # Within the range
                    temperature_factor = 1
                # Extract month and day from weather data
                date_str = weatherdata[0].split()[0]  # Extract date part from weather data
                date = datetime.strptime(date_str, "%Y-%m-%d")
                month_day = (date.month, date.day)
                #reconert month_day into datetime object to compare with the start and end date
                month_day = datetime.strptime(str(month_day[0]) + "-" + str(month_day[1]), "%m-%d")

                if start_date <= month_day <= end_date:
                    if illness["min_temperature"] <= weatherdata[4] <= illness["max_temperature"]:
                        possible_illnesses.append(illness)
            if len(possible_illnesses) == 0:
                pass
            else:
                illness = random.choice(possible_illnesses)
                if random.randint(0, 100000) < weatherdata[5]*temperature_factor:
                    self.illnesses.append(illness["name"])
                    debug_print(
                        f"Illness {illness['name']} at x:{self.x_coordinate}, y:{self.y_coordinate}"
                    )
        else:
            print(self.illnesses)
            #check for all overlaping plants
            radius = self.calculate_radius_from_bbch()
            for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
                for j in range(self.y_coordinate - radius, self.y_coordinate + radius + 1):
                    if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                        for plant in field.plants[i][j]:
                            if plant!= self:
                                if plant.plant["name"] != "Empty":
                                    if random.randint(0, 1000) < weatherdata[5]:
                                        field.plants[plant.x_coordinate][plant.y_coordinate][0].illnesses.append(self.illnesses)
                                        input("T")
                                        for ill in field.plants[plant.x_coordinate][plant.y_coordinate][0].illnesses:
                                            debug_print(
                                                f"Illness {ill} at x:{plant.x_coordinate}, y:{plant.y_coordinate}"
                                            )

    ### Function to check if the plant is overgrown
    def check_overgrowth(self, field):
        radius = self.calculate_radius_from_bbch()
        not_overgrown_spots = 0
        for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
            for j in range(self.y_coordinate - radius, self.y_coordinate + radius + 1):
                if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                    if len(field.plants[i][j]) <2 :
                        not_overgrown_spots =+1
        if not_overgrown_spots == 0:
            debug_print(f"Plant{self.plant["name"]} at x:{self.x_coordinate}, y:{self.y_coordinate} is overgrown. Press Enter to continue.") 
            for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
                for j in range(self.y_coordinate - radius, self.y_coordinate + radius + 1):
                    if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                        for plant in field.plants[i][j]:
                            if plant.x_coordinate == self.x_coordinate and plant.y_coordinate == self.y_coordinate:
                                plant.plant = {"name": "Empty"}
                                plant.bbch = 0
                                plant.harvested_yields = 0
                                plant.illnesses = []
                                plant.pests = {}
                                plant.sowing_date = -1
    def check_harvest(self, current_date, field):
        if not self.plant["is_weed"]:
            if self.bbch >= self.plant["harvest_at"]:
                optimal_growing_time = self.plant["growth_speed"] * self.plant["harvest_at"]
                # Calculate the actual growing time
                growing_time = (datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S") - self.sowing_date).days
                yield_loss_factor = ((growing_time * 24) / optimal_growing_time) / 10
                harvest_yield = self.plant["harvest_yield"] * yield_loss_factor
                self.harvested_yields = harvest_yield
                debug_print(f"Harvested at x:{self.x_coordinate}, y:{self.y_coordinate}")
                field.harvested_plants.append(self)
                sum_yield = 0
                for plants in field.harvested_plants:
                    print(plants.harvested_yields)
                    sum_yield += plants.harvested_yields
                radius = self.calculate_radius_from_bbch()
                for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
                    for j in range(self.y_coordinate - radius, self.y_coordinate + radius + 1):
                        if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                            cell = field.plants[i][j]
                            for crop in cell:
                                if crop.x_coordinate == self.x_coordinate and crop.y_coordinate == self.y_coordinate:
                                    crop.plant = {"name": "Empty"}
                                    crop.bbch = 0
                                    crop.harvested_yields = 0
                                    crop.illnesses = []
                                    crop.pests = {}
                                    crop.sowing_date = -1
                self.plant = {"name": "Empty"}
                self.bbch = 0
                self.illnesses = []
                self.pests = {}
                self.sowing_date = -1
                self.harvested_yields = 0
        return field.harvested_plants


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
                    # Iterate over each Crop instance in the cell
                    #print(f"i: {i}, j: {j}{field.plants}")
                    for crop_instance in farm.fields[field_index].plants[i][j]:
                        # Check if the found plant is not empty
                        if crop_instance.plant["name"] != "Empty":
                            # Check if the found plant overlaps with the current plant
                            if (i - xcoord) ** 2 + (j - ycoord) ** 2 <= radius ** 2:
                                if not (i == xcoord and j == ycoord):
                                    # Calculate the overlapping area
                                    plant_radius = crop_instance.calculate_radius_from_bbch()
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
        if weed_fct <= 0:
            weed_fct = 0.1
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

    ### Function to check if the Field has the required water level
    def check_waterlevel(self, weatherdata, waterlevel, soiltype, soil_thickness=30):
        date = str(weatherdata[0])
        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        if date_obj.hour % datainput["irrigation_frequency"] == 0:
            irrigation = (
                datainput["irrigation_ammount"] * datainput["irrigation_duration"]
            )
        else:
            irrigation = 0

        steam_pressure = weatherdata[1]
        wet_temperature = weatherdata[2]
        global_radiation = weatherdata[3]
        air_temperature = weatherdata[4]
        wind_speed = weatherdata[5]
        Kc_Value = self.get_kc_value()
        rain = weatherdata[6]
        Evapotranspiration = (
            0.480
            * ((steam_pressure / 10) / wet_temperature)
            * ((global_radiation / 10000) + 0.066)
            * (900 / (air_temperature + 273))
            * wind_speed
        ) / (
            ((steam_pressure / 10) / wet_temperature) + 0.066 * (1 + 0.34 * wind_speed)
        )
        waterusage = Evapotranspiration * Kc_Value
        waterlevel = waterlevel + rain + irrigation - waterusage
        # values per 10 cm of soil
        if (
            waterlevel > soil_thickness * soiltype.FK / 10
        ):  # soil is full of water the ovrflow is lost
            waterlevel = (
                soil_thickness * soiltype.FK / 10
            )  # set waterlevel to the maximum
        elif (
            waterlevel < soil_thickness * soiltype.PWP / 10
        ):  # soil ist dryed out the Plant cant extract any water
            waterlevel = (
                soil_thickness * soiltype.PWP / 10
            )  # set waterlevel to the minimum
        optimal_water = self.plant["optimal_water"]
        Fk = soiltype.FK / 10 * 30
        PWP = soiltype.PWP / 10 * 30
        if waterlevel == optimal_water:
            factor = 1
        elif waterlevel >= Fk:
            factor = 0
        elif waterlevel <= PWP:
            factor = 0
        else:
            factor = (waterlevel - PWP) / (Fk - PWP)
        return factor, waterlevel

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
        debug_print(f"No data found for the date {query_date}.")
        return None


def debug_print(*args, **kwargs):
    debug_mode = datainput["debugmode"]
    if debug_mode:
        print(*args, **kwargs)


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
    "harvest_yield" : 0.1, #Kg/plant
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
FrenchherbCharacteristics  = { ##Franzosenkraut
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
JacobsragwortCharacteristics = {##Jakobs-Greiskraut
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
thistleCharacteristics  = {##Distel
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
CouchGrassCharacteristics  = {##Quecke
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
ChickweedCharacteristics  = {##Voegelmiere
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
    "name": "Report ",
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




Couchgrass= Crop(CouchGrassCharacteristics)
Thistle = Crop(thistleCharacteristics)
Frenchherb = Crop(FrenchherbCharacteristics)
Chickweed = Crop(ChickweedCharacteristics )
Jacobsragwort = Crop(JacobsragwortCharacteristics)
Report = Crop(ReportCharacteristics )
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
#Pests
aphids = {
    "name":"Aphids",
    "period":"01.04-01.11",
    'majorperiod':'01.05-30.06',
    "impact":3,
    "EndangeredCrop":"RedCabage",
}
thrips = {
    "name":"Thrips",
    "period":"01.06-31.08",
    'majorperiod':'15.07-15.08',
    "impact":3,
    "EndangeredCrop":"WhiteCabage",
}
CabbageWhiteButterfly = {
    "name":"Cabbage White Butterfly",
    "period":"01.05-15.09",
    'majorperiod':'01.06-31.07',
    "impact":2,
}
Cabbagefly = {
    "name":"Cabbagefly",
    "period":"15-04,15-05",
    "period":"15-06,15-10",
    "majorperiod":"15-04,15-05",
    "impact":3,

}
#Illnesses
Bacterialsoftrot = {
    "name":"Bacterial soft rot",
    "period":"05-01:10-01",
    "impact":2,
    "min_temperature": 20,
    "max_temperature": 30,
}
Leafspot = {
    "name":"Leaf spot",
    "period":"05-01:10-01",
    "impact":1,
    "min_temperature": 20,
    "max_temperature": 30,
}
#Falscher Mehltau
Mildew = {
    "name":" Mildew",
    "period":"05-01:10-01",
    "majorperiod":"01-05:01-08",
    "impact":2,
    "min_temperature": 15,
    "max_temperature": 25,
}
#Kohlhernie
Clubroot = {
    "name":"Clubroot",
    "period":"05-01:10-01",
    "majorperiod":"01-05:01-08",
    "impact":3,
    "min_temperature": 18,
    "max_temperature": 25,
}
#Ringfleckenkrankheit 
RingSpotDisease = {
    "name":" Ring spot disease",
    "period":"05-01:10-01",
    "majorperiod":"01-05:01-08",
    "impact":3,
    "min_temperature": 15,
    "max_temperature": 25,
}
illness_list = [Bacterialsoftrot, Leafspot, Mildew, Clubroot, RingSpotDisease]
############################################################################################################
# Input data
############################################################################################################
datainput = {
    "Farmname": "MyFarm",
    "Fieldname": "Field_001",
    "length": 50,
    "width": 30,
    "crop": carrot,
    "cropproportion": 1,
    "soiltype": silty_clay,
    "groundthickness": 30,
    "startdate": "2023-05-30 00:00:00",
    "enddate": "2023-10-30 00:00:00",
    "debugmode": False,
    "irrigation_ammount": 0.05,  # mm/irrigation
    "irrigation_frequency": 7,  # 1 times evry 7 hours
    "irrigation_duration": 1,  # h
}
############################################################################################################
# Simulation
############################################################################################################
farm = Farm(datainput["Farmname"])
farm.create_field(
    datainput["Fieldname"],
    datainput["length"],
    datainput["width"],
    datainput["crop"],
    datainput["cropproportion"],
    random.uniform(
        datainput["soiltype"].PWP / 10 * datainput["groundthickness"],
        datainput["soiltype"].FK / 10 * datainput["groundthickness"],
    ),
    datainput["soiltype"],
)
"""
farm.create_field(
    "Field_002",
    datainput["length"],
    datainput["width"],
    datainput["crop"],
    datainput["cropproportion"],
    random.uniform(
        datainput["soiltype"].PWP / 10 * datainput["groundthickness"],
        datainput["soiltype"].FK / 10 * datainput["groundthickness"],
    ),
    datainput["soiltype"],
)"""
farm.start_simulation(
    datetime.strptime(datainput["startdate"], "%Y-%m-%d %H:00:00"),
    datetime.strptime(datainput["enddate"], "%Y-%m-%d %H:%M:%S"),
)
