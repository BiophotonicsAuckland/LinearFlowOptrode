# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 11:00:10 2016
This code runs the Optrode version 2
@author: Yaqub Jonmohamadi
"""

#%%
import h5py
import DAQT7_Objective as DAQ
import SeaBreeze_Objective as SBO
import ThorlabsPM100_Objective as P100
import time
import datetime
import numpy as np
from multiprocessing import Process, Value, Array
import matplotlib.pyplot as plt
import os.path
#%%
time_start =  time.time()


# ######################### Naming the DAQ ports ##########################
# FIO0 = shutter of the green laser and FIO1 is the shutter of the blue laser
# FIO2 = is the green laser and the FIO3 is the blue laser
Green_Laser = "FIO1"
Green_Shutter = "DAC0"
Blue_Laser = "FIO0"
Blue_Shutter = "DAC1"

PhotoDiod_Port = "AIN1"
#Spectrometer_Trigger_Port = "DAC1"

Pradigm = 'm'       # Pardigm refers to the continious or multi-integration performance of the Optrode ==> c: continious, and m: multi-integration recording



# ######## A function for reading the DAQ analogue inpute on AINX ########
def DAQ_Read_Process(No_DAC_Sample):
    while DAQ_Index[0] < No_DAC_Sample:
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        DAQ_Index[0] = DAQ_Index[0] + 1
    DAQ_Is_Read.value = 1

# ######## A function for testing the speed of the DAQ analogue inpute on AINX ########
def DAQ_Speed_Test(No_DAQ_Tests):
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

# ######## A function for testing the speed of the Power meter LabJack ########
def Power_Speed_Test(No_Power_Tests):
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


# ######## A function for reading the Power meter ########
def Power_Read_Process(No_Power_Sample):

    while Power_Index[0] < No_Power_Sample:
        Power_Signal[Power_Index[0]], Power_Time[Power_Index[0]] = Power_meter.readPower()
        Power_Index[0] = Power_Index[0] + 1
    Power_Is_Read.value = 1


# ####################### Interrupt like delays (s) #######################
# Usage Ex: Px = Process(target=Timer_Multi_Process, args=(Timer_time,))
# Px.start() and in your code constantly check for "Timer_Is_Done"

def Timer_Multi_Process(Time_In_Seconds):
    if Timer_Is_Over.value is 1:
        print ('Error: This timer can be called one at a time. The previous timer is still running')
    time.sleep(Time_In_Seconds)
    Timer_Is_Over.value = 1


######## A function for initializing the spectrometer (integration time and triggering mode #########
def Spec_Init_Process(Integration_Time, Trigger_mode):      # Integration time in milliseconds
    #print 'Spectrometer is initialized'
    Spec1.setTriggerMode(Trigger_mode)
    time.sleep(0.01)
    Spec1.setIntegrationTime(Integration_Time*1000)          # Conversting it to Microseconds
    time.sleep(0.01)
    Spec_Init_Done.value = 1

# ####### A function for testing the spectrometer speed in free running mode ##################
def Spec_Speed_Test(No_Spec_Tests):
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

# ########## A function for reading the spectrometer intensities ###########
def Spec_Read_Process(No_Spec_Sample):
    I = 0
    Wave_len = len(Spec1.Handle.wavelengths())
    while (I < No_Spec_Sample):
        #Last_Spec_Record[:] = Current_Spec_Record[:]
        #Current_Spec_Record[:], Spec_Time[Spec_Index[0]] = Spec1.readIntensity(True, True)
        Full_Spec_Records2[Spec_Index[0]*Wave_len : (Spec_Index[0] + 1)*Wave_len ], Spec_Time[Spec_Index[0]] = Spec1.readIntensity(True, True)
        Spec_Index[0] = Spec_Index[0] + 1
        Spec_Is_Read.value = 1
        #print ("spectrometer Index is %i" % Spec_Index[0])
        I = I + 1


# ################### Below paradigm is based on free running of the spectrometer ##############################
def Multi_Integration_Paradigm(Integration_list_MilSec, Integration_Buffer_Time, Shutter_Delay, No_Power_Sample):
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
    DAQ1.writePort(Shutter_Port, 0)

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


################ Start of the main code #################################################3
if __name__ == "__main__":
    #try:
    Spec1 = SBO.DetectSpectrometer()
    DAQ1 = DAQ.DetectDAQT7()
    if (Spec1.Error == 1) | (DAQ1.Error == 1):
        print ('Cession failed: could not detect devices')
    else:
        Power_meter = P100.DetectPM100D()

        Integration_Time = 100                                        # Integration time in ms
        Spec1.setTriggerMode(3)                                       # It is set for free running mode
        #Spec1.setIntegrationTime(Integration_Time*1000)              # Integration time is in microseconds when using the library

        ######################## Checkt to see if the folder called Records exist #############################
        Path_to_Records = os.path.abspath(os.path.join( os.getcwd())) + "/Records"
        try:
            os.chdir(Path_to_Records)
        except Exception, e:
            print("Warning: a folder called \'Records\' does not exist in " +  os.path.abspath(os.path.join( os.getcwd())) + "\n Please creat a folder called \'Records\' in the current directory before proceeding with the experiment")


        DAQ1.writePort(Green_Shutter, 0)
        DAQ1.writePort(Blue_Shutter, 0)


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


        #%%
        # ##################### Initializing the variables ###################
        Integration_list_MilSec = [8, 16, 32, 64, 128, 256, 512, 1024 ]    #Integration time for the spectrometer in ms
        Shutter_Delay = 4                 #ms

        No_DAQ_Tests = 20000
        DAQ_SamplingRate = DAQ_Speed_Test(No_DAQ_Tests)*1000            #Shows the sampling speed in ms


        Current_Spec_Record = Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths()) ,1), dtype = float ))
        #Last_Spec_Record = Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths()) ,1), dtype = float ))
        No_Spec_Tests = 500
        Full_Spec_Records2= Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths())*No_Spec_Tests ,1), dtype = float ))
        Spec_Time   = Array('d', np.zeros(shape=(No_Spec_Tests ,1), dtype = float ))
        Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
        Spec_SamplingRate = Spec_Speed_Test(No_Spec_Tests)
        Integration_Buffer_Time = 100       #ms               # This is for the spectrometer. This is the time from the integration started till shutter opens
        #DurationOfReading = np.sum(Integration_list_MilSec)  + len(Integration_list_MilSec)*Delay_Between_Integrations   # Duration of reading in seconds.
        DurationOfReading = (Integration_list_MilSec[-1] + Integration_Buffer_Time + Shutter_Delay*3)*len(Integration_list_MilSec)     # Duration of reading in seconds.
        No_BakGro_Spec = 10       # This is for continious reading and refers to the last few spectrom reading wich are background and the laser is off

        if (Power_meter.Error == 0):
            #Powermeter_SamplingRate = 5.1     #ms
            No_Power_Tests = 200
            Power_SamplingRate = Power_Speed_Test(No_Power_Tests)*1000            #Shows the sampling speed in ms



        while 1==1:
            Paradigm = raw_input('Which paradigm are you running? press c for continious integration and m for multi-integration and then press Enter: ')
            print ('\n')
            if (Paradigm == 'c') | (Paradigm == 'C'):
                Paradigm == 'c'
                #print ('Integration time for the spectrometer must be at least 2 ms and also greater than the minimum integration time of the spectrometer.')
                print ('Integration time for this spectrometer must be at least %f ms\n' %Spec_SamplingRate)
                print ('We recommend integration time of %f ms or higher \n' %(Spec_SamplingRate + Spec1.Handle.minimum_integration_time_micros/float(2000)))
                #print ('Example, for QE65000 it should be at least 8 ms and for HR2000+ it should be at least 2 ms.')
                while 1==1:
                    Integration_Continious = raw_input('Enter the integration time for the spectrometer in MILLISECONDS (e.g., press 4 and then press Enter): ')
                    print ('\n')
                    try:
                        val = float(Integration_Continious)
                        if (float(Integration_Continious) < Spec1.Handle.minimum_integration_time_micros/float(1000)):
                        #if (float(Integration_Continious) < Spec_SamplingRate):
                            print ('Integration time is too short. Enter a greater number')
                        else:
                            break
                    except ValueError:
                       print("That's not a number!")
                       print ('\n')

                while 1==1:
                    DurationOfReading = raw_input('Enter the duration of the recording in SECONDS (e.g., press 7 and then press Enter): ')
                    print ('\n')
                    try:
                       val = float(DurationOfReading)
                       DurationOfReading = float(DurationOfReading)*1000
                       if (DurationOfReading < 0):
                            print ('DurationOfReading is too short. Enter a greater number')
                       else:
                            DurationOfReading = DurationOfReading + No_BakGro_Spec*float(Integration_Continious)

                            break
                    except ValueError:
                       print("That's not a number!")
                       print ('\n')
                break
            elif (Paradigm == 'm') | (Paradigm == 'M'):
                Paradigm = 'm'
                break
            else:
                print ('Wrong input! try again print \n')


        while 1==1:
            Current_Laser = raw_input('Chose a laser. Press G for green laser or press B for blue laser and then press Enter: ')
            print ('\n')
            if (Current_Laser == 'G') | (Current_Laser == 'g'):
                #Laser_Port = Green_Laser
                Shutter_Port = Green_Shutter
                break
            elif (Current_Laser == 'B') | (Current_Laser == 'b'):
                #Laser_Port = Blue_Laser
                Shutter_Port = Blue_Shutter
                break
            else:
                print ('Wrong input! try again')



        #%% ############## Defining the size of the arrays and matrices for recording the signals beased on the duration of the recording #######
        #No_DAC_Sample =   int(round((DurationOfReading + DurationOfReading/4) /DAQ_SamplingRate))        # Number of samples for DAQ analogue to digital converter (AINx).
        No_DAC_Sample =   int((DurationOfReading + DurationOfReading) /DAQ_SamplingRate)

        if (Power_meter.Error == 0):
            No_Power_Sample =   int((DurationOfReading + DurationOfReading/float(2)) /Power_SamplingRate)
        else:
            No_Power_Sample = 0
        #No_Power_Sample = int(round(DurationOfReading/Powermeter_SamplingRate)) # Number of samples for P100D Power meter to read.
                                                                                # Roughly P100 can read the power every 2.7 ms.


        if (Paradigm == 'c'):           # Continious paradigm
            No_Spec_Sample =  int(round(float(DurationOfReading)/float(float(Integration_Continious))))  # Number of samples for spectrometer to read.
        else:
            No_Spec_Sample =  len(Integration_list_MilSec)                                    # Number of samples for spectrometer to read.




        Rerun = 'First'
        while True:
            if (Rerun == 'r') | (Rerun == 'R') | (Rerun == 'First'):
                File_name_PreFix = raw_input('Please enter the prefix for the file name: ')
                Rerun = 'n'
                ################################ Variables initializations #############################################
                Current_Spec_Record = Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths()) ,1), dtype = float ))
                #Last_Spec_Record = Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths()) ,1), dtype = float ))                 
                Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
                Full_Spec_Records = np.zeros(shape=(len(Spec1.Handle.wavelengths()), No_Spec_Sample ), dtype = float )
                Full_Spec_Records2= Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths())*No_Spec_Sample ,1), dtype = float ))
                Spec_Time   = Array('d', np.zeros(shape=( No_Spec_Sample ,1), dtype = float ))

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
                #########################3# Starting the chosen paradigm #####################################
                if (Paradigm == 'm'):             # Multi-integration paradigm
                    print ('step1')
                    Multi_Integration_Paradigm(Integration_list_MilSec, Integration_Buffer_Time, Shutter_Delay, No_Power_Sample)
                else:                           # Continious paradigm
                    Continious_Paradigm(float(Integration_Continious), No_Spec_Sample, No_DAC_Sample, No_Power_Sample, No_BakGro_Spec)

                ######## Loading the Spectrometer Array to a matrix before saving and plotting ###############
                Wave_len = len(Spec1.Handle.wavelengths())
                for I in range(Spec_Index[0]):
                    Full_Spec_Records[:, I] =  Full_Spec_Records2[I*Wave_len : (I + 1)*Wave_len ]


                ################################Closing the devices#############################
                Spec_Details = Spec1.readDetails()
                DAQ_Details = DAQ1.getDetails()
                DAQ1.writePort(Shutter_Port, 0)


                # ########### The file containing the records (HDF5 format)###########
                #Path_to_Records = os.path.abspath(os.path.join( os.getcwd(), os.pardir)) + "/Records"
                #Path_to_Records = os.path.abspath(os.path.join( os.getcwd())) + "/Records"
                os.chdir(Path_to_Records)
                File_name_Suffix = str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))+ ".hdf5"
                File_name = File_name_PreFix + '-' + File_name_Suffix
                #File_name = "Chose_a_Prifix" + str('%i' %time.time())+ ".hdf5"
                #File_name = "Opterode_Recording_At" + str('%i' %time.time())+ ".hdf5"
                f = h5py.File(File_name, "w")

                # ########### Saving the recorded signals in HDF5 format ############

                Optrode_DAQ = f.create_group('DAQT7')
                f.create_dataset('DAQT7/PhotoDiode', data = np.asanyarray(DAQ_Signal[:]))
                f.create_dataset('DAQT7/TimeIndex', data = np.asanyarray(DAQ_Time[:]))
                Optrode_DAQ.attrs['DAQT7 Details'] = np.string_(DAQ_Details)

                Optrode_Spectrometer = f.create_group('Spectrometer')
                f.create_dataset('Spectrometer/Intensities', data = np.asanyarray(Full_Spec_Records))
                f.create_dataset('Spectrometer/Time_Index', data = np.asanyarray(Spec_Time))
                f.create_dataset('Spectrometer/WaveLength', data = np.asanyarray(Spec1.Handle.wavelengths()))
                Optrode_Spectrometer.attrs['Spectrometer Details'] = np.string_(Spec_Details)


                if (Power_meter.Error == 0):
                    Optrode_Power = f.create_group('PM100_PowerMeter')
                    f.create_dataset('PM100_PowerMeter/Power', data = np.asanyarray(Power_Signal[:]))
                    f.create_dataset('PM100_PowerMeter/TimeIndex', data = np.asanyarray(Power_Time[:]))
                    #Optrode_DAQ.attrs['PowerMeter Details'] = np.string_(DAQ_Details)

                f.close()

                Path_to_Fred_Codes = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
                os.chdir(Path_to_Fred_Codes)
                # %%
                # ######### Plotting the spectrumeter and the photodiod recordings ########
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

                #%%
                #################### Estimate the latencies of the devices ###################################
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

                if (Power_meter.Error == 0):
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
                ############################## Here is where you can ask to rerun the paradigm ########################
                print('\n')
                print('Data is saved. \n')

                Rerun = raw_input('Press r or R if you want to rerun the paradigm and then press Enter. Alternetively to quit press any otehr key. ')
            else:
                break

        time.sleep(0.1)
        DAQ1.close()
        Spec1.close()
    '''
    except Exception, e:
        print ('time of failior %f:' %time.time())
        print(e.message)
        print('Error happend and cession failed \n')
        time.sleep(0.1)
        DAQ1.close()
        Spec1.close()
    '''
