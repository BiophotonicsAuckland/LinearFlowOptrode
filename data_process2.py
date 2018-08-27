""""Written by Liam Murphy, July 5th 2018
a
This program is for processing many fluorescent recordings/samples from hdf5 files created from OptrodeVersion4.2 etc
It assumes that the background file and the sample file have the same recording length and integration time for correct subtraction.

Integration of spectra curves is done over 495 to 560nm. This can be modified in the code.
The temporal plots assume an integration time with the int_time var (in seconds) below and must be overwritten with the correct value for correct plotting.

This code is a refactoring of the previous data_process.py file written in 2017.
"""

import h5py, bisect,re
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
from time import gmtime, strftime

DIRECTORY = "./Records/test-5/"
BACKGROUND_FILENAME = "background-1"
dataFiles = ["10to5-3","10to5-2","10to5-1","10to4-3","10to3-3","10to2-3","10to4-2","10to3-2","10to2-2","10to4-1","10to3-1","10to2-1"]
shouldPlot = False#Set to false to prevent plots as it is time intensive. 
REC_LENGTH = 150 #Recording length for each spectra file in seconds
FLOW_RATE = 0.2/60 #Flow rate of sample in mL/sec
CONC_VAL = 2.274#Value of the concentration, order of mag is computed from each file

class Spectra():
	"""This class represents a given spectra recording and contains functionality for computing and plotting particular data"""
	#Constants
	INT_TIME  = 0.05#Integration time, aka exposure time of spectrometer 
	INTEGRATE_RANGE = (495,550) #Wavelength range over which the spectral curves are integrated
	PLOT_RANGE = (450,650) #Plot a particular range of the dataset
	#THRESHOLD = 220 #Arbitary threshold, deprecated

	def __init__(self,name,dir, *args):
		"""Open the data file, and assign instance vars"""
		self.name = name
		
		#Block below tries to identify the concentration of sample from file name as it is not encoded in the hdf5 file.
		match  = re.match(r"10to\d{1}.*",self.name)
		if match:
			self.conc = 10**int(self.name[4])
		else:
			self.conc = None
			print("WARNING: Concentration not found in file name: "+self.name)

		self.DIRECTORY = dir
		file = self.DIRECTORY+self.name+".hdf5"
		dataF = h5py.File(file,"r")
		spec = dataF["Spectrometer"]
		self.intense = np.array(spec["Intensities"])
		self.wave = np.array(spec["WaveLength"])
		dataF.close()		
		self.plot_index = (bisect.bisect(self.wave,self.PLOT_RANGE[0]),bisect.bisect(self.wave,self.PLOT_RANGE[1]))

		if args:#if additional arg is given then this file is not a background spectra and has been parsed the average background spectra
			self.avg_intense = args[0]

	def plot(self,x,y,xl,yl,title,ifTime):
		"""Plots the parsed data, may want to move this func outside of spectra class"""
		plt.clf()
		plt.grid()
		plt.xlabel(xl)
		plt.ylabel(yl)
		plt.title(title+" "+self.name)
		if not ifTime:#If not a time plot it will make the following slices 
			x = x[self.plot_index[0]:self.plot_index[1]]
			y = y[self.plot_index[0]:self.plot_index[1]]	
		plt.plot(x,y)		
		plt.savefig(self.DIRECTORY+title+self.name+".png",format="png")#may want to move this function call separately.
	
	def savePlot(self,fileName):
		"""Alternative method of saving plot to specified file name """
		plt.savefig(self.DIRECTORY+fileName+self.name+".png")
	def subtract(self):
		""" Subtracts the average intensity of the background spectra from this spectra"""
		self.sub_intense = np.zeros(self.intense.shape) 
		for i in range(self.intense.shape[1]):
			self.sub_intense.T[i] = self.intense.T[i] - self.avg_intense
			
	def integration(self):
		"""Using simpsons numerical methods, computes the area under the curve over the specified domain, used to quantify the amount of fluorescence in a given time"""
		left_indice = bisect.bisect(self.wave,self.INTEGRATE_RANGE[0])
		right_indice = bisect.bisect(self.wave,self.INTEGRATE_RANGE[1])
		self.areas = np.zeros((self.intense.shape[1],1))
		
		for i in range(self.intense.shape[1]):
			self.areas[i] = simps(self.sub_intense.T[i][left_indice:right_indice],x=self.wave[left_indice:right_indice])
		self.time_axis = np.arange(0,self.intense.shape[1])*self.INT_TIME
		tempThreshold = 3*np.std(self.areas)
		print(tempThreshold)
		peakIntense = []
		for i in self.areas:
			if i>tempThreshold:
				peakIntense.append(i)
		return peakIntense

class backgroundSpectra(Spectra):
	"""Extension of spectra class, extending an averaging function that is only needed for background spectra"""
	
	def __init__(self,name,dir):
		Spectra.__init__(self,name,dir)
		self.avg_intense = self.average() 

	def average(self):
		"""Averages all the spectra over time"""
		avg_intense = np.zeros(self.intense.shape[0])
		for integration in self.intense.T:
			avg_intense+=integration
		avg_intense/=self.intense.shape[1]
		return avg_intense

if __name__ == "__main__":

	def timeStampS(a):
		"""Time stamping function takes in a string and prefixes it with time in HMS format then returns altered string"""
		return strftime("%H:%M:%S - ",gmtime())+a

	specList = []
	peakData = []
	"""index legend for peakString array 
	0 name
	1 no. peaks
	2 sum of peaks
	3 spec conc
	"""
	print(timeStampS("Processing background data"))
	back = backgroundSpectra(BACKGROUND_FILENAME,DIRECTORY)
	if shouldPlot:
		back.plot(back.wave,back.avg_intense,"Wavelength (nm)","Intensity (au)","Background spectra ",False)
	else:
		print("Skipping background plot")

	for file in dataFiles:#Create list of spectra objects
		specList.append(Spectra(file,DIRECTORY,back.avg_intense))

	print(timeStampS("Loaded data files"+"\n--------------\n\n"))
	
	for spec in specList:#Plotting and computation calls here
		print(timeStampS("Beginning with "+spec.name))

		
		spec.subtract()
		print(timeStampS("Subtracting background"))


		peak = spec.integration()
		print(timeStampS("Integrated spectra and counted peaks"))

		print("Peak Count for "+spec.name+": "+str(len(peak)))
		peakData.append([spec.name,len(peak),sum(peak), spec.conc])#Create an array containing name, number of peaks, sum of peaks, and the concentration and then adds this list to another list.		
	
		if shouldPlot:#Plotting takes a lot of time
			print(timeStampS("Plotting raw Spectra"))
			spec.plot(spec.wave,spec.intense,"Wavelength (nm)","Intesnity (arb.u)","Emission Spectra ",False)
				
			print(timeStampS("Plotting corrected spectra"))
			spec.plot(spec.wave,spec.sub_intense,"Wavelength (nm)","Intensity (arb.u)","Corrected Spectra ",False)	
			
			print(timeStampS("Plotting fluorescence over time"))
			spec.plot(spec.time_axis,spec.areas,"time (s)","Fluorescence Intensity Arbitary Units","Fluorescence over time ",True)
		else:
			print("Skipping plots")

		print(timeStampS("Finished processing "+spec.name+"\n-----------------------------\n\n"))
			


	"""Bead Intensity analysis and enumeration """

	x = []#Contains concentration
	y = []#Contains intesntiy values measured, x and y must be of the same length, parallel arrays

	for specDat in peakData:
       		if specDat[3] in x:#If we already have a measurement for this concentration avg the values
			index = x.index(specDat[3])
			y[index]+=specDat[2]
			y[index]/=2
        	else:#Otherwise we add it to our data array	
			x.append(specDat[3])
			y.append(specDat[2])

	x = np.array(x)
	x= x*CONC_VAL

	cc = np.polyfit(np.log10(x),np.log10(y),1)#Fit the data points

	linspace = np.linspace(2,6,20)#line space for fitted line
	plt.plot(np.log10(x),np.log10(y),marker=".",linestyle="None")#Plot data
	plt.plot(linspace,cc[0]*linspace+cc[1])#Plot fitted line

	plt.xlabel("Cocentration "+str(CONC_VAL)+"x 10^x beads/ml")
	plt.ylabel("Total intensity measured 10^y arb units")
	plt.show()
	plt.savefig("singleIntense.png",format="png")
	sI = 10**cc[0][0]
	
	print("Fitted intensity value for 1 bead: ",sI)

	print("\nBeads observed:\nConc : BeadCount : ExpectedBeadCount")
	f= open(DIRECTORY+"data_output.txt","w+")
	f.write("Outputted Data for "+DIRECTORY+"\n")
	f.write("Single Bead Intensity, Fitted value: "+str(sI)+"\n")
	f.write("Bead Table\nConcentration : Bead Count : Expected Bead Count\n")
	for i in range(0,len(x)):
		stringToAppend = str(int(x[i]))+"  "+str(int(y[i][0]/sI))+"  "+str(int(int(x[i])*FLOW_RATE*REC_LENGTH)) + "\n"
		print(stringToAppend)
		f.write(stringToAppend)
	f.close()

