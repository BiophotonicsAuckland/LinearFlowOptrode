import Tkinter as tk
import tkFileDialog as filedialog

import h5py, bisect,cPickle,re
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
from time import gmtime, strftime

class App:
    """This object contains all graphical elements and handling"""
    
    WIN_TITLE = "Data Process V3"
    WIN_WIDTH =500
    WIN_HEIGHT =500
    
    def __init__(self,root):
        """Initialisation of root frame"""

        root.title(self.WIN_TITLE)
        root.minsize(self.WIN_WIDTH,self.WIN_HEIGHT)
        
        self.bg_sv = tk.StringVar()
        dir_entry = tk.Entry(root,state="readonly",textvariable=self.bg_sv,width=50)
        dir_browse = tk.Button(text="Browse",command=lambda: self.getFile(self.bg_sv))

        self.dat_entry = tk.Listbox(root,state="normal",width=50,height=5)
        dat_browse= tk.Button(root,text="Browse",command=lambda: self.getFiles(self.dat_entry))
        
        tk.Label(root, text="Background").grid(row=0,column=0,sticky=tk.W)
        dir_browse.grid(row=0,column=2,sticky=tk.E)
        dir_entry.grid(row=0,column=1)
        
        tk.Label(root,text="Data Files").grid(row=1,column=0,sticky=tk.W)
        dat_browse.grid(row=1,column=2,sticky=tk.E)
        self.dat_entry.grid(row=1,column=1)

        self.toPlot = tk.IntVar()
        plotCheck = tk.Checkbutton(root,text="Do you wish to plot? (This takes longer)",variable=self.toPlot)
        plotCheck.grid(row=2,column=1)

        tk.Label(root,text="Recording Length (s)").grid(row=3,column=0,sticky=tk.E)
        self.rl_sv = tk.StringVar(value="150")
        rec_entry = tk.Entry(root,textvariable=self.rl_sv,width=10)
        rec_entry.grid(row=3,column=1,sticky=tk.W)
        
        tk.Label(root,text="Flow Rate (mL/s)").grid(row=3,column=2,sticky=tk.E)
        self.fr_sv = tk.StringVar(value=str(0.2/60.0))
        fr_entry = tk.Entry(root,textvariable=self.fr_sv,width=10)
        fr_entry.grid(row=3,column=3,sticky=tk.W)
        
        tk.Label(root,text="Conc Val").grid(row=4,column=0,sticky=tk.E)
        self.cv_sv = tk.StringVar(value="2.274")
        cv_entry = tk.Entry(root,textvariable=self.cv_sv,width=10)
        cv_entry.grid(row=4,column=1,sticky=tk.W)

        tk.Label(root,text="Integration Time (s)").grid(row=4,column=2,sticky=tk.E)
        self.it_sv = tk.StringVar(value="0.05")
        it_entry = tk.Entry(root,textvariable=self.it_sv,width=10)
        it_entry.grid(row=4,column=3,sticky=tk.W)

        tk.Label(root,text="Integration Range ").grid(row=5,column=0,sticky=tk.E)
        self.ir_sv = tk.StringVar(value="495,550")
        ir_entry = tk.Entry(root,textvariable=self.ir_sv,width=10)
        ir_entry.grid(row=5,column=1,sticky=tk.W)
        
        tk.Label(root,text="Plot Range").grid(row=5,column=2,sticky=tk.E)
        self.pr_sv = tk.StringVar(value="450,650")
        pr_entry = tk.Entry(root,textvariable=self.pr_sv,width=10)
        pr_entry.grid(row=5,column=3,sticky=tk.W)

        self.st_button = tk.Button(root, text="start",command=self.startProcess)
        self.st_button.grid(row=6)

        self.outputText = tk.Text(root)
        self.outputText.grid(row=7,columnspan=4)

    def getFile(self,sv):
        """Takes a string var object, and opens a file select dialog, changes text entry to chosen file"""
        filename = filedialog.askopenfilename(filetypes=(("HDF5 Files","*.hdf5"),("All Files","*.*")))
        #print(filename)
        if filename:
            sv.set(filename)

    def getFiles(self,lb):
        """Same as getFile but takes a listbox and allows multiple file select"""
        filenames = filedialog.askopenfilenames(filetypes=(("HDF5 Files", "*.hdf5"),("All Files","*.*")))
        #print(type(filenames))
        if filenames:
            lb.delete(0, tk.END)
            for filename in filenames:
                #print(filename)
                lb.insert(tk.END, str(filename))


    def startProcess(self):
        """Grabs all relevant values from user input and starts processing of data"""
        self.st_button.state="disabled"#Disable start button
        bgFileName = self.bg_sv.get() #Filename/dir of background file
        directory = bgFileName[0:bgFileName.rindex("/")+1]#Grab directory from the background file location
        dataFiles = self.dat_entry.get(0,tk.END)#List of all data files
	
	intRange= map(lambda x: float(x), self.ir_sv.get().split(","))
	plotRange = map(lambda x: float(x), self.pr_sv.get().split(","))
	intTime = float(self.it_sv.get())
	flowRate = float(self.fr_sv.get())
	recLen  = float(self.rl_sv.get())
	conVal = float(self.cv_sv.get())

        a = analysis(directory,bgFileName,dataFiles,self.toPlot.get(),intTime,intRange,plotRange,self.outputText,flowRate,recLen,conVal)
        
        #Parse all these values to an instance of the script? and the output window.
        
class Spectra():
	"""This class represents a given spectra recording and contains functionality for computing and plotting particular data"""
	#Constants #old/deprecated default vals
	#INT_TIME  = 0.05#Integration time, aka exposure time of spectrometer 
	#INTEGRATE_RANGE = (495,550) #Wavelength range over which the spectral curves are integrated
	#PLOT_RANGE = (450,650) #Plot a particular range of the dataset
	

	def __init__(self,name,dir,intTime,intRange,pltRange,oS, *args):
		"""Open the data file, and assign instance vars"""
		self.name = name
		self.INT_TIME = intTime
		self.INTEGRATE_RANGE = intRange
		self.PLOT_RANGE= pltRange
		self.DIRECTORY = dir
		self.oS = oS #output object(GUI element), use this inplace of any print statements
		
		#Block below tries to identify the concentration of sample from file name as it is not encoded in the hdf5 file.
		match  = re.match(r"10to\d{1}.*",self.name)
		if match:
			self.conc = 10**int(self.name[4])
		else:
			self.conc = None
			print("WARNING: Concentration not found in file name: "+self.name)

		
		file = self.DIRECTORY+self.name
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
	
	def __init__(self,name,dir,intTime,intRange,pltRange,oS):
		Spectra.__init__(self,name,dir,intTime,intRange,pltRange,oS)
		self.avg_intense = self.average() 

	def average(self):
		"""Averages all the spectra over time"""
		avg_intense = np.zeros(self.intense.shape[0])
		for integration in self.intense.T:
			avg_intense+=integration
		avg_intense/=self.intense.shape[1]
		return avg_intense

