#models.py
from django.db import models



class DataModelInput(models.Model):
    """
    Model to store input parameters for the simulation.

    Attributes
    ----------
    startDate : DateField
        The start date for the simulation.
    stepSize : IntegerField
        The time step size for the simulation.
    rowLength : IntegerField
        The length of each row in the simulation.
    testingMode : BooleanField
        A flag indicating whether the simulation is in testing mode.
    testingValue : FloatField
        The value used for testing the simulation.
    testingKey : CharField
        The key used for testing the simulation.
    """

    startDate = models.DateField()
    stepSize = models.IntegerField()
    rowLength = models.IntegerField()
    testingMode = models.BooleanField(default=False, null=True)
    testingValue = models.FloatField(default=None, null=True)
    testingKey = models.CharField(max_length=100,default=None, null=True)
    simName = models.CharField(max_length=100)

    def set_data(self, data):
        """
        Set the input data for the simulation model.

        Parameters
        ----------
        data : dict
            A dictionary containing the input parameters.
        """
        self.startDate = data.get('startDate')
        self.stepSize = data.get('stepSize')
        self.rowLength = data.get('rowLength')
        self.testingMode = data.get('testingMode')
        testing_data = data.get('testingData', {})
       
        if testing_data and self.testingMode:
            self.testingKey, self.testingValue = next(iter(testing_data.items()), (None, None))
            if isinstance(self.testingValue,dict):
                self.testingValue = -99
        else:
            self.testingKey = None
            self.testingValue = None
        self.simName = data.get('simName')

    def get_data(self):
        """
        Get the input data from the simulation model.

        Returns
        -------
        dict
            A dictionary containing the input parameters and associated row details.
        """
        return {
            'startDate': self.startDate,
            'stepSize': self.stepSize,
            'rowLength': self.rowLength,
            'rows': [row.get_data() for row in self.rowdetails_set.all()],
        }


class RowDetail(models.Model):
    """
    Model to store details for each row in the simulation input.

    Attributes
    ----------
    plantType : CharField
        The type of plant in the row (e.g., Lettuce, Cabbage).
    plantingType : CharField
        The planting method used in the row (e.g., Direct seeding, Transplanting).
    stripWidth : IntegerField
        The width of the strip in the row (in cm).
    rowSpacing : IntegerField
        The spacing between rows (in cm).
    input_data : ForeignKey
        A foreign key linking to the corresponding DataModelInput.
    """

    plantType = models.CharField(max_length=100)
    plantingType = models.CharField(max_length=100)
    stripWidth = models.IntegerField()
    rowSpacing = models.IntegerField()
    numSets = models.IntegerField()
    input_data = models.ForeignKey(DataModelInput, on_delete=models.CASCADE, related_name='rows')

    def set_data(self, data):
        """
        Set the row detail data.
        """
        self.plantType = data.get('plantType')
        self.plantingType = data.get('plantingType')
        self.stripWidth = data.get('stripWidth')
        self.rowSpacing = data.get('rowSpacing')
        self.numSets = data.get('numSets')

    def get_data(self):
        """
        Get the row detail data.
        """
        return {
            'plantType': self.plantType,
            'plantingType': self.plantingType,
            'stripWidth': self.stripWidth,
            'rowSpacing': self.rowSpacing,
        }




class SimulationIteration(models.Model):
    """
    Model to represent an iteration of a simulation.

    Attributes
    ----------
    simulation : ForeignKey
        A foreign key linking to the Simulation.
    iteration_index : IntegerField
        The index of the current iteration (e.g., 0, 1, 2, etc.).
    param_value : FloatField
        The value of the parameter being changed in this iteration (if applicable).
    """

    input = models.ForeignKey(DataModelInput, on_delete=models.CASCADE, related_name='iterations')
    iteration_index = models.IntegerField(default=0)
    param_value = models.FloatField(default=None, null=True)

    def set_data(self, data):
        """
        Set iteration data.
        """
        self.iteration_index = data.get('iteration_index', 0)
        self.param_value = data.get('param_value', 0.0)
        

    def get_data(self):
        return {
            'simulation': self.simulation.name,
            'iteration_index': self.iteration_index,
            'param_value': self.param_value,
        }


