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
import matplotlib.pyplot as plt
import pandas as pd
import math
import DropletRadiusDetection
from matplotlib_scalebar.scalebar import ScaleBar
import skimage.filters.thresholding
from skimage import filters, io, feature, data
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects
from skimage.filters import try_all_threshold
from skimage.util import img_as_ubyte
from skimage.measure import label, regionprops, regionprops_table
import numpy as np
import glob
from skimage import io
import DropletRadiusDetection
from DropletRadiusDetection import showFig

path = "C:/Users/mborj/Documents/Rogers Lab/22-08-05 LLPS Data Analysis/Trial 5 0.1mM/"
conc = "0.1mM"
files = (glob.glob("C:/Users/mborj/Documents/Rogers Lab/22-08-05 LLPS Data Analysis/Trial 5 0.1mM/*.tif"))

for i in range (25,80):
    temp = i
    list = []
    for filename in files:
        if str(temp) in filename:
            list.append(filename)
    print(list)
    print(len(list))
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
        condgauss = filters.gaussian(condensates, sigma=(sig - 1))

        # Use a Canny edge detector to detected condensate edges
        edges = feature.canny(condgauss, sigma=0.5)
        fill_edges = ndi.binary_fill_holes(edges)
        fill_edges = remove_small_objects(fill_edges, min_size=200)

        showFig(droplets, title=str(temp) + "C inner")

    # temp = filename[-7:-5]
    # print(temp)
    # showFig(io.imread(filename), title = "temp")
