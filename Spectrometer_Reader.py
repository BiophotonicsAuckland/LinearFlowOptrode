# -*- coding: utf-8 -*-
"""
This code demonstrates the reading of spectrometers, and saving the data in HDF5 format.
@author: Yaqub Jonmohamadi
"""

import SeaBreeze_Objective as SBO
import matplotlib.pyplot as plt
import numpy as np
import time
import h5py
import datetime

Spec = SBO.DetectSpectrometer()

Spec.setTriggerMode(0)                                      
Spec.setIntegrationTime(200000)                             # Integration time is 10ms

No_iterations = 20

WaveLength = Spec.readWavelength()                                          #Number of iterations for reading the intensities.
Intensities = np.zeros(shape=(len(WaveLength), No_iterations ), dtype = float )  #This is a matrix which will contain the intensities after the loop is finished.
Time_Index = np.zeros(shape=(1, No_iterations ), dtype = float )

def PlotOfIntensities(Wavelengthes, Intensities):               # This function plots the intensities and it incurs delay on reading the intensities. Do not use if you want to read the intensities as fast as possible.
    plt.clf()
    plt.plot(WaveLength[1:], Intensities)
    plt.xlabel('WaveLength')
    plt.ylabel('Intensity')
    plt.pause(0.1)


def SaveData(WaveLength, Intensities):                          # This function save the recorded date in the HDF5 format. You don't need to call it when using for testing.
    File_name = "Chose_a_Name_Spectrometer" + str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))+ ".hdf5"
    file = h5py.File(File_name, "w")
    Spec_subgroup1 = file.create_group("Spectrometer")
    Spec_intensities = file.create_dataset('Spectrometer/Intensities', data = Intensities)
    Spec_time = file.create_dataset('Spectrometer/Time_Index', data = Time_Index)
    Spec_wavelength = file.create_dataset('Spectrometer/WaveLength', data = WaveLength)
    Spec_subgroup1.attrs['Spectrometer Details'] = np.string_(Spec.readDetails())
    file.close()


if __name__ == "__main__":

    for I in range(No_iterations):
        try:

            Time_Label = time.time()
            Intensities[:,I], Time_Index[0,I] =  Spec.readIntensity(True, True)
            print ('read at %f' %Time_Index[0,I] )
            
            PlotOfIntensities( WaveLength[1:], Intensities[1:,I])      # This calls the function for plotting the intensities and it incures delay on reading the intensities. Comment out this line (by #) if you want to read the intensities according to the integration time.
            print ("Last Intensitie are read %f seconds ago" % (time.time() - Time_Label))
        except KeyboardInterrupt:
	        break

    SaveData(WaveLength, Intensities)       # This calls the function to save the recorded data in the HDF5 format. You can comment it out (by #) when using this code for testing.

    Spec.close()