class DataModelOutput(models.Model):
    """
    Model to store output data from the simulation.

    Attributes
    ----------
    iteration : ForeignKey
        A foreign key linking to the SimulationIteration.
    yield_value : FloatField
        The yield value from the simulation at a specific iteration.
    growth : FloatField
        The growth value from the simulation.
    water : FloatField
        The water level recorded during the iteration.
    overlap : IntegerField
        The overlap count of crops during the iteration.
    map : JSONField
        A JSON representation of the crop map during the iteration.
    """

    iteration = models.ForeignKey(SimulationIteration, on_delete=models.CASCADE, related_name='outputs')
    date = models.CharField(max_length=100)
    yield_value = models.FloatField(null=True)
    growth = models.FloatField()
    water = models.FloatField()
    overlap = models.IntegerField()
    map = models.JSONField()
    weed = models.JSONField()
    time_needed = models.FloatField()
    profit = models.FloatField()
    rain = models.FloatField()
    temperature = models.FloatField()
    num_plants = models.IntegerField()
    def set_data(self, data):
        """
        Set the output data for this iteration.
        """
        self.date = data.get('date')
        self.yield_value = data.get('yield')
        self.growth = data.get('growth')
        self.water = data.get('water')
        self.overlap = data.get('overlap')
        self.map = data.get('map')
        self.weed = data.get('weed')
        self.time_needed = data.get('time_needed')
        self.profit = data.get('profit')
        self.rain = data.get('rain')
        self.temperature = data.get('temperature')
        self.num_plants = data.get('num_plants')


        

    def get_data(self):
        """
        Get the output data for this iteration.
        """
        return {
            'date': self.date,
            'yield_value': self.yield_value,
            'growth': self.growth,
            'water': self.water,
            'overlap': self.overlap,
            'map': self.map,
            'weed': self.weed,
            'time_needed': self.time_needed,
            'profit': self.profit,
            'rain': self.rain,
            'temperature': self.temperature,
            'num_plants': self.num_plants,
        }

class Plant(models.Model):
    """
    Model to store parameters for each type of plant used in the simulation.

    Attributes
    ----------
    name : CharField
        The name of the plant (e.g., Lettuce, Cabbage).
    W_max : FloatField
        Maximum width of the plant (in cm).
    H_max : FloatField
        Maximum height of the plant (in cm).
    k : FloatField
        Growth rate constant (specific to plant type).
    n : IntegerField
        Shape factor (specific to plant growth model).
    max_moves : IntegerField
        Maximum number of moves for the plant (e.g., in a simulation context).
    Yield : FloatField
        Yield per plant (e.g., kg).
    size_per_plant : FloatField
        Size of the plant (in cm).
    row_distance : FloatField
        Distance between rows of plants (in cm).
    column_distance : FloatField
        Distance between columns of plants (in cm).
    """
    name = models.CharField(max_length=100)
    W_max = models.FloatField()  # Maximum width
    H_max = models.FloatField()  # Maximum height
    k = models.FloatField()  # Growth rate constant
    n = models.IntegerField()  # Shape factor
    b = models.FloatField()  # Shape factor
    max_moves = models.IntegerField()  # Maximum moves
    Yield = models.FloatField()  # Yield per plant
    size_per_plant = models.FloatField()  # Size per plant
    row_distance = models.FloatField()  # Distance between rows
    column_distance = models.FloatField()  # Distance between columns
    test=models.TextField(max_length=100)
    planting_cost = models.FloatField()
    revenue = models.FloatField()

    def __str__(self):
        return self.name
class Weather(models.Model):

    date = models.CharField(max_length=100)
    temperature = models.FloatField()
    rain = models.FloatField()


    def set_data(self, data):
        """
        Set the test data for the simulation model.

        Parameters
        ----------
        data : dict
            A dictionary containing the test parameters.
        """
        self.temperature = data.get('temperature')
        self.rain = data.get('rain')
        self.date = data.get('date')

    def get_data(self):
        """
        Get the test data from the simulation model.

        Returns
        -------
        dict
            A dictionary containing the test parameters.
        """
        return {
            'temperature': self.temperature,
            'rain': self.rain,
            'date': self.date,
        }