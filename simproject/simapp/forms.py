from django import forms

class SimulationForm(forms.Form):
    length = forms.IntegerField(label='Length (cm)', initial=31)
    width = forms.IntegerField(label='Width (cm)', initial=31)
    field_name = forms.CharField(label='Field Name', initial='My Field')
    plant = forms.ChoiceField(choices=[
        ('lettuce', 'Lettuce'),
        ('spinach', 'Spinach'),
        ('cabbage', 'Cabbage'),
    ])
    pattern = forms.ChoiceField(choices=[
        ('grid', 'Grid'),
        ('alternating', 'Alternating'),
        ('random', 'Random'),
        ('custom', 'Custom'),
    ])
    start_date = forms.DateField(label='Start Date', initial='2022-01-01')
    end_date = forms.DateField(label='End Date', initial='2022-05-01')
    initial_water_layer = forms.IntegerField(label='Initial Water Level (mm)', initial=1)
class FieldRowForm(forms.Form):
    width = forms.FloatField(label='Width', min_value=0)
    crop_type = forms.CharField(label='Crop Type', max_length=100)
    offset = forms.FloatField(label='Offset', min_value=0)