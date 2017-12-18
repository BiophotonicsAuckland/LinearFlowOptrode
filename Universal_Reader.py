"""
This code attempted to be able to detect and read any connnected device by any format decided by the user. 
However, there are some aspects of this code which are not finished yet. Hence the code is incomplete at this point.
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

# Functions to save data

No_iterations = 10

    
Time_Index = np.zeros(shape=(1, No_iterations ), dtype = float )



def SaveDataPWR(TimeIndex, Power):  
                        # This function save the recorded date in the HDF5 format. You don't need to call it when using for testing.

    File_name = "Chose_a_Name_ThorlabsPM100" + str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))+ ".hdf5"
    file = h5py.File(File_name, "w")
    file.create_group("ThorlabsPM100")
    file.create_dataset('ThorlabsPM100/Power', data = Power)
    file.create_dataset('ThorlabsPM100/TimeIndex', data = TimeIndex)
    file.close()

def SaveDataDAQ(TimeIndex, Voltages):          # This function save the recorded date in the HDF5 format. You don't need to call it when using for testing.
    File_name = "Chose_a_Name_DAQT7" + str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))+ ".hdf5"
    file = h5py.File(File_name, "w")
    Spec_subgroup1 = file.create_group("DAQT7")
    file.create_dataset('DAQT7/Voltages', data = Voltages)
    file.create_dataset('DAQT7/TimeIndex', data = TimeIndex)
    #dset.attrs["attr"] = b"Hello"
    Spec_subgroup1.attrs['DAQT7 Details'] = np.string_(DAQ1.getDetails())
    file.close()

# This function save the recorded date in the HDF5 format. You don't need to call it when using for testing.
def SaveDataSpec(WaveLength, Intensities,Spec_Index): 
    File_name = "Chose_a_Name_Spectrometer" + str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))+ ".hdf5"
    file = h5py.File(File_name, "w")
    Spec_subgroup1 = file.create_group("Spectrometer")
    file.create_dataset('Spectrometer/Intensities', data = Intensities)
    file.create_dataset('Spectrometer/Spec_Latency', data = Spec_Latency)
    file.create_dataset('Spectrometer/WaveLength', data = WaveLength)
    Spec_subgroup1.attrs['Spectrometer Details'] = np.string_(Spec1.readDetails())
    file.close()
    

   
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
    Spec_Is_Done.value = 1


 # ######## A function for reading the DAQ analogue inpute on AINX ########
def DAQ_Read_Process(No_DAC_Sample, Port):    
    while DAQ_Index[0] < No_DAC_Sample:
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(Port)
        DAQ_Index[0] = DAQ_Index[0] + 1
    DAQ_Is_Read.value = 1

        

    
def DAQ_Read_Process_Buffer(DAQ_SamplingRate, ScansPerRead, Port):
    Read, DAQ_Starting[0], DAQ_Ending[0] = DAQ1.streamRead(DAQ_SamplingRate, ScansPerRead, Port)
 
    print len(Read[0])
    DAQ_Signal[0:len(Read[0])] = np.asarray(Read[0])
    
        
    '''
    # ######## A function for reading the DAQ analogue inpute on AINX ########
    while DAQ_Index[0] < No_DAC_Sample:
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort('AIN1')
        DAQ_Index[0] = DAQ_Index[0] + 1
    '''    
    DAQ_Is_Read.value = 1

def Power_Read_Process(No_Power_Sample):
    # ######## A function for reading the Power meter ########
    while Power_Index[0] < No_Power_Sample:
        Power_Signal[Power_Index[0]], Power_Time[Power_Index[0]] = Power_meter.readPower()
        Power_Index[0] = Power_Index[0] + 1
    Power_Is_Read.value = 1



######################################################################################################
if __name__ == "__main__":
    
    DAQ1 = DAQ.DetectDAQT7()
    Spec1 = SBO.DetectSpectrometer()
    Power_meter = P100.DetectPM100D()
    
    ######################################################################################################
    if (Spec1.Error == 1) & (DAQ1.Error == 1) & (Power_meter.Error == 1):
        print ('Cession failed: could not detect any devices')
    else:
        PhotoDiod_Port = "AIN1"
        DurationOfReading = 2    # Duration of reading in seconds.
        Timer_Is_Over = Value('i', 0)
        Timer_Is_Over.value = 0        
        
        Spec_Is_Done = Value('i', 0)
        Spec_Is_Done.value = 1
        DAQ_Is_Read = Value('i', 0)
        DAQ_Is_Read.value = 1
        Power_Is_Read = Value('i', 0)
        Power_Is_Read.value = 1
        
        ######################################################################################################       
        if (Spec1.Error == 0):
            Integration_Time = 2                                         # Integration time in ms
            Spec1.setTriggerMode(0)                                      # It is set for free running mode
            Spec1.setIntegrationTime(Integration_Time*1000)              # Integration time is in microseconds when using the library
            Spec_Is_Read = Value('i', 0)
            Spec_Is_Read.value = 0
            Spec_Is_Done.value = 0
            No_Spec_Sample =  int(round(DurationOfReading*1000/(Integration_Time))) # Number of samples for spectrometer to read.
            Full_Spec_Records = np.zeros(shape=(len(Spec1.Handle.wavelengths()), No_Spec_Sample ), dtype = float )
            Full_Spec_Records2= Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths())*No_Spec_Sample ,1), dtype = float ))
            Spec_Time   = Array('d', np.zeros(shape=(No_Spec_Sample ,1), dtype = float ))
            Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
            
        ######################################################################################################
        if (DAQ1.Error == 0):
            DAQ_Is_Read.value = 0
            StreamPort = ['AIN0', 'AIN1']          
            while 1==1:
                print ('Which working mode for the analogue input you want?') 
                print ('Hint: using the internal buffer is faster and can go up to 100 kHz but less stable (DAQT7 may crass)')
                print ('Refer to https://labjack.com/support/datasheets/t7/appendix-a-1 for more details')
                print ('Scanning mode is more stable but slower (up to 3.5 kHz, depending on the computer)')
                print ('\n')        
                Paradigm = raw_input('Press b for using internal buffer mode and press s for scanning mode: ')
                if (Paradigm == 's') | (Paradigm == 'S'):
                    while 1==1:
                        DurationOfReading = raw_input('Enter the duration of the reading in seconds: \n')
                        try:
                            DurationOfReading = float(DurationOfReading)
                            No_DAC_Sample = int(round(DurationOfReading*1000/0.5)) # Number of samples for DAQ analogue to digital converter (AINx).
                            break
                            break
                        except ValueError:
                           print("That's not a number!")  
                           print ('\n')  
                elif (Paradigm == 'b') | (Paradigm == 'B'):
                    while 1==1:
                        DurationOfReading = raw_input('Enter the duration of the reading in seconds (a number between 0.5 to 6 seconds): \n')
                        try:
                            DurationOfReading = float(DurationOfReading)
                            if (float(DurationOfReading) < 0.5):
                            #if (float(Integration_Continious) < Spec_SamplingRate):
                                print ('Duration time is too short. Enter a greater number')
                            elif (float(DurationOfReading) > 6):
                                print ('Duration is too long. Enter a smaller number')
                            else:
                                DAQ_SamplingRate = raw_input('Enter the sampling rate in Hz (egxample: 12000): \n')
                                DAQ_SamplingRate = 45000                     # this sampling rate in HZ is for when the internal buffer of DAQ is used
                                                                             # check this link to see what sampling rates are appropriate:
                                                                             # https://labjack.com/support/datasheets/t7/appendix-a-1          
                                ScansPerRead = int(DAQ_SamplingRate*DurationOfReading/float(2))
                                #No_DAC_Sample = DAQ_SamplingRate*4           # if you are using only on AIN then: No_DAC_Sample = DAQ_SamplingRate*2 
                                                                             # if you are using two AINs then: No_DAC_Sample = DAQ_SamplingRate*4
                                No_DAC_Sample = ScansPerRead*len(StreamPort)
                                break
                                break
                        except ValueError:
                           print("That's not a number!")  
                           print ('\n')  
                                                                                                   
            
            DAQ_Signal = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
            DAQ_Time   = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
            DAQ_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
            DAQ_Starting = Array('d', np.zeros(shape=( 1 ,1), dtype = float ))
            DAQ_Ending = Array('d', np.zeros(shape=( 1 ,1), dtype = float ))
    
        ######################################################################################################
        if (Power_meter.Error == 0):
            No_Power_Sample = int(round(DurationOfReading*1000/4.5))                # Number of samples for P100D Power meter to read. 
                                                                                    # Roughly P100 can read the power every 2.7 ms.
            Power_Signal = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
            Power_Time   = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
            Power_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
            Power_Is_Read.value = 0        
    
        ################################## Start the the processes ###########################################
        if (Spec1.Error == 0):
            Pros_Spec = Process(target=Spec_Read_Process, args=(No_Spec_Sample,))
            Pros_Spec.start()
        if (DAQ1.Error == 0):  
            if (Paradigm == 'B') | (Paradigm == 'b'):
                Pros_DAQ = Process(target=DAQ_Read_Process_Buffer, args=(DAQ_SamplingRate, ScansPerRead, StreamPort))
                Pros_DAQ.start()
            elif if (Paradigm == 's') | (Paradigm == 's'):
                Pros_DAQ = Process(target=DAQ_Read_Process, args=(NO_DAQ_Sample,))
                Pros_DAQ.start()
        if (Power_meter.Error == 0):
            Pros_Power = Process(target=Power_Read_Process, args=(No_Power_Sample,))
            Pros_Power.start()
        
        ################################# Stay here till all the processes finsh##############################
        while True:
            if ((DAQ_Is_Read.value == 0) | (Power_Is_Read.value == 0) | (Spec_Is_Done.value == 0)):
                time.sleep(0.001)
            else:
                break

        ############################ Estimate the latencies of the devices ###################################
        if (Spec1.Error == 0):
            Spec_Latency = Spec_Time[0:np.int(Spec_Index[0])]
            Spec_Latency[0] = 0
            for I in range(1,Spec_Index[0]):
                Spec_Latency[I] = np.float(Spec_Time[I] - Spec_Time[I-1])
            
            plt.figure()
            plt.plot(Spec_Latency)
            plt.ylabel("Time (s)")
            plt.title("Spectrometer integration durations")
            plt.show()            
            ######## Loading the Spectrometer Array to a matrix before saving and plotting #######
            Wave_len = len(Spec1.Handle.wavelengths())
            for I in range(Spec_Index[0]):
                Full_Spec_Records[:, I] =  Full_Spec_Records2[I*Wave_len : (I + 1)*Wave_len ]
            SaveDataSpec(Spec1.readWavelength()[1:],Full_Spec_Records[1:],Spec_Latency)
            
            plt.plot(Spec1.readWavelength()[3:],Full_Spec_Records[3:]);
            #plt.ylim(-500,5000)    
            plt.title('Spectrum')
            plt.xlabel('Wavelength (nano meters)')
            plt.ylabel('Intensity')
            plt.show()
            
            Spec1.close()
        ##################################################################################################    
        if (DAQ1.Error == 0):
            DAQ_Time = np.linspace(DAQ_Starting[0], (No_DAC_Sample*1)/float(DAQ_SamplingRate), No_DAC_Sample)
            if len(StreamPort) == 2:
                DAQ_Stack1 = DAQ_Signal[0::2]
                DAQ_Stack2 = DAQ_Signal[1::2]
                del(DAQ_Signal)
                DAQ_Signal = np.zeros(shape=(len(StreamPort), No_DAC_Sample/len(StreamPort) ), dtype = float )
                DAQ_Signal[0] = DAQ_Stack1
                DAQ_Signal[1] = DAQ_Stack2
                
                DAQ_Stack1 = DAQ_Time[0::2]
                DAQ_Stack2 = DAQ_Time[1::2]
                del(DAQ_Time)
                DAQ_Time = np.zeros(shape=(len(StreamPort), No_DAC_Sample/len(StreamPort) ), dtype = float )
                DAQ_Time[0] = DAQ_Stack1
                DAQ_Time[1] = DAQ_Stack2
                
                
            elif len(StreamPort) == 3:     
                DAQ_Stack1 = DAQ_Signal[0::2]
                DAQ_Stack2 = DAQ_Signal[1::2]
                DAQ_Stack3 = DAQ_Signal[2::2]
                del(DAQ_Signal)
                DAQ_Signal = np.zeros(shape=(len(StreamPort), No_DAC_Sample/len(StreamPort) ), dtype = float )
                DAQ_Signal[0] = DAQ_Stack1
                DAQ_Signal[1] = DAQ_Stack2
                DAQ_Signal[2] = DAQ_Stack3
                
                DAQ_Stack1 = DAQ_Time[0::2]
                DAQ_Stack2 = DAQ_Time[1::2]
                DAQ_Stack3 = DAQ_Time[2::2]
                del(DAQ_Time)
                DAQ_Time = np.zeros(shape=(len(StreamPort), No_DAC_Sample/len(StreamPort) ), dtype = float )
                DAQ_Time[0] = DAQ_Stack1
                DAQ_Time[1] = DAQ_Stack2
                DAQ_Time[2] = DAQ_Stack3
                    
            SaveDataDAQ(DAQ_Time,DAQ_Signal) 
            
            for I in range(len(DAQ_Signal)):
                plt.plot(DAQ_Time[I], DAQ_Signal[I])
                
            #plt.title('Photo diode')
            #plt.xlabel('Time (s)')
            #plt.ylabel('Voltage (v)')
           
            
            DAQ1.close()
        ##################################################################################################    
        if (Power_meter.Error == 0):
            Power_Latency = Power_Time[0:Power_Index[0]]
            Power_Latency[0] = 0
            for I in range(1,Power_Index[0]):
                Power_Latency[I] = Power_Time[I] - Power_Time[I-1]
        
            plt.subplot(1,3,2)
            plt.plot(Power_Latency)
            plt.title("P100 latencies")
            plt.ylabel("Time (s)")
            
            SaveDataPWR(Power_Latency, Power_Signal[0:Power_Index[0]])
            
            Power_Signal = np.asarray(Power_Signal[0:Power_Index[0]])
            plt.plot(Power_Latency, label = "Power meter")
            plt.title('Power meter')
            plt.xlabel('Time (s)')
            plt.ylabel('Power (w)')
            
            
            
            
        
        ##################################################################################################
        plt.show()
        
        

        '''
        plt.figure()
        plt.scatter(DAQ_Time, (DAQ_Signal-np.mean(DAQ_Signal))/float( np.max(np.abs(DAQ_Signal))),  c='r',marker='+')    
        plt.scatter(Power_Latency, (Power_Signal[0:Power_Index[0]]-np.mean(Power_Signal))/float( np.max(np.abs(Power_Signal))))
        plt.title("Superimposed Power and DAQ signals ")
        plt.ylabel("Normalized Amplitude")
        plt.xlabel("Time (s)")
        plt.legend(['DAQ', 'Power Meter'])
        plt.show()
        time.sleep(0.1)
        '''
        
