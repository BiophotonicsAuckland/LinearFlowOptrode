
"""
This code demonstrates the reading of Power meter PM100, and saving the data in HDF5 format.
@author: Yaqub Jonmohamadi
"""
import numpy as np
import time
import h5py
import datetime
import matplotlib.pyplot as plt
import ThorlabsPM100_Objective


Power_meter = ThorlabsPM100_Objective.DetectPM100D()

No_Power_Sample = 1000                   # This is the lenght of the signal (Power) will be recorded
No_Power_WindowPlot = 150                        # This is the lenght of the signal (Power) will be plotted

Read_power = np.zeros(No_Power_Sample)
Read_time  = np.zeros(No_Power_Sample)

Read_Power = np.zeros(No_Power_Sample, dtype = float )
Read_TimeIndex = np.zeros( No_Power_Sample, dtype = float )
Read_Power_WindowPlot = np.zeros(No_Power_WindowPlot, dtype = float )


def PlotSignal(TimeIndex, Power):               # This function plots the recorded Power and it incurs delay on reading the sensor power. Do not use if you want to read the sensor power as fast as possible.
    plt.clf()
    plt.plot(TimeIndex, Power)
    plt.xlabel('TimeIndex (ms)')
    plt.ylabel('Power')
    plt.pause(0.1)


def SaveData(TimeIndex, Power):                          # This function save the recorded date in the HDF5 format. You don't need to call it when using for testing.
    File_name = "Chose_a_Name_ThorlabsPM100" + str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))+ ".hdf5"
    file = h5py.File(File_name, "w")
    P100_subgroup1 = file.create_group("ThorlabsPM100")
    P100_Powers = file.create_dataset('ThorlabsPM100/Power', data = Power)
    P100_TimeIndex = file.create_dataset('ThorlabsPM100/TimeIndex', data = TimeIndex)
    file.close()

if __name__ == "__main__":

	for I in range(No_Power_Sample):
	    try:
	        Time_Label = time.time()
	        Read_Power[I], Read_TimeIndex[I] = Power_meter.readPower()

		# This 'if' and 'else' are used when you want to plot the read signal on the sensor power. If you want to record the signal as fast as possible then you need to commend this 'if' and 'else'.
		'''
	        if I < No_Power_WindowPlot:
	            Read_Power_WindowPlot[I: :-1] = Read_Power[I: :-1]
	            PlotSignal(Read_TimeIndex[I : :-1] - Read_TimeIndex[0], Read_Power_WindowPlot[I: :-1])      # This calls the function for plotting the intensities and it incures delay on reading the intensities. Comment out this line (by #) if you want to read the intensities according to the integration time.
	        else:
	            Read_Power_WindowPlot = Read_Power[ I : I - No_Power_WindowPlot : -1]
	            PlotSignal(Read_TimeIndex[I : I - No_Power_WindowPlot : -1] - Read_TimeIndex[0], Read_Power_WindowPlot)      # This calls the function for plotting the intensities and it incures delay on reading the intensities. Comment out this line (by #) if you want to read the intensities according to the integration time.
		'''
	        print ("Last power was read %f seconds ago" % (time.time() - Time_Label))
	        I = I + 1
	    except KeyboardInterrupt:
	        break


	SaveData(Read_TimeIndex, Read_Power)       # This calls the function to save the recorded data in the HDF5 format. You can comment it out (by #) when using this code for testing.
