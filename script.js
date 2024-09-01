document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('parametersForm');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const parameters = {
            length: document.getElementById('length').value,
            width: document.getElementById('width').value,
            field_name: document.getElementById('fieldName').value,
            plant: document.getElementById('plant').value,
            pattern: document.getElementById('pattern').value,
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value,
            initial_water_layer: document.getElementById('initialWaterLayer').value
        };

        console.log('Collected Parameters:', parameters);

        // Send data to the Flask backend
        fetch('/run_simulation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parameters)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Simulation results:', data);
            // Handle the received data (e.g., display on the web app)
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            console.log('ERROR');
        });
    });

    function displayResults(data) {
        // Display the simulation results on the web app
        const resultsDiv = document.createElement('div');
        resultsDiv.innerHTML = `
            <h2>Simulation Results</h2>
            <p>Yield: ${data.yield} kg</p>
            <p>Water Used: ${data.water_used} liters</p>
            <p>Growth Rate: ${data.growth_rate}</p>
        `;
        document.body.appendChild(resultsDiv);
    }
});


// Load the first CSV data
d3.csv("data.csv").then(function(data) {
    // Parse the data
    let dates = data.map(d => d.Date);
    let yields = data.map(d => parseFloat(d.Yield));
    let growths = data.map(d => parseFloat(d.Growth));
    let waters = data.map(d => parseFloat(d.Water));
    let overlaps = data.map(d => parseFloat(d.Overlap));

    // Create traces for each data series
    let growthTrace = {
        x: dates,
        y: growths,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Growthrate'
    };
    
    let yieldTrace = {
        x: dates,
        y: yields,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Yield',
        yaxis: 'y2'
    };

    let waterTrace = {
        x: dates,
        y: waters,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Water'
    };

    let overlapTrace = {
        x: dates,
        y: overlaps,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Overlap'
    };

    // Define layout with secondary y-axis for the first plot
    let layout1 = {
        title: 'Growthrate and Yield Over Time',
        xaxis: {
            title: 'Date',
            tickformat: '%Y-%m-%d %H:%M:%S'
        },
        yaxis: {
            title: 'Growthrate'
        },
        yaxis2: {
            title: 'Yield',
            overlaying: 'y',
            side: 'right'
        },
        showlegend: true
    };

    // Define layout for the second plot
    let layout2 = {
        title: 'Water Over Time',
        xaxis: {
            title: 'Date',
            tickformat: '%Y-%m-%d %H:%M:%S'
        },
        yaxis: {
            title: 'Water'
        },
        showlegend: true
    };

    // Define layout for the third plot
    let layout3 = {
        title: 'Overlap Over Time',
        xaxis: {
            title: 'Date',
            tickformat: '%Y-%m-%d %H:%M:%S'
        },
        yaxis: {
            title: 'Overlap'
        },
        showlegend: true
    };

    // Plot the charts
    Plotly.newPlot('plot1', [growthTrace, yieldTrace], layout1);
    Plotly.newPlot('plot2', [waterTrace], layout2);
    Plotly.newPlot('plot3', [overlapTrace], layout3);

    // Load the second CSV data for weather
    d3.csv("transformed_weather_data.csv").then(function(data) {
        // Parse the data
        let dates = data.map(d => d.Date);
        let temp = data.map(d => parseFloat(d.Temp));
        let hum = data.map(d => parseFloat(d.Hum));
        let wind = data.map(d => parseFloat(d.Wind));
        let rain = data.map(d => parseFloat(d.Rain));

        // Create traces for each data series
        let tempTrace = {
            x: dates,
            y: temp,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Temperature'
        };
        
        let humTrace = {
            x: dates,
            y: hum,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Humidity',
            yaxis: 'y2'
        };

        let windTrace = {
            x: dates,
            y: wind,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Wind'
        };

        let rainTrace = {
            x: dates,
            y: rain,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Rain'
        };

        // Define layout with secondary y-axis for the fourth plot
        let layout4 = {
            title: 'Temperature and Humidity Over Time',
            xaxis: {
                title: 'Date',
                tickformat: '%Y-%m-%d %H:%M:%S'
            },
            yaxis: {
                title: 'Temperature'
            },
            yaxis2: {
                title: 'Humidity',
                overlaying: 'y',
                side: 'right'
            },
            showlegend: true
        };

        // Define layout for the fifth plot
        let layout5 = {
            title: 'Wind Over Time',
            xaxis: {
                title: 'Date',
                tickformat: '%Y-%m-%d %H:%M:%S'
            },
            yaxis: {
                title: 'Wind'
            },
            showlegend: true
        };

        // Define layout for the sixth plot
        let layout6 = {
            title: 'Rain Over Time',
            xaxis: {
                title: 'Date',
                tickformat: '%Y-%m-%d %H:%M:%S'
            },
            yaxis: {
                title: 'Rain'
            },
            showlegend: true
        };

        // Plot the weather charts
        Plotly.newPlot('plot4', [tempTrace, humTrace], layout4);
        Plotly.newPlot('plot5', [windTrace], layout5);
        Plotly.newPlot('plot6', [rainTrace], layout6);

        // Dropdown event listener
        document.getElementById('plotSelector').addEventListener('change', function() {
            let selectedPlot = this.value;
            document.getElementById('plot2').classList.add('d-none');
            document.getElementById('plot3').classList.add('d-none');
            document.getElementById('plot4').classList.add('d-none');
            document.getElementById('plot5').classList.add('d-none');
            document.getElementById('plot6').classList.add('d-none');
            document.getElementById(selectedPlot).classList.remove('d-none');
        });
    });
});
