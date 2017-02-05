"""
This code runs the power meter, DAQT7 analogue to digital convertor (using normal mode), and specrometer simultaneously using multiprocessing library. 
@author: Yaqub Jonmohamadi
"""

import h5py
import DAQT7_Objective as DAQ
import SeaBreeze_Objective as SBO
import ThorlabsPM100_Objective as P100
import time
import datetime
import numpy as np
from multiprocessing import Process, Value, Array
import matplotlib.pyplot as plt

time_start =  time.time()




def Spec_Read_Process(No_Spec_Sample):
    # ########## A function for reading the spectrometer intensities ###########
    while Spec_Index[0] < (No_Spec_Sample -1):
        #Time_Label = time.time()
        Current_Spec_Record[:], Spec_Time[Spec_Index[0]]  = Spec1.readIntensity(True, True)
        Spec_Is_Read.value = 1
        Spec_Index[0] = Spec_Index[0] + 1
        print "spectrometer Index is %i" % Spec_Index[0]
    Spec_Is_Done.value = 1


def DAQ_Read_Process(No_DAC_Sample,):
    # ######## A function for reading the DAQ analogue inpute on AINX ########
    while DAQ_Index[0] < No_DAC_Sample:
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort('AIN1')
        DAQ_Index[0] = DAQ_Index[0] + 1
    DAQ_Is_Read.value = 1

def Power_Read_Process(No_Power_Sample):
    # ######## A function for reading the Power meter ########
    while Power_Index[0] < No_Power_Sample:
        Power_Signal[Power_Index[0]], Power_Time[Power_Index[0]] = Power_meter.readPower()
        Power_Index[0] = Power_Index[0] + 1
    Power_Is_Read.value = 1


if __name__ == "__main__":

    PhotoDiod_Port = "AIN1"
    Spec1 = SBO.DetectSpectrometer()
    Integration_Time = 10                                        # Integration time in ms
    Spec1.setTriggerMode(0)                                      # It is set for free running mode
    Spec1.setIntegrationTime(Integration_Time*1000)              # Integration time is in microseconds when using the library
    DAQ1 = DAQ.DetectDAQT7()
    Power_meter = P100.DetectPM100D()
    Spec_Is_Read = Value('i', 0)
    Spec_Is_Read.value = 0
    Spec_Is_Done = Value('i', 0)
    Spec_Is_Done.value = 0
    DAQ_Is_Read = Value('i', 0)
    DAQ_Is_Read.value = 0
    Power_Is_Read = Value('i', 0)
    Power_Is_Read.value = 0
    Timer_Is_Over = Value('i', 0)
    Timer_Is_Over.value = 0

    DurationOfReading = 1.12      # Duration of reading in seconds.
    No_DAC_Sample =   int(round(DurationOfReading*1000/0.5))                # Number of samples for DAQ analogue to digital converter (AINx). Roughly DAQ can read AINx every 0.4 ms
    No_Power_Sample = int(round(DurationOfReading*1000/5.1))                # Number of samples for P100D Power meter to read. Roughly P100 can read the power every 2.7 ms.
    No_Spec_Sample =  int(round(DurationOfReading*1000/(Integration_Time))) # Number of samples for spectrometer to read.

    Current_Spec_Record = Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths()) ,1), dtype = float ))
    #Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    Full_Spec_Records = np.zeros(shape=(len(Spec1.Handle.wavelengths()), No_Spec_Sample ), dtype = float )
    Spec_Time   = Array('d', np.zeros(shape=( No_Spec_Sample ,1), dtype = float ))
    #Spec_Index = 0
    Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))

    DAQ_Signal = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
    DAQ_Time   = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
    DAQ_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))


    Power_Signal = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
    Power_Time   = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
    Power_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))

    # ########### The file containing the records (HDF5 format)###########'''


    Pros_DAQ = Process(target=DAQ_Read_Process, args=(No_DAC_Sample,))
    Pros_DAQ.start()
    Pros_Power = Process(target=Power_Read_Process, args=(No_Power_Sample,))
    Pros_Power.start()
    Pros_Spec = Process(target=Spec_Read_Process, args=(No_Spec_Sample,))
    Pros_Spec.start()


    while((Spec_Is_Done.value == 0)):
        if  Spec_Is_Read.value == 1:
            Spec_Is_Read.value = 0
            Full_Spec_Records[:, np.int(Spec_Index[0])-1] = Current_Spec_Record[:]
    print('Spectrometer is done')
    while True:
        if ((DAQ_Is_Read.value == 1) & (Power_Is_Read.value == 1)):
            break

    time.sleep(0.1)
    DAQ1.close()
    Spec1.close()

    # ######### Plotting the spectrumeter and the photodiod recordings ########
    plt.figure()

    plt.subplot(1,3,1)
    DAQ_Signal = np.asarray(DAQ_Signal[0:DAQ_Index[0]])
    plt.plot(DAQ_Time[0:DAQ_Index[0]], DAQ_Signal[0:DAQ_Index[0]], label = "Photo Diode")
    plt.title('Photo diode')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (v)')

    plt.subplot(1,3,2)
    Power_Signal = np.asarray(Power_Signal[0:Power_Index[0]])
    plt.plot(Power_Time[0:Power_Index[0]], Power_Signal[0:Power_Index[0]], label = "Power meter")
    plt.title('Power meter')
    plt.xlabel('Time (s)')
    plt.ylabel('Pwor (w)')

    plt.subplot(1,3,3)
    plt.plot(Spec1.readWavelength()[1:],Full_Spec_Records[1:]);
    plt.title('Specrometer recordings')
    plt.xlabel('Wavelength (nano meter)')
    plt.ylabel('Intensity')
    plt.show()

    ################################Closing the devices#############################

    plt.figure()
    plt.plot(DAQ_Time, (DAQ_Signal[0:DAQ_Index[0]]-np.mean(DAQ_Signal))/float( np.max(np.abs(DAQ_Signal))))
    plt.plot(Power_Time, (Power_Signal[0:Power_Index[0]]-np.mean(Power_Signal))/float( np.max(np.abs(Power_Signal))))
    plt.title("Super imposed Power and DAQ signals (not the actual signals)")
    plt.xlabel("Unix time")
    plt.legend(['DAQ', 'P100'])
    plt.show()


    #################### Estimate the latencies of the devices ###################################
    plt.figure()

    DAQ_Latency = DAQ_Time[0:DAQ_Index[0]]
    DAQ_Latency[0] = 0
    for I in range(1,DAQ_Index[0]):
        DAQ_Latency[I] = DAQ_Time[I] - DAQ_Time[I-1]
    plt.subplot(1,3,1)
    plt.plot(DAQ_Latency)
    plt.ylabel("Time (s)")
    plt.title("DAQ latencies")

    Power_Latency = Power_Time[0:Power_Index[0]]
    Power_Latency[0] = 0
    for I in range(1,Power_Index[0]):
        Power_Latency[I] = Power_Time[I] - Power_Time[I-1]
    plt.subplot(1,3,2)
    plt.plot(Power_Latency)
    plt.title("P100 latencies")
    plt.ylabel("Time (s)")

    plt.subplot(1,3,3)
    Spec_Latency = Spec_Time[0:np.int(Spec_Index[0])]
    Spec_Latency[0] = 0
    for I in range(1,Spec_Index[0]):
        Spec_Latency[I] = np.float(Spec_Time[I] - Spec_Time[I-1])
    plt.plot(Spec_Latency)
    plt.ylabel("Time (s)")
    plt.title("Spectrometer integration durations")
    plt.show()