class analysis():

    def __init__(self,dir,bgFile,datFiles,toPlot,intTime,intRange,pltRange,oS,flowRate,recLen,conVal):
        self.shouldPlot = toPlot
        self.FLOW_RATE = flowRate 
        self.REC_LENGTH = recLen
        self.BACKGROUND_FILENAME = bgFile[bgFile.rindex("/")+1:]
        self.dataFiles = datFiles
        self.INT_TIME = intTime
        self.INT_RANGE = intRange
        self.PLOT_RANGE = pltRange
        self.oS = oS #output stream, aka a text object from tkinter
	self.DIRECTORY=dir
	self.CONC_VAL = conVal
        self.processing()#start the processing!

    def timeStampS(self,a):
        """Time stamping function takes in a string and prefixes it with time in HMS format then returns altered string"""
	return strftime("%H:%M:%S - ",gmtime())+a
    
    def processing(self):
	specList = []
	peakData = []
	"""index legend for peakString array 
	0 name
	1 no. peaks
	2 sum of peaks
	3 spec conc
	"""
	print(("Processing background data"))
	back = backgroundSpectra(self.BACKGROUND_FILENAME,self.DIRECTORY,self.INT_TIME,self.INT_RANGE,self.PLOT_RANGE,self.oS)
	if self.shouldPlot:
		back.plot(back.wave,back.avg_intense,"Wavelength (nm)","Intensity (au)","Background spectra ",False)
	else:
		print("Skipping background plot")

	for file in self.dataFiles:#Create list of spectra objects
                name = file[file.rindex("/")+1:]
		specList.append(Spectra(name,self.DIRECTORY,self.INT_TIME,self.INT_RANGE,self.PLOT_RANGE,self.oS,back.avg_intense))

	print(self.timeStampS("Loaded data files"+"\n--------------\n\n"))
	
	for spec in specList:#Plotting and computation calls here
		print(self.timeStampS("Beginning with "+spec.name))

		
		spec.subtract()
		print(self.timeStampS("Subtracting background"))


		peak = spec.integration()
		print(self.timeStampS("Integrated spectra and counted peaks"))

		print("Peak Count for "+spec.name+": "+str(len(peak))+" Sum: "+str(sum(peak))+" Conc: "+str(spec.conc))
		peakData.append([spec.name,len(peak),sum(peak), spec.conc])#Create an array containing name, number of peaks, sum of peaks, and the concentration and then adds this list to another list.      
	
		if self.shouldPlot:#Plotting takes a lot of time
			print(self.timeStampS("Plotting raw Spectra"))
			spec.plot(spec.wave,spec.intense,"Wavelength (nm)","Intensity (arb.u)","Emission Spectra ",False)
				
			print(self.timeStampS("Plotting corrected spectra"))
			spec.plot(spec.wave,spec.sub_intense,"Wavelength (nm)","Intensity (arb.u)","Corrected Spectra ",False)  
			
			print(self.timeStampS("Plotting fluorescence over time"))
			spec.plot(spec.time_axis,spec.areas,"time (s)","Fluorescence Intensity Arbitary Units","Fluorescence over time ",True)
		else:
			print("Skipping plots")

		print(self.timeStampS("Finished processing "+spec.name+"\n-----------------------------\n\n"))
            


	"""Bead Intensity analysis and enumeration """
	
	x = []#Contains concentration
	y = []#Contains intentiy values measured, x and y must be of the same length, parallel arrays
	 xDict = {}#Used to count number of data points at each concentration, so averaging can be done.

        for specDat in peakData:
                if specDat[3] in x:#If we already have a measurement for this concentration avg the values
                        xDict[specDat[3]]+=1
                        index = x.index(specDat[3])
                        y[index]+=specDat[2]
                else:#Otherwise we add it to our data array     
                        xDict[specDat[3]] = 0#start counter for no. data points
                        x.append(specDat[3])
                        y.append(specDat[2])

        for i in range(0,len(y)):#Averaging
                y[i]/=float(xDict[x[i]])

	x = np.array(x)
	x= x*self.CONC_VAL
	print(x,y)
	cc = np.polyfit(np.log10(x),np.log10(y),1)#Fit the data points

	linspace = np.linspace(2,6,20)#line space for fitted line
	plt.plot(np.log10(x),np.log10(y),marker=".",linestyle="None")#Plot data
	plt.plot(linspace,cc[0]*linspace+cc[1])#Plot fitted line

	plt.xlabel("Cocentration "+str(self.CONC_VAL)+"x 10^x beads/ml")
	plt.ylabel("Total intensity measured 10^y arb units")
	plt.show()
	plt.savefig("singleIntense.png",format="png")
	sI = 10**cc[0][0]
	
	print("Fitted intensity value for 1 bead: ",sI)

	print("\nBeads observed:\nConc : BeadCount : ExpectedBeadCount")
	f= open(self.DIRECTORY+"data_output.txt","w+")
	f.write("Outputted Data for "+self.DIRECTORY+"\n")
	f.write("Single Bead Intensity, Fitted value: "+str(sI)+"\n")
	f.write("Bead Table\nConcentration : Bead Count : Expected Bead Count\n")
	for i in range(0,len(x)):
		stringToAppend = str(int(x[i]))+"  "+str(int(y[i][0]/sI))+"  "+str(int(int(x[i])*self.FLOW_RATE*self.REC_LENGTH)) + "\n"
		print(stringToAppend)
		f.write(stringToAppend)
	f.close()
        
if __name__ =="__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
