
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

#%%

# General File Reading
for i in range(5):
    # Temperature readings start at 58C and go up to 66C
    temp = 58 + (2*i)
    path = "C:/Users/mborj/Documents/Rogers Lab/20220707-Hysteresis-heating-cleaned/20220707-Hysteresis-heating-cleaned/"

    #Naming Convention ("[Concentration]_[outer/inner]_[temp]C.tif")
    droplets = io.imread(path + "1.5mM_outer_%dC.tif" % temp)
    condensates =  io.imread(path + "1.5mM_inner_%dC.tif" % temp)

    #Remove 5 pixels from each image edge
    droplets = droplets[5:1195,5:1915]
    condensates = condensates[5:1195,5:1915]

    #Apply a Gaussian Filter of Sigma 3 on inner and outer images
    sig = 3
    gauss = filters.gaussian(droplets, sigma=sig)
    condgauss = filters.gaussian(condensates, sigma = (sig-1))

    #Use a Canny edge detector to detected condensate edges
    edges = feature.canny(condgauss, sigma = 0.2)
    fill_edges = ndi.binary_fill_holes(edges)
    fill_edges = remove_small_objects(fill_edges, min_size = 200)

    #Label each new region of condensate and measure using reginoprops
    cond_label = label(fill_edges)
    props = regionprops_table(cond_label, properties = ('area', 'centroid', 'orientation', 'axis_major_length', 'axis_minor_length'))
    cond_props = pd.DataFrame(props)
    cond_props.rename(columns={'area': 'condensate area'}, inplace = True)

    #TODO Add more documentation (starting here)
    # fig, axes = plt.subplots(1,2, sharey = True)
    # axes[0].imshow(edges)
    # axes[1].imshow(condgauss)
    # plt.show()
    fill_edges = ~fill_edges
    fill_edges = fill_edges
    cond_img = condgauss*fill_edges

    param1 = 25
    param2 = 60

    cv_img = img_as_ubyte(gauss)
    circles = cv.HoughCircles(cv_img, cv.HOUGH_GRADIENT, 1, 200, param1=param1, param2=param2, minRadius=50, maxRadius=0)
    result = np.uint32(np.int32(circles))

    numCond = cond_props.shape[0]
    droplet_x = pd.Series(float("NaN"), range(numCond))
    droplet_y = pd.Series(float("NaN"), range(numCond))
    droplet_radius = pd.Series(float("NaN"), range(numCond))
    for j in range(cond_props.shape[0]):
        x = cond_props['centroid-0'][j]
        y = cond_props['centroid-1'][j]
        for k in range(circles.shape[1]):
            drop_x = circles[0][k][1]
            drop_y = circles[0][k][0]
            radius = circles[0][k][2]
            if isContained(x,y,drop_x,drop_y,radius):
                droplet_x[j] = drop_x
                droplet_y[j] = drop_y
                droplet_radius[j] = radius

    cond_props['droplet-x'] = droplet_x
    cond_props['droplet-y'] = droplet_y
    cond_props['droplet_radius'] = droplet_radius

    for j in result[0, :]:
        cv.circle(cv_img, (j[0], j[1]), j[2], (0, 255, 0), 2)
        cv.circle(cond_img, (j[0], j[1]), j[2], (0, 255, 0), 2)

    fig, axes = plt.subplots(1,2, sharey = True)
    axes[0].imshow(cond_img)
    axes[0].set_title("Condensates Temp = " + str(temp))

    axes[1].imshow(cv_img)
    axes[1].set_title("Droplets Temp = %d" % (temp))

    fig.suptitle('1.5 mM DNA')
    fig.subplots_adjust(top=0.88)
    plt.savefig("C:/Users/mborj/Documents/Rogers Lab/20220707-Hysteresis-heating-cleaned/20220707-Hysteresis-heating-cleaned/1.5mM Data CSV/FigureMatched%dC.png" % temp)
    plt.show()

    cond_props.to_csv("C:/Users/mborj/Documents/Rogers Lab/20220707-Hysteresis-heating-cleaned/20220707-Hysteresis-heating-cleaned/1.5mM Data CSV/Matched%dC.csv" % temp)