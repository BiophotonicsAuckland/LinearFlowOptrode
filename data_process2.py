""""Written by Liam Murphy, July 5th 2018

This program is for processing many fluorescent recordings/samples with$
It assumes that the background file and the sample file have the same recording length and integration time$

Integration of spectra curves is done over 495 to 560nm. This can be modified in the code.
The temporal plots assume an integration time with the int_time var (in seconds) below and must be overwritten with the correct value for correct plotting.

This code is a refactoring of the previous data_process.py file written in 2017.
"""

import h5py, bisect,cPickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
from time import gmtime, strftime

DIRECTORY = "./Records/test-3/"

dataFiles = ["10to4-1","10to4-2","10to4-3"]

class Spectra():
	"""This class represents a given spectra recording and contains functionality for computing and plotting particular data"""
	#Constants
	INT_TIME  = 0.015
	INTEGRATE_RANGE = (495,550)
	PLOT_RANGE = (450,650)
	THRESHOLD = 220

	def __init__(self,name,dir, *args):
		"""Open the data file, and assign instance vars"""
		self.name = name
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
		"""Plots the parsed data"""
		plt.clf()
		plt.grid()
		plt.xlabel(xl)
		plt.ylabel(yl)
		plt.title(title+" "+self.name)
		if not ifTime:#If not a time plot it will make the following slices 
			x = x[self.plot_index[0]:self.plot_index[1]]
			y = y[self.plot_index[0]:self.plot_index[1]]	
		plt.plot(x,y)		
		plt.savefig(self.DIRECTORY+title+self.name+".png",format="png")
	
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
				
		peaks = 0
		for i in self.areas:
			if i>self.THRESHOLD:
				peaks+=1
		return peaks
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
	print(strftime("%H:%M:%S",gmtime())+" - Processing background data")
	back = backgroundSpectra("background-2",DIRECTORY)

	specList = []
	peakString = ""

	for file in dataFiles:#Create list of spectra objects
		specList.append(Spectra(file,DIRECTORY,back.avg_intense))

	print(strftime("%H:%M:%S",gmtime())+" - Loaded data files")

	for spec in specList:#Plotting and computation calls here
		print(strftime("%H:%M:%S",gmtime())+" - Beginning with "+spec.name)

		spec.plot(spec.wave,spec.intense,"Wavelength (nm)","Intesnity (arb.u)","Emission Spectra "+spec.name,False)
		print(strftime("%H:%M:%S",gmtime())+" - Plotting raw spectra")

		spec.subtract()
		print(strftime("%H:%M:%S",gmtime())+" - Subtracting background")

		spec.plot(spec.wave,spec.sub_intense,"Wavelength (nm)","Intensity (arb.u)","Corrected Spectra "+spec.name,False)	
		print(strftime("%H:%M:%S",gmtime())+" - Plotting corrected spectra")

		peak = spec.integration()
		print(strftime("%H:%M:%S",gmtime())+" - Integrated spectra and counted peaks")

		print("Peaks for "+spec.name+": "+str(peak))
		peakString+=spec.name+": "+str(peak)+"\n"
		spec.plot(spec.time_axis,spec.areas,"time (s)","Fluorescence Intensity Arbitary Units","Fluorescnece over time "+spec.name,True)
		print(strftime("%H:%M:%S",gmtime())+" - Finished with "+spec.name)

	with open("peakData.txt","w") as f:# Write the no. peaks to a text file.
		f.write(peakString)
	
