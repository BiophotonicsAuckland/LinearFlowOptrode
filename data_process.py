"""Written by Liam Murphy, Nov 30 2017"""

import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps

plt.ioff()
print("running")

files = ["bac-10to7-2","bac-10to7-3","bac-10to6-1","bac-10to6-2","bac-10to6-3","bac-10to5-1","bac-10to5-2","bac-10to5-3","bac-10to4-1","bac-10to4-2","bac-10to4-3","bac-10to3-1","bac-10to3-2","bac-10to3-3"]
file_dir = "C:\\Users\\Fuck Windows\\Desktop\\Research\\bead_data\\bac_data\\"


############################## BACKGROUND AVERAGING ##########################
background = h5py.File(file_dir+"background.hdf5","r")
back_spec = background["Spectrometer"]
back_intense = np.array(back_spec["Intensities"])
back_wave = np.array(back_spec["WaveLength"])

avg_intense =np.zeros(back_intense.shape[0])

plt.figure(0)
plt.clf()
for integration in back_intense.T:
	avg_intense+=integration
		
avg_intense/=back_intense.shape[1]
#Average Plotting

plt.plot(back_wave,avg_intense)#Spec group contains releavant data
plt.xlabel("Wavelength (nm)")
plt.ylabel("Intensity (arb.u)")
plt.title("Average Background Spectra")
plt.savefig(file_dir+"avg_back.png",format="png")

print("Background Calculated and averaged")

##Analysis Code
def analysis(file_name):
    run = h5py.File(file_dir+file_name+".hdf5","r")
    spec = run["Spectrometer"]
    intense = np.array(spec["Intensities"])
    wave = np.array(spec["WaveLength"])
    
    #Plotting Emission Spec
    plt.figure(1)
    plt.clf()
    plt.plot(wave,intense)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (arb.u)")
    plt.title("Emission Spectra"+file_name)
    plt.savefig(file_dir+"Emission_spec_"+file_name+".png",format="png")

    print(file_name+"Spectrum Plotted...")
    
    ######################### Subtraction ##########################

    cor_intense = np.zeros(intense.shape) #making a carbon copy
    for i in range(intense.shape[1]):
        cor_intense.T[i] = intense.T[i]-avg_intense
        
        
    print("Background Subtracted...")
    
    plt.figure(2)
    plt.clf()
    plt.plot(wave,cor_intense)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (arb.u)")
    plt.title("Emission Spectra Corrected"+file_name)
    
    plt.savefig(file_dir+"Emission_spec_cor_"+file_name+".png",format="png")
    print(file_name+" Corrected Emission Spec plotted...")
    
    ########### INTEGRATION #####################
    #399 and 850
    areas = np.zeros((intense.shape[1],1))
    for i in range(intense.shape[1]):
        areas[i] = simps(cor_intense.T[i][221:677],x=wave[221:677])
        
    print(areas.shape)
    time_axis = np.arange(0,intense.shape[1])*0.015
    plt.figure(3)
    plt.clf()
    plt.plot(time_axis,areas)
    plt.title("Fluorenscence over time"+file_name)
    plt.xlabel("Time (s)")
    plt.ylabel("Fluorescence Intensity Arbitary Units")
    plt.savefig(file_dir+"over_time_spec_"+file_name+".png",format="png")
    print("Integration complete and second plot complete")
    
    
for file_name in files:
    analysis(file_name)
    


#finding index values for 500-600 wavelengths...
"""
pot_500 = []
pot_600 = []
for i in range(0,len(wave)):
    if np.abs(wave[i]-500) < 0.5:
        pot_500.append((wave[i],i))
    if np.abs(wave[i]-600) < 0.5:
        pot_500.append((wave[i],i))
print(pot_500,pot_600)
"""
#Will use index 221 and 676 for integration[221:677]
#use index 177 and 1084 for data selection in optrode_v4.py[177:1084]