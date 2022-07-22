#%%
"""
Created on 2022/8/7

@author: Marco
"""
import matplotlib.pyplot as plt
import skimage.filters.thresholding
from skimage import filters, io, data
from skimage.filters import try_all_threshold
from skimage.util import img_as_ubyte
import numpy as np

import cv2 as cv

# Marco Vial 9 Test Run
droplets = io.imread("Z:/mborja/22-07-01 3 Channel Droplet Measuring/Vial 9 Room Temp/Default/img_channel000_position000_time000000001_z000.tif")

#Remove 5 pixels from each image edge
droplets = droplets[5:1195,5:1915]

#%%
def sciShow(image):
    plt.imshow(image)
    plt.show()


#%%

# Gaussian blur on original image
sig = 3
gauss = filters.gaussian(droplets, sigma = sig)

median = cv.medianBlur(droplets, 9)

#fig, axes = plt.subplots(1,3, sharey = True)


#%%
# axes[0].imshow(droplets)
# axes[0].set_title('Original')
#
# axes[1].imshow(gauss)
# axes[1].set_title('Gaussian Blur, sigma = %d' % (sig))
#
# axes[2].imshow(median)
# axes[2].set_title('Median Blur,')
#
# plt.tight_layout()
# plt.show()

#%% Remove background

# fig, ax = try_all_threshold(gauss, figsize = (10, 8), verbose = False)
# plt.show()

li_thresh = filters.thresholding.threshold_li(gauss)
binary = li_thresh > gauss

# plt.imshow(binary, cmap = 'gray')
# plt.show()

remove_background = gauss*binary

#%% Circle Location

# Masked
# cv_img = img_as_ubyte(remove_background)
# circles = cv.HoughCircles(cv_img, cv.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 0, maxRadius = 0)

# No mask
#%%
param1 = 25
param2 = 70

cv_img = img_as_ubyte(gauss)
circles = cv.HoughCircles(cv_img, cv.HOUGH_GRADIENT, 1, 200, param1 = param1, param2 = param2, minRadius = 50, maxRadius = 0)

result = np.uint32( np.int32(circles))
for i in result[0,:]:
    cv.circle(cv_img, (i[0],i[1]),i[2],(0,255,0),2)

plt.imshow(cv_img)
plt.title(" param1 = %d, param 2 = %d" % (param1, param2))
plt.show()
# cv.imshow('detected circles', cv_img)
# cv.waitKey(0)
# cv.destroyAllWindows()