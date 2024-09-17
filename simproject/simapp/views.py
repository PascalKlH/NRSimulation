from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from .scripts.calculate import main  # Ensure this function exists and is correct
import json
from .models import DataModelInput,DataModelOutputDetails,DataModelOutput
import pandas as pd


def index(request):
    return render(request, 'simapp/index.html')

def run_simulation(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))
            
            # Perform any processing needed, for example:
            result,last = main(data)  
            # Ensure this function returns data for plotting
            data_instance = DataModelInput()
            data_instance.set_data(data)
            data_instance.save()
          
            last_instance = DataModelOutput()
            last_instance.set_data(last)
            last_instance.save()
            
            result_instance = DataModelOutputDetails()
            result_instance.set_data(result)
            result_instance.save()

            


            
            return JsonResponse(result, safe=False)  # Sending result as JSON for client-side processing
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format")
    else:
        return JsonResponse({'error': 'POST request required'}, status=405)



def plot_simulation(request):
    # Fetch data
    inputs = DataModelInput.objects.all()
    outputs = DataModelOutput.objects.all()
    
    # Prepare data for plotting
    input_data = []
    output_data = []
    
    for input_record, output_record in zip(inputs, outputs):
        input_data.append({
            'rowLength': input_record.rowLength
        })
        output_data.append({
            'yield': output_record.yield_value
        })
    
    # Convert to DataFrame for easier manipulation
    df_inputs = pd.DataFrame(input_data)
    df_outputs = pd.DataFrame(output_data)
    
    # Merge DataFrames on index or other key if necessary
    df = pd.concat([df_inputs, df_outputs], axis=1)
    
    # Prepare data for template
    context = {
        'data': df.to_dict(orient='records')
    }
    
    return render(request, 'simapp/plot_simulation.html', context)
