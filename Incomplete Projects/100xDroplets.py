#%%
"""
Created on Wed June 22 2022

@author: Marco
"""
import skimage.segmentation
import skimage
import math
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from skimage.measure import label, regionprops, regionprops_table, find_contours
from skimage import feature, io
from scipy import ndimage as ndi
import matplotlib.pyplot as plt

droplets = io.imread("Z:/Omkar_Hegde/21_6/0.1mM_20X/Default/img_channel000_position000_time000000000_z000.tif")

# plt.imshow(droplets)
# plt.show()

##Sobel Filter
##edges = skimage.filters.sobel(droplets)

##Canny Edge Detector
edges = feature.canny(droplets,sigma = 4)
# plt.imshow(edges)
# plt.show()

##Filling edges with binary_fill_holes
fill_edges = ndi.binary_fill_holes(edges)
# plt.imshow(fill_edges)
# plt.show()


fig, axes = plt.subplots(1,3, sharey = True)

axes[0].imshow(droplets)
axes[0].set_title('Original')

axes[1].imshow(edges)
axes[1].set_title('Edges Canny, sigma = 4')

axes[2].imshow(fill_edges)
axes[2].set_title('Filled Edges')

# for a in axes:
#     a.axis('off')

plt.tight_layout()
plt.show()

fill_edges = fill_edges[5:1195,5:1915]
final = skimage.segmentation.clear_border(fill_edges)
#
# plt.imshow(final)
# plt.title("Final")
# plt.show()

removed_objects = skimage.morphology.remove_small_objects(final,min_size = 300)
# plt.imshow(removed_objects)
# plt.title("Removed Small Objects")
# plt.show()

dilated = removed_objects
for i in range(5):
    print(i)
    dilated = skimage.morphology.binary_dilation(dilated)

# plt.imshow(dilated)
# plt.title("Dilated")
# plt.show()

presentation_mask = droplets[5:1195,5:1915] + dilated*500
# plt.imshow(presentation_mask)
# plt.title("Final Mask")
# plt.show()

fig,axes = plt.subplots(1,2, sharey = True)

axes[0].imshow(droplets[5:1195,5:1915])
axes[0].set_title("Original")

axes[1].imshow(presentation_mask)
axes[1].set_title("Mask")

plt.show()
#%% Regionprops data
label_img = label(dilated)
regions = regionprops(label_img,droplets[5:1195,5:1915])
props = regionprops_table(label_img, properties = ('centroid','orientation','axis_major_length','axis_minor_length'))
pd.DataFrame(props)


#%%
fig = px.imshow(droplets[5:1195,5:1915], binary_string=True)
fig.update_traces(hoverinfo='skip')

properties = ['area', 'eccentricity', 'perimeter', 'intensity_mean']

for index in range(0, label_img.max()):
    label_i = regions[index].label
    contour = find_contours(label_img == label_i, 0.5)[0]
    y, x = contour.T
    hoverinfo = ''
    for prop_name in properties:
        hoverinfo += f'<b>{prop_name}: {getattr(regions[index], prop_name):.2f}</b><br>'
        if prop_name == "area":
            Areus = getattr(regions[index], prop_name)
            radius = math.sqrt(Areus/math.pi)
            hoverinfo += f'<b>{"radius"}: {radius:.2f}</b><br>'
    fig.add_trace(go.Scatter(
        x=x, y=y, name=label_i,
        mode='lines', fill='toself', showlegend=False,
        hovertemplate=hoverinfo, hoveron='points+fills'))

plotly.io.show(fig)