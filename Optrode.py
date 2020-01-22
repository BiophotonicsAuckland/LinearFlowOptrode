#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rewrite of originally spaghetti.

"""

import matplotlib, socket, subprocess,struct, os, sys,tempfile, glob,datetime,time, bisect,os.path,h5py
from multiprocessing import Process, Value, Array
import tkinter as tk
#from ttk import Button, Style, Label, Entry, Notebook, Scale
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk



import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from GUI import View
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

def Continious_Paradigm(Integration_Continious, No_Spec_Sample, No_DAC_Sample, No_Power_Sample, No_BakGro_Spec):
    DAQ1.writePort(Shutter_Port, 5)

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
    ####DAQ1.writePort(Shutter_Port, 0)

    while (int(Spec_Index[0]) < No_Spec_Sample  ):
        '''
        if  Spec_Is_Read.value == 1:
            Spec_Is_Read.value = 0
            Full_Spec_Records[:, np.int(Spec_Index[0]) - 1] = Current_Spec_Record[:]
        '''
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        DAQ_Index[0] = DAQ_Index[0] + 1

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

    Finishes setup phase, then waits for button input to continue.
    Setup phase takes a while, mainly due to DAQ_Speed_Test() and DAQ_Speed_Test().
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

    Integration_Time = 100                                    # Integration time in ms
    Spec1.setTriggerMode(3)                                   # It is set for free running mode
    #Spec1.setIntegrationTime(Integration_Time*1000)          # Integration time is in microseconds when using the library

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
                                # Number of samples for spectrometer to read.

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
        debug("Ready to start paradigm. Press start to begin.")
        but_setup.wait_variable(wait_var)
        but_start.config(state=DISABLED)

        
        Continious_Paradigm(float(Integration_Continious), No_Spec_Sample, No_DAC_Sample, No_Power_Sample, No_BakGro_Spec)

        # Loading the Spectrometer Array to a matrix before saving and plotting ###############
        Wave_len = len(Wavelengths)
        for I in range(Spec_Index[0]):
            Full_Spec_Records[:, I] =  Full_Spec_Records2[I*Wave_len : (I + 1)*Wave_len ]

        # Closing the devices
        Spec_Details = Spec1.readDetails()
        DAQ_Details = DAQ1.getDetails()

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
        DAQ1.writePort(Shutter_Port, 0)

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
        debug("Re-run test with same parameters, change parameters, or quit.")
        but_rerun.wait_variable(wait_var)
        but_rerun.config(state=DISABLED)
        but_change.config(state=DISABLED)

        # If we clicked the 'change' button, quit loop, otherwise keep going.
        if wait_var.get() == 2:
            but_setup.config(state=NORMAL)
            Disable_UI(root, False)
            debug(" ")
            break


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

        
def close(root, DAQ, Spec):
    try:
        

        if plt.fignum_exists(0):
            plt.close(0)
        else:
            time.sleep(0.1)
            DAQ1.close()
            Spec1.close()
    except:
        print("Failed to close devices properly, please replug them")
    finally:
        root.destroy()

if __name__ == "__main__":
    #spec = Spectrometer()
    #daq = DAQ()
    
    
    root = tk.Tk()
    gui = View(root)
    root.mainloop()
    
    """
The MVC Design pattern
The model knows nothing about the view or the controller. Basically a resource that is consumed?
The view knows nothing about the controller or the model. Basically a Listing of GUI elements, no logic.
The controller understands both the model and the view

The model uses observables, when important data is changed any interested listener gets notified through a callback mechanism.

For this example The controller monitors any changes in the model, if the controller notices youc clicked and mofiied    
    
    """