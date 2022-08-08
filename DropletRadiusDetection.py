
"""
Created on 2022/8/7

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

def isContained(x, y, center_x, center_y, radius):
    """
    This returns true if point (x,y) is inside a circle with center (center_x,center_y) and
    a specified radius
    :param x: x-coordinate of point
    :param y: y-coordinate of point
    :param center_x: x-coordinate of circle's center
    :param center_y: y-coordinate of circle's center
    :param radius: radius of circle
    :return: True if contained, False otherwise
    """
    dx = abs(x - center_x)
    dy = abs(y - center_y)
    left = int(dx**2) + int(dy**2)
    right = int(radius**2)
    if left < right:
        return True
    else:
        return False

def showFig(figure, title = ""):
    """
    Quickly show figure on PyCharm SciView
    :param figure: Image to be plotted using matplotlib's imshow
    :param title: Set a title for the plot
    :return:
    """
    plt.imshow(figure)
    plt.title = title
    plt.show()

def encircleProps(img, props):
    """
    Encircle each detected and matched droplet and condensate radius
    :param img: ndarray image to be labeled with circles
    :param props: Dataframe containing droplet and condensate information
    :return: encircled image img
    """
    for j, row in props.iterrows():
        if(not math.isnan(row['droplet_radius'])):
            cv.putText(img, str(j), (int(row['droplet-y']), int(row['droplet-x'] - 40)), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,0),thickness= 4)
            cv.circle(img, (int(row['centroid-1']), int(row['centroid-0'])), int(row['cond-radius']), (255,255,255), 5)
            cv.circle(img, (int(row['droplet-y']), int(row['droplet-x'])), int(row['droplet_radius']), (50,255,0), 5)
        else:
            print("swag")
            props.drop(j, inplace = True)
    return img, props

def deleteLargeCondensates(props, min_size = 20000):
    """
    Deletes any objects in the pandas dataframe whose conen
    :param props: Dataframe containing droplet and condensate information
    :param size: Minimum size of things to be deleted
    :return: Dataframe with deleted props
    """
    for index, row in props.iterrows():
        if row['condensate area'] > min_size:
            props.drop(index, inplace=True)
    return props

def plotWithScaleBar(img, scale, lscale = "", temp = "", conc = ""):
    """
    This function plots an image with a specific scalebar
    :param img: ndarray to be plotted
    :param scale: pixel to measurement scale measure/pixels
    :param lscale: specific length scale (ie. um, mm, m, km)
    :param temp: temperature
    :param conc:
    :return:
    """
    plt.imshow(img)
    scalebar = ScaleBar(scale, lscale)
    plt.gca().add_artist(scalebar)
    plt.title(("Temp = " + str(temp)) + (" Conc = " + str(conc)))
    plt.show()