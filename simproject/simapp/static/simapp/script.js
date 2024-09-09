document.addEventListener('DOMContentLoaded', function () {
    const addRowButton = document.getElementById('addRowButton');
    const runSimulationButton = document.getElementById('runSimulation');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    let rowCount = 0; // Assuming rowCount is declared globally

    // Event listener for adding a new row
    addRowButton.addEventListener('click', function () {
        rowCount++;
        const rowList = document.getElementById('row-list');
    
        const newRow = document.createElement('div');
        newRow.className = 'row-container';
        newRow.id = `row-${rowCount}`;
    
        // Set the inner HTML for the new row
        newRow.innerHTML = `
            <div class="row mb-2">
                <div class="col-md-3">
                    <label for="plant-type-${rowCount}" class="form-label">Plant Type:</label>
                </div>
                <div class="col-md-9">
                    <select id="plant-type-${rowCount}" class="form-control plant-type">
                        <option value="lettuce">Lettuce</option>
                        <option value="cabbage">Cabbage</option>
                        <option value="spinach">Spinach</option>
                    </select>
                </div>
            </div>
            <div class="row mb-2">
                <div class="col-md-3">
                    <label for="row-width-${rowCount}" class="form-label">Width of the row (cm):</label>
                </div>
                <div class="col-md-9">
                    <input type="number" id="row-width-${rowCount}" class="form-control row-width" placeholder="Width in cm" value="30" min="1" max="30">
                </div>
            </div>
            <div class="row mb-2">
                <div class="col-md-3">
                    <label for="planting-type-${rowCount}" class="form-label">Planting Type:</label>
                </div>
                <div class="col-md-9">
                    <select id="planting-type-${rowCount}" class="form-control planting-type">
                        <option value="grid">Grid</option>
                        <option value="alternating">Alternating</option>
                        <option value="random">Random</option>
                        <option value="empty">Empty</option>
                    </select>
                </div>
            </div>
            <div class="row mb-2">
                <div class="col-md-3">
                    <label for="row-spacing-${rowCount}" class="form-label">Space between plants (cm):</label>
                </div>
                <div class="col-md-9">
                    <input type="number" id="row-spacing-${rowCount}" class="form-control row-spacing" placeholder="Row spacing in cm" value="15" min="1" max="30">
                </div>
            </div>
            <button class="btn btn-danger remove-btn">Delete Row</button>
        `;
    
        // Append the new row to the DOM
        rowList.appendChild(newRow);
    
        // Add event listener for the remove button
        const removeButton = newRow.querySelector('.remove-btn');
        removeButton.addEventListener('click', function () {
            newRow.remove();
        });
    
        // Add event listener for the planting type dropdown
        const plantingTypeSelect = document.getElementById(`planting-type-${rowCount}`);
        plantingTypeSelect.addEventListener('change', function() {
            const plantingType = this.value;
            const plantTypeField = document.getElementById(`plant-type-${rowCount}`).closest('.row');
            const rowSpacingField = document.getElementById(`row-spacing-${rowCount}`).closest('.row');
    
            if (plantingType === 'empty') {
                plantTypeField.style.display = 'none';
                rowSpacingField.style.display = 'none';
            } else {
                plantTypeField.style.display = 'flex';
                rowSpacingField.style.display = 'flex';
            }
        });
    });
    

    runSimulationButton.addEventListener('click', function (event) {
        alert("Simulation is running, please wait for the results to load");
        event.preventDefault();  // Prevent the default form submission

        const rows = document.querySelectorAll('.row-container');
        const rowData = [];

        rows.forEach(row => {
            const plantType = row.querySelector('.plant-type').value;
            const plantingType = row.querySelector('.planting-type').value;
            const rowWidth = row.querySelector('.row-width').value;
            const rowSpacing = row.querySelector('.row-spacing').value;

            rowData.push({
                plantType: plantType,
                plantingType: plantingType,
                stripWidth: parseFloat(rowWidth),
                rowSpacing: parseFloat(rowSpacing)
            });
        });
        const requestData = {

            //convert the values to integers
            startDate: document.getElementById('startDate').value,
            numIterations: parseInt(document.getElementById('numIterations').value),
            stepSize: parseInt(document.getElementById('stepSize').value),
            rowLength: parseInt(document.getElementById('rowLength').value),
            rows: rowData
        };
        fetch('/run_simulation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Ensure the CSRF token is correctly included
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(result => {
            displayResults(result);
            // Handle the response data here
        })
        .catch(error => {
            console.error('Error:', error);
        });
        
    });

    function displayResults(data) {
        console.log(data);
        const dates = data.time || [];
        const yields = data.yield || [];
        const growths = data.growth || [];
        const waters = data.water || [];
        const overlaps = data.overlap || [];
        const heatmapData = data.map || [];
        const boundary = data.boundary || [];
        const weed = data.weed || []; 
        

        // Create traces for each data series
        const growthTrace = {
            x: dates,
            y: growths,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Growthrate'
        };

        const yieldTrace = {
            x: dates,
            y: yields,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Yield',
            yaxis: 'y2'
        };

        const waterTrace = {
            x: dates,
            y: waters,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Water'
        };

        const overlapTrace = {
            x: dates,
            y: overlaps,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Overlap'
        };

        // Define layouts for each plot
        const layout1 = {
            title: 'Growthrate and Yield Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Growthrate' },
            yaxis2: { title: 'Yield', overlaying: 'y', side: 'right' }
        };

        const layout2 = {
            title: 'Water Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Water' }
        };

        const layout3 = {
            title: 'Overlap Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Overlap' }
        };

        // Plot the charts
        Plotly.newPlot('plot1', [growthTrace, yieldTrace], layout1);
        Plotly.newPlot('plot2', [waterTrace], layout2);
        Plotly.newPlot('plot3', [overlapTrace], layout3);

        // Handle additional plots for weather data if available
        if (data.weather) {
            const tempTrace = {
                x: data.weather.dates,
                y: data.weather.temps,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Temperature'
            };

            const humTrace = {
                x: data.weather.dates,
                y: data.weather.hums,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Humidity',
                yaxis: 'y2'
            };

            const windTrace = {
                x: data.weather.dates,
                y: data.weather.winds,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Wind'
            };

            const rainTrace = {
                x: data.weather.dates,
                y: data.weather.rains,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Rain'
            };

            const layout4 = {
                title: 'Temperature and Humidity Over Time',
                xaxis: { title: 'Date' },
                yaxis: { title: 'Temperature' },
                yaxis2: { title: 'Humidity', overlaying: 'y', side: 'right' }
            };

            const layout5 = {
                title: 'Wind Over Time',
                xaxis: { title: 'Date' },
                yaxis: { title: 'Wind' }
            };

            const layout6 = {
                title: 'Rain Over Time',
                xaxis: { title: 'Date' },
                yaxis: { title: 'Rain' }
            };

            // Plot weather data
            Plotly.newPlot('plot4', [tempTrace, humTrace], layout4);
            Plotly.newPlot('plot5', [windTrace], layout5);
            Plotly.newPlot('plot6', [rainTrace], layout6);
        }

        // Dropdown event listener to toggle plots
        document.getElementById('plotSelector').addEventListener('change', function() {
            const selectedPlot = this.value;
            ['plot2', 'plot3', 'plot4', 'plot5', 'plot6'].forEach(plotId => {
                document.getElementById(plotId).classList.add('d-none');
            });
            document.getElementById(selectedPlot).classList.remove('d-none');
        });

        const mapArray = heatmapData;
        const weedArray = weed;
        const slider = document.getElementById('dateSlider');
        const sliderValueDisplay = document.getElementById('sliderValue');

        // Initialize slider
        slider.max = mapArray.length - 1; // max value is the length of mapArray minus 1

        // Event Listener for slider movement
        slider.addEventListener('input', function() {
            const sliderValue = slider.value;
            sliderValueDisplay.textContent = sliderValue;
            displayHeatmap(sliderValue);
        });

        // Function to display the corresponding Heatmap data
        function displayHeatmap(index) {
            const mapData = mapArray[index];  // Access the data for the heatmap at the given index
            const weedData = weedArray[index];
        
            if (mapData) {
                // Heatmap data trace
                const heatmapTrace = {
                    z: mapData,  // mapData contains the 2D array for the heatmap
                    type: 'heatmap',
                    colorscale: [
                        [0,    'rgb(100,50,0)'],  // Brown for all values = 0
                        [0.01, 'rgb(150,255,150)'],  // Light green for smaller values
                        [1,    'rgb(0,100,0)']  // Dark green for higher values up to 50
                    ],
                    colorbar: {
                        title: 'Value',
                        titleside: 'right'
                    }
                };
        
                // Weed data trace with opacity
                const weedTrace = {
                    z: weedData,
                    type: 'heatmap',
                    colorscale: [
                        [0,    'rgb(100,50,0)'],  // Brown for all values = 0
                        [0.01, 'rgb(255,150,150)'],  // Light green for smaller values
                        [1,    'rgb(100,0,0)']  // Dark green for higher values up to 50

                    ],
                    colorbar: {
                        title: 'Weed Presence',
                        titleside: 'left',  // Move the colorbar to the left side
                        x: -0.15,  // Adjust the x position to make sure it is properly placed on the left
                    },
                    opacity: 0.5  // Adjust opacity so that both layers are visible
                };
                const layout = {
                    title: `Heatmap on ${dates[index]}`,
                    xaxis: {
                        title: 'X Axis',
                        showgrid: false,
                    },
                    yaxis: {
                        title: 'Y Axis',
                        showgrid: false,
                    },
                    margin: { t: 40, r: 20, b: 40, l: 50 },
                };
                const selectedOption = document.getElementById('heatmapOption').value;
                if (selectedOption === 'plants') {
                    Plotly.newPlot('heatmap', [heatmapTrace], layout);
                }
                else if (selectedOption === 'weeds') {
                    Plotly.newPlot('heatmap', [weedTrace], layout);
                }
                else if (selectedOption === 'plantsweeds') {
                    Plotly.newPlot('heatmap', [heatmapTrace, weedTrace], layout);
                }
            } else {
                console.error(`No data found for index ${index}.`);
            }
        }

        // Display the initial heatmap
        displayHeatmap(1);
    }
}
);
