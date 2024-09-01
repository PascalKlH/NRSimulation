from django.shortcuts import render
from django.http import JsonResponse
<<<<<<< HEAD
from .forms import SimulationForm
=======
from .forms import SimulationForm, FieldRowForm
>>>>>>> a8b6987e74094664ade0de6a902412d782cfb234
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
<<<<<<< HEAD
=======
            print(result)
>>>>>>> a8b6987e74094664ade0de6a902412d782cfb234
            # Here you might save the results or prepare them for rendering
            return JsonResponse(result,safe=False)  # Sending result as JSON for client-side processing

    else:
        form = SimulationForm()

    return render(request, 'simapp/index.html', {'form': form})
<<<<<<< HEAD
=======

def configure_field(request):
    if request.method == 'POST':
        # Handle form submission
        formset = FieldRowForm(request.POST)
        if formset.is_valid():
            # Process form data here
            # You can save to the database or send to calculate.py
            pass
    else:
        formset = FieldRowForm()
    
    return render(request, 'configure_field.html', {'formset': formset})
>>>>>>> a8b6987e74094664ade0de6a902412d782cfb234
