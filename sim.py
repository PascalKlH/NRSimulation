import numpy as np
import plotly.graph_objects as go

def create_sphere_outline(radius, center=(0, 0, 0), num_samples=100):
    # Create points on the circumference of a circle in the xy-plane
    theta = np.linspace(0, 2 * np.pi, num_samples)
    x_circle = radius * np.cos(theta) + center[0]
    y_circle = radius * np.sin(theta) + center[1]
    z_circle = np.full_like(theta, center[2])

    # Create points on the circumference of a circle in the yz-plane
    phi = np.linspace(0, np.pi, num_samples)
    y_circle2 = radius * np.cos(phi) + center[1]
    z_circle2 = radius * np.sin(phi) + center[2]
    x_circle2 = np.full_like(phi, center[0])

    # Create points on the circumference of a circle in the xz-plane
    psi = np.linspace(0, np.pi, num_samples)
    x_circle3 = radius * np.cos(psi) + center[0]
    z_circle3 = radius * np.sin(psi) + center[2]
    y_circle3 = np.full_like(psi, center[1])

    # Combine all circle points
    x = np.concatenate([x_circle, x_circle2, x_circle3])
    y = np.concatenate([y_circle, y_circle2, y_circle3])
    z = np.concatenate([z_circle, z_circle2, z_circle3])

    return x, y, z

# Define the radius and center of the sphere
radius = 15
center = (25, 25, 25)

# Generate sphere outline coordinates
x, y, z = create_sphere_outline(radius, center)

# Create the plot
fig = go.Figure(data=[
    go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='lines',
        line=dict(color='red', width=2),
    )
])

# Set the layout of the plot
fig.update_layout(scene=dict(
    xaxis=dict(nticks=10, range=[0, 50]),
    yaxis=dict(nticks=10, range=[0, 50]),
    zaxis=dict(nticks=10, range=[0, 50]),
))

fig.show()
