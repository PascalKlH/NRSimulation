import numpy as np
import plotly.graph_objects as go

def create_hemisphere(radius):
    diameter = 2 * radius
    hemisphere = np.zeros((diameter, diameter))

    for x in range(diameter):
        for y in range(diameter):
            distance = np.sqrt((x - radius)**2 + (y - radius)**2)
            if distance <= radius:
                hemisphere[x, y] = np.sqrt(radius**2 - distance**2)
            else:
                hemisphere[x, y] = 0
    return hemisphere

def plot_hemisphere(hemisphere):
    fig = go.Figure(data=go.Heatmap(
        z=hemisphere,
        colorscale='Viridis'
    ))

    fig.update_layout(
        title='2D Heatmap of a Hemisphere',
        xaxis_title='X (cm)',
        yaxis_title='Y (cm)',
        width=600,
        height=600
    )

    fig.show()

# Set the radius of the hemisphere
radius = 11  # 10 cm

# Create the hemisphere
hemisphere = create_hemisphere(radius)

# Plot the hemisphere
plot_hemisphere(hemisphere)





