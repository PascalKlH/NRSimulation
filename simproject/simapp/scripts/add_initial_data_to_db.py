import os
import pandas as pd
from simapp.models import Plant, Weather
plants_data = [
    {
        "name": "lettuce",
        "W_max": 30,
        "H_max": 30,
        "k": 0.001,
        "n": 2,
        "max_moves": 5,
        "Yield": 0.8,
        "size_per_plant": 7068.3,
        "row_distance": 30,
        "column_distance": 30,
    },
    {
        "name": "cabbage",
        "W_max": 60,
        "H_max": 40,
        "k": 0.0005,
        "n": 2,
        "max_moves": 5,
        "Yield": 1.6,
        "size_per_plant": 9000.3,
        "row_distance": 60,
        "column_distance": 40,
    },
    {
        "name": "spinach",
        "W_max": 20,
        "H_max": 30,
        "k": 0.002,
        "n": 2,
        "max_moves": 5,
        "Yield": 0.4,
        "size_per_plant": 5068.3,
        "row_distance": 20,
        "column_distance": 30,
    },
    {
        "name": "weed",
        "W_max": 30,
        "H_max": 30,
        "k": 0.001,
        "n": 2,
        "max_moves": 5,
        "Yield": 0.8,
        "size_per_plant": 7068.3,
        "row_distance": 30,
        "column_distance": 30,
    },
]

# Save the data to the database
def add_initial_plant_data_to_db():
    print("Loading plant data...")
    for plant_data in plants_data:
        print("Creating plant: ", plant_data["name"])
        Plant.objects.create(**plant_data)



#check if the weather data is in the db

# Construct the path to the CSV file
def add_initial_weather_data_to_db():
    print("Loading weather data...")
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory where the script is located
    data_file = os.path.join(base_dir, 'data', 'transformed_weather_data.csv')  # Path to the CSV file
    print("Loading weather data...")
    try:
        df = pd.read_csv(data_file)
        for _, row in df.iterrows():
            weather_instance = Weather()
            weather_instance.set_data({
                'date': row['date'],
                'temperature': row['temperature'],
                'rain': row['rain']
            })
            weather_instance.save()

    except Exception as e:
        print(f'Error loading weather data: {e}')