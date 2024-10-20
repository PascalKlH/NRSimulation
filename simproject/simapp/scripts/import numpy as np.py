import numpy as np

def adjusted_growth(x, h=24.41, r=0.002, b=35.625, m=2.077):
    """
    Calculate the size of the crop using adjusted growth parameters.

    Parameters:
    - x : float or ndarray, time or other suitable growth measure
    - h : float, asymptotic maximum size
    - r : float, modified growth rate to stretch the curve
    - b : float, scaling factor affecting the steepness
    - m : float, shape parameter affecting the curve's symmetry

    Returns:
    - size : float or ndarray, calculated size of the crop
    """
    size =(h*b*r)/(1-m)*np.exp(-r*x)*(1+b*np.exp(-r*x))**(1/(1-m))
    return size

# Example of using the function
x_values = np.linspace(-5000, 10000)  # Time from 0 to 100 units
sizes = adjusted_growth(x_values)

# Plotting the result if needed
import matplotlib.pyplot as plt
plt.figure()
plt.plot(x_values, sizes, label='Adjusted Growth Curve')
plt.xlabel('Time')
plt.ylabel('Size')
plt.title('Adjusted Crop Growth Over Time')
plt.legend()
plt.show()
