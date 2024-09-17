from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('run_simulation/', views.run_simulation, name='run_simulation'),  # URL to trigger the script
    path('plot_simulation/', views.plot_simulation, name='plot_simulation'),
]
