from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from .scripts.calculate import main  # Ensure this function exists and is correct
import json
from .models import DataModelInput,DataModelOutput,SimulationIteration,Simulation,RowDetail


def index(request):
    return render(request, 'simapp/index.html')


def run_simulation(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            # Run the main simulation logic, which handles both testing and non-testing mode
            result, last_instance, usable_input_data = main(data)

            # Create and save the input data instance
            input_instance = DataModelInput()
            input_instance.set_data(usable_input_data)
            input_instance.save()

            # Save row details for each row in usable_input_data['rows']
            for row in usable_input_data['rows']:
                row_instance = RowDetail()
                row_instance.set_data(row)
                row_instance.input_data = input_instance
                row_instance.save()

            # Create and save a new Simulation instance
            simulation_instance = Simulation(
                input=input_instance,
                tag="testing" if isinstance(last_instance, list) else "normal",  # Tagging to recognize if testing mode was enabled
                name = usable_input_data.get('simName')
            )
            simulation_instance.save()
            # Determine the key used for parameter variation (e.g., rowLength, stepSize)
            param_key = next(iter(result[0]))  # Get the key used for param_value (dynamic key)

            # Check if the result contains multiple iterations (testing mode)
            if isinstance(last_instance, list):  # Testing mode scenario
                # Loop over each result iteration and save the outputs
                for iteration_data in last_instance:
                    param_value = iteration_data[param_key]  # Dynamically access param_value using the dynamic key
                    iteration_results = iteration_data['last_instance']
                    
                    # Create and save a SimulationIteration for this iteration
                    iteration_instance = SimulationIteration(
                        simulation=simulation_instance,
                        iteration_index=param_value,
                        param_value=param_value  # Dynamically store the param_value
                    )
                    iteration_instance.save()
                    
                    # Save each individual result from this iteration
                    output_instance = DataModelOutput(
                        iteration=iteration_instance
                    )
                    output_instance.set_data(iteration_results)
                    output_instance.save()

                # Save the final output for the last iteration
                for last in last_instance:
                    param_value = last[param_key]  # Dynamically access param_value using the dynamic key
                    last_data = last['last_instance']

                    # Find the corresponding iteration and save the last output
                    iteration_instance = SimulationIteration.objects.filter(
                        simulation=simulation_instance,
                        param_value=param_value
                    ).first()

                    if iteration_instance:
                        last_output_instance = DataModelOutput(
                            iteration=iteration_instance
                        )
                        last_output_instance.set_data(last_data)
                        last_output_instance.save()

                return JsonResponse(result, safe=False)  # Return the list of results for testing mode

            else:  # Non-testing mode (single iteration)
                # Create a SimulationIteration for the single run
                iteration_instance = SimulationIteration(
                    simulation=simulation_instance,
                    iteration_index=0,  # Default iteration index
                    param_value=0  # No parameter variation
                )
                iteration_instance.save()

                # Save the last instance separately
                last_output_instance = DataModelOutput(iteration=iteration_instance)
                last_output_instance.set_data(last_instance)
                last_output_instance.save()

                return JsonResponse(result, safe=False)  # Return the result for non-testing mode
            
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format")
    else:
        return JsonResponse({'error': 'POST request required'}, status=405)






def get_simulation_results(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)
    try:
        data = json.loads(request.body)
        sim_name = data['simulation_name']
        simulation = Simulation.objects.get(name=sim_name)  # Assuming 'name' is the correct field
        outputs = DataModelOutput.objects.filter(iteration__simulation=simulation)

        results = [{
            'iteration_index': output.iteration.iteration_index,
            'yield_value': output.yield_value,
            'growth': output.growth,
            'water': output.water,
            'overlap': output.overlap,
            'map': output.map
        } for output in outputs]

        return JsonResponse({'results': results}, safe=False)

    except Simulation.DoesNotExist:
        return JsonResponse({'error': 'Simulation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def plot_simulation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        simulation_name = data.get('simulation_name')

        try:
            simulation = Simulation.objects.get(name=simulation_name)
            outputs = DataModelOutput.objects.filter(iteration__simulation=simulation)
            results = [output.get_data() for output in outputs]
            return JsonResponse({'results': results})
        except Simulation.DoesNotExist:
            return JsonResponse({'error': 'Simulation not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)