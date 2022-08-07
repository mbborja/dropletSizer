#%%
"""
Created on 2022/8/7

This file reads data from the FIJI plugin called 3D manager. Data is read as a pandas DataFrame and plotted.
For more information in segmenting 3d confocal images refer the following protocol:
TODO Write this protocol
https://docs.google.com/document/d/1ND0b4Q0BMJwMQk75DTJni6TjGzhjJKKuMhz1ZiWM7GY/edit

Scientist notes:
Plotting histograms and scatter plots has become much easier using the defined methods of the DataFrame object

@author: Marco
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

df = pd.read_csv("C:/Users/mborj/Documents/Rogers Lab/Project Series22_Small/Project 22 Data.csv")
df2 = pd.read_csv("C:/Users/mborj/Documents/Rogers Lab/Project Series019_large/Series019 Large 3d Measure.csv")
df3 = pd.read_csv("C:/Users/mborj/Documents/Rogers Lab/Project Series016-Small/3dmeasure.csv")
df4 = pd.read_csv("C:/Users/mborj/Documents/Rogers Lab/Project Series018-Large/measure3d.csv")

def myExpFunc(x, a, b):
    return a * np.power(x, b)

#%%


#DELETE
list = [df,df2,df3,df4]
for data in list:
    volNano = data['Vol (unit)'] * 10e-6
    data['Vol (nano)'] = volNano
    CAone = 1 - 1 / data['Ell_Flatness']
    data['1 - c/a'] = CAone
#

dfmix = pd.concat([df, df2, df3, df4])
volNano = dfmix['Vol (unit)']*10e-6
dfmix['Vol (nano)'] = volNano
CAone = 1 - 1/dfmix['Ell_Flatness']
dfmix['1 - c/a'] = CAone

#%%
ax = dfmix.plot.scatter(x = 'Vol (nano)', y = 'Ell_Flatness', c = 'Blue')
ax.set_xlabel(r'Ellipse Volume (nl)')
plt.show()

ax = dfmix.plot.scatter(x = 'Ell_MajRad', y = 'Ell_Flatness', c = 'Orange')
ax.set_xlabel(r'Ellipse Major Radius $(\mu m)$')
plt.show()

ax = dfmix.plot.scatter(x = 'Ell_MajRad', y = '1 - c/a', c = 'Green')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel(r'Ellipse Major Radius $(\mu m)$')

newX = np.logspace(0, 2, base = 10)

popt, pcov = curve_fit(myExpFunc, dfmix['Ell_MajRad'], dfmix["1 - c/a"])
plt.plot(newX, myExpFunc(newX, *popt), 'r-',
         label="({0:.3f}*x**{1:.3f})".format(*popt))
ax.grid(visible='on')
plt.legend(loc='lower right')

plt.tight_layout()
plt.show()

#%%
ax = dfmix.plot.scatter(x = 'Ell_MajRad', y = 'Vol (nano)', c = 'Red')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel(r'Ellipse Major Radius $(\mu m)$')

newX = np.logspace(0, 2, base = 10)
popt, pcov = curve_fit(myExpFunc, dfmix['Ell_MajRad'], dfmix["Vol (nano)"])
plt.plot(newX, myExpFunc(newX, *popt), 'r-',
         label="({0:.3f}*x**{1:.3f})".format(*popt))
ax.grid(visible = 'on')
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()

#%%

dfmix['RatioVolEllipsoid'].plot(kind = 'hist')
plt.xlabel('Volume / Fitted Ellipsoid Volume')
plt.show()

dfmix['Vol (unit)'].plot(kind = 'hist')
plt.xlabel(r'Ellipse Volume (nl)')
plt.show()

dfmix['Ell_Elon'].plot(kind = 'hist')
plt.xlabel("Ellipse Elongation")
plt.show()

dfmix['Ell_MajRad'].plot(kind = 'hist')
plt.xlabel(r'Ellipse Major Radius $(\mu m)$')
plt.show()

#%%

ax = df.reset_index().plot.scatter(x = 'Vol (nano)', y = 'Ell_Flatness', c = 'Blue', label='Series 1 Small')

df2.reset_index().plot.scatter(x = 'Vol (nano)', y = 'Ell_Flatness', c = 'Red', label = 'Series 2 Small', ax = ax)

df3.reset_index().plot.scatter(x = 'Vol (nano)', y = 'Ell_Flatness', c = 'Green', label = 'Series 3 large', ax = ax)

df4.reset_index().plot.scatter(x = 'Vol (nano)', y = 'Ell_Flatness', c = 'Orange', label = 'Series 3 large', ax = ax)


plt.title ("Volume vs Flatness")
plt.show()

ax = df.reset_index().plot.scatter(x = 'Ell_MajRad', y = '1 - c/a', c = 'Blue', label='Series 1 Small')

df2.reset_index().plot.scatter(x = 'Ell_MajRad', y = '1 - c/a', c = 'Red', label = 'Series 2 Small', ax = ax)

df3.reset_index().plot.scatter(x = 'Ell_MajRad', y = '1 - c/a', c = 'Green', label = 'Series 3 large', ax = ax)

df4.reset_index().plot.scatter(x = 'Ell_MajRad', y = '1 - c/a', c = 'Orange', label = 'Series 3 large', ax = ax)

plt.title("Major Radius vs. (1-c/a)")
plt.show()