from django.db import models
import json
import pandas as pd


class DataModelInput(models.Model):

    def set_data(self, data_frame):
        # Konvertiere das DataFrame in ein Dictionary mit Listen als Spaltenwerten
        if isinstance(data_frame, pd.DataFrame):
            data_dict = data_frame.to_dict(orient='list')
        else:
            # Falls es sich nicht um ein DataFrame handelt, konvertiere es direkt
            data_dict = data_frame
        
        # Speichere es als JSON in der Datenbank
        self.data = json.dumps(data_dict)


    def get_data(self):
        # Lade die Daten als Dictionary und konvertiere es zurück in ein DataFrame
        data_dict = json.loads(self.data)
        return pd.DataFrame.from_dict(data_dict)

    
class DataModelOutput(models.Model):
    
    def set_data(self, data_frame):
        # Konvertiere das DataFrame in ein Dictionary mit Listen als Spaltenwerten
        if isinstance(data_frame, pd.DataFrame):
            data_dict = data_frame.to_dict(orient='list')
        else:
            # Falls es sich nicht um ein DataFrame handelt, konvertiere es direkt
            data_dict = data_frame
        
        # Speichere es als JSON in der Datenbank
        self.data = json.dumps(data_dict)


    def get_data(self):
        # Lade die Daten als Dictionary und konvertiere es zurück in ein DataFrame
        data_dict = json.loads(self.data)
        return pd.DataFrame.from_dict(data_dict)