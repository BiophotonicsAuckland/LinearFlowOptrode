"""Written by Liam Murphy, Nov 30 2017

This program is for processing many fluorescent recordings/samples with a single background file.
It assumes that the background file and the sample file have the same recording length, the same wavelength range, and the same integration time.
As a result their intensitiy matrices are of the same shape and allow for background subtraction. If they do not meet this requirement the program will crash.

Currently the user has to manually enter file names in the files array below, and specify the background file name in back_name.
(this could be changed for an automatic file searching system)

Integration is done over 495 to 560nm. This can be modified in the code.
The temporal plots assume an integration time with the int_time var (in seconds) below and must be overwritten with the correct value for correct plotting.
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
import bisect

INT_TIME = 0.15 #Integration time in seconds, over write this if using a different value, otherwise plot will be inaccurate.
INTEGRATE_RANGE= (495,560)#Range of wavelength to be integrated over e.g.495-560 nm
PLOT_RANGE = (450,650)#Range of wavelengths to plot in the fluorescent spectra and corrected plot, used to omit any outliers.
THRESHOLD = 1000
files = ["10to4-4","10to4-5","10to4-6"] #Array contains name of each fluorescent recording file
file_dir = "./Records/2um/" #Directory the above files are contained

back_name = "back-5" #Name of the background recording file, assumed that it is in the same directory as file_dir

plt.ioff()#Plots are not displayed when they're created. (Prevents program from pausing)
print("running")

def err_dec(f):
    """This is an error decorator, errors are handled here."""
    def decorator(f_name,*args):
        try:
            return f(f_name,*args)
        except IOError as e:
            print("Error!\n Error Information: "+str(e))
    return decorator

@err_dec
def background_averaging(f_name):
    """This function calculates the average background spectra, and plots it. Returns the average intensity array"""
    
    background = h5py.File(file_dir+f_name+".hdf5","r") #Load background file

    back_spec = background["Spectrometer"] #Getting intensity and wavelength data from the back-file
    back_intense = np.array(back_spec["Intensities"])
    back_wave = np.array(back_spec["WaveLength"])

    avg_intense =np.zeros(back_intense.shape[0])#Empty 0 array, this is our average spectra array.

    plt.figure(0)
    plt.clf()
    plt.grid()
    for integration in back_intense.T:#Adding each spectra ontop of each other
        avg_intense+=integration

    avg_intense/=back_intense.shape[1]#Dividing by the total number of spectra.

    #Plotting of the backgroud average

    plt.plot(back_wave,avg_intense)#Spec group contains releavant data
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (arb.u)")
    plt.title("Average Background Spectra")
    plt.savefig(file_dir+f_name+".png",format="png")

    print("Background Calculated and averaged")
    return avg_intense

@err_dec
def analysis(file_name,avg_intense):
    """This function processes fluorescent recording files,
        it is parsed the file name of the file to be processed """
      
    run = h5py.File(file_dir+file_name+".hdf5","r")
    spec = run["Spectrometer"]
    intense = np.array(spec["Intensities"])
    wave = np.array(spec["WaveLength"])

    plot_index = (bisect.bisect(wave,PLOT_RANGE[0]),bisect.bisect(wave,PLOT_RANGE[1]))

    #Plotting Emission Spec
    plt.figure(1)
    plt.clf()
    plt.grid()
    plt.plot(wave[plot_index[0]:plot_index[1]],intense[plot_index[0]:plot_index[1]])
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (arb.u)")
    plt.title("Emission Spectra"+file_name)
    plt.savefig(file_dir+"Emission_spec_"+file_name+".png",format="png")

    print(file_name+"Spectrum Plotted...")

    ######################### Subtraction ##########################

    cor_intense = np.zeros(intense.shape) #making a carbon copy
    for i in range(intense.shape[1]):
        cor_intense.T[i] = intense.T[i]-avg_intense#subtracting the average


    print("Background Subtracted...")

    plt.figure(2)
    plt.clf()
    plt.grid()
    plt.plot(wave[plot_index[0]:plot_index[1]],cor_intense[plot_index[0]:plot_index[1]])
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (arb.u)")
    plt.title("Emission Spectra Corrected"+file_name)

    plt.savefig(file_dir+"Emission_spec_cor_"+file_name+".png",format="png")
    print(file_name+" Corrected Emission Spec plotted...")

    ########### INTEGRATION #####################

    left_indice = bisect.bisect(wave,INTEGRATE_RANGE[0])#Finding the indexes closest to the specifies integrating range wavelengths.
    right_indice =bisect.bisect(wave,INTEGRATE_RANGE[1])
    areas = np.zeros((intense.shape[1],1))

    for i in range(intense.shape[1]):
        areas[i] = simps(cor_intense.T[i][left_indice:right_indice],x=wave[left_indice:right_indice])#Using simpsons numerical approximation


    time_axis = np.arange(0,intense.shape[1])*INT_TIME

    plt.figure(3)
    plt.clf()
    plt.grid()

    plt.plot(time_axis,areas,color="g")
    plt.plot(time_axis,np.full((len(time_axis),1),THRESHOLD),color="r")
    plt.title("Fluorenscence over time"+file_name)
    plt.xlabel("Time (s)")
    plt.ylabel("Fluorescence Intensity Arbitary Units")
    plt.savefig(file_dir+"over_time_spec_"+file_name+".png",format="png")
    print("Integration complete and second plot complete")
    ######### SPIKE/PEAK COUNTING OF FLUORESCENCE OVER TIME ############
    
    peaks = 0
    for i in areas:
        if i >THRESHOLD:
            peaks+=1
    print("Peak counting complete\nPeaks Counted: "+str(peaks))
   

back_avg = background_averaging(back_name)

for file_name in files:#Calls analysis for each file to process
    analysis(file_name,back_avg)
