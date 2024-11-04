import os
import csv
from django.conf import settings
from django.db.models import Avg
from simapp.models import DataModelInput, DataModelOutput

def export_simulation_comparison_data_to_csv():
    # Set the directory to save CSV files
    output_dir = os.path.join(settings.BASE_DIR, 'simulation_exports')
    os.makedirs(output_dir, exist_ok=True)

    # Fetch all simulations
    simulations = DataModelInput.objects.all()
    
    for simulation in simulations:
        # Prepare the filename with the simulation name
        filename = f"{simulation.simName}_comparison.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Define the headers based on the comparison plot
        headers = [
            "param_value", "profit_per_plant", "profit_per_area", "yield_per_plant",
            "growth_per_plant", "yield_per_area", "growth_per_area", "number_of_plants",
            "mean_growth", "yield", "profit"
        ]
        
        # Check if the file already exists to avoid rewriting headers
        file_exists = os.path.isfile(filepath)

        # Write data to CSV with specified formatting
        with open(filepath, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers, delimiter=';')
            
            # Write the header only if the file is newly created
            if not file_exists:
                writer.writeheader()

            # Helper function to format decimal numbers with a comma
            def format_decimal(value):
                if isinstance(value, float):
                    return f"{value:.2f}".replace('.', ',')
                return value

            # Process each iteration and export the data
            iterations = simulation.iterations.all()
            for iteration in iterations:
                last_output = DataModelOutput.objects.filter(iteration=iteration).last()
                mean_growth = DataModelOutput.objects.filter(iteration=iteration).aggregate(Avg('growth'))['growth__avg']
                area = last_output.map[0].__len__() * last_output.map.__len__()
                param_value = iteration.param_value

                # Prepare row with formatted values
                row = {
                    "param_value": format_decimal(param_value),
                    "profit_per_plant": format_decimal(last_output.profit / last_output.num_plants if last_output.num_plants else None),
                    "profit_per_area": format_decimal(last_output.profit / area * 10000 if area else None),
                    "yield_per_plant": format_decimal(last_output.yield_value / last_output.num_plants if last_output.num_plants else None),
                    "growth_per_plant": format_decimal(mean_growth / last_output.num_plants if last_output.num_plants else None),
                    "yield_per_area": format_decimal(last_output.yield_value / area * 10000 if area else None),
                    "growth_per_area": format_decimal(mean_growth / area * 10000 if area else None),
                    "number_of_plants": last_output.num_plants,
                    "mean_growth": format_decimal(mean_growth),
                    "yield": format_decimal(last_output.yield_value),
                    "profit": format_decimal(last_output.profit)
                }
                
                writer.writerow(row)

        print(f"Exported {filename} with {iterations.count()} iterations")

# Run the export function
export_simulation_comparison_data_to_csv()
