from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from .scripts.calculate import main  # Ensure this function exists and is correct
from .scripts.add_initial_data_to_db import add_initial_weather_data_to_db, add_initial_plant_data_to_db
import json
from .models import  DataModelOutput, SimulationIteration
from .models import Weather, Plant,DataModelInput
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .forms import PlantForm
from django.http import StreamingHttpResponse
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
        return redirect('index')  

    try:
        data = json.loads(request.body.decode('utf-8'))  # Ensure this is where you intend to get your data
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





from django.http import StreamingHttpResponse
import json

def get_simulation_data(request):
    simulation_name = request.GET.get('name', None)
    
    if not simulation_name:
        return JsonResponse({'error': 'No simulation name provided'}, status=400)
    
    def data_generator():
        iterations = SimulationIteration.objects.filter(input__simName=simulation_name).order_by('iteration_index')
        for iteration in iterations:
            iteration_data = {
                "iteration_index": iteration.iteration_index,
                "param_value": iteration.param_value,
                "outputs": [
                    {
                        "date": output.date,
                        "yield": output.yield_value,
                        "growth": output.growth,
                        "water": output.water,
                        "overlap": output.overlap,
                        "map": output.map,
                        "weed": output.weed,
                        "time_needed": output.time_needed,
                        "profit": output.profit,
                        "rain": output.rain,
                        "temperature": output.temperature,
                        "num_plants": output.num_plants,
                    }
                    for output in DataModelOutput.objects.filter(iteration=iteration).order_by('date')
                ]
            }
            yield json.dumps(iteration_data) + '\n'  # Füge eine neue Zeile hinzu

    response = StreamingHttpResponse(data_generator(), content_type="application/x-ndjson")
    return response







def plant_list(request):
    plants = Plant.objects.all()
    return render(request, 'simapp/plants/list.html', {'plants': plants})

def plant_manage(request, plant_id=None):
    print("HERE")
    if plant_id:
        plant = get_object_or_404(Plant, pk=plant_id)
        print(plant)
    else:
        print("HEdRE")
        plant = None

    if request.method == 'POST':
        form = PlantForm(request.POST, instance=plant)
        if form.is_valid():
            form.save()
            return redirect(reverse('plant_list'))
    else:
        form = PlantForm(instance=plant)

    return render(request, 'simapp/plants/manage.html', {'form': form, 'plant': plant})

def plant_delete(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)
    plant.delete()
    return redirect(reverse('plant_list'))