# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 11:00:10 2016
This code runs the Optrode version 2
@author: Yaqub Jonmohamadi
"""

import matplotlib, socket, subprocess, time, struct, os, sys, tempfile, glob, datetime, time, bisect, h5py, os.path

from multiprocessing import Process, Value, Array
from Tkinter import *
from ttk import Button, Style, Label, Entry, Notebook, Scale
from tkFileDialog import askopenfilename
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import DAQT7_Objective as DAQ
import SeaBreeze_Objective as SBO
import ThorlabsPM100_Objective as P100
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#%%
time_start =  time.time()

# ######################### Naming the DAQ ports ##########################
# FIO0 = shutter of the green laser and FIO1 is the shutter of the blue laser
# FIO2 = is the green laser and the FIO3 is the blue laser
Blue_Laser = "FIO1"
Blue_Shutter = "DAC0"
Green_Laser = "FIO0"
Green_Shutter = "DAC1"

PhotoDiod_Port = "AIN1"
#Spectrometer_Trigger_Port = "DAC1"


Pradigm = 'm' # Pardigm refers to the continious or multi-integration performance of the Optrode ==> c: continious, and m: multi-integration recording

def DAQ_Read_Process(No_DAC_Sample):
    '''
    A function for reading the DAQ analogue inpute on AINX
    '''
    while DAQ_Index[0] < No_DAC_Sample:
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        DAQ_Index[0] = DAQ_Index[0] + 1
    DAQ_Is_Read.value = 1

def DAQ_Speed_Test(No_DAQ_Tests):
    '''
    A function for testing the speed of the DAQ analogue inpute on AINX
    '''
    Scratch_Signal = 0
    Mean_Time = 0
    I = 0
    Start_Time = time.time()
    while I < No_DAQ_Tests:
        Scratch_Signal, Scratch_Time = DAQ1.readPort(PhotoDiod_Port)
        I = I + 1
    Duration = time.time() - Start_Time
    Mean_Time = Duration/float(No_DAQ_Tests)
    print ('DAQ Analogue reading requires %f s per sample \n' %Mean_Time)

    return Mean_Time

def Power_Speed_Test(No_Power_Tests):
    '''
    A function for testing the speed of the Power meter LabJack
    '''
    Scratch_Signal = 0
    Mean_Time = 0
    I = 0
    Start_Time = time.time()
    while I < No_Power_Tests:
        Scratch_Signal, Scratch_Time = Power_meter.readPower()
        I = I + 1
    Duration = time.time() - Start_Time
    Mean_Time = Duration/float(No_Power_Tests)
    print ('Power meter reading requires %f s per sample \n' %Mean_Time)

    return Mean_Time

def Power_Read_Process(No_Power_Sample):
    '''
    A function for reading the Power meter
    '''
    while Power_Index[0] < No_Power_Sample:
        Power_Signal[Power_Index[0]], Power_Time[Power_Index[0]] = Power_meter.readPower()
        Power_Index[0] = Power_Index[0] + 1
    Power_Is_Read.value = 1

def Timer_Multi_Process(Time_In_Seconds):
    '''
    Interrupt like delays (s)
    Usage Ex: Px = Process(target=Timer_Multi_Process, args=(Timer_time,))
    Px.start() and in your code constantly check for "Timer_Is_Done"
    '''
    if Timer_Is_Over.value is 1:
        print ('Error: This timer can be called one at a time. The previous timer is still running')
    time.sleep(Time_In_Seconds)
    Timer_Is_Over.value = 1

def Spec_Init_Process(Integration_Time, Trigger_mode):
    '''
    A function for initializing the spectrometer (integration time and triggering mode
    Integration_Time is given in milliseconds
    '''
    #print 'Spectrometer is initialized'
    Spec1.setTriggerMode(Trigger_mode)
    time.sleep(0.01)
    Spec1.setIntegrationTime(Integration_Time*1000)          # Conversting it to Microseconds
    time.sleep(0.01)
    Spec_Init_Done.value = 1

def Spec_Speed_Test(No_Spec_Tests):
    '''
    A function for testing the spectrometer speed in free running mode
    '''
    Test_Integration_Time = Spec1.Handle.minimum_integration_time_micros/float(1000)
    Spec_Init_Process(Test_Integration_Time, 0)
    Mean_Time = 0
    #I = 0
    Threshold = 1.2
    while True:
        Start_Time = time.time()
        Spec_Read_Process(No_Spec_Tests)
        Spec_Index[0] = 0
        '''
        while I < No_Spec_Tests:
            Scratch_Signal, Mean_Time = Spec1.readIntensity(True, True)
            I = I + 1
        '''
        Duration = (time.time() - Start_Time)*1000
        Mean_Time = Duration/float(No_Spec_Tests)
        if (Mean_Time < Threshold*float(Test_Integration_Time)):
            print ('Finisehd. Duration: %f' %Duration)
            print ('Mean time %f' %Mean_Time)
            print ('Test_Integration_Time %f' %Test_Integration_Time)
            break
        else:         # The integration time was not enough for the spectromer so it is increased by 0.5 portion of the minimum integration time
            print ('Mean time %f' %Mean_Time)
            print ('Test_Integration_Time %f' %Test_Integration_Time)
            print ('Duration: %f' %Duration)
            Test_Integration_Time = Test_Integration_Time + Spec1.Handle.minimum_integration_time_micros/float(2000)
            Spec_Init_Process(Test_Integration_Time, 0)
            #I = 0

    print ('Spectrometer minimum integration time is %f ms and the practical minimum integration time is %f ms \n' %(Spec1.Handle.minimum_integration_time_micros/float(1000), Test_Integration_Time))

    return Test_Integration_Time

def Spec_Read_Process(No_Spec_Sample):
    '''
    A function for reading the spectrometer intensities
    '''
    I = 0
    Wave_len = len(Wavelengths)
    while (I < No_Spec_Sample):
        #Last_Spec_Record[:] = Current_Spec_Record[:]
        #Current_Spec_Record[:], Spec_Time[Spec_Index[0]] = Spec1.readIntensity(True, True)
        a,b = Spec1.readIntensity(True, True)
        Full_Spec_Records2[Spec_Index[0]*Wave_len : (Spec_Index[0] + 1)*Wave_len] = a[Min_Wave_Index:Max_Wave_Index]
        Spec_Time[Spec_Index[0]] = b
        Spec_Index[0] = Spec_Index[0] + 1
        Spec_Is_Read.value = 1
        #print ("spectrometer Index is %i" % Spec_Index[0])
        I = I + 1

def Multi_Integration_Paradigm(Integration_list_MilSec, Integration_Buffer_Time, Shutter_Delay, No_Power_Sample):
    '''
    Below paradigm is based on free running of the spectrometer.
    '''
    if (Power_meter.Error == 0):
        Pros_Power = Process(target=Power_Read_Process, args=(No_Power_Sample,))
        Pros_Power.start()

    Integration_Base = Integration_list_MilSec[-1] + 2*Integration_Buffer_Time

    Trigger_mode = 0        # Free running
    OrderOfTheProcess = 2   # Order of Process: 0 = setting the timer for the duration of the laser exposure
                            # 1 = turning off the laser (the exposure time is over) and waiting for the spectromer to finish the current integration cycle
                            # 2 = integration time is over and spectrom must be read and setting the timer for the buffer time of the integration cycle

    Spec_Init_Done.value = 0
    #Pros_Spec_Init = Process(target = Spec_Init_Process, args=(Integration_list_MilSec[Spec_Index[0]], Trigger_mode))
    Pros_Spec_Init = Process(target = Spec_Init_Process, args=(Integration_Base, Trigger_mode))
    Pros_Spec_Init.start()
    time.sleep(0.1)

    Spec_Is_Read.value = 0
    Pros_Spec = Process(target=Spec_Read_Process, args=(len(Integration_list_MilSec), ))
    Pros_Spec.start()

    print ('Step1, First itegration does not have laser exposure', time.time())
    while (Spec_Index[0] < len(Integration_list_MilSec)):
        if  (Timer_Is_Over.value == 1) & (OrderOfTheProcess == 0):
            Timer_Is_Over.value = 0
            P_Timer = Process(target=Timer_Multi_Process, args=(Integration_list_MilSec[Spec_Index[0]-1]/float(1000),))
            P_Timer.start()
            DAQ1.writePort(Shutter_Port, 5)
            #Ref_Time[DAQ_Index[0]] = time.time()
            print ('Step2, Raising edge is started',  time.time())
            OrderOfTheProcess = 1

        elif(Timer_Is_Over.value == 1) & (OrderOfTheProcess == 1):
            DAQ1.writePort(Shutter_Port, 0)
            print ('Step3, Falling edge is started',  time.time())
            #Ref_Time[DAQ_Index[0]] = time.time()
            Timer_Is_Over.value = 0
            OrderOfTheProcess = 2
        elif(Spec_Is_Read.value == 1) & (OrderOfTheProcess == 2):
            print ('Step4, Spec is read',  time.time())
            Spec_Is_Read.value = 0
            #Full_Spec_Records[:, np.int(Spec_Index[0])] = Current_Spec_Record[:]
            #Spec_Index[0] = Spec_Index[0]  + 1
            #if (Spec_Index[0] == len(Integration_list_MilSec)):
            #    break

            Timer_Is_Over.value = 0
            P_Timer = Process(target=Timer_Multi_Process, args=(Integration_Buffer_Time/float(1000),))
            P_Timer.start()
            #Pros_Spec_Init = Process(target = Spec_Init_Process, args=(Integration_Base, Trigger_mode))
            #Pros_Spec_Init.start()
            OrderOfTheProcess = 0


        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        #print (DAQ_Signal[DAQ_Index[0]])
        DAQ_Index[0] = DAQ_Index[0] + 1
        #Ref_Time[DAQ_Index[0]] = time.time()
    Pros_Spec.terminate()


    Timer_Is_Over.value = 0
    P_Timer = Process(target=Timer_Multi_Process, args=(Integration_Buffer_Time/float(1000),))
    P_Timer.start()
    print ('time of Timer start %f:' %time.time())
    while  Timer_Is_Over.value == 0:
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        #print (DAQ_Signal[DAQ_Index[0]])
        DAQ_Index[0] = DAQ_Index[0] + 1
        #Ref_Time[DAQ_Index[0]] = time.time()
    P_Timer.terminate()
    if (Power_meter.Error == 0):
        Pros_Power.terminate()

def Continious_Paradigm(Integration_Continious, No_Spec_Sample, No_DAC_Sample, No_Power_Sample, No_BakGro_Spec):
    if (Power_meter.Error == 0):
        Pros_Power = Process(target=Power_Read_Process, args=(No_Power_Sample,))
        Pros_Power.start()
    #Local_Spec_Index = 0
    Spec_Init_Done.value = 0
    Pros_Spec_Init = Process(target = Spec_Init_Process, args=(Integration_Continious, 0))
    Pros_Spec_Init.start()
    Spec_Is_Read.value = 0
    Pros_Spec = Process(target=Spec_Read_Process, args=(No_Spec_Sample, ))
    Timer_Is_Over.value = 0
    P_Timer = Process(target=Timer_Multi_Process, args=(0.1,))
    P_Timer.start()
    while  Timer_Is_Over.value == 0:
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        DAQ_Index[0] = DAQ_Index[0] + 1

    Pros_Spec.start()
    DAQ1.writePort(Shutter_Port, 5)

    #Pros_DAQ = Process(target=DAQ_Read_Process, args=(No_DAC_Sample,))
    #Pros_DAQ.start()
    #Last_DAQ_Signals = 0 # This is a flag bit used to detect the last part of the continious recording
    while (int(Spec_Index[0]) < No_Spec_Sample - No_BakGro_Spec ):

        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        DAQ_Index[0] = DAQ_Index[0] + 1

        '''
        if  Spec_Is_Read.value == 1:
            Spec_Is_Read.value = 0

            Full_Spec_Records[:, np.int(Spec_Index[0]) - 1] = Current_Spec_Record[:]
        '''
    

    while (int(Spec_Index[0]) < No_Spec_Sample  ):
        '''
        if  Spec_Is_Read.value == 1:
            Spec_Is_Read.value = 0
            Full_Spec_Records[:, np.int(Spec_Index[0]) - 1] = Current_Spec_Record[:]
        '''
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        DAQ_Index[0] = DAQ_Index[0] + 1
	#DAQ1.writePort(Shutter_Port, 0)
    if (Power_meter.Error == 0):
        Pros_Power.terminate()

def Begin_Test():
    '''
    Test if parameters are appropriate, update UI and start the test.
    '''
    MIN_INT_TIME = Spec1.Handle.minimum_integration_time_micros/1000.0
    MAX_INT_TIME = 2000
    MIN_REC_TIME = 1
    MAX_REC_TIME = 3600
    MIN_WAVE_LEN = 100
    MAX_WAVE_LEN = 10000

    if Spec1.Error == 1:
        debug("ERROR: Cession failed, could not detect spectrometer.")
    elif DAQ1.Error == 1:
        debug("ERROR: Cession failed, could not detect DAQ, try unplugging and plugging back in.")
    elif not is_number(int_time.get()):
        debug("ERROR: Integration duration is not a number.")
    elif float(int_time.get()) < MIN_INT_TIME:
        debug("ERROR: Integration duration is smaller than " + str(MIN_INT_TIME) + ".")
    elif float(int_time.get()) > MAX_INT_TIME:
        debug("ERROR: Integration duration is greater than " + str(MAX_INT_TIME) + ".")
    elif not is_number(rec_time.get()):
        debug("ERROR: Recording duration is not a number.")
    elif float(int_time.get()) < MIN_REC_TIME:
        debug("ERROR: Recording duration is smaller than " + str(MIN_REC_TIME) + ".")
    elif float(int_time.get()) > MAX_REC_TIME:
        debug("ERROR: Recording duration is greater than " + str(MAX_REC_TIME) + ".")
    elif not is_number(min_len.get()):
        debug("ERROR: Minimum wavelength is not a number.")
    elif float(min_len.get()) < MIN_WAVE_LEN:
        debug("ERROR: Minimum wavelength is smaller than " + str(MIN_WAVE_LEN) + ".")
    elif float(min_len.get()) > MAX_WAVE_LEN:
        debug("ERROR: Minimum wavelength is greater than " + str(MAX_WAVE_LEN) + ".")
    elif not is_number(max_len.get()):
        debug("ERROR: Maximum wavelength is not a number.")
    elif float(min_len.get()) < MIN_WAVE_LEN:
        debug("ERROR: Maximum wavelength is smaller than " + str(MIN_WAVE_LEN) + ".")
    elif float(min_len.get()) > MAX_WAVE_LEN:
        debug("ERROR: Maximum wavelength is greater than " + str(MAX_WAVE_LEN) + ".")
    elif float(min_len.get()) >= float(max_len.get()):
        debug("ERROR: Minimum wavelength is smaller than maximum wavelength.")
    elif par_mode.get() != "c" and par_mode.get() != "m":
        debug("ERROR: Invalid paradigm mode selected.")
    elif shut_mode.get() != Green_Shutter and shut_mode.get() != Blue_Shutter:
        debug("ERROR: Invalid shutter selected.")
    else:

        # If no errors, then start the test after 10ms, to allow UI time to update
        debug("SETTING UP...")
        but_setup.config(state=DISABLED)
        Disable_UI(root)
        root.after(10, Perform_Test)

def Perform_Test():
    '''
    Main function that performs entire spectrometer test.
    '''

    global Spec_Is_Read, Spec_Init_Done, DAQ_Is_Read, Power_Is_Read, Timer_Is_Over
    Spec_Is_Read = Value('i', 0)
    Spec_Is_Read.value = 0
    Spec_Init_Done = Value('i',0)
    Spec_Init_Done.value = 0
    DAQ_Is_Read = Value('i', 0)
    DAQ_Is_Read.value = 0
    Power_Is_Read = Value('i', 0)
    Power_Is_Read.value = 0
    Timer_Is_Over = Value('i', 0)
    Timer_Is_Over.value = 0

    Integration_Time = 100                                        # Integration time in ms
    Spec1.setTriggerMode(3)                                       # It is set for free running mode
    #Spec1.setIntegrationTime(Integration_Time*1000)              # Integration time is in microseconds when using the library

    # Check to see if the folder called Records exist
    Path_to_Records = os.path.abspath(os.path.join( os.getcwd())) + "/Records"
    if not os.path.exists(Path_to_Records):
        os.makedirs(Path_to_Records)

    DAQ1.writePort(Green_Shutter, 0)
    DAQ1.writePort(Blue_Shutter, 0)

    # Initializing the variables
    Integration_list_MilSec = [8, 16, 32, 64, 128, 256, 512, 1024]    #Integration time for the spectrometer in ms
    Shutter_Delay = 4                 #ms

    No_DAQ_Tests = 20000
    DAQ_SamplingRate = DAQ_Speed_Test(No_DAQ_Tests)*1000            #Shows the sampling speed in ms

    global Wavelengths, Min_Wave_Index, Max_Wave_Index, Full_Spec_Records2, Spec_Time, Spec_Index
    Wavelengths = Spec1.readWavelength()
    Min_Wave_Index = max(bisect.bisect(Wavelengths, float(min_len.get())-1), 0)
    Max_Wave_Index = bisect.bisect(Wavelengths, float(max_len.get()))
    Wavelengths = Wavelengths[Min_Wave_Index:Max_Wave_Index]

    Current_Spec_Record = Array('d', np.zeros(shape=( len(Wavelengths) ,1), dtype = float ))
    No_Spec_Tests = 500
    Full_Spec_Records2 = Array('d', np.zeros(shape=( len(Wavelengths)*No_Spec_Tests ,1), dtype = float ))
    Spec_Time = Array('d', np.zeros(shape=(No_Spec_Tests ,1), dtype = float ))
    Spec_Index = Array('i', np.zeros(shape=(1, 1), dtype = int))

    Spec_SamplingRate = Spec_Speed_Test(No_Spec_Tests)
    Integration_Buffer_Time = 100       #ms               # This is for the spectrometer. This is the time from the integration started till shutter opens
    #DurationOfReading = np.sum(Integration_list_MilSec)  + len(Integration_list_MilSec)*Delay_Between_Integrations   # Duration of reading in seconds.
    DurationOfReading = (Integration_list_MilSec[-1] + Integration_Buffer_Time + Shutter_Delay*3)*len(Integration_list_MilSec)     # Duration of reading in seconds.
    No_BakGro_Spec = 10       # This is for continious reading and refers to the last few spectrom reading wich are background and the laser is off

    # Finding parameter values from GUI
    # - Port to use, either Green_Shutter or Blue_Shutter
    # - Integration time in ms
    # - Total recording duration in s
    # - Prefix of filename
    global Shutter_Port
    Shutter_Port = shut_mode.get()
    Integration_Continious = float(int_time.get())
    DurationOfReading = float(rec_time.get())*1000.0 + No_BakGro_Spec*float(int_time.get())
    File_name_PreFix = filename.get()
    if File_name_PreFix == "":
        File_name_PreFix = "OptrodeData"

    if (Power_meter.Error == 0):
        #Powermeter_SamplingRate = 5.1     #ms
        No_Power_Tests = 200
        Power_SamplingRate = Power_Speed_Test(No_Power_Tests)*1000            #Shows the sampling speed in ms

    #%% ############## Defining the size of the arrays and matrices for recording the signals beased on the duration of the recording #######
    #No_DAC_Sample = int(round((DurationOfReading + DurationOfReading/4) /DAQ_SamplingRate))        # Number of samples for DAQ analogue to digital converter (AINx).
    No_DAC_Sample = int((2. * DurationOfReading) /DAQ_SamplingRate)

    if (Power_meter.Error == 0):
        No_Power_Sample = int((1.5 * DurationOfReading) /Power_SamplingRate)
    else:
        No_Power_Sample = 0
    #No_Power_Sample = int(round(DurationOfReading/Powermeter_SamplingRate))
    # Number of samples for P100D Power meter to read.
    # Roughly P100 can read the power every 2.7 ms.

    if (par_mode.get() == 'c'):           # Continious paradigm
        No_Spec_Sample =  int(round(float(DurationOfReading)/float(float(Integration_Continious))))  # Number of samples for spectrometer to read.
    else:
        No_Spec_Sample =  len(Integration_list_MilSec)                                    # Number of samples for spectrometer to read.


    Rerun = 'First'
    while True:
        ################################ Variables initializations #############################################
        Current_Spec_Record = Array('d', np.zeros(shape=( len(Wavelengths) ,1), dtype = float ))
        #Last_Spec_Record = Array('d', np.zeros(shape=( len(Wavelengths) ,1), dtype = float ))
        Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
        Full_Spec_Records = np.zeros(shape=(len(Wavelengths), No_Spec_Sample ), dtype = float )
        Full_Spec_Records2= Array('d', np.zeros(shape=( len(Wavelengths)*No_Spec_Sample ,1), dtype = float ))
        Spec_Time   = Array('d', np.zeros(shape=( No_Spec_Sample ,1), dtype = float ))

        global DAQ_Signal, DAQ_Time, DAQ_Index
        DAQ_Signal = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
        DAQ_Time   = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
        DAQ_Index  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
        #DAQ_Index_Total  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
        #Ref_Signal = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
        #Ref_Time   = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))

        if (Power_meter.Error == 0):
            Power_Signal = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
            Power_Time   = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
            Power_Index  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))


        ##### Finished Setup
        ##### Waiting for button press
        but_start.config(state=NORMAL)
        if auto_flow.get() == 0:
            but_sflow.config(state=NORMAL)

        debug("Ready to start paradigm. Press start to begin.")
        but_setup.wait_variable(wait_var)

        but_start.config(state=DISABLED)
        but_sflow.config(state=DISABLED)
        if auto_flow.get() == 1:
            pass # start_flow()


        # Starting the chosen paradigm
        if (par_mode.get() == 'm'):
            Multi_Integration_Paradigm(Integration_list_MilSec, Integration_Buffer_Time, Shutter_Delay, No_Power_Sample)
        else:
            Continious_Paradigm(float(Integration_Continious), No_Spec_Sample, No_DAC_Sample, No_Power_Sample, No_BakGro_Spec)

        # Loading the Spectrometer Array to a matrix before saving and plotting ###############
        Wave_len = len(Wavelengths)
        for I in range(Spec_Index[0]):
            Full_Spec_Records[:, I] =  Full_Spec_Records2[I*Wave_len : (I + 1)*Wave_len ]

        # Closing the devices
        Spec_Details = Spec1.readDetails()
        DAQ_Details = DAQ1.getDetails()
        DAQ1.writePort(Shutter_Port, 0)

        # ########### The file containing the records (HDF5 format)###########
        #Path_to_Records = os.path.abspath(os.path.join( os.getcwd(), os.pardir)) + "/Records"
        #Path_to_Records = os.path.abspath(os.path.join( os.getcwd())) + "/Records"
        os.chdir(Path_to_Records)
        if is_suff.get() == 1:
            File_name_Suffix = str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))
            File_name = File_name_PreFix + '-' + File_name_Suffix + ".hdf5"
        else:
            File_name = File_name_PreFix + ".hdf5"
        f = h5py.File(File_name, "w")

        # Saving the recorded signals in HDF5 format
        Optrode_DAQ = f.create_group('DAQT7')
        f.create_dataset('DAQT7/PhotoDiode', data = np.asanyarray(DAQ_Signal[:]))
        f.create_dataset('DAQT7/TimeIndex', data = np.asanyarray(DAQ_Time[:]))
        Optrode_DAQ.attrs['DAQT7 Details'] = np.string_(DAQ_Details)

        Optrode_Spectrometer = f.create_group('Spectrometer')
        f.create_dataset('Spectrometer/Intensities', data = np.asanyarray(Full_Spec_Records))
        f.create_dataset('Spectrometer/Time_Index', data = np.asanyarray(Spec_Time))
        f.create_dataset('Spectrometer/WaveLength', data = np.asanyarray(Wavelengths))
        Optrode_Spectrometer.attrs['Spectrometer Details'] = np.string_(Spec_Details)

        if (Power_meter.Error == 0):
            Optrode_Power = f.create_group('PM100_PowerMeter')
            f.create_dataset('PM100_PowerMeter/Power', data = np.asanyarray(Power_Signal[:]))
            f.create_dataset('PM100_PowerMeter/TimeIndex', data = np.asanyarray(Power_Time[:]))
            #Optrode_DAQ.attrs['PowerMeter Details'] = np.string_(DAQ_Details)

        f.close()

        Path_to_Fred_Codes = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        os.chdir(Path_to_Fred_Codes)

        # Plotting the spectrumeter and the photodiod recordings ########
        if plots[0].get() == 1:
            plt.figure()
            plt.plot(np.asarray(DAQ_Time[0:DAQ_Index[0]]) - DAQ_Time[0], np.asanyarray(DAQ_Signal[0:DAQ_Index[0]]))
            plt.title('Photo diode')
            plt.xlabel('Ellapsed time (s)')
            plt.ylabel('Voltage (v)')


        '''
        plt.figure()
        plt.plot(Spec1.readWavelength()[2:],Full_Spec_Records[2:])
        plt.title('Specrometer recordings')
        plt.xlabel('Wavelength (nano meter)')
        plt.ylabel('Intensity')
        #plt.plot(np.asarray(Ref_Time[0:DAQ_Index[0]]) - DAQ_Time[0],Ref_Signal[0:DAQ_Index[0]])
        '''

        # Estimate the latencies of the devices ###################################
        if plots[1].get() == 1:
            plt.figure()
            plt.subplot(1,2,1)
            DAQ_Latency = np.asanyarray(DAQ_Time[0:DAQ_Index[0]])
            DAQ_Latency[0] = 0
            for I in range(1,DAQ_Index[0]):
                DAQ_Latency[I] = DAQ_Time[I] - DAQ_Time[I-1]
            #plt.subplot(1,3,1)
            plt.plot(DAQ_Latency)
            plt.ylabel("Time (s)")
            plt.title("DAQ latencies")
            plt.show()

            plt.subplot(1,2,2)
            Spec_Latency = np.asarray(Spec_Time[0:np.int(Spec_Index[0])])
            Spec_Latency[0] = 0
            for I in range(1,Spec_Index[0]):
                Spec_Latency[I] = np.float(Spec_Time[I] - Spec_Time[I-1])
            plt.plot(Spec_Latency[1:])

            plt.ylabel("Time (s)")
            plt.title("Spectrometer integration durations")
            plt.show()

        if plots[2].get() == 1 and Power_meter.Error == 0:
            plt.figure()
            plt.subplot(1,2,1)
            Power_Latency = np.asanyarray(Power_Time[0:Power_Index[0]])
            Power_Latency[0] = 0
            for I in range(1,int(Power_Index[0])):
                Power_Latency[I] = Power_Time[I] - Power_Time[I-1]
            #plt.subplot(1,3,1)
            plt.plot(Power_Latency)
            plt.ylabel("Time (s)")
            plt.title("Power latencies")
            plt.show()
            plt.subplot(1,2,2)
            plt.plot(np.asarray(Power_Time[0:Power_Index[0]]) - Power_Time[0], np.asanyarray(Power_Signal[0:Power_Index[0]]))
            plt.title('Power Meter')
            plt.xlabel('Ellapsed time (s)')
            plt.ylabel('Power (w)')
            plt.show()

        print('\n')
        print('Data is saved. \n')

        # Wait for button press
        but_rerun.config(state=NORMAL)
        but_change.config(state=NORMAL)
        if auto_flow.get() == 0:
            but_eflow.config(state=NORMAL)
        debug("Re-run test with same parameters, change parameters, or quit.")
        but_rerun.wait_variable(wait_var)
        but_rerun.config(state=DISABLED)
        but_change.config(state=DISABLED)
        but_eflow.config(state=DISABLED)

        # If we clicked the 'change' button, quit loop, otherwise keep going.
        if wait_var.get() == 2:
            but_setup.config(state=NORMAL)
            Disable_UI(root, False)
            debug(" ")
            break

def Close_GUI():
	'''
	Closes alignment window if open, otherwise closes GUI.
	'''
	if plt.fignum_exists(0):
		plt.close(0)
	else:
		time.sleep(0.1)
		DAQ1.close()
		Spec1.close()
		root.destroy()

def Help_GUI():
	'''
	Creates a help window if none exists.
	'''
	if root.help_window == None or root.help_window.winfo_exists() == 0:
		root.help_window = Toplevel(root)
		root.help_window.geometry("260x350+450+150")
		root.help_window.wm_title("Help")

		w = 250

		Message(root.help_window, width=w, font=(None, 13), text="Help:")																												.grid(row=1, column=1, sticky=W)
		Message(root.help_window, width=w, font=(None, 11), text="Press begin to setup test, then press start to begin data collection.")												.grid(row=2, column=1, sticky=W)
		Message(root.help_window, width=w, font=(None, 11), text="Press align to open live read of data to help calibrate setup.")														.grid(row=3, column=1, sticky=W)
		Message(root.help_window, width=w, font=(None, 11), text="After data collection is complete, press re-run to run test with same parameters, or change to change parameters.")	.grid(row=4, column=1, sticky=W)
		Message(root.help_window, width=w, font=(None, 11), text="Checking extension checkbox adds a time tag to end of filename.")														.grid(row=5, column=1, sticky=W)
		Message(root.help_window, width=w, font=(None, 11), text="Checking blit checkbox makes the alignment animations run more smoothly but means axis values will be incorrect.")	.grid(row=6, column=1, sticky=W)

	else:
		root.help_window.focus_set()

def Update_Spec_Line(num, data, line):
	line.set_data(Spec1.Handle.Wavelengths(), Spec1.readIntensity(True, True)[0])
	lim = l.set_xlim(np.amin(data), np.amax(data))
	return line,l

def Align():
	'''
	Creates a help window if none exists.
	'''

	#DISABLE UI

	Spec1.setTriggerMode(0)
	Spec1.setIntegrationTime(40000)
	DAQ1.writePort(shut_mode.get(), 5)

	# Sent for figure
	font = {'size':9}
	matplotlib.rc('font', **font)

	# Setup figure and subplots
	fig = plt.figure(num=0, figsize = (12, 8))
	fig.suptitle("Live Data for Alignment", fontsize=12)
	fig.canvas.mpl_connect('close_event', stop_animation)
	ax01 = plt.subplot2grid((2, 1), (0, 0))
	ax02 = plt.subplot2grid((2, 1), (1, 0))

	# Set x-limits
	ax01.set_xlim(0, 200)
	ax02.set_xlim(max(300, float(min_len.get())), min(900, float(max_len.get())))

	# Set y-limits
	ax01.set_ylim(0, 6)
	ax02.set_ylim(-500, 10000)

	# Turn on grids
	ax01.grid(True)
	ax02.grid(True)

	# Set label names and titles
	ax01.set_title("Photodiode Feed")
	ax01.set_xlabel("Voltage (V)")
	ax01.set_ylabel("Time (unit)")

	ax02.set_title("Live Spectrometer Feed")
	ax02.set_xlabel("Wavelength (nm)")
	ax02.set_ylabel("Intensity (unit)")

	# Data Placeholders
	global DAQdata, PDdata, t, x
	DAQdata = np.zeros(0)
	PDdata = np.zeros(0)
	t = np.zeros(0)
	x = 0.

	# Set plots
	global plot1, plot2
	plot1, = ax01.plot(t,DAQdata,'b-', label="DAQdata")
	plot2, = ax02.plot(t,PDdata,'b-', label="Voltage")

	global Wavelengths, Min_Wave_Index, Max_Wave_Index
	Wavelengths = Spec1.readWavelength()
	Min_Wave_Index = max(bisect.bisect(Wavelengths, float(min_len.get())-1), 0)
	Max_Wave_Index = bisect.bisect(Wavelengths, float(max_len.get()))
	Wavelengths = Wavelengths[Min_Wave_Index:Max_Wave_Index]

	# Create animation
	global anim
	anim = animation.FuncAnimation(fig, Update_Data, blit=use_blit.get(), interval=20, repeat=False)
	plt.show()

def Update_Data(self):

	global DAQdata
	global PDdata
	global t
	global x

	specData = Spec1.readIntensity(True, True)[0][Min_Wave_Index:Max_Wave_Index]

	newDAQ,_ = DAQ1.readPort(PhotoDiod_Port)
	DAQdata = np.append(DAQdata, newDAQ)

	t = np.append(t, x)

	x += 1

	plot1.set_data(t, DAQdata)
	plot2.set_data(Wavelengths, specData)

	if x >= 170:
		plot1.axes.set_xlim(x-170, x+30)
	minVal = np.amin(specData)
	maxVal = np.amax(specData)
	plot2.axes.set_ylim(0.9*minVal - 0.1*maxVal, 0.1*minVal + 1.1*maxVal)

	return plot1, plot2

def Disable_UI(parent, disable=True):
    '''
    Disables non-button UI. Functions recursively.
    '''
    for w in parent.winfo_children():
        if w.winfo_class() == "TEntry" or w.winfo_class() == "Radiobutton" or w.winfo_class() == "Checkbutton":
            if disable == True:
                w.config(state=DISABLED)
            else:
                w.config(state=NORMAL)
        else:
            Disable_UI(w, disable)

def debug(msg):
	print(msg)
	error_msg.set(msg)

def stop_animation(event):
	anim.event_source.stop()

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

if __name__ == "__main__":

	Spec1 = SBO.DetectSpectrometer()
	DAQ1 = DAQ.DetectDAQT7()
	Power_meter = P100.DetectPM100D()

	# Creating GUI
	root = Tk()
	root.title("Linear Flow Fluorescence")
	root.protocol("WM_DELETE_WINDOW", Close_GUI)
	root.geometry("380x580+150+100")
	root.grid_columnconfigure(0, weight=1)

	# Setting variables
	filename = StringVar(value="")      # Filename of output data
	is_suff = IntVar(value=0)           # 0 or 1 depending on whether or not to add a suffix to filename
	int_time = StringVar(value="15")    # Integration time of spectrometer (ms)
	rec_time = StringVar(value="10")    # Recording duration of spectrometer (s)
	min_len = StringVar(value="300")    # Minimum wavelength to record (nm)
	max_len = StringVar(value="900")    # Maximum wavelength to record (nm)
	par_mode = StringVar(value="c")     # Paradigm mode ('c' or 'm')
	shut_mode = StringVar(value=Blue_Shutter)   # Shutter to use (Blue_Shutter or Green_Shutter)

	no_of_plots = 3
	plots = []                          # Booleans on whether or not to plot each plot after collecting data
	for i in range(no_of_plots):
		plots.append(IntVar())
	use_blit = IntVar(value=1)			# Boolean on whether or not to use blit in alignment animation
	auto_flow = IntVar(value=1)			# Boolean on whether or not start and stop flow automatically during tests

	error_msg = StringVar(value=" ")    # Variable that stores the error message displayed on GUI
	wait_var = IntVar(value=0)          # Variable used to keep GUI waiting for user input during tests

	root.help_window = None

	small_entry = 6
	large_entry = 19

	# Title frame
	frame1 = Frame(root)
	frame1.grid(row=0, column=0)

	title = Label(frame1, text="LINEAR FLOW FLUORESCENCE", font=("Times", 13))
	title.grid(row=0, column=1, padx=10, pady=10)

	# Parameter frame
	frame2 = Frame(root, relief=RAISED, borderwidth=1)
	frame2.grid(row=1, column=0, padx=8, pady=4, sticky=W+E)

	rowfn = 1   # Filename row
	rowsu = 2   # Filename suffix row
	rowrd = 3   # Recording duration row
	rowit = 4   # Integration time row
	rowwr = 5   # Wavelength range row

	fnlbl = Label(frame2, text="Select Filename", font=(None, 11))
	fnlbl.grid(row=rowfn, column=1, padx=6, pady=(6,0), sticky=E)
	fntxt = Entry(frame2, textvariable=filename, width=large_entry)
	fntxt.grid(row=rowfn, column=2, padx=6, pady=(6,0), columnspan=3)

	sulbl = Label(frame2, text="Add Suffix", font=(None, 11))
	sulbl.grid(row=rowsu, column=1, padx=9, pady=6, sticky=E)
	fntxt = Checkbutton(frame2, variable=is_suff)
	fntxt.grid(row=rowsu, column=2, padx=0, pady=6, sticky=W)

	rdlbl = Label(frame2, text="Recording duration (s)", font=(None, 11))
	rdlbl.grid(row=rowrd, column=1, padx=6, pady=6, sticky=E)
	rdtxt = Entry(frame2, textvariable=rec_time, width=large_entry)
	rdtxt.grid(row=rowrd, column=2, padx=6, pady=6, columnspan=3)

	itlbl = Label(frame2, text="Integration time (ms)", font=(None, 11))
	itlbl.grid(row=rowit, column=1, padx=6, pady=6, sticky=E)
	ittxt = Entry(frame2, textvariable=int_time, width=large_entry)
	ittxt.grid(row=rowit, column=2, padx=6, pady=6, columnspan=3)

	wrlbl = Label(frame2, text="Wavelength range (nm)", font=(None, 11))
	wrlbl.grid(row=rowwr, column=1, padx=6, pady=6, sticky=E)
	wrtxt = Entry(frame2, textvariable=min_len, width=small_entry)
	wrtxt.grid(row=rowwr, column=2, padx=6, pady=6, sticky=W)
	wrlbl = Label(frame2, text="to", font=(None, 11))
	wrlbl.grid(row=rowwr, column=3, padx=0, pady=6)
	wrtxt = Entry(frame2, textvariable=max_len, width=small_entry)
	wrtxt.grid(row=rowwr, column=4, padx=6, pady=6, sticky=E)

	# Frame for checkbox frames
	framech = Frame(root, relief=RAISED, borderwidth=1)
	framech.grid(row=2, column=0, padx=8, pady=4, sticky=W+E)
	framech.grid_columnconfigure(1, weight=1)
	framech.grid_columnconfigure(2, weight=1)
	framech.grid_columnconfigure(3, weight=1)

	# Paradigm select frame
	frame3 = Frame(framech)
	frame3.grid(row=1, column=1, padx=4, pady=4)
	frame3.grid_columnconfigure(1, weight=1)

	palbl = Label(frame3, text="Paradigm:")
	palbl.grid(row=0, column=0, padx=6, pady=6, sticky=W)

	MODES = [
		("Continuous", "c"),
		("Multi Integration", "m"),
	]
	i = 1
	for text, mode in MODES:
		box = Radiobutton(frame3, text=text, variable=par_mode, value=mode)
		box.grid(row=i, column=0, padx=4, pady=4, sticky=W)
		i = i+1

	# Shutter select frame
	frame4 = Frame(framech)
	frame4.grid(row=1, column=2, padx=4, pady=4)
	frame4.grid_columnconfigure(1, weight=1)

	shlbl = Label(frame4, text="Shutter:")
	shlbl.grid(row=0, column=0, padx=6, pady=6, sticky=W)

	MODES = [
		("Blue", Blue_Shutter),
		("Green", Green_Shutter),
	]
	i = 1
	for text, mode in MODES:
		box = Radiobutton(frame4, text=text, variable=shut_mode, value=mode)
		box.grid(row=i, column=0, padx=4, pady=4, sticky=W)
		i = i+1

	# Plot select frame
	frame5 = Frame(framech)
	frame5.grid(row=1, column=3, padx=4, pady=4)
	frame5.grid_columnconfigure(1, weight=1)

	for i in range(no_of_plots):
		check = Checkbutton(frame5, text="plot"+str(i+1), variable=plots[i])
		check.grid(row=i, column=0, padx=4, pady=4, sticky=W)

	# Error message
	erlbl = Message(framech, width=360, textvariable=error_msg, font=(None, 11))
	erlbl.grid(row=2, column=1, columnspan=3)

	# Button frames
	frame6 = Frame(root)
	frame6.grid(row=3, column=0)

	but_setup = Button(frame6, text="Setup Test", command=Begin_Test)
	but_setup.grid(row=1, column=1, padx=10, pady=10)
	but_start = Button(frame6, text="Start Test", command=lambda: wait_var.set(0), state=DISABLED)
	but_start.grid(row=1, column=2, padx=10, pady=10)
	box2 = Checkbutton(frame6, text="Auto-Flow", variable=auto_flow)
	box2.grid(row=1, column=3, pady=10, sticky=W)

	but_sflow = Button(frame6, text="Start Flow", state=DISABLED)
	but_sflow.grid(row=2, column=1, padx=10, pady=10)
	but_eflow = Button(frame6, text="Stop Flow", state=DISABLED)
	but_eflow.grid(row=2, column=2, padx=10, pady=10)

	but_rerun = Button(frame6, text="Re-run", command=lambda: wait_var.set(1), state=DISABLED)
	but_rerun.grid(row=3, column=1, padx=10, pady=10)
	but_change = Button(frame6, text="Change", command=lambda: wait_var.set(2), state=DISABLED)
	but_change.grid(row=3, column=2, padx=10, pady=10)

	but_help = Button(frame6, text="Help", command=Help_GUI)
	but_help.grid(row=4, column=1, padx=10, pady=10)
	but_align = Button(frame6, text="Align", command=Align)
	but_align.grid(row=4, column=2, padx=10, pady=10)
	box3 = Checkbutton(frame6, text="Blit", variable=use_blit)
	box3.grid(row=4, column=3, pady=10, sticky=W)

	but_close = Button(frame6, text="Close", command=Close_GUI)
	but_close.grid(row=5, column=1, padx=10, pady=10, columnspan=2)

	root.mainloop()
