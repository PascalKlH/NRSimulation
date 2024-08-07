import numpy as np
import random

def move_center_opposite(array, center_pos, random_pos):
    rows, cols = array.shape

    # Get the center and random positions
    center_x, center_y = center_pos
    random_x, random_y = random_pos

    # Calculate the direction from the center to the random element
    direction_x = random_x - center_x
    direction_y = random_y - center_y

    # Calculate the opposite movement
    if direction_x > 0:
        movementx = -1
    elif direction_x < 0:
        movementx = 1
    else:
        movementx = 0

    if direction_y > 0:
        movementy = -1
    elif direction_y < 0:
        movementy = 1
    else:
        movementy = 0

    # Move the center to the opposite direction
    new_center_x = center_x + movementx
    new_center_y = center_y + movementy

    # Check if the new center is within the bounds
    if new_center_x < 0 or new_center_x >= rows:
        new_center_x = center_x

    if new_center_y < 0 or new_center_y >= cols:
        new_center_y = center_y

    return new_center_x, new_center_y

# Create a 5x5 array
array = np.zeros((5, 5))

# Set the center element initially to 1
array[2, 2] = 1

# Get the initial center position
center_pos = (2, 2)

# Number of iterations for the loop
iterations = 10

for _ in range(iterations):
    # Get a random position
    random_pos = (random.randint(0, 4), random.randint(0, 4))
    
    # Ensure the random position is not the same as the center position
    while random_pos == center_pos:
        random_pos = (random.randint(0, 4), random.randint(0, 4))

    # Set the random position to 2
    array[random_pos] = 2

    # Move the center to the opposite direction
    new_center_pos = move_center_opposite(array, center_pos, random_pos)
    
    # Update the array with the new center position
    array[center_pos] = 0  # Clear the old center position
    array[new_center_pos] = 1  # Set the new center position

    # Print the result
    print("Original array:")
    print(array)
    
    # Clear the random position for the next iteration
    array[random_pos] = 0

    # Update center_pos for the next iteration
    center_pos = new_center_pos

    print("Updated array:")
    print(array)
    print("Center position:", center_pos)
    print("Random position:", random_pos)
    print("New center position:", new_center_pos)
    print()

