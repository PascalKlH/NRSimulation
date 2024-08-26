document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('parametersForm');

    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Prevent the default form submission

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Data received:', data);

            // Call the function to handle and display the data
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    function displayResults(data) {
        console.log('Data in displayResults:', data);

        const dates = data.time || [];
        const yields = data.yield || [];
        const growths = data.growth || [];
        const waters = data.water || [];
        const overlaps = data.overlap || [];
        const heatmapData = data.map || [];

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
        const slider = document.getElementById('dateSlider');
        const sliderValueDisplay = document.getElementById('sliderValue');
        const heatmap = document.getElementById('heatmap');

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

            if (mapData) {
                const data = [{
                    z: mapData,  // mapData contains the 2D array for the heatmap
                    type: 'heatmap',
                    colorscale: [
                        [0, 'rgb(100,50,0)'],  // Brown for all values = 0
                        [0.01, 'rgb(150,255,150)'],  // Light green for smaller values
                        [1, 'rgb(0,100,0)']  // Dark green for higher values up to 50
                    ],
                    colorbar: {
                        title: 'Value',
                        titleside: 'right'
                    }
                }];

                const layout = {
                    //take the first date of the array and add the index to it
                    title: `Heatmap for Hour ${index} on ${dates[0]}`,
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

                Plotly.newPlot('heatmap', data, layout);
            } else {
                console.error(`No data found for index ${index}.`);
            }
        }

        // Initially display the first heatmap data
        displayHeatmap(0);
    }
});