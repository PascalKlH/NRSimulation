from django.shortcuts import render,redirect
from django.http import JsonResponse, HttpResponseBadRequest
from .scripts.calculate import main  # Ensure this function exists and is correct
import json


def index(request):
    return render(request, 'simapp/index.html')

def run_simulation(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))
            
            # Perform any processing needed, for example:
            result = main(data)  # Ensure this function returns data for plotting
            
            return JsonResponse(result, safe=False)  # Sending result as JSON for client-side processing
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format")
    else:
        return JsonResponse({'error': 'POST request required'}, status=405)




