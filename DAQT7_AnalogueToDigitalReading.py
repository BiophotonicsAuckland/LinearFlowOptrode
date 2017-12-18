"""
Demonstrates reading 1 analog input (AINs) in a loop from a LabJack.
This code demonstrates the analogue to digital conversion for DAQT7, and saving the data in HDF5 format.
@author: Yaqub Jonmohamadi
"""
#%%
import DAQT7_Objective as DAQ
import matplotlib.pyplot as plt
import numpy as np
import time
import h5py
import datetime

#%%
DAQ1 = DAQ.DetectDAQT7()

No_D2AC_Sample = 50000                   # This is the lenght of the signal (voltage) will be recorded
No_D2AC_WindowPlot = 150                        # This is the lenght of the signal (voltage) will be plotted

Read_Voltages = np.zeros(No_D2AC_Sample, dtype = float )
Read_TimeIndex = np.zeros( No_D2AC_Sample, dtype = float )
Read_Voltages_WindowPlot = np.zeros(No_D2AC_WindowPlot, dtype = float )

#%%
def PlotSignal(TimeIndex, Voltages):               # This function plots the recorded voltage and it incurs delay on reading the port. Do not use if you want to read the port voltage as fast as possible.
    plt.clf()
    plt.plot(TimeIndex, Voltages)
    plt.xlabel('TimeIndex (ms)')
    plt.ylabel('Voltages')
    plt.xlim([TimeIndex[-1], TimeIndex[0]])
    plt.ylim([0, 10.5])
    plt.pause(0.1)


def SaveData(TimeIndex, Voltages):                          # This function save the recorded date in the HDF5 format. You don't need to call it when using for testing.
    File_name = "Chose_a_Name_DAQT7" + str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))+ ".hdf5"
    file = h5py.File(File_name, "w")
    Spec_subgroup1 = file.create_group("DAQT7")
    Spec_intensities = file.create_dataset('DAQT7/Voltages', data = Voltages)
    Spec_wavelength = file.create_dataset('DAQT7/TimeIndex', data = TimeIndex)
    #dset.attrs["attr"] = b"Hello"
    Spec_subgroup1.attrs['DAQT7 Details'] = np.string_(DAQ1.getDetails())
    file.close()

if __name__ == "__main__":
    DAQ1.writePort('DAC0', 5)

    for I in range(No_D2AC_Sample):
        try:
            Time_Label = time.time()
            Read_Voltages[I], Read_TimeIndex[I] = np.asarray(DAQ1.readPort('AIN1'))


            
            ########## # This 'if' and 'else' are used when you want to plot the read signal on the port. If you want to record the signal as fast as possible then you need to commend this 'if' and 'else'.
            if I < No_D2AC_WindowPlot:
                Read_Voltages_WindowPlot[I: :-1] = Read_Voltages[I: :-1]
                PlotSignal(Read_TimeIndex[I : :-1] - Read_TimeIndex[0], Read_Voltages_WindowPlot[I: :-1])      # This calls the function for plotting the intensities and it incures delay on reading the intensities. Comment out this line (by #) if you want to read the intensities according to the integration time.
            else:
                Read_Voltages_WindowPlot = Read_Voltages[ I : I - No_D2AC_WindowPlot : -1]
                PlotSignal(Read_TimeIndex[I : I - No_D2AC_WindowPlot : -1] - Read_TimeIndex[0], Read_Voltages_WindowPlot)      # This calls the function for plotting the intensities and it incures delay on reading the intensities. Comment out this line (by #) if you want to read the intensities according to the integration time.
            

            print ("Last voltage was read %f seconds ago" % (time.time() - Time_Label))
            I = I + 1
        except KeyboardInterrupt:
            break


    SaveData(Read_TimeIndex, Read_Voltages)       # This calls the function to save the recorded data in the HDF5 format. You can comment it out (by #) when using this code for testing.

    DAQ1.close()
