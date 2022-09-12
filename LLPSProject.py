"""
Created on 2022/8/8

This file was

Images are divided by inner radii and outer radii
A HoughCircles algorithm is run to obtain outer radii from the droplets
A Canny Edge Detection algorithm is run to obtain the inner radii from the condensates

Once these radii are obtained, each condensate is matched with its respective droplet and
its data will be matched containing each droplet's [inner radius, outer radius, concentration, temp]

Scientist notes:
Needs a cleanup

@author: Marco
"""
#%%
param1 = 12
param2 = 100
mindist= 100

dparam1 = 25
dparam2 = 60

import matplotlib.pyplot as plt
import pandas as pd
import math
import DropletRadiusDetection as drd
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
import glob
from skimage import io
import DropletRadiusDetection
from DropletRadiusDetection import showFig

path = "C:/Users/mborj/Documents/Rogers Lab/22-08-05 LLPS Data Analysis/Trial 1 0.6mM/"
conc = "0.6mM"
files = (glob.glob(path + "*.tif"))
finalcsv = pd.DataFrame()


for i in range (20,80):
    temp = i
    list = []
    for filename in files:
        if str(temp) in filename:
            list.append(filename)
    if len(list) == 2:
        condensates = io.imread(list[0])
        droplets = io.imread(list[1])

        droplets = droplets[5:1195, 5:1915]
        condensates = condensates[5:1195, 5:1915]

        # Remove 5 pixels from each image edge
        droplets = droplets[5:1195, 5:1915]
        condensates = condensates[5:1195, 5:1915]

        # Apply a Gaussian Filter of Sigma 3 on inner and outer images
        sig = 3
        gauss = filters.gaussian(droplets, sigma=sig)
        condgauss = filters.gaussian(condensates, sigma = sig-2)

        cv_img = img_as_ubyte(condgauss)
        circles = cv.HoughCircles(cv_img, cv.HOUGH_GRADIENT, 1, mindist, param1=param1, param2=param2, minRadius=2, maxRadius=100)

        cv_img_drop = img_as_ubyte(gauss)
        circles_drop = cv.HoughCircles(cv_img_drop, cv.HOUGH_GRADIENT, 1, 200, param1=dparam1, param2=dparam2, minRadius=50, maxRadius=0)

        if circles is not None and circles_drop is not None:
            props = pd.DataFrame(circles[0])
            props = props.rename(columns = {0:"cond_x", 1:"cond_y", 2:"cond_radius" } )
            props_drop = pd.DataFrame(circles_drop[0])
            props_drop = props_drop.rename(columns = {0:"drop_x", 1:"drop_y", 2:"drop_radius" })

            numCond = props.shape[0]
            drop_x= pd.Series(float("NaN"), range(numCond))
            drop_y = pd.Series(float("NaN"), range(numCond))
            drop_radius = pd.Series(float("NaN"), range(numCond))

            complete = pd.DataFrame(columns = ["cond_x", "cond_y", "cond_radius", "drop_x", "drop_y", "drop_radius"])
            for i, row in props.iterrows():
                x = row["cond_x"]
                y = row["cond_y"]

                for j, drow in props_drop.iterrows():
                    dx = drow["drop_x"]
                    dy = drow["drop_y"]
                    radius = drow["drop_radius"]
                    # if(drd.isContained(x,y,dx,dy, radius)):
                    #     print("TRUE")
                    #     print("dropx: " + str(dx) + " condx: " + str(x))
                    #     print("dropy: " + str(dy) + " condy: " + str(y))
                    if drd.isContained(x,y,dx,dy,radius):
                        complete.loc[len(complete.index)] = [x,y,row["cond_radius"],dx,dy,radius]
                        # drop_x[j] = dx
                        # drop_y[j] = dy
                        # drop_radius[j] = radius


            # props['drop_x'] = drop_x
            # props['drop_y'] = drop_y
            # props['drop_radius'] = drop_radius
            complete['temp'] = temp
            complete['conc'] = conc

            cv_img, complete = drd.encircleProps(cv_img, complete)

            complete['drop_radius'] = 100/345 * complete['drop_radius']
            complete['cond_radius'] = 100/345 * complete['cond_radius']
            complete['drop_volume'] = 4.4332 * complete['drop_radius'] ** 2.89346
            complete['cond_volume'] = 4 / 3 * math.pi * complete['cond_radius'] ** 3

            finalcsv = pd.concat([finalcsv, complete])



        showFig(cv_img, title = str(temp) + "C")

finalcsv.to_csv(path + conc + " Matched Final.csv")
        #
        #
        # detectionTests = []
        # for i in [0.25*i for i in range(1,5)]:
        #     detectionTests.append(feature.canny(condensates, sigma = i))
        #
        # fig, axes = plt.subplots(figsize=(15, 6), nrows=2, ncols=2, sharex=True, sharey=True)
        #
        # for i in range(4):
        #     axes.flat[i].imshow(detectionTests[i], cmap=plt.cm.gray)
        #     axes.flat[i].set_axis_off()
        #     axes.flat[i].set_title(str(temp) + "C Sigma = {}".format(0.25 * i), fontsize=16)
        #
        # fig.tight_layout()
        # plt.show()
        # Use a Canny edge detector to detected condensate edges
        #
        # edges = feature.canny(condensates, sigma=0.25, low_threshold=25, high_threshold= 50)
        # fill_edges = ndi.binary_fill_holes(edges)
        # fill_edges = remove_small_objects(fill_edges, min_size=200)
        #
        # kernel = np.ones((5, 5), 'uint8')
        # bigEdges = ndi.binary_dilation(edges)
        # showFig(condensates+(bigEdges*255), title=str(temp) + "C inner")
        #
    # temp = filename[-7:-5]
    # print(temp)
    # showFig(io.imread(filename), title = "temp")
