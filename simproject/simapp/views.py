from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from .scripts.calculate import main  # Ensure this function exists and is correct
from .scripts.add_initial_data_to_db import add_initial_weather_data_to_db, add_initial_plant_data_to_db
import json
from .models import  DataModelOutput, SimulationIteration
from .models import Weather, Plant,DataModelInput
from django.shortcuts import redirect
from django.contrib import messages



def index(request):
    simulations = DataModelInput.objects.all().values_list('simName', flat=True)
    print(simulations)
    return render(request, 'simapp/index.html',{"simulations": simulations})


def run_simulation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)
    simulation_name = request.POST.get('simName')
    if DataModelInput.objects.filter(simName=simulation_name).exists():
        print("Simulation name already exists. Please choose a different name.")
        messages.error(request, 'Simulation name already exists. Please choose a different name.')
        return redirect('index')  # Redirect to the main page or the form page

    try:
        data = json.loads(request.body.decode('utf-8'))  # Ensure this is where you intend to get your data
        # Assume that `main(data)` runs your simulation and does not return a value
        # Insert code to add weather and plant data if not present
        if Weather.objects.count() == 0:
            add_initial_weather_data_to_db()
        if Plant.objects.count() == 0:
            add_initial_plant_data_to_db()

        main(data)  # This will process your data and presumably save results
        # Return the name of the simulation after it runs
        return JsonResponse({'name': data["simName"]})

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format")






def get_simulation_data(request):
    simulation_name = request.GET.get('name', None)
    if not simulation_name:
        return JsonResponse({'error': 'No simulation name provided'}, status=400)
    
    try:
        # Fetch all iterations linked to the specified simulation name via the input relationship
        iterations = SimulationIteration.objects.filter(input__simName=simulation_name)

        data_by_iteration = []
        for iteration in iterations:
            # Fetch outputs for each iteration
            outputs = DataModelOutput.objects.filter(iteration=iteration).order_by('date')
            iteration_data = {
                "iteration_index": iteration.iteration_index,
                "param_value": iteration.param_value,
                "outputs": []
            }

            for output in outputs:
                output_data = {
                    "date": output.date,
                    "yield": output.yield_value,
                    "growth": output.growth,
                    "water": output.water,
                    "overlap": output.overlap,
                    "map": output.map,
                    "weed": output.weed
                }
                iteration_data["outputs"].append(output_data)
            data_by_iteration.append(iteration_data)

        return JsonResponse(data_by_iteration, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


