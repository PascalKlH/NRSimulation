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
        newRow.id =` row-${rowCount}`;
        newRow.innerHTML = `
        <!-- Plant Type -->
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
    
        <!-- Row Width -->
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
    
        <!-- Planting Type -->
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
    
        <!-- Row Spacing -->
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
    
        <!-- Number of Iterations -->
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
        <!-- Delete Row Button -->
        <div class="row mb-2">
            <div class="col-md-12">
                <button class="btn btn-danger remove-btn">Delete Row</button>
            </div>
        </div>
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



    runSimulationButton.addEventListener('click', function (event) {
        event.preventDefault();  // Prevent form submission
        const testingModeEnabled = document.getElementById('testingMode').checked;
        const rows = document.querySelectorAll('.row-container');
        const rowData = [];

        // Initialize the testingData object to store row-level testing data if testing mode is enabled
        let testingData = {};
        const requestData = {
                    simName: document.getElementById('simName').value,
                    startDate: document.getElementById('startDate').value,
                    stepSize: parseInt(document.getElementById('stepSize').value),
                    rowLength: parseInt(document.getElementById('rowLength').value),
                    harvestType: document.getElementById('harvestType').value,
                    rows: rowData,
                    testingMode: testingModeEnabled,
                    testingData: testingData,  // Now contains data for each row, if applicable
                    useTemperature: document.getElementById('useTemperature').checked,
                    useWater: document.getElementById('useWater').checked,
                    allowWeedgrowth: document.getElementById('allowWeedgrowth').checked,
                };
        // Collect data for each row
        rows.forEach((row, index) => {
            const plantType = row.querySelector('.plant-type').value;
            const plantingType = row.querySelector('.planting-type').value;
            const rowWidthInput = row.querySelector('.row-width');
            const rowSpacingInput = row.querySelector('.row-spacing');
            const numIterationsInput = row.querySelector('.numIterations');

            const rowDetails = {
                plantType: plantType,
                plantingType: plantingType,
                stripWidth: parseFloat(rowWidthInput.value),
                rowSpacing: parseFloat(rowSpacingInput.value),
                numSets: parseInt(numIterationsInput.value)
            };
        
            // Append testing mode data if enabled
            if (testingModeEnabled) {
                const rowWidthClone = document.getElementById(`${rowWidthInput.id}-clone`);
                const rowSpacingClone = document.getElementById(`${rowSpacingInput.id}-clone`);
                const numSetsClone = document.getElementById(`${numIterationsInput.id}-clone`);
                const startDateClone = document.getElementById('startDate-clone');
                const stepSizeClone = document.getElementById('stepSize-clone');
                const rowLengthClone = document.getElementById('rowLength-clone');
                const rowsClone = document.getElementById('multiRowCheckbox');
                if (rowWidthClone) {
                    requestData.testingData.stripWidth = parseFloat(rowWidthClone.value);
                }
                if (rowSpacingClone) {
                    requestData.testingData.rowSpacing = parseFloat(rowSpacingClone.value);
                }
                if (numSetsClone) {
                    requestData.testingData.numSets = parseInt(numSetsClone.value);
                }
                if (startDateClone) {
                    requestData.testingData.startDate = startDateClone.value;
                }
                if (stepSizeClone) {
                    requestData.testingData.stepSize = parseInt(stepSizeClone.value);
                }
                if (rowLengthClone) {
                    requestData.testingData.rowLength = parseInt(rowLengthClone.value);
                }
                if (rowsClone.checked) {
                    requestData.testingData.rows = rowDetails;
                }
                // Append individual row testing data to the main testingData object
            }

            rowData.push(rowDetails);
        });



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
            fetchSimulationData(result.name);
        })
        .catch(error => {
            console.error('Error:', error);
        });
        function fetchSimulationData(simulationName, page = 1, pageSize = 2000) {
            fetch(`/api/get_simulation_data/?name=${encodeURIComponent(simulationName)}&page=${page}&page_size=${pageSize}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data.iterations);
                    setupCarousel(data.iterations);
                    setupComparisonPlot(data.iterations);
        
                    // If there is a next page, fetch it recursively
                    if (data.has_next) {
                        fetchSimulationData(simulationName, page + 1, pageSize);
                    }
                })
                .catch(error => {
                    console.error('Failed to fetch:', error);
                });
        }
        
       
        
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
        const selectPlotType = document.getElementById('selectPlotType');
        selectPlotType.addEventListener('change', function() {
            const selectedPlotType = selectPlotType.value;
            updateAllSecondCarouselPlots(selectedPlotType,allData);
        });
    
        function updateAllSecondCarouselPlots(plotType, allData) {
            const allPlot2Elements = document.querySelectorAll('[id^="plot2_"]');
            console.log(`Updating ${allPlot2Elements.length} plots with type ${plotType}`);
        
            allPlot2Elements.forEach((plotContainer, index) => {
                const plotId = plotContainer.id; // Ensure IDs are unique and correctly assigned
                if (allData[index]) { // Check if data at index exists
                    const data = allData[index];
                    displaySecondPlot(data, plotId, plotType);
                } else {
                    console.error(`No data available for plot index ${index}`);
                }
            });
        }
        
    }

