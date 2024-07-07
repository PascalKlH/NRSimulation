import numpy as np
import plotly.graph_objects as go

size = 12  # Example size of the circular mask
center = size // 2  # Calculate the center of the mask

# Create coordinate matrices using np.ogrid
y, x = np.ogrid[:size, :size]
mask = (x - center) ** 2 + (y - center) ** 2 <= (center) ** 2  # Create a circular mask
# x and y now hold the coordinate matrices
print("x coordinates:")
print(x)
print("y coordinates:")
print(y)
print("Circular mask:")
print(mask)
#visualize the circular mask
data=np.zeros((size,size))
data[mask]=1
fig = go.Figure()
fig.add_trace(go.Heatmap(z=data, colorscale='gray'))
fig.show()