from django.shortcuts import render
from django.http import JsonResponse
from .forms import SimulationForm
from .scripts.calculate import main  # Ensure this function exists and is correct

def index(request):
    form = SimulationForm()
    return render(request, 'simapp/index.html', {'form': form})

def run_simulation(request):
    if request.method == 'POST':
        form = SimulationForm(request.POST)
        if form.is_valid():
            # Extract data from the form
            data = form.cleaned_data

            # Call the simulation function
            result = main(data)  # Ensure this function returns data for plotting
            # Here you might save the results or prepare them for rendering
            return JsonResponse(result,safe=False)  # Sending result as JSON for client-side processing

    else:
        form = SimulationForm()

    return render(request, 'simapp/index.html', {'form': form})
