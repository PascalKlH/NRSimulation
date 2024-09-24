# Project Title

**Simulation of Crop Growth and Weed Management**

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Models Overview](#models-overview)
- [Running the Simulation](#running-the-simulation)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This project simulates the growth of crops and the management of weeds in agricultural fields. It allows users to input parameters related to planting and manage the growth process through a structured simulation. The results can be analyzed and visualized using various data analysis techniques.

## Features

- Dynamic simulation of crop growth based on user-defined parameters.
- Support for multiple planting types (grid, alternating, random).
- Weed growth simulation and management.
- Data storage in SQLite for easy retrieval and analysis.
- Visualization of simulation results using Plotly.
- Integration with Django for web-based interface.

## Technologies Used

- Python
- Django
- SQLite
- NumPy
- Pandas
- Plotly
- JSON
- Bootstrap (for front-end styling)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
2. **Create a virtual environment (optional but recommended):**
   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. **Install dependencies:**
   ```bash
    pip install -r requirements.txt
4. **Apply migrations:**
   ```bash
   python manage.py migrate
5. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
6. **Run the development server:**
   ```bash
    python manage.py runserver


Usage
Open your web browser and navigate to http://127.0.0.1:8000/.
Use the web interface to input the simulation parameters (e.g., start date, number of iterations, step size).
Choose the planting configuration (e.g., plant types, strip widths) and run the simulation.
View the results, which are stored in the database and can be visualized.


## Project Structure

```csharp
NRSsimulation/
│
├── simproject/
│   ├── simapp/
│   │   ├── __pycache__/
│   │   ├── migrations/         # Django migrations folder
│   │   ├── scripts/
│   │   │   ├── __pycache__/
│   │   │   ├── calculate.py     # Calculation scripts of the simulation
│   │   │   └── transformed_weather_data.csv  # Weather data of simulation
│   │   ├── static/
│   │   │   ├── images/          # Images folder of favicon or other assets
│   │   │   ├── simapp/          # Static files of simapp like JS, CSS
│   │   │   │   ├── script.js    # JavaScript file
│   │   │   │   └── style.css    # Stylesheet file
│   │   ├── templates/
│   │   │   └── simapp/          # HTML templates
│   │   │       ├── index.html
│   │   │       └── plot_simulation.html
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── db.sqlite3                 # SQLite database file
├── manage.py                  # Django management script
└── README.md                  # Project README file
