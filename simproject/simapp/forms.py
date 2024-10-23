import django.forms as forms
from .models import Plant
class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = '__all__'  # or list specific fields if you want to exclude some