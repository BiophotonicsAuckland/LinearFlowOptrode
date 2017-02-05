'''
Please refer to this website in for installation and prerequisites of the LabJack device python library:
https://labjack.com/support/software/examples/ljm/python
To use this class and its functions, folowing syntax is recommended:
import DAQT7_Objective
Assuming that your device name is DeviceName then here are some sample commands:
DeviceName = DAQT7_Objective.DetectDAQT7()
This command puts 4.2 volts on DAC1 port (digital to analogue conversion): DeviceName.writePort('DAC1', 4.2)
This command reads the analogue values from AIN0 port (analogue to digital conversion): ReadVoltage = DeviceName.readPort('AIN0')
This command writes a digital value (3.3v) to a digital port (FIO0) port: DeviceName.writePort('FIO0', 1)
This command reads the digital value (zero or one) from a digital port (FIO0) port: State = DeviceName.readPort('FIO0'). State: 0 or 1
*The analogue ports are DACs and AINs. The DACs are read and writable. The AINs are only readable and they are only used for measuring an external voltages (0 to 10v) connected to the port. The FIOs are digital ports and their state are read and writable and they can have only 0 or 3.3 v values (equivalent to 0 and 1 digits).
This command reads a stream of analogue to digital conversion on port AIN1 at the sampling rate of 100kHz: ReadSignal = DeviceName.streanRead(100000, 'AIN1'):
To close the device: DeviceName.close()
print
In order to change the setup of the DAQT7, you need to access to the detailed attributes of the labjack library. The detailed attributes can be accessed:
DeviceName.Handle.Attribute, where the Attribute is one of the following:
eReadNames
eStreamRead
eStreamStart
eStreamStop
eWriteAddress
eWriteAddressArray
eWriteAddressString
eWriteAddresses
eWriteName
eWriteNameArray
eWriteNameString
eWriteNames
errorToString
errorcodes
float32ToByteArray
getHandleInfo
handle
int32ToByteArray
ipToNumber
listAll
listAllExtended
listAllS
ljm
loadConfigurationFile
loadConstants
loadConstantsFromFile
loadConstantsFromString
log
lookupConstantName
lookupConstantValue
macToNumber
mbfbComm
nameToAddress
namesToAddresses
numberToIP
numberToMAC
open
openAll
openS
readLibraryConfigS
readLibraryConfigStringS
readRaw
resetLog
streamBurst
sys
tcVoltsToTemp
uint16ToByteArray
uint32ToByteArray
updateValues
writeLibraryConfigS
writeLibraryConfigStringS
writeRaw

Changing the setup for Labjack device is described in the device manual.

@author: Yaqub Jonmohamadi
June 24, 2016
'''


from labjack import ljm
import time
import numpy as np
import sys

