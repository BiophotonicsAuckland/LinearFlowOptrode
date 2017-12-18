# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 14:53:46 2016
This code calculates and plost the latencies of the connected devices such as spectrometer, DAQT7 analogue to digital convertor, and power meter.
@author: Yaqub
"""

import h5py
import DAQT7_Objective as DAQ
import SeaBreeze_Objective as SBO
import ThorlabsPM100_Objective as P100
import time
#import datetime
import numpy as np
from multiprocessing import Process, Value, Array
import matplotlib.pyplot as plt
import os.path

time_start =  time.time()


def Timer_Multi_Process(Time_In_Seconds):
    if Timer_Is_Done.value is 1:
        print 'Error: This timer can be run one at a time. Either the previous timer is still running, or Timer_Is_Done bit is reset from previous timer run'
    time.sleep(Time_In_Seconds)
    Timer_Is_Done.value = 1




def DAQ_Read_Process(No_DAC_Sample,):
    I = 0
    while DAQ_Is_Read.value == 0:
    #while I < Shutter_Index_Cycle[0]:
    
        if  Shutter_Open.value == 1:
            Shutter_Open.value = 0
            DAQ1.writePort(Shutter_Port, 5)
            
        Ref_Time[DAQ_Index_Total[0]] = time.time()
            
        DAQ_Index[0] = 0
        DAQ1.writePort(Shutter_Port, 0)
        Ref_Time[DAQ_Index_Total[0]] = time.time()
        State = -1        
        while DAQ_Index[0] < No_DAC_Sample:
            DAQ_Signal[DAQ_Index_Total[0]], DAQ_Time[DAQ_Index_Total[0]] = DAQ1.readPort(PhotoDiod_Port)
            #Ref_Signal[DAQ_Index_Total[0]] = 0
            DAQ_Index[0] = DAQ_Index[0] + 1
            DAQ_Index_Total[0] = DAQ_Index_Total[0] + 1
            Ref_Time[DAQ_Index_Total[0]] = time.time()
        I = I + 1 
        print (I)
        print (time.time())

        DAQ_Index[0] = 0
        DAQ1.writePort(Shutter_Port, 5)
        Ref_Time[DAQ_Index_Total[0]] = time.time()
        State = 1
        while DAQ_Index[0] < No_DAC_Sample - 1:
            DAQ_Signal[DAQ_Index_Total[0]], DAQ_Time[DAQ_Index_Total[0]] = DAQ1.readPort(PhotoDiod_Port)
            Ref_Signal[DAQ_Index_Total[0]] = 1
            DAQ_Index[0] = DAQ_Index[0] + 1
            DAQ_Index_Total[0] = DAQ_Index_Total[0] + 1
            Ref_Time[DAQ_Index_Total[0]] = time.time()
        I = I + 1    
        print (I)
        print (time.time())
    DAQ1.writePort(Shutter_Port, 0)
    
    
    

def Spec_Read_Process(No_Spec_Sample):
    # ########## A function for reading the spectrometer intensities ###########
    while Spec_Index[0] < (No_Spec_Sample -1):
        #Time_Label = time.time()
        Current_Spec_Record[:], Spec_Time[Spec_Index[0]]  = Spec1.readIntensity(True, True)
        Spec_Is_Read.value = 1
        Spec_Index[0] = Spec_Index[0] + 1
        print "spectrometer Index is %i" % Spec_Index[0]
    Spec_Is_Done.value = 1


def Power_Read_Process(No_Power_Sample):
    # ######## A function for reading the Power meter ########
    while Power_Index[0] < No_Power_Sample:
        Power_Signal[DAQ_Index_Total[0]], Power_Time[DAQ_Index_Total[0]] = Power_meter.readPower()
        Power_Index[0] = Power_Index[0] + 1
    Power_Is_Read.value = 1


if __name__ == "__main__":

    Shutter_Port = "DAC0"
    
    PhotoDiod_Port = "AIN1"
    #Spec1 = SBO.open()
    Integration_Time = 2                                        # Integration time in ms
    #Spec1.setTriggerMode(0)                                      # It is set for free running mode
    #Spec1.setIntegrationTime(Integration_Time*1000)              # Integration time is in microseconds when using the library
    DAQ1 = DAQ.DetectDAQT7()
    DAQ1.writePort(Shutter_Port, 0)
    time.sleep(0.4)
    #Power_meter = P100.open()
    Spec_Is_Read = Value('i', 0)
    Spec_Is_Read.value = 0
    Timer_Is_Done = Value('i', 0)
    Timer_Is_Done.value = 0
    Spec_Is_Done = Value('i', 0)
    Spec_Is_Done.value = 0
    DAQ_Is_Read = Value('i', 0)
    DAQ_Is_Read.value = 0
    Power_Is_Read = Value('i', 0)
    Power_Is_Read.value = 0
    Timer_Is_Over = Value('i', 0)
    Timer_Is_Over.value = 0

    No_Shutter_Cycles = 20
    DurationOfReading = 0.010      # Duration of reading in seconds.
    No_DAC_Sample =   int(round(DurationOfReading*1000/0.4))                # Number of samples for DAQ analogue to digital converter (AINx). Roughly DAQ can read AIN1 2 and 3 evry 1.5 ms and 2.4 ms for AIN0,
    No_Power_Sample = int(round(DurationOfReading*1000/5.1))                # Number of samples for P100D Power meter to read. Roughly P100 can read the power every 2.7 ms.
    No_Spec_Sample =  int(round(DurationOfReading*1000/(Integration_Time))) # Number of samples for spectrometer to read. It takes integration time can read the power every 2.7 ms.


    '''
    Current_Spec_Record = Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths()) ,1), dtype = float ))
    #Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    Full_Spec_Records = np.zeros(shape=(len(Spec1.Handle.wavelengths()), No_Spec_Sample ), dtype = float )
    Spec_Time   = Array('d', np.zeros(shape=( No_Spec_Sample ,1), dtype = float ))
    #Spec_Index = 0
    Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    '''
    DAQ_Signal = Array('d', np.zeros(shape=( No_DAC_Sample*No_Shutter_Cycles ,1), dtype = float ))
    DAQ_Time   = Array('d', np.zeros(shape=( No_DAC_Sample*No_Shutter_Cycles ,1), dtype = float ))
    DAQ_Index  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    DAQ_Index_Total  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    Shutter_Index_Cycle = Array('i', np.zeros(shape=( 1 ,1), dtype = int )) 
    Shutter_Index_Cycle[0] = No_Shutter_Cycles
    Ref_Signal = Array('d', np.zeros(shape=( No_DAC_Sample*No_Shutter_Cycles ,1), dtype = float ))
    Ref_Time   = Array('d', np.zeros(shape=( No_DAC_Sample*No_Shutter_Cycles ,1), dtype = float ))
    '''
    Power_Signal = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
    Power_Time   = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
    Power_Index  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    '''
    # ########### The file containing the records (HDF5 format)###########'''


    Pros_DAQ = Process(target=DAQ_Read_Process, args=(No_DAC_Sample,))
    Pros_DAQ.start()
    '''
    Pros_Power = Process(target=Power_Read_Process, args=(No_Power_Sample,))
    Pros_Power.start()
    Pros_Spec = Process(target=Spec_Read_Process, args=(No_Spec_Sample,))
    Pros_Spec.start()


    while((Spec_Is_Done.value == 0)):
        if  Spec_Is_Read.value == 1:
            Spec_Is_Read.value = 0
            Full_Spec_Records[:, np.int(Spec_Index[0])] = Current_Spec_Record[:]
    print('Spectrometer is done')
    '''
    II = 0 
    while (DAQ_Is_Read.value == 0):
        time.sleep(1)
        print (time.time())
        '''        
        try:
            time.sleep(1)
            print (time.time())
        except KeyboardInterrupt:
            break 
        '''



    time.sleep(0.1)
    DAQ1.close()
    #Spec1.close()

    # ######### Plotting the spectrumeter and the photodiod recordings ########
    plt.figure()
    plt.plot(np.asarray(DAQ_Time[0:DAQ_Index_Total[0]]) - DAQ_Time[0],DAQ_Signal[0:DAQ_Index_Total[0]])    
    plt.plot(np.asarray(Ref_Time[0:DAQ_Index_Total[0]]) - DAQ_Time[0],Ref_Signal[0:DAQ_Index_Total[0]])
    
    '''   
    plt.subplot(1,3,1)
    #DAQ_Signal = np.asarray(DAQ_Signal[0:DAQ_Index_Total[0]])
    plt.plot(DAQ_Time[0:DAQ_Index_Total[0]], DAQ_Signal[0:DAQ_Index_Total[0]], label = "Photo Diode")
    plt.title('Photo diode')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (v)')
    '''
    '''
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
    '''
    ################################Closing the devices#############################
    '''
    plt.figure()
    plt.plot(DAQ_Time, (DAQ_Signal[0:DAQ_Index_Total[0]]-np.mean(DAQ_Signal))/float( np.max(np.abs(DAQ_Signal))))
    #plt.plot(Power_Time, (Power_Signal[0:Power_Index[0]]-np.mean(Power_Signal))/float( np.max(np.abs(Power_Signal))))
    #plt.title("Super imposed Power and DAQ signals (not the actual signals)")
    plt.plot(Ref_Signal, (Ref_Signal[0:DAQ_Index_Total[0]]))
    
    plt.xlabel("Unix time")
    plt.legend(['DAQ', 'P100'])
    plt.show()
    '''

    #################### Estimate the latencies of the devices ###################################
    plt.figure()

    DAQ_Latency = DAQ_Time[0:DAQ_Index_Total[0]]
    DAQ_Latency[0] = 0
    for I in range(1,DAQ_Index_Total[0]):
        DAQ_Latency[I] = DAQ_Time[I] - DAQ_Time[I-1]
    plt.subplot(1,3,1)
    plt.plot(DAQ_Latency)
    plt.ylabel("Time (s)")
    plt.title("DAQ latencies")
    plt.show()
    '''
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
    '''    
    
