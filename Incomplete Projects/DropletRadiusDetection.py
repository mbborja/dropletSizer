
"""
Created on 2022/8/7

This file was run on the data from the Hysteresis-heated-cleaning DNA nanostar experiments
run at high temperatures 58C-66C

Images are divided by inner radii and outer radii
A HoughCircles algorithm is run to obtain outer radii from the droplets
A Canny Edge Detection algorithm is run to obtain the inner radii from the condensates

Once these radii are obtained, each condensate is matched with its respective droplet and
its data will be matched containing each droplet's [inner radius, outer radius, concentration, temp]

Scientist notes:
Needs a cleanup

@author: Marco
"""
import matplotlib.pyplot as plt
import pandas as pd
import math
from matplotlib_scalebar.scalebar import ScaleBar
import skimage.filters.thresholding
from skimage import filters, io, feature, data
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects
from skimage.filters import try_all_threshold
from skimage.util import img_as_ubyte
from skimage.measure import label, regionprops, regionprops_table
import numpy as np

import cv2 as cv

# TODO Write function documentation
def isContained(x, y, center_x, center_y, radius):
    dx = abs(x - center_x)
    dy = abs(y - center_y)
    left = int(dx**2) + int(dy**2)
    right = int(radius**2)
    if left < right:
        return True
    else:
        return False

# TODO Write function documentation
def showFig(figure, title = ""):
    plt.imshow(figure)
    plt.title = title
    plt.show()

# TODO Write function documentation
def circleProps(img, props):
    for j, row in props.iterrows():
        if(not math.isnan(row['droplet_radius'])):
            cv.putText(img, str(j), (int(row['droplet-y']), int(row['droplet-x'] - 40)), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,0),thickness= 4)
            cv.circle(img, (int(row['centroid-1']), int(row['centroid-0'])), int(row['cond-radius']), (255,255,255), 5)
            cv.circle(img, (int(row['droplet-y']), int(row['droplet-x'])), int(row['droplet_radius']), (50,255,0), 5)
        else:
            props.drop(j, inplace = True)
    return(img)

def deleteLargeObjects(props):
    for index, row in props.iterrows():
        if row['condensate area'] > 20000:
            props.drop(index, inplace=True)
    return(props)