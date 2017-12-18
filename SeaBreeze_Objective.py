'''
Please refer to this website in for installation and prerequisites of the OceanOptice spectrometers python library:"

https://github.com/ap--/python-seabreeze"

To use this class and its functions, following syntax is recommended:
import SeaBreeze_Objective as SBO
DeviceName = SBO.DetectSpectrometer()
To clear the spectrometer use DeviceName.clear()
To reset the spectrometer use DeviceName.reset()
To close the spectrometer use DeviceName.close()
To get the detailed information about connected spectrometer use DeviceName.readDetails()
To read the intensities the recommended format is Intensities = DeviceName.readIntensity(True, True). The True values refer to Correct_dark_counts and Correct_nonlinearity
The first element of Intensities (Intensities[0]) is the moment when the intensities are read (in unix time format)
To read the wavelengthes the recommended format is Wavelengthes = DeviceName.readWavelenght()


To chose an integration time use DeviceName.setIntegrationTime(IntegrationTime), where IntegrationTime is in microseconds and is from minimum integration time to maximum integration time
To chose an integration time use DeviceName.setTriggerMode(TriggerValue), where TriggerValue is the TriggerValue is a value between 0 to 4 depending on the spectrometer. Read below information to chose a value for triggering:

for HR2000+, USB2000+and Flame-S:
Trigger Value = 0 ==> Normal (Free running) Mode
Trigger Value = 1 ==> Software Trigger Mode
Trigger Value = 2 ==> External Hardware Level Trigger Mode
Trigger Value = 3 ==> External Synchronization Trigger Mode
Trigger Value = 4 ==> External Hardware Edge Trigger Mode


for HR4000, USB4000 and Flame-T Set Trigger Mode
Trigger Value = 0 ==> Normal (Free running) Mode
Trigger Value = 1 ==> Software Trigger Mode
Trigger Value = 2 ==> External Hardware Level Trigger Mode
Trigger Value = 3 ==> Normal (Shutter) Mode
Trigger Value = 4 ==> External Hardware Edge Trigger Mode


for Maya2000Pro and Maya - LSL, QE65000, QE65 Pro, and QE Pro
Trigger Value = 0 ==> Normal (Free running) Mode
Trigger Value = 1 ==> External Hardware Level Trigger Mode
Trigger Value = 2 ==> External Synchronous Trigger Mode*
Trigger Value = 3 ==> External Hardware Edge Trigger Mode
*Not yet implemented on the QE Pro

For NIRQuest

Trigger Value = 0 ==> Normal (Free running) Mode
Trigger Value = 3 ==> External Hardware Edge Trigger Mode

To access to all the callable attributes of the spectrometer use DeviceName.Handle.Attribute, where the Attribute could be one of the followings:
close
continuous_strobe_set_enable
continuous_strobe_set_period_micros
eeprom_read_slot
from_serial_number
integration_time_micros
intensities
irrad_calibration
irrad_calibration_collection_area
lamp_set_enable
light_sources
minimum_integration_time_micros
model
pixels
serial_number
shutter_set_open
spectrum
stray_light_coeffs
tec_get_temperature_C
tec_set_enable
tec_set_temperature_C
trigger_mode
wavelengths

@author: Yaqub Jonmohamadi
June 24, 2016
'''

import time
import seabreeze.spectrometers as sb


class DetectSpectrometer:
    ''' ************** Detection of the OceanOptics spectrumeter **************** '''
    def __init__(self):
        try:
            sb.list_devices()
            if len(sb.list_devices()) == 0:
                print ("No spectrometer is detected! \n")
                self.Error = 1
                return         
            else:
                self.detect()
        except Exception, e:
            if (e.message == 'This should not have happened. Apparently this device has 0 serial number features. The code expects it to have 1 and only 1. Please file a bug report including a description of your device.'):
                #print ('Please unplug the spectrometer and then plug again. Then close the python command line and reopen it. Last')
                print ('Unplug the spectrometer and then plug again, then close the python command line and reopen it.')
                self.Error = 1
                return
        #return             
    
    
    
    def detect(self):
        try:                 
            devices = sb.list_devices()
            sb.Spectrometer(devices[0]).close()
            self.Handle = sb.Spectrometer(devices[0])
            self.Error = 0
            print (devices)
            print ('Serial number:%s' % self.Handle.serial_number)
            print ('Model:%s' % self.Handle.model)
            print ('minimum_integration_time_micros: %s microseconds' % self.Handle.minimum_integration_time_micros)
            self.clear()
            self.Error = 0
            return
        except Exception, e:
            if  (e.message == 'Device already opened.'):
                #print ('Device will be reseted')                        
                #self.reset()
                print ('Error: ' + e.message)
                print ('Unplug the spectrometer and then plug again')
            elif (e.message == 'Error: Data transfer error'):
                print ('Error: ' + e.message)
                print ('Please unplug the spectrometer and then plug again. Then close the python command line and reopen it.')
                #return
            else:
                print (e.message)
                print ('Please unplug the spectrometer and then plug again. Then close the python command line and reopen it. ')
                #return
            self.Error = 1    
            print('Openning spectrometer failed!')
            return

    def readDetails(self):
        attrs = vars(self.Handle)
        return attrs

    def reset(self):
        ''' This function resets the spectrometer. To make a hardware reset unplug it from the computer and then plug in again. '''
        devices = sb.list_devices()
        if len(sb.list_devices()) == 0:
            print ("No spectrometer is detected! \n")
            return
        else:
            self.Handle.close()
            self.Handle = sb.Spectrometer(devices[0])
        self.clear()


    def setIntegrationTime(self, Integration_time):
        ''' Setting the integration time (microseconds) '''
        self.Handle.integration_time_micros(Integration_time)
        time.sleep(0.01)


    def setTriggerMode(self, Trigger_mode):
        ''' Setting the triggering mode (e.g., free running or external trigger) '''
        self.Handle.trigger_mode(Trigger_mode)
        time.sleep(0.01)



    def readIntensity(self, Correct_dark_counts, Correct_nonlinearity):
        ''' Reading the intensities.
        Important! the first element in the Intensities array is the unix time for when the reading is finished.
        '''
        Intensities = self.Handle.intensities(correct_dark_counts=Correct_dark_counts, correct_nonlinearity=Correct_nonlinearity)
        return Intensities, time.time()


    def readWavelength(self):
        ''' Reading the wavelengthes of the spectrometer '''
        return self.Handle.wavelengths()


    def clear(self):
        for I in range(3):
            self.Handle.trigger_mode(0)            #Flushing the stuff down and make the spectrometer ready for the next steps!
            time.sleep(0.01)
            self.Handle.integration_time_micros(10000)
            time.sleep(0.01)
            self.Handle.intensities(correct_dark_counts=True, correct_nonlinearity=True)
            time.sleep(0.01)


    def close(self):
        ''' Closing the device '''
        self.Handle.close()
