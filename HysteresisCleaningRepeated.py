
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

#%%

# General File Reading
for i in range(5):
    # Temperature readings start at 58C and go up to 66C
    conc = "1.5"
    temp = 58 + (2*i)
    path = "C:/Users/mborj/Documents/Rogers Lab/20220707-Hysteresis-heating-cleaned/20220707-Hysteresis-heating-cleaned/"

    #Naming Convention ("[Concentration]_[outer/inner]_[temp]C.tif")
    droplets = io.imread(path + conc + "mM_outer_%dC.tif" % temp)
    condensates = io.imread(path + conc + "mM_inner_%dC.tif" % temp)

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
    cond_img = condgauss*(fill_edges)
    param1 = 25
    param2 = 60

    cv_img = img_as_ubyte(gauss)
    circles = cv.HoughCircles(cv_img, cv.HOUGH_GRADIENT, 1, 200, param1=param1, param2=param2, minRadius=50, maxRadius=0)
    result = np.uint32(np.int32(circles))

    numCond = cond_props.shape[0]
    test_temp = pd.Series(temp, range(numCond))
    test_conc = pd.Series(conc, range(numCond))
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

    cond_radius = np.sqrt(cond_props["condensate area"].apply(lambda x: float(x))/math.pi)
    cond_props['cond-radius'] = cond_radius
    cond_props['droplet-x'] = droplet_x
    cond_props['droplet-y'] = droplet_y
    cond_props['droplet_radius'] = droplet_radius
    cond_props['temp'] = test_temp
    cond_props['concentration (mM)'] = test_conc

    # for j in result[0, :]:
    #     cv.circle(cv_img, (j[0], j[1]), j[2], (0, 255, 0), 2)
    #     cv.circle(droplets, (j[0], j[1]), j[2], (0, 255, 0), 2)
    #     cv.circle(condensates, (j[0], j[1]), j[2], (0, 255, 0), 2)

    for index, row in cond_props.iterrows():
        if row['condensate area'] > 20000:
            cond_props.drop(index, inplace=True)

    for j, row in cond_props.iterrows():
        if(not math.isnan(row['droplet_radius'])):
            cv.putText(condensates, str(j), (int(row['droplet-y']), int(row['droplet-x'])), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,0),thickness= 4)
            cv.circle(condensates, (int(row['centroid-1']), int(row['centroid-0'])), int(row['cond-radius']), (255,255,255), 2)
            cv.circle(condensates, (int(row['droplet-y']), int(row['droplet-x'])), int(row['droplet_radius']), (0,255,0), 2)
        else:
            cond_props.drop(j, inplace = True)
            print("WHATT" + str(j))

    # plt.imshow(condensates)
    # scalebar = ScaleBar(0.58, 'um')
    # plt.gca().add_artist(scalebar)
    # plt.title(("Condensates Temp = " + str(temp)))
    # plt.show()


    fig, axes = plt.subplots(1,2, sharey = True)
    axes[0].imshow(condensates)
    axes[0].set_title("Condensates Temp = " + str(temp))

    axes[1].imshow(droplets)
    axes[1].set_title("Droplets Temp = %d" % (temp))


    fig.suptitle(conc +' mM DNA')
    fig.subplots_adjust(top=0.88)
    plt.savefig("C:/Users/mborj/Documents/Rogers Lab/20220707-Hysteresis-heating-cleaned/20220707-Hysteresis-heating-cleaned/" + conc + "mM Data CSV/FigureMatched%dC.png" % temp)
    plt.show()

    plt.imshow(condensates)
    plt.title("Labeled Condensates " + conc + "mM %dC" % temp)
    plt.savefig("C:/Users/mborj/Documents/Rogers Lab/20220707-Hysteresis-heating-cleaned/20220707-Hysteresis-heating-cleaned/" + conc + "mM Data CSV/"+ conc + "mM-Labeled-Condensates%dC.png" % temp)
    plt.show()

    cond_props.to_csv("C:/Users/mborj/Documents/Rogers Lab/20220707-Hysteresis-heating-cleaned/20220707-Hysteresis-heating-cleaned/" + conc + "mM Data CSV/Matched%dC.csv" % temp)