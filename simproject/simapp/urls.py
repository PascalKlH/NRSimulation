''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('run_simulation/', views.run_simulation, name='run_simulation'),  # URL to trigger the script
    path('api/get_simulation_data/', views.get_simulation_data, name='get_simulation_data'),  # API to fetch simulation results
    
]
