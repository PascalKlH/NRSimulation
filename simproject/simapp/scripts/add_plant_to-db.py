import os
import django
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simproject.settings')

# Initialize Django
django.setup()

from simapp.models import Plant

# Create plant instances
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
for plant_data in plants_data:
    print("Creating plant: ", plant_data["name"])
    Plant.objects.create(**plant_data)