// Function to create and populate slides and plots once
    // Function to create and populate slides and plots once
    function createAndPopulateSlides(numSlides, carouselId, plotPrefix, allData, plotFunction) {
        const carouselInner = document.querySelector(`#${carouselId} .carousel-inner`);
        const carouselIndicators = document.querySelector(`#${carouselId} .carousel-indicators`);
    
        carouselInner.innerHTML = '';  // Clear existing slides
        carouselIndicators.innerHTML = '';  // Clear indicators
    
        for (let i = 0; i < numSlides; i++) {
            const slide = document.createElement('div');
            slide.classList.add('carousel-item');
            if (i === 0) slide.classList.add('active');
            const content = document.createElement('div');
            const plotId = `${plotPrefix}${i}`;
            content.innerHTML += `<div id="${plotId}" class="plot-container"></div>`;
            slide.appendChild(content);
            carouselInner.appendChild(slide);
            const indicator = document.createElement('li');
            indicator.setAttribute('data-bs-target', `#${carouselId}`);
            indicator.setAttribute('data-bs-slide-to', i);
            if (i === 0) indicator.classList.add('active');
            carouselIndicators.appendChild(indicator);
        }
    
    
        // Initialize the plot with the default selection for all slides
        setTimeout(() => {
            for (let i = 0; i < numSlides; i++) {
                const plotId = `${plotPrefix}${i}`;
                plotFunction(allData[i], plotId, 'growth');  // Default to 'growth' for the second carousel
            }
        }, 0);
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

    const xValues = allData.map(entry => entry.param_value); // x-axis based on the parameter values
    const xKey = allData[0].param_name; // Assume the parameter name is the same for all entries

    const yValues = allData.map(entry => {
        const lastOutput = entry.outputs[entry.outputs.length - 1]; // Get the last output of each iteration
        const area = lastOutput.map[0].length * lastOutput.map.length;
        switch (yAxisKey) {
            case "profit_per_plant":
                return lastOutput.profit / lastOutput.num_plants;
            case "profit_per_area":
                return lastOutput.profit / area;
            case "yield_per_plant":
                return lastOutput.yield / lastOutput.num_plants;
            case "growth_per_plant":
                return lastOutput.growth / lastOutput.num_plants;
            case "yield_per_area":
                return lastOutput.yield / area;
            case "growth_per_area":
                return lastOutput.growth / area;
            default:
                return lastOutput[yAxisKey]; // For other keys like yield, growth, etc.
        }
    });

    const trace = {
        x: xValues,
        y: yValues,
        type: 'scatter',
        mode: 'lines+markers',
        name: `Comparison of ${yAxisKey.replace('_', ' ')}`,
        line: {
            color: 'rgb(126,185,48)',
            width: 3
        },
        marker: {
            color: 'rgb(126,185,48)',
            size: 8
        }
    };

    const layout = {
        title: `Comparison of ${yAxisKey.replace('_', ' ')} Across Iterations`,
        xaxis: {
            title: xKey,
            showline: true,
            showgrid: true,
            showticklabels: true,
            linecolor: 'black',
            linewidth: 2,
            mirror: true
        },
        yaxis: {
            title: yAxisKey.charAt(0).toUpperCase() + yAxisKey.slice(1).replace('_', ' '),
            showline: true,
            showgrid: true,
            showticklabels: true,
            linecolor: 'black',
            linewidth: 2,
            mirror: true
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        margin: { t: 30, b: 30, l: 80, r: 30 }
    };

    // Plot the comparison chart using Plotly
    Plotly.newPlot('comparisonPlot', [trace], layout);
}

    function displayFirstPlot(data, plotId) {
        const dates = data.outputs.map(output => output.date);
        const yields = data.outputs.map(output => output.yield);
        const growths = data.outputs.map(output => output.growth);
        const growthTrace = {
            x: dates,
            y: growths,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Growthrate',
            line: {
                color: 'rgb(3,98,76)',
                width: 2
            },
            marker: {
                color: 'rgb(3,98,76)',
                size: 8
            }
        };
        const yieldTrace = {
            x: dates,
            y: yields,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Yield',
            yaxis: 'y2',
            line: {
                color: 'rgb(126,185,48)',
                width: 2
            },
            marker: {
                color: 'rgb(126,185,48)',
                size: 8
            }
        };
        const layout1 = {
            title: 'Growthrate and Yield Over Time',
            xaxis: {
                title: 'Date',
                showgrid: true, // Show grid lines
                zeroline: false, // Remove the zero line
                showline: true, // Show the line at axis base
                mirror: 'allticks', // Mirror the tick lines on all sides
                linewidth: 2, // Width of the axis line
                linecolor: 'black' // Color of the axis line
            },
            yaxis: {
                title: 'Growthrate in (g/TU)',
                showgrid: true,
                zeroline: false,
                showline: true,
                mirror: 'allticks',
                linewidth: 2,
                linecolor: 'black'
            },
            yaxis2: {
                title: 'Yield in (g)',
                overlaying: 'y',
                side: 'right',
                showgrid: true,
                zeroline: false,
                showline: true,
                mirror: 'allticks',
                linewidth: 2,
                linecolor: 'black'
            },
            plot_bgcolor: 'white', // Set the background color to white
            margin: {t: 40, r: 40, b: 40, l: 40}, // Adjust margin to ensure all elements fit
            paper_bgcolor: 'white' // Set the paper background color to white
        };
        Plotly.newPlot(plotId, [growthTrace, yieldTrace], layout1);
    }
    

    function displaySecondPlot(data, plotId, plotType) {
        const dates = data.outputs.map(output => output.date);
        const map = data.outputs.map(output => output.map); 
        const area = map[0].length * map[0][0].length;
        let traces = [];
        let layout;
        
        switch (plotType) {
            case "growth":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.growth),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Growthrate in (g/TU)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "yield":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.yield),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Yield in (g)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "growth_per_plant":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.growth / output.num_plants),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Growth per Plant (g/TU)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "yield_per_plant":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.yield / output.num_plants),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Yield per Plant (g)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "growth_per_area":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.growth / area),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Growth per Area (g/m²)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "yield_per_area":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.yield / area),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Yield per Area (g/m²)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "temperature":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.temperature),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Temperature in (°C)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "water":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.water),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Water in (ml)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "overlap":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.overlap),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Overlap in (cm)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "rain":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.rain),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Rain in (mm)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "time_needed":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.time_needed),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Time Needed in (s)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
            case "profit":
                traces.push({
                    x: dates,
                    y: data.outputs.map(output => output.profit),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'profit in (€)',
                    line: { color: 'rgb(126,185,48)' }
                });
                break;
        }
    
        layout = {
            title: `${plotType.charAt(0).toUpperCase() + plotType.slice(1).replace('_', ' ')} Over Time`,
            xaxis: {
                title: 'Date',
                showgrid: true,
                zeroline: false,
                showline: true,
                mirror: 'allticks',
                linewidth: 2,
                linecolor: 'black'
            },
            yaxis: {
                title: `${plotType.charAt(0).toUpperCase() + plotType.slice(1).replace('_', ' ')}`,
                showgrid: true,
                zeroline: false,
                showline: true,
                mirror: 'allticks',
                linewidth: 2,
                linecolor: 'black'
            },
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            margin: {t: 40, r: 40, b: 40, l: 40}
        };
    
        // Clear previous plot
        Plotly.react(plotId, traces, layout);
    }
    
    
    

    function displayHeatmap(data, plotId) {
        const heatmapData = data.outputs.map(output => output.map);
        const weed = data.outputs.map(output => output.weed);
        const dates = data.outputs.map(output => output.date);
        const slider = document.getElementById('dateSlider');
        const sliderValueDisplay = document.getElementById('sliderValue');
    
        // Initialize slider
        slider.max = heatmapData.length - 1; // max value is the length of the heatmapData minus 1
    
        // Event Listener for slider movement
        slider.addEventListener('input', function() {
            const sliderValue = slider.value;
            sliderValueDisplay.textContent = sliderValue;
            Heatmap(sliderValue, heatmapData, weed, dates);
        });
    
        const showStrips = document.getElementById('showStrips')
        const selectedOption = document.getElementById('heatmapOption');
        showStrips.addEventListener('change', function() {
            Heatmap(slider.value, heatmapData, weed, dates);
        });
        selectedOption.addEventListener('change', function() {
            Heatmap(slider.value, heatmapData, weed, dates);
        });
    
        // Function to display the corresponding Heatmap data
        function Heatmap(index, map, weed, dates) {
            const mapData = map[index];  // Access the data for the heatmap at the given index
            const weedData = weed[index];
            const showStrips = document.getElementById('showStrips').checked;
            const selectedOption = document.getElementById('heatmapOption').value;
    
            if (mapData) {
                // Heatmap data trace
                const heatmapTrace = {
                    z: mapData,
                    type: 'heatmap',
                    colorscale: [
                        [0,    'rgb(100,50,0)'],  // Brown for all values = 0
                        [0.01, 'rgb(126,185,48)'],  // Light green for smaller values
                        [1,    'rgb(0,100,0)']  // Dark green for higher values up to 50
                    ],
                    colorbar: {
                        title: 'Plant Density',
                        titleside: 'right'
                    }
                };
    
                // Weed data trace with opacity
                const weedTrace = {
                    z: weedData,
                    type: 'heatmap',
                    colorscale: 'Hot', // Using a 'Hot' colorscale for differentiation
                    colorbar: {
                        title: 'Weed Presence',
                        titleside: 'left', // Move the colorbar to the left side
                        x: -0.15, // Adjust the x position
                    },
                    opacity: 0.5 // Semi-transparent to view overlay with plant data
                };
    
                const layout = {
                    title: `Heatmap on ${dates[index]}`,
                    xaxis: {
                        title: 'X Axis',
                        showgrid: false,
                        zeroline: false,
                        showline: true,
                        mirror: 'allticks',
                        linewidth: 2,
                        linecolor: 'black'
                    },
                    yaxis: {
                        title: 'Y Axis',
                        showgrid: false,
                        zeroline: false,
                        showline: true,
                        mirror: 'allticks',
                        linewidth: 2,
                        linecolor: 'black'
                    },
                    margin: { t: 40, r: 20, b: 40, l: 50 },
                    plot_bgcolor: 'white',
                    paper_bgcolor: 'white'
                };
    
                let traces = [];
                if (selectedOption === 'plants') {
                    traces.push(heatmapTrace);
                } else if (selectedOption === 'weeds') {
                    traces.push(weedTrace);
                } else if (selectedOption === 'plantsweeds') {
                    traces.push(heatmapTrace, weedTrace);
                }
    
                // If strips are to be shown, they can be added here as additional trace
                if (showStrips) {
                    // Define and add stripTrace
                }
    
                Plotly.newPlot(plotId, traces, layout);
            } else {
                console.error(`No data found for index ${index}.`);
            }
        }
    
        // Display the initial heatmap
        Heatmap(0, heatmapData, weed, dates); // Updated to start at the first index
    }
    
    },);
});
});
