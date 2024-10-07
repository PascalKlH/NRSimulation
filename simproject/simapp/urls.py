''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('run_simulation/', views.run_simulation, name='run_simulation'),  # URL to trigger the script
    path('get_simulation_results/', views.get_simulation_results, name='get_simulation_results'),
    path('plot_simulation/', views.plot_simulation, name='plot_simulation'),
]