class DetectDAQT7:
    '''
    Initialization and detection of the LabJack device
    '''
    def __init__(self):
        self.Handle = ljm
        self.Error = 0
        try:
            self.Handle.handle = self.Handle.open(self.Handle.constants.dtANY, self.Handle.constants.ctANY, "ANY")
            info = self.Handle.getHandleInfo(self.Handle.handle)
            print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
            "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
            (info[0], info[1], info[2], self.Handle.numberToIP(info[3]), info[4], info[5]))
    
            ''' Setup and call eWriteNames to configure AINs on the LabJack.'''
            numFrames = 3
            names = ["AIN_ALL_NEGATIVE_CH", "AIN_ALL_RANGE", "AIN_ALL_RESOLUTION_INDEX"]
            aValues = [199, 10, 1]
            self.Handle.eWriteNames(self.Handle.handle, numFrames, names, aValues)
            return
        except Exception, e:
            print (e.message)
            print ('Failed to detect DAQ device. Please unplug the device and plug it again. \n')
            self.Error = 1
            return

    def getDetails(self):
        info = self.Handle.getHandleInfo(self.Handle.handle)

        return "Device type: %i, Connection type: %i,\n" \
            "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
            (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5])


    def writePort(self, Port, Volt):      # DAC is one of the DAC ports (e.g., 'DAC0') and Volt is an integer from 0 to 5 volt (e.g., can be used for clossing or openning Shutter: 0=close, 5=open)
        '''
        Writing values to the ports
        * AIN ports are not writable
        '''
        if type(Port) == str:
            Port = [Port]
            print(len(Port))
        if (type(Volt) == str) | (type(Volt) == int) | (type(Volt) == float):
            Volt = [Volt]
            
        self.Handle.eWriteNames(self.Handle.handle,len(Port) , Port, Volt)
        #self.Handle.eWriteName(self.Handle.handle, Port, Volt)
        return


    def readPort(self, Port):
        '''
        Reading analogue inpute values (0 to 10 v) in the AIN ports.
        To change the range of input voltage or speed of conversion, below lines should be changed in the initialization:
        numFrames = 1
        names = [")AIN0_NEGATIVE_CH"), ")AIN0_RANGE"), ")AIN0_RESOLUTION_INDEX")]
        aValues = [199, 2, 1]
        self.Handle.handle.eWriteNames(self.Handle.handle, numFrames, names, aValues)
        '''
        if type(Port) == str:
            Port = [Port]
        return np.float(self.Handle.eReadNames(self.Handle.handle, len(Port) , Port)[0]), time.time()


    def streamRead(self, scanRate, scansPerRead, Port):
        '''
        Reading analogue inpute values (0 to 10 v) in the AIN ports, in stream mode (using the internal buffer of the DAQ).
        scanRate should be below 100000 when using one port only. Using two ports (e.g., AIN0 and AIN1, then it should be below 45000). Please refer to the manual.         
        '''
        Read = [0, 1,2]
        StartingMoment = 0 
        FinishingMoment = 0
        if type(Port) == str:
            Port = [Port]
        try:
            aScanList = self.Handle.namesToAddresses(len(Port), Port)[0]
            
            aNames = ["AIN_ALL_NEGATIVE_CH", "AIN_ALL_RANGE", "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            #aValues = [ljm.constants.GND, 10.0, 0, 0] #single-ended, +/-10V, 0 (default), 0 (default)
            #ljm.eWriteNames(handle, len(aNames), aNames, aValues)
            
            aValues = [self.Handle.constants.GND, 10.0, 0, 0] #single-ended, +/-10V, 0 (default), 0 (default)
            
            self.Handle.eWriteNames(self.Handle.handle, 4, aNames, aValues)
            '''
            aNames = ["AIN1_RANGE"]
            aValues = [0.1] #single-ended, +/-10V, 0 (default), 0 (default)
            self.Handle.eWriteNames(self.Handle.handle, 1, aNames, aValues)
            '''
            
            #scansPerRead = int(scanRate*2)
            scansPerRead = int(scansPerRead)
            #scansPerRead = 32764
            scanRate = self.Handle.eStreamStart(self.Handle.handle, scansPerRead, len(Port), aScanList, scanRate)
            print("\nStream started with a scan rate of %0.0f Hz." % scanRate)
            StartingMoment = time.time()
            Read = self.Handle.eStreamRead(self.Handle.handle)
            self.Handle.eStreamStop(self.Handle.handle)
            FinishingMoment = time.time()
            #Signal = Read[0]
            #curSkip = Signal.count(-9999.0)
            print ('Elapsed time %f seconds' %(FinishingMoment - StartingMoment))
            #print("Supposed Scan Rate = %f scans/second" % (scanRate))
            #print("Timed Scan Rate = %f scans/second" % (len(Signal)/(StartingMoment - FinishingMoment))
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            print(ljme)
        except Exception:
            e = sys.exc_info()[1]
            print(e)
        return Read, StartingMoment, FinishingMoment
        

    def close(self):
        ''' Closing the device '''
        self.Handle.close(self.Handle.handle)
