document.addEventListener('DOMContentLoaded', function() {
    const plotButton = document.getElementById('plotresults');
    const simNameInput = document.getElementById('simname');
    const carousel1 = document.getElementById('carouselExampleCaptions1');
    const carousel2 = document.getElementById('carouselExampleCaptions2');
    const carousel3 = document.getElementById('carouselExampleCaptions3');
    const comparisonPlot = document.getElementById('comparisonPlot');

    plotButton.addEventListener('click', function() {
        const simName = simNameInput.value.trim();
        if (!simName) {
            alert("Please enter a simulation name.");
            return;
        }

        // Fetch simulation data from the server
        fetch(`/plot_simulation/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({simulation_name: simName})
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            setupCarousels(data.outputs);
            setupComparisonPlot(data.outputs);
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Failed to retrieve data.");
        });
    });

    function setupCarousels(outputs) {
        // Populate carousel items
        outputs.forEach((output, index) => {
            const newItem = document.createElement('div');
            newItem.className = 'carousel-item' + (index === 0 ? ' active' : '');
            newItem.innerHTML = `<div class="plot-container" id="plot${index}"></div>`;
            carousel1.appendChild(newItem);

            // Assume data structure contains appropriate keys
            Plotly.newPlot(`plot${index}`, [{
                x: output.data.time,
                y: output.data.values,
                type: 'scatter'
            }]);
        });

        // Setup indicators and inner content if more carousels needed
    }

    function setupComparisonPlot(outputs) {
        // Setup comparison plot logic
        const yAxisSelect = document.getElementById('y-axis-select');
        const yAxisValue = yAxisSelect.value;

        const trace = {
            x: outputs.map(o => o.param_value),
            y: outputs.map(o => o.data[yAxisValue]),
            type: 'scatter',
            mode: 'lines+markers',
            name: yAxisValue
        };

        const layout = {
            title: 'Comparison of ' + yAxisValue + ' Across Iterations',
            xaxis: { title: 'Iteration Parameter' },
            yaxis: { title: yAxisValue }
        };

        Plotly.newPlot(comparisonPlot, [trace], layout);
    }

    // Additional functionality to dynamically update plots on dropdown change
    yAxisSelect.addEventListener('change', function() {
        setupComparisonPlot(outputs);
    });
});
