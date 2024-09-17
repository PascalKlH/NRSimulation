from django.db import models
import json
import pandas as pd


from django.db import models
import json

class DataModelInput(models.Model):
    startDate = models.DateField()
    numIterations = models.IntegerField()
    stepSize = models.IntegerField()
    rowLength = models.IntegerField()
    rows = models.JSONField()

    def set_data(self, data):
        self.startDate = data.get('startDate')
        self.numIterations = data.get('numIterations')
        self.stepSize = data.get('stepSize')
        self.rowLength = data.get('rowLength')
        self.rows = data.get('rows')

    def get_data(self):
        return {
            'startDate': self.startDate,
            'numIterations': self.numIterations,
            'stepSize': self.stepSize,
            'rowLength': self.rowLength,
            'rows': self.rows,
        }

class DataModelOutput(models.Model):
    time = models.TimeField()         # Store as JSON for lists
    yield_value = models.FloatField()  # Assuming this is a single float value
    growth = models.FloatField()
    water = models.FloatField()
    overlap = models.IntegerField()    # Added missing parentheses
    map = models.JSONField()
    boundary = models.JSONField()
    weed = models.JSONField()

    def set_data(self, data):
        self.time = data.iloc[0]
        self.yield_value = data.iloc[1]
        self.growth = data.iloc[2]
        self.water = data.iloc[3]
        self.overlap = data.iloc[4]
        self.map = data.iloc[5]
        self.boundary = data.iloc[6]
        self.weed = data.iloc[7]


    def get_data(self):
        return {
            'time': json.loads(self.time),
            'yield': self.yield_value,
            'growth': self.growth,
            'water': self.water,
            'overlap': self.overlap,
            'map': json.loads(self.map),
            'boundary': json.loads(self.boundary),
            'weed': json.loads(self.weed),
        }

class DataModelOutputDetails(models.Model):
    time = models.JSONField()     # Store as JSON for lists
    yield_value = models.JSONField()  # For list of floats
    growth = models.JSONField()
    water = models.JSONField()
    overlap = models.JSONField()
    map = models.JSONField()
    boundary = models.JSONField()
    weed = models.JSONField()

    def set_data(self, data):
        self.time = json.dumps([x.strftime('%Y-%m-%d %H:%M:%S') for x in data.get('time', [])])
        self.yield_value = json.dumps(data.get('yield', []))
        self.growth = json.dumps(data.get('growth', []))
        self.water = json.dumps(data.get('water', []))
        self.overlap = json.dumps(data.get('overlap', []))
        self.map = json.dumps(data.get('map', []))
        self.boundary = json.dumps(data.get('boundary', []))
        self.weed = json.dumps(data.get('weed', []))

    def get_data(self):
        return {
            'time': json.loads(self.time),
            'yield': json.loads(self.yield_value),
            'growth': json.loads(self.growth),
            'water': json.loads(self.water),
            'overlap': json.loads(self.overlap),
            'map': json.loads(self.map),
            'boundary': json.loads(self.boundary),
            'weed': json.loads(self.weed),
        }
