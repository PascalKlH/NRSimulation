document.addEventListener('DOMContentLoaded', function () {
    const addRowButton = document.getElementById('addRowButton');
    const runSimulationButton = document.getElementById('runSimulation');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    let rowCount = 0;
    const plantTypeSelect = document.getElementById('plantTypeSelect');
    const plantDescriptionContainer = document.getElementById('plantDescription');
    const testingModeCheckbox = document.getElementById('testingMode');
    let currentlyCheckedBox = null;
    let singleRowAdded = false;
    
    document.getElementById('plotSimulation').addEventListener('click', function() {
        const simulationName = document.getElementById('simulationName').value;
        if (!simulationName) {
            alert('Please enter a simulation name.');
            return;
        }
    
        // Assuming you have a Django URL setup to handle this post request
        fetch('/get_simulation_results/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Ensure csrfToken is defined in your script
            },
            body: JSON.stringify({simulation_name: simulationName})
        })
        .then(response => {
            console.log(response);
            if (!response.ok) throw new Error('Network response was not ok.');
            return response.json();
        })
        .then(data => {
            console.log(data);  // Process and display your data as needed
            // You may want to call a function here to update your page with the simulation results
        })
        .catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
    });

    // Toggle testing mode
    testingModeCheckbox.addEventListener('change', function () {
        const testingCheckboxes = document.querySelectorAll('.testing-checkbox');
        if (this.checked) {
            testingCheckboxes.forEach(checkbox => {
                checkbox.classList.remove('d-none');
                checkbox.addEventListener('change', handleSplitForms);
            });
        } else {
            testingCheckboxes.forEach(checkbox => {
                checkbox.classList.add('d-none');
                checkbox.checked = false;
            });
            resetAllForms();
            currentlyCheckedBox = null;
        }
    });

    function handleSplitForms(event) {
        const targetCheckbox = event.target;

        // Uncheck the previously checked checkbox
        if (currentlyCheckedBox && currentlyCheckedBox !== targetCheckbox) {
            currentlyCheckedBox.checked = false;
            if (currentlyCheckedBox.id === 'multiRowCheckbox') {
                // Reset to allow only one row
                singleRowAdded = false;
            } else {
                resetForm(currentlyCheckedBox.closest('.row'));
            }
        }

        if (targetCheckbox.checked) {
            currentlyCheckedBox = targetCheckbox;
            if (targetCheckbox.id === 'multiRowCheckbox') {
                // Allow multiple rows
                singleRowAdded = false;
            } else {
                // Split the form
                const formContainer = targetCheckbox.closest('.row');
                const clonedForm = formContainer.querySelector('.cloned-form');

                if (!clonedForm) {
                    splitForm(formContainer);
                }
            }
        } else {
            if (targetCheckbox.id === 'multiRowCheckbox') {
                // Reset to allow only one row
                singleRowAdded = false;
            } else {
                // Reset the form
                const formContainer = targetCheckbox.closest('.row');
                resetForm(formContainer);
            }
            currentlyCheckedBox = null;
        }
    }

    function splitForm(formContainer) {
        const formCol = formContainer.querySelector('.col-md-8');
        formCol.classList.remove('col-md-8');
        formCol.classList.add('col-md-4'); // Shrink to half width
    
        const clone = formCol.cloneNode(true);
    
        // Update the IDs of the cloned form inputs
        const inputFields = clone.querySelectorAll('input, select');
        inputFields.forEach((inputField) => {
            inputField.id += '-clone'; // Append '-clone' to each ID
        });
    
        clone.classList.add('cloned-form');
        formContainer.appendChild(clone);
    
        const nextSibling = formCol.nextElementSibling;
        if (nextSibling) {
            formContainer.insertBefore(clone, nextSibling);
        } else {
            formContainer.appendChild(clone);
        }
    }
    
    function resetForm(formContainer) {
        const formCol = formContainer.querySelector('.col-md-4');
        if (formCol) {
            formCol.classList.remove('col-md-4');
            formCol.classList.add('col-md-8'); // Reset to full width
        }
    
        const clonedForm = formContainer.querySelector('.cloned-form');
        if (clonedForm) {
            clonedForm.remove(); // Remove cloned form
        }
    }
    
   
    function resetAllForms() {
        const rows = document.querySelectorAll('.row');
        rows.forEach(row => resetForm(row));
    }

    // Plant descriptions (same as before)
    const descriptions = {
        'lettuce': `<strong>Max Height:</strong> 30cm<br><strong>Max Width:</strong> 30cm<br><strong>Growth Rate:</strong> ca. 1cm/day<br><strong>Recommended Distance Between Plants:</strong> 20-30cm<br><strong>Yield per Plant:</strong> ca. 200-300g`,
        'cabbage': `<strong>Max Height:</strong> 30cm<br><strong>Max Width:</strong> 60cm<br><strong>Growth Rate:</strong> ca. 0.5cm/day<br><strong>Recommended Distance Between Plants:</strong> 40-50cm<br><strong>Yield per Plant:</strong> ca. 1-2kg<br><strong>Additional Info:</strong> Cabbage can be eaten raw or cooked and is known for its high vitamin C content.`,
        'spinach': `<strong>Max Height:</strong> 30cm<br><strong>Max Width:</strong> 20cm<br><strong>Growth Rate:</strong> ca. 1.5cm/day<br><strong>Recommended Distance Between Plants:</strong> 10-20cm<br><strong>Yield per Plant:</strong> ca. 100-150g<br><strong>Additional Info:</strong> Spinach is rich in iron and vitamins A and C, and is commonly used in salads and cooking.`
    };

    // Plant type change listener (same as before)
    plantTypeSelect.addEventListener('change', function () {
        const selectedValue = this.value;
        const description = descriptions[selectedValue] || '';
        plantDescriptionContainer.innerHTML = description ? `<div class="plant-description">${description}</div>` : '';
    });

    // Add new row when button is clicked
    addRowButton.addEventListener('click', function () {
        const isTestingModeEnabled = testingModeCheckbox.checked;
        const allowMultipleRowsChecked = document.getElementById('multiRowCheckbox').checked;
    
        // Check if testing mode is enabled
        if (isTestingModeEnabled) {
            // In testing mode, only allow multiple rows if 'allow multiple rows' is checked
            if (!allowMultipleRowsChecked && singleRowAdded) {
                alert("You can only add one row when 'Allow Multiple Rows' is unchecked in testing mode.");
                return;
            }
        } else {
            // If testing mode is disabled, allow adding rows freely
            if (!allowMultipleRowsChecked && singleRowAdded) {
                singleRowAdded = false; // Reset singleRowAdded if testing mode is off
            }
        }
    
        rowCount++;
        const rowList = document.getElementById('row-list');
        const newRow = document.createElement('div');
        newRow.className = 'row-container';
        newRow.id = `row-${rowCount}`;
        newRow.innerHTML = `
        <div class="row mb-2">
            <div class="col-md-3">
                <label for="plant-type-${rowCount}" class="form-label">Plant Type:</label>
            </div>
            <div class="col-md-8">
                <select id="plant-type-${rowCount}" class="form-control plant-type">
                    <option value="lettuce">Lettuce</option>
                    <option value="cabbage">Cabbage</option>
                    <option value="spinach">Spinach</option>
                </select>
            </div>
            <div class="col-md-3">
                <input type="checkbox" class="form-check-input testing-checkbox d-none" id="splitPlantType-${rowCount}">
            </div>
        </div>
    
        <div class="row mb-2">
            <div class="col-md-3">
                <label for="row-width-${rowCount}" class="form-label">Width of the row (cm):</label>
            </div>
            <div class="col-md-8">
                <input type="number" id="row-width-${rowCount}" class="form-control row-width" placeholder="Width in cm" value="30" min="1" max="30">
            </div>
            <div class="col-md-3">
                <input type="checkbox" class="form-check-input testing-checkbox d-none" id="splitRowWidth-${rowCount}">
            </div>
        </div>
    
        <div class="row mb-2">
            <div class="col-md-3">
                <label for="planting-type-${rowCount}" class="form-label">Planting Type:</label>
            </div>
            <div class="col-md-8">
                <select id="planting-type-${rowCount}" class="form-control planting-type">
                    <option value="grid">Grid</option>
                    <option value="alternating">Alternating</option>
                    <option value="random">Random</option>
                    <option value="empty">Empty</option>
                </select>
            </div>
            <div class="col-md-3">
                <input type="checkbox" class="form-check-input testing-checkbox d-none" id="splitPlantingType-${rowCount}">
            </div>
        </div>
    
        <div class="row mb-2">
            <div class="col-md-3">
                <label for="row-spacing-${rowCount}" class="form-label">Space between plants (cm):</label>
            </div>
            <div class="col-md-8">
                <input type="number" id="row-spacing-${rowCount}" class="form-control row-spacing" placeholder="Row spacing in cm" value="15" min="1" max="30">
            </div>
            <div class="col-md-3">
                <input type="checkbox" class="form-check-input testing-checkbox d-none" id="splitRowSpacing-${rowCount}">
            </div>
        </div>
    
        <!-- New section for Number of Iterations -->
        <div class="row mb-2">
            <div class="col-md-3">
                <label for="num-iterations-${rowCount}" class="form-label">Number of Iterations:</label>
            </div>
            <div class="col-md-8">
                <input type="number" id="num-iterations-${rowCount}" class="form-control numIterations" placeholder="Number of Iterations" value="1" min="1" max="10">
            </div>
            <div class="col-md-3">
                <input type="checkbox" class="form-check-input testing-checkbox d-none" id="splitNumIterations-${rowCount}">
            </div>
        </div>
    
        <button class="btn btn-danger remove-btn">Delete Row</button>
    `;
    
    rowList.appendChild(newRow);

    // Corrected way to handle adding 'd-none' class to testing checkboxes
    const newTestingCheckboxes = newRow.querySelectorAll('.testing-checkbox');
    newTestingCheckboxes.forEach(checkbox => {
        checkbox.classList.add('d-none');
    });

    if (!multiRowCheckbox.checked) {
        singleRowAdded = true;
    }

    // Event listeners for new testing checkboxes
    newTestingCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleSplitForms);
    });

    // Remove button event listener
    const removeButton = newRow.querySelector('.remove-btn');
    removeButton.addEventListener('click', function () {
        newRow.remove();
        if (!multiRowCheckbox.checked) {
            singleRowAdded = false; // Allow adding another row
        }
    });

    if (!document.getElementById('multiRowCheckbox').checked) {
        newTestingCheckboxes.forEach(checkbox => checkbox.classList.remove('d-none'));
        singleRowAdded = true;
    }
});


    runSimulationButton.addEventListener('click', function (event) {
        event.preventDefault();  // Prevent form submission
        
        const testingModeEnabled = document.getElementById('testingMode').checked;
        const rows = document.querySelectorAll('.row-container');
        const rowData = [];
        
        // Collect data for each row
        rows.forEach(row => {
            const plantType = row.querySelector('.plant-type').value;
            const plantingType = row.querySelector('.planting-type').value;
            const rowWidth = row.querySelector('.row-width').value;
            const rowSpacing = row.querySelector('.row-spacing').value;
            const numSets = row.querySelector('.numIterations').value;
    
            const rowWidthTuple = testingModeEnabled
                ? [parseFloat(rowWidth), parseFloat(document.getElementById(`${row.querySelector('.row-width').id}-clone`)?.value || -1)]
                : parseFloat(rowWidth);
            const rowSpacingTuple = testingModeEnabled
                ? [parseFloat(rowSpacing), parseFloat(document.getElementById(`${row.querySelector('.row-spacing').id}-clone`)?.value || -1)]
                : parseFloat(rowSpacing);
            const numSetsTuple = testingModeEnabled
                ? [parseInt(numSets), parseInt(document.getElementById(`${row.querySelector('.numIterations').id}-clone`)?.value || -1)]
                : parseInt(numSets);
    
            rowData.push({
                plantType: plantType,
                plantingType: plantingType,
                stripWidth: rowWidthTuple,
                rowSpacing: rowSpacingTuple,
                numSets: numSetsTuple
            });
        });
    
        const rowLength = parseInt(document.getElementById('rowLength').value);
        const rowLengthValue = testingModeEnabled
            ? [rowLength, parseInt(document.getElementById('rowLength-clone')?.value || -1)]
            : rowLength;
    
        // Prepare the data for the POST request
        const requestData = {
            simName: testingModeEnabled 
                ? [document.getElementById('simName').value, document.getElementById('simName-clone')?.value || -1]
                : document.getElementById('simName').value,
            startDate: testingModeEnabled 
                ? [document.getElementById('startDate').value, document.getElementById('startDate-clone')?.value || -1]
                : document.getElementById('startDate').value,
            stepSize: testingModeEnabled 
                ? [parseInt(document.getElementById('stepSize').value), parseInt(document.getElementById('stepSize-clone')?.value || -1)]
                : parseInt(document.getElementById('stepSize').value),
            rowLength: rowLengthValue,
            harvestType: testingModeEnabled 
                ? [document.getElementById('harvestType').value, document.getElementById('harvestType-clone')?.value || -1]
                : document.getElementById('harvestType').value,
            rows: rowData
        };
    
        
        // Send the request to the backend
        fetch('/run_simulation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
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
            console.log(result,"result");
            // Ensure data is available
            if (Array.isArray(result) && result.length > 0) {
                const allData = result.map(entry => entry.data);
                if (allData.length > 0) {
                    setupCarousel(allData); // Setup all 3 carousels
                    setupComparisonPlot(result); // Setup the final comparison plot

                }
            } else {
                console.error("No data found in the result.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    
    function setupCarousel(allData) {
        // Elements for each carousel
        const carouselElement1 = document.getElementById('carouselExampleCaptions1');
        const carouselElement2 = document.getElementById('carouselExampleCaptions2');
        const carouselElement3 = document.getElementById('carouselExampleCaptions3');

        let totalSlides = allData.length;

        // Create carousel slides and plots once
        createAndPopulateSlides(totalSlides, 'carouselExampleCaptions1', 'plot1_', allData, displayFirstPlot);
        createAndPopulateSlides(totalSlides, 'carouselExampleCaptions2', 'plot2_', allData, displaySecondPlot);
        createAndPopulateSlides(totalSlides, 'carouselExampleCaptions3', 'heatmap_', allData, displayHeatmap);

        // Event listeners for each carousel's slide change (just manage the slide switching, not re-creating)
        carouselElement1.addEventListener('slid.bs.carousel', function (event) {
            let currentIndex = event.to % totalSlides;  // Loop back to first slide after last
        });

        carouselElement2.addEventListener('slid.bs.carousel', function (event) {
            let currentIndex = event.to % totalSlides;  // Loop back to first slide after last
        });

        carouselElement3.addEventListener('slid.bs.carousel', function (event) {
            let currentIndex = event.to % totalSlides;  // Loop back to first slide after last
        });
    }

// Function to create and populate slides and plots once
    // Function to create and populate slides and plots once
    function createAndPopulateSlides(numSlides, carouselId, plotPrefix, allData, plotFunction) {
        const carouselInner = document.querySelector(`#${carouselId} .carousel-inner`);
        const carouselIndicators = document.querySelector(`#${carouselId} .carousel-indicators`);

        carouselInner.innerHTML = ''; // Clear existing slides
        carouselIndicators.innerHTML = ''; // Clear indicators

        for (let i = 0; i < numSlides; i++) {
            const slide = document.createElement('div');
            slide.classList.add('carousel-item');
            if (i === 0) slide.classList.add('active');

            const content = document.createElement('div');
            const plotId = `${plotPrefix}${i}`;
            content.innerHTML = `<div id="${plotId}" class="plot-container"></div>`;
            slide.appendChild(content);

            carouselInner.appendChild(slide);

            const indicator = document.createElement('li');
            indicator.setAttribute('data-bs-target', `#${carouselId}`);
            indicator.setAttribute('data-bs-slide-to', i);
            if (i === 0) indicator.classList.add('active');

            carouselIndicators.appendChild(indicator);

            // Use setTimeout to delay the plotting, ensuring that the DOM has time to render the new elements
            setTimeout(() => {
                plotFunction(allData[i], plotId);  // Pass the unique plot ID
            }, 0);
        }
    }
    // Function to setup the comparison plot
    function setupComparisonPlot(result) {
        const yAxisSelect = document.getElementById('y-axis-select');
        
        // Initial plot with default value (growth)
        plotComparison(result, 'growth');
    
        // Listen for changes in the Y-Axis dropdown and update the plot
        yAxisSelect.addEventListener('change', function () {
            const selectedValue = this.value;
            plotComparison(result, selectedValue);
        });
    }
    
    function plotComparison(allData, yAxisKey) {
        if (!allData || allData.length === 0) {
            console.error("No data available for plotting.");
            return;
        }
    
        // Dynamically determine the X-axis key from the first entry (assuming the first entry has this key)
        // This key should represent the varying parameter across different simulation runs
        const xKey = Object.keys(allData[0]).find(key => key !== 'data');
        console.log("Dynamic X-axis key identified:", xKey);
    
        // Use the dynamically determined key for the X-axis
        const xValues = allData.map(entry => entry[xKey]);
    
        // Extract only the last value for the selected parameter (yAxisKey) from each iteration's data
        const yValues = allData.map(entry => {
            const series = entry.data[yAxisKey];  // Get the array for the selected parameter (growth, yield, etc.)
            return series ? series[series.length - 1] : null;  // Get the last value of the array or null if not present
        });
    
        const trace = {
            x: xValues,
            y: yValues,
            type: 'scatter',
            mode: 'lines+markers',
            name: `Comparison of ${yAxisKey}`
        };
    
        const layout = {
            title: `Comparison of ${yAxisKey} Across Iterations`,
            xaxis: { title: xKey },
            yaxis: { title: yAxisKey.charAt(0).toUpperCase() + yAxisKey.slice(1) }  // Capitalize the Y-axis key
        };
    
        // Plot the comparison chart using Plotly
        Plotly.newPlot('comparisonPlot', [trace], layout);  
    }
    
        
    
    function displayFirstPlot(data, plotId) {
        const dates = data.time || [];
        const yields = data.yield || [];
        const growths = data.growth || [];
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
        const layout1 = {
            title: 'Growthrate and Yield Over Time',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Growthrate' },
            yaxis2: { title: 'Yield', overlaying: 'y', side: 'right' }
        };
        Plotly.newPlot(plotId, [growthTrace, yieldTrace], layout1);

    }

    function displaySecondPlot(data, plotId) {
        const dates = data.time || [];
        const yields = data.yield || [];
        const growths = data.growth || [];
        const waters = data.water || [];
        const overlaps = data.overlap || [];

        

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
        Plotly.newPlot(plotId, [waterTrace], layout2);
       // Plotly.newPlot('plot3', [overlapTrace], layout3);

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
        //document.getElementById('plotSelector').addEventListener('change', function() {
           //const selectedPlot = this.value;
           // ['plot2', 'plot3', 'plot4', 'plot5', 'plot6'].forEach(plotId => {
           //     document.getElementById(plotId).classList.add('d-none');
           // });
           // document.getElementById(selectedPlot).classList.remove('d-none');
       // });
    }

    function displayHeatmap(data, plotId) {
        const heatmapData = data.map || [];
        const boundary = data.boundary || [];
        const weed = data.weed || []; 
        const dates = data.time || [];
        const weedArray = weed;
        const slider = document.getElementById('dateSlider');
        const sliderValueDisplay = document.getElementById('sliderValue');

        // Initialize slider
        slider.max = heatmapData.length - 1; // max value is the length of mapArray minus 1

        // Event Listener for slider movement
        slider.addEventListener('input', function() {
            const sliderValue = slider.value;
            sliderValueDisplay.textContent = sliderValue;
            Heatmap(sliderValue,heatmapData,weedArray,dates);
        });
        const showStrips = document.getElementById('showStrips')
        const selectedOption = document.getElementById('heatmapOption');
        showStrips.addEventListener('change', function() {
            Heatmap(slider.value,heatmapData,weedArray,dates);
        }
        );
        selectedOption.addEventListener('change', function() {
            Heatmap(slider.value,heatmapData,weedArray,dates);
        }
        );
        // Function to display the corresponding Heatmap data
        function Heatmap(index,map,weed,dates) {
            const mapData =map[index];  // Access the data for the heatmap at the given index
            const weedData = weed[index];
            const showStrips = document.getElementById('showStrips').checked;
            const selectedOption = document.getElementById('heatmapOption').value;


    
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
                `
                const stripTrace = {
                    z: rowArray2D,
                    type: 'heatmap',
                    colorscale: [
                        [0, 'rgb(200,200,200)'],
                        [1, 'rgb(150,150,150)']
                    ],
                    showscale: false,
                    opacity: 0.3
                };
                `
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
                
                let traces = [];
                if (selectedOption === 'plants') {
                    traces.push(heatmapTrace);
                } else if (selectedOption === 'weeds') {
                    traces.push(weedTrace);
                } else if (selectedOption === 'plantsweeds') {
                    traces.push(heatmapTrace, weedTrace);
                }

                if (showStrips) {
                    pass
                    //traces.push(stripTrace);  // Add the strip trace if the checkbox is checked
                }

                Plotly.newPlot(plotId, traces, layout);
            } else {
                console.error(`No data found for index ${index}.`);
            }
        }

        // Display the initial heatmap
        Heatmap(1,heatmapData,weedArray,dates);

        }
    
    },);
});