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

    def to_dict(self):
        return {"name": self.name, "Fields": [field.to_dict() for field in self.fields]}

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

    def start_simulation():
        farm = Farm(datainput["Farmname"])

        for i in range(datainput["number_of_fields"]):
            field = Field(
                datainput["Fieldname"],
                datainput["length"],
                datainput["width"],
                datainput["crop"],
                datainput["cropproportion"],
                datainput["beginning_waterlevel"],
                datainput["soiltype"],
            )
            farm.fields.append(field)

        for field in farm.fields:
            field.plant_plants(
                datetime.strptime(datainput["startdate"], "%Y-%m-%d %H:%M:%S")
            )
            field.create_plot()

        hour_step = timedelta(hours=1)
        current_date = datetime.strptime(datainput["startdate"], "%Y-%m-%d %H:%M:%S")
        while current_date <= datetime.strptime(
            datainput["enddate"], "%Y-%m-%d %H:%M:%S"
        ):
            #if current_date.hour == 0:
                #farm.farm_to_json_async()
            date = current_date.strftime("%Y-%m-%d %H:00:00")
            current_date += hour_step
            weather_data = Farm.query_weather_data_by_date(
                "transformed_weather_data.csv", date
            )
            for field in farm.fields:
                field.simulate_async(weather_data, field)
                plants_data, pests, illnesses = field.update_plot(weather_data[0])
                field.im_plants.set_data(plants_data)
                # field.im.set_data(pests)
                # field.im.set_data(illnesses)

            plt.pause(0.001)

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
    def simulate_async(self,wheatherdata,field):
        thread = threading.Thread(target=self.simulate(wheatherdata,field))
        thread.start()
    def to_dict(self):
        return {
            "name": self.name,
            "length": self.length,
            "width": self.width,
            "crop": self.crop.plant["name"],
            "proportion": self.proportion,
            "waterlevel": self.waterlevel,
            "soiltype": self.soiltype.name,
            "plants": [
                [[plant.to_dict() for plant in cell] for cell in row]
                for row in self.plants
            ],
            "harvested": [plant.to_dict() for plant in self.harvested_plants],
        }
    def create_plot(self):
        self.fig, self.ax = plt.subplots()  # Create the plot
        self.ax.set_title(f"Field {self.name}, date: {datainput['startdate']}")

        # Define color map for different categories
        cmap_plants = ListedColormap([
            "#994c00", "#008000", "#FFA500", "#FFFF00", "#FF0000", "#00FF00", "#00FFFF", "#0000FF", "#800000"
        ])

        cmap_pests = ListedColormap([
            "#000000", "#000000", "#000000", "#000000"  # Colors for different pests
        ])

        cmap_illnesses = ListedColormap([
            "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"  # Colors for different illnesses
        ])

        # Create separate arrays for each category
        plants_data, pests_data, illnesses_data = self.update_plot("")


        self.im_plants = self.ax.imshow(
            plants_data,  # Plant data
            cmap=cmap_plants,
            interpolation="nearest",
            vmin=0,
            vmax=8,  # Adjust according to the number of categories
        )


        # Define tick labels for the color bar
        tick_labels = [
            "Empty", "Carrot", "Frenchherb", "Jacobsragwort", "Thistle", "Couchgrass", "Chickweed", "Report"
        ]
        

        # Add color bars
        plt.colorbar(
            self.im_plants,
            ticks=range(len(tick_labels)),
            label="Plant Category",
            format=plt.FuncFormatter(lambda val, loc: tick_labels[int(val)]),
        )

        # Add legend for pests and illnesses
        self.ax.legend(['Pests', 'Illnesses'], loc='upper left')

        #self.ax.grid(True, which="major", color="black", linewidth=0.5)
        self.ax.set_xticks(np.arange(0, self.width, 1), minor=False)
        self.ax.set_yticks(np.arange(0, self.length, 1), minor=False)
        self.ax.set_xticklabels(
            np.arange(0, self.width, 1), rotation=90, fontsize=6
        )
        self.ax.set_yticklabels(
            np.arange(0, self.length, 1), rotation=0, fontsize=6
        )

        cursor = mplcursors.cursor(hover=True)

        @cursor.connect("add")
        def on_add(sel):
            i, j = int(sel.target[1]), int(sel.target[0])
            plants_at_location = self.plants[i][j]
            last_plant = plants_at_location[-1]  # Access the last element of the list
            sel.annotation.set(text=f"PLANT: {last_plant.plant['name']}\nIllnesses: {', '.join(ill['name'] for ill in last_plant.illnesses)}\nPests: {', '.join(pest['name'] for pest in last_plant.pests)}\nBBCH: {round(last_plant.bbch,2)}\nPlant Type: {last_plant.plant_type}")


        plt.ion()
        plt.show()


    def update_plot(self,date):
        #crate the array with tupels instead of zeros
        plants = np.zeros((len(self.plants), len(self.plants[0])))
        pests = np.zeros((len(self.plants), len(self.plants[0])))
        illnesses = np.zeros((len(self.plants), len(self.plants[0])))
        self.ax.set_title(f"Field {self.name}, date: {date} ")
        for i in range(len(self.plants)):
            for j in range(len(self.plants[0])):
                for plant in self.plants[i][j]:
                    if plant.plant["name"] != "Empty":
                        if plant.plant["name"] == "Carrot":
                            plants[i][j] = 1
                        elif plant.plant["name"] == "Frenchherb":
                            plants[i][j] = 2
                        elif plant.plant["name"] == "Jacobsragwort":
                            plants[i][j] = 3
                        elif plant.plant["name"] == "Thistle":
                            plants[i][j] = 4
                        elif plant.plant["name"] == "Couchgrass":
                            plants[i][j] = 5
                        elif plant.plant["name"] == "Chickweed":
                            plants[i][j] = 6
                        elif plant.plant["name"] == "Report":
                            plants[i][j] = 7
                        for pest in plant.pests:
                            if pest["name"] == "Apids":
                                pests[i][j] = 1
                            elif pest["name"] == "Thrips":
                                pests[i][j] = 2
                            elif pest["name"] == "CabbageWhiteButterfly":
                                pests[i][j] = 3
                            elif pest["name"] == "Cabbagefly":
                                pests[i][j] = 4
                            else:
                                pests[i][j] = 0
                        for ill in plant.illnesses:
                            if ill["name"] == "Bacterialsoftrot":
                                pests[i][j] = 1
                            elif ill["name"] == "Leafspot":
                                pests[i][j] = 2
                            elif ill["name"] == "Mildew":
                                pests[i][j] = 3
                            elif ill["name"] == "Clubroot":
                                pests[i][j] = 4
                            elif ill["name"] == "RingSpotDisease":
                                pests[i][j] = 5
                            else:
                                pests[i][j] = 0
        return plants, pests, illnesses


    def plant_plants(self, start_date):
        self.plants = []  # Initialize or clear the field grid
        for i in range(self.length):
            row = []
            for j in range(self.width):
                cell = []
                if (i % self.crop.plant["row_distance"] == 0 or i == 0) and (
                    j % self.crop.plant["plant_distance"] == 0 or j == 0
                ):
                    if random.random() < self.proportion:
                        plant = Crop(self.crop.plant, i, j, i, j, start_date, "Plant")
                        cell.append(plant)
                    else:
                        plant = Crop(
                            {"name": "Empty", "added": "planting"},
                            i,
                            j,
                            i,
                            j,
                            -1,
                            "Empty",
                        )
                        cell.append(plant)
                else:
                    plant = Crop(
                        {"name": "Empty", "added": "planting"}, i, j, i, j, -1, "Empty"
                    )
                    cell.append(plant)
                row.append(cell)  # Append the cell to the row
            self.plants.append(row)  # Append the row to the field grid

    def weeding(self, date):
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        intervall = 10
        if date.day % intervall == 0:
            if date.hour == 0:
                for row in self.plants:
                    for cell in row:
                        for plant in cell:
                            if any(
                                plant.plant["name"] == weed.plant["name"]
                                for weed in weed_list
                            ):
                                if random.randint(0, 100) < 10 * plant.bbch:
                                    # Weeding logic
                                    plant.delete_plant(self)

    def simulate(self, weatherdata, field):
        self.weeding(weatherdata[0])
        for row in self.plants:
            for cell in row:
                for plant_in_cell in cell:
                    if plant_in_cell.plant_type == "Empty":
                        plant_in_cell = plant_in_cell.weed_germination(weatherdata[0])
                    elif plant_in_cell.plant_type == "Plant":
                        plant_in_cell.grow(weatherdata, field)
                    elif plant_in_cell.plant_type == "leafs":
                        pass
                    else:
                        print(
                            f"Error: Unknown plant type at x:{plant_in_cell.x_coordinate}, y:{plant_in_cell.y_coordinate}  plant type: {plant_in_cell.plant_type},plant: {plant_in_cell.plant}"
                        )


class Crop:
    def __init__(
        self,
        plant,
        x_coordinate=-1,
        y_coordinate=-1,
        roots_x=-1,
        roots_y=-1,
        sow_date=-1,
        plant_type=None,
        pests=None,
        illnesses=None,
        bbch=0,
        harvested_yield_factor=1,
    ):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.roots_x = roots_x
        self.roots_y = roots_y
        self.plant = plant
        self.pests = pests if pests is not None else []
        self.bbch = bbch
        self.illnesses = illnesses if illnesses is not None else []
        self.sow_date = sow_date
        self.harvested_yield_factor = harvested_yield_factor
        self.harvested_yield = 0
        self.plant_type = plant_type

    def to_dict(self):
        return {
            "x": self.x_coordinate,
            "y": self.y_coordinate,
            "roots_x": self.roots_x,
            "roots_y": self.roots_y,
            "plant": self.plant,
            "bbch": self.bbch,
            "illness": self.illnesses,
            "pests": self.pests,
            "sowingdate": self.sow_date.strftime("%Y-%m-%d")
            if isinstance(self.sow_date, datetime)
            else self.sow_date,
            "harvested_yield": self.harvested_yield,
            "plant_type": self.plant_type,
        }

    ### Function to simulate the growth of the plant
    def grow(self, weatherdata, field):
        plant_factor = self.plant["growth_speed"]
        pst_factor = self.check_pests(weatherdata, field)
        ill_factor = self.check_illnesses(weatherdata, field)
        wed_factor = self.check_weed_impact(field)
        wtr_factor = self.check_waterlevel(weatherdata, field)
        tmp_factor = self.check_temperature(weatherdata[4])
        growth_factor =  wtr_factor* tmp_factor* wed_factor* pst_factor* ill_factor* random.random()
        self.bbch += (growth_factor * plant_factor)
        self.harvested_yield_factor = (growth_factor+self.harvested_yield_factor)/2
        self.check_harvest(field)
        if self.plant_type == "Plant":
            self.check_overgrowth(field)

        if self.plant_type == "Plant":
            # Fill the Grid with the plant in the radius of the plant in a circular shape
            radius = self.calculate_radius_from_bbch() - 1
            for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
                for j in range(
                    self.y_coordinate - radius, self.y_coordinate + radius + 1
                ):
                    if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                        if not (i == self.x_coordinate and j == self.y_coordinate):
                            if (i - self.x_coordinate) ** 2 + (
                                j - self.y_coordinate
                            ) ** 2 <= radius**2:
                                # Ensure the cell is not duplicated

                                new_plant = Crop(
                                    {
                                        "name":self.plant["name"],
                                        "added": 2,
                                    },
                                    i,
                                    j,
                                    self.roots_x,
                                    self.roots_y,
                                    self.sow_date,
                                    "leafs",
                                    self.pests,
                                    self.illnesses,
                                    self.bbch,
                                )
                                for plant in field.plants[i][j]:
                                    if (
                                        plant.roots_x == new_plant.roots_x
                                        and plant.roots_y == new_plant.roots_y
                                        and plant.plant_type == new_plant.plant_type
                                    ):
                                        break
                                else:
                                    field.plants[i][j].append(new_plant)
                                    break

    def delete_plant(self, field):
        radius = self.calculate_radius_from_bbch() + 1
        deleted_plants = []

        for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
            for j in range(self.y_coordinate - radius, self.y_coordinate + radius + 1):
                if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                    plants_to_remove = [
                        plant
                        for plant in field.plants[i][j]
                        if plant.roots_x == self.x_coordinate
                        and plant.roots_y == self.y_coordinate
                        and plant.plant_type != "Plant"
                    ]
                    for plant in plants_to_remove:
                        deleted_plants.append(plant)
                        field.plants[i][j].remove(plant)

        # Append self to deleted plants before modifying it
        deleted_plants.append(self)

        # Modify the attributes of self to indicate it's deleted
        self.plant = {"name": "Empty", "added": "deleting"}
        self.bbch = -1
        self.illnesses = []
        self.pests = []
        self.plant_type = "Empty"

    def check_sunlight(self, weatherdata):
        global_radiation = weatherdata[3]
        if global_radiation <= 0.055555:
            return 0
        else:
            return 1

    ### Function to simulate the germination of a weed
    def weed_germination(self, timestring):
        if self.plant["name"] == "Empty":
            timestring = str(timestring)
            date_str = timestring.split()[0]  # Extract date part from weather data
            date = datetime.strptime(date_str, "%Y-%m-%d")
            month_day = (date.month, date.day)
            # reconert month_day into datetime object to compare with the start and end date
            month_day = datetime.strptime(
                str(month_day[0]) + "-" + str(month_day[1]), "%m-%d"
            )
            possible_weeds = []
            if random.randint(0, 50000) == 1:
                for weed in weed_list:
                    if (
                        datetime.strptime(weed.plant["earliest_appearance"], "%m-%d")
                        <= month_day
                        <= datetime.strptime(weed.plant["latest_appearance"], "%m-%d")
                    ):
                        possible_weeds.append(weed)
                if len(possible_weeds) != 0:
                    weed = random.choice(possible_weeds)
                    self.plant = weed.plant
                    self.bbch = 0
                    self.pests = []
                    self.illnesses = []
                    self.sow_date = timestring
                    self.plant_type = "Plant"

            return self

    def check_pests(self, weatherdata, field):
        if len(self.pests) == 0:
            possible_pests = []

            for pest in pest_list:
                # convert daterange string into start and end date string: 15.04-15.05 -> 15.04 and 15.05, than convert into datetime object to compare with the weatherdata
                start_date_str, end_date_str = pest["period"].split(":")
                start_date = datetime.strptime(start_date_str, "%m-%d")
                end_date = datetime.strptime(end_date_str, "%m-%d")
                # calculate the temperature factor if between the min and max temperature factor =1, if below min temperature factor = 0, if above max
                max_temperature = pest["max_temperature"]
                min_temperature = pest["min_temperature"]
                current_temperature = weatherdata[4]
                # Calculate the difference (range) between max and min temperatures
                temperature_range = max_temperature - min_temperature
                if current_temperature < min_temperature:
                    # Below min_temperature, calculate the factor linearly
                    temperature_factor = max(
                        0,
                        1 - (min_temperature - current_temperature) / temperature_range,
                    )
                elif current_temperature > max_temperature:
                    # Above max_temperature, calculate the factor linearly
                    temperature_factor = max(
                        0,
                        1 - (current_temperature - max_temperature) / temperature_range,
                    )
                else:
                    # Within the range
                    temperature_factor = 1
                # Extract month and day from weather data
                date_str = weatherdata[0].split()[
                    0
                ]  # Extract date part from weather data
                date = datetime.strptime(date_str, "%Y-%m-%d")
                month_day = (date.month, date.day)
                # reconert month_day into datetime object to compare with the start and end date
                month_day = datetime.strptime(
                    str(month_day[0]) + "-" + str(month_day[1]), "%m-%d"
                )

                if start_date <= month_day <= end_date:
                    if (
                        pest["min_temperature"]
                        <= weatherdata[4]
                        <= pest["max_temperature"]
                    ):
                        possible_pests.append(pest)
            if len(possible_pests) == 0:
                pass
            else:
                pest = random.choice(possible_pests)
                if random.randint(0, 10000) < weatherdata[5] * temperature_factor:
                    self.pests.append(pest)
        else:
            # check for all overlaping plants
            plants_in_radius = self.get_all_plants_in_radius(field)
            if plants_in_radius:
                for plant in plants_in_radius:
                    if plant != self:
                        if random.randint(0, 100000) < weatherdata[5]:
                            for pest in self.pests:
                                if pest not in plant.pests:
                                    plant.pests.append(pest)
                                break
                    break

        impact = 0
        for pest in self.pests:
            impact = +pest["impact"]
        factor = 1 - impact * 0.1
        return factor

    def check_illnesses(self, weatherdata, field):
        if len(self.illnesses) == 0:
            possible_illnesses = []

            for illness in illness_list:
                start_date_str, end_date_str = illness["period"].split(":")
                start_date = datetime.strptime(start_date_str, "%m-%d")
                end_date = datetime.strptime(end_date_str, "%m-%d")

                max_temperature = illness["max_temperature"]
                min_temperature = illness["min_temperature"]
                current_temperature = weatherdata[4]

                temperature_range = max_temperature - min_temperature
                if current_temperature < min_temperature:
                    temperature_factor = max(0, 1 - (min_temperature - current_temperature) / temperature_range)
                elif current_temperature > max_temperature:
                    temperature_factor = max(0, 1 - (current_temperature - max_temperature) / temperature_range)
                else:
                    temperature_factor = 1

                date_str = weatherdata[0].split()[0]
                date = datetime.strptime(date_str, "%Y-%m-%d")
                month_day = (date.month, date.day)
                month_day = datetime.strptime(f"{month_day[0]}-{month_day[1]}", "%m-%d")

                if start_date <= month_day <= end_date:
                    if min_temperature <= current_temperature <= max_temperature:
                        possible_illnesses.append(illness)

            if possible_illnesses:
                illness = random.choice(possible_illnesses)
                if random.randint(0, 10000) < weatherdata[5] * temperature_factor:
                    self.illnesses.append(illness)
        else:
            # Check for all overlapping plants using get_all_plants_in_radius
            plants_in_radius = self.get_all_plants_in_radius(field)
            if plants_in_radius:
                for plant in plants_in_radius:
                    if plant != self:
                        if random.randint(0, 100000) < weatherdata[5]:
                            for ill in self.illnesses:
                                if ill not in plant.illnesses:
                                    plant.illnesses.append(ill)

        # Calculate the impact factor
        impact = sum(ill["impact"] for ill in self.illnesses)
        factor = 1 - impact * 0.1
        return factor

    ### Function to check if the plant is overgrown
    def check_overgrowth(self, field):
        surrounding_plants = self.get_all_plants_in_radius(field)

        # Überprüfe, ob alle umgebenden Pflanzen einen höheren BBCH-Wert haben
        if all(plant.bbch > self.bbch for plant in surrounding_plants):
            # Überprüfe, ob alle Felder, in denen die Pflanze wächst, mindestens eine weitere Pflanze haben
            has_other_plants = True
            for plant in surrounding_plants:
                if (
                    plant.roots_x == self.x_coordinate
                    and plant.roots_y == self.y_coordinate
                ):
                    if (
                        len([plant for plant in surrounding_plants if plant != self])
                        == 1
                    ):
                        has_other_plants = False
                        break

            if has_other_plants:
                self.delete_plant(field)

    def check_harvest(self, field):
        if not self.plant["is_weed"]:
            if self.bbch >= self.plant["harvest_at"]:
                self.harvested_yield = self.harvested_yield_factor*self.plant["harvest_yield"]
                field.harvested_plants.append(self)
                self.delete_plant(field)

    def get_all_plants_in_radius(self, field):
        radius = self.calculate_radius_from_bbch() - 1
        plants_in_radius = []
        if radius > 0:
            for i in range(self.x_coordinate - radius, self.x_coordinate + radius + 1):
                for j in range(
                    self.y_coordinate - radius, self.y_coordinate + radius + 1
                ):
                    if 0 <= i < len(field.plants) and 0 <= j < len(field.plants[0]):
                        if (i - self.x_coordinate) ** 2 + (j - self.y_coordinate) ** 2 <= radius**2:
                            for plant in field.plants[i][j]:
                                if plant.roots_x == self.roots_x and plant.roots_y == self.roots_y:
                                    if plant.plant_type != "Empty":
                                        plants_in_radius.extend(field.plants[i][j])
            return plants_in_radius
        else:
            return [self]

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
        plants_in_radius = self.get_all_plants_in_radius(field)
        return 1 / len(plants_in_radius)

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
    "row_distance": 5,
    "plant_distance": 5,
    "optimal_ph": 6,
    "harvest_yield": 0.1,  # Kg/plant
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
    "name": "Cabbagefly",
    "period": "04-15:05-15",
    "period2": "06-15:10-15",
    "majorperiod": "15-04,15-05",
    "impact": 3,
    "min_temperature": 10,
    "max_temperature": 35,
}
# Illnesses
Bacterialsoftrot = {
    "name": "Bacterial soft rot",
    "period": "05-01:10-01",
    "impact": 2,
    "min_temperature": 20,
    "max_temperature": 30,
}
Leafspot = {
    "name": "Leaf spot",
    "period": "05-01:10-01",
    "impact": 1,
    "min_temperature": 20,
    "max_temperature": 30,
}
# Falscher Mehltau
Mildew = {
    "name": " Mildew",
    "period": "05-01:10-01",
    "majorperiod": "01-05:01-08",
    "impact": 2,
    "min_temperature": 15,
    "max_temperature": 25,
}
# Kohlhernie
Clubroot = {
    "name": "Clubroot",
    "period": "05-01:10-01",
    "majorperiod": "01-05:01-08",
    "impact": 3,
    "min_temperature": 18,
    "max_temperature": 25,
}
# Ringfleckenkrankheit
RingSpotDisease = {
    "name": " Ring spot disease",
    "period": "05-01:10-01",
    "majorperiod": "01-05:01-08",
    "impact": 3,
    "min_temperature": 15,
    "max_temperature": 25,
}
pest_list = [aphids, thrips, CabbageWhiteButterfly, Cabbagefly]
illness_list = [Bacterialsoftrot, Leafspot, Mildew, Clubroot, RingSpotDisease]
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