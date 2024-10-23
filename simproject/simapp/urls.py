''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('run_simulation/', views.run_simulation, name='run_simulation'),  # URL to trigger the script
    path('api/get_simulation_data/', views.get_simulation_data, name='get_simulation_data'),  # API to fetch simulation results
    path('plants/', views.plant_list, name='plant_list'),
    path('plants/manage/', views.plant_manage, name='plant_manage'),
    path('plants/manage/<int:plant_id>/', views.plant_manage, name='plant_manage'),
    path('plants/delete/<int:plant_id>/', views.plant_delete, name='plant_delete'),
]
