"""This program takes total intensity and conc arrays, 
log plots and fits a line to find the intensity at 10^0 (aka the y intercept), 
to be used for dividing total intensity by to calculate the number of beads.
"""

import matplotlib.pyplot as plt
import numpy as np
import cPickle

DIRECTORY  = "./Records/test-5/"
with open(DIRECTORY+"peakData.txt","r") as f:
	peakData = cPickle.load(f)
initial_conc = 2.274
x = []
y = []
for specDat in peakData:
	x.append(specDat[3])
	y.append(specDat[2])

x = np.array(x)
x= x*initial_conc
y= np.array(y)

cc = np.polyfit(np.log10(x),np.log10(y),1)#Fit the data points
linspace = np.linspace(2,6,20)#line space for fitted line
plt.plot(np.log10(x),np.log10(y),marker=".",linestyle="None")#Plot data points
plt.plot(linspace,cc[0]*linspace+cc[1])#Plot fitted line

plt.xlabel("Cocentration 10^x beads/ml")
plt.ylabel("Total intensity measured 10^y arb units")
plt.show()
plt.savefig("singleIntense.png",format="png")
sI = 10**cc[0]
print("Fitted intensity value for 1 bead: ",sI)

""" print("\nBeads observed:")
for i in range(0,len(x)):
	print(x[i],y[i]/sI)
"""
