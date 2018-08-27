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

REC_LENGTH = peakData[0]
FLOW_RATE = peakData[1]

initial_conc = 2.274
x = []#Contains concentration
y = []#Contains intesntiy values measured, x and y must be of the same length. (Parallel arrays)

for specDat in peakData[2:]:
	if specDat[3] in x:#If we already have a measurement for this concentration then we average it with the pre-existing one.
		index = x.index(specDat[3])
		y[index]+=specDat[2]
		y[index]/=2

	else:#Otherwise we add it to our data array
		x.append(specDat[3])
		y.append(specDat[2])

x = np.array(x)
x= x*initial_conc

cc = np.polyfit(np.log10(x),np.log10(y),1)#Fit the data points
linspace = np.linspace(2,6,20)#line space for fitted line
plt.plot(np.log10(x),np.log10(y),marker=".",linestyle="None")#Plot data points
plt.plot(linspace,cc[0]*linspace+cc[1])#Plot fitted line

plt.xlabel("Cocentration 10^x beads/ml")
plt.ylabel("Total intensity measured 10^y arb units")
plt.show()
plt.savefig("singleIntense.png",format="png")
sI = 10**cc[0][0]

print("Fitted intensity value for 1 bead: ",sI)

print("\nBeads observed:\nConc : BeadCount : ExpectedBeadCount")
for i in range(0,len(x)):
	print(int(x[i]),int(y[i][0]/sI),int(x[i])*FLOW_RATE*REC_LENGTH)
