Title: Transform forward camera to top view
Date: 2017-12-04 10:00

When dealing with robotics, we often get to a point, where we need to map our surroundings and localize the agent in the environment. If we equip our robot with a front facing camera, things get much easier. But this also creates a problem, of presenting the data we get as input in a way, that will become useful. Today I will present you how to transform the image we are getting from a camera mounted at the front of our robot, to a top view.

First of all we will be using Python 3 (since its already a couple of years old and most libraries are ported, so this IS what you should be using) and we need the following python modules to be installed:

- `Numpy` – for making our life easier with numbers,
- `Matplotlib` – for displaying our data in a readable fashion,
- `OpenCV` – for dealing with transformations.

## Making this work

We will start by doing all the imports:

```python
import matplotlib.image as img
import matplotlib.pyplot as plt
import cv2
import numpy as np
```

Now we will read the image and assign our source and destination points using `numpy`. This can be a bit tricky to get working. The numpy values for your source and destination arrays go as follows:

- bottom left -> bottom right-> top right -> top left.

We will display the image, so that you can read the points of a square meter from your image. Below in image_source you can see how I assigned my points and compare them to the previous image. The bigger the side value you set, the “lower” the camera will be.

```python
# Load the image from your camera
image = img.imread('camera_image.jpg')
# Display the image to see points
plt.imshow(image)
plt.show()

# Values taken from my image
image_source = np.float32([
    [600,900], # bottom left
    [380,1150], # bottom right
    [1220,1150], # top right
    [1000,900] # top left
])

# Destination square size
side = 120
# The destination to create a top view
image_destination = np.float32([
 [image.shape[1]/2 - side, image.shape[0]], 
 [image.shape[1]/2 + side, image.shape[0]], 
 [image.shape[1]/2 + side, image.shape[0] - 2*side], 
 [image.shape[1]/2 - side, image.shape[0] - 2*side]
])
```

Once we have that done, we will use OpenCV to do all the work for us. First we will get the perspective matrix using `cv2.getPerspectiveTransform()`, and then we will use `cv2.warpPerspective()` to warp our image into the top view output.

```python
# Get our perspective matrix
M = cv2.getPerspectiveTransform(
   image_source, 
   image_destination
)

# Apply the matrix to the image
warped = cv2.warpPerspective(
   image, 
   M, 
   (image.shape[1], image.shape[0])
)
```
