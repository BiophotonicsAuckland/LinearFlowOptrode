'''
Please refer to this website in for installation and prerequisites of the Thorlabs PM100 power meter python library:
https://pypi.python.org/pypi/ThorlabsPM100
To use this class and its functions, folowing syntax is recommended:
import ThorlabsPM100_Objective
Assuming that your device name is DeviceName then here are some sample commands:
DeviceName = ThorlabsPM100_Objective.DetectPM100D()
To read power Power = DevieceName.readPower()

To close the device: DeviceName.close()

In order to change the setup of the power meter, you need to access to its attributes. The detailed attributes can be accessed:")
DeviceName.Attribute, where the Attribute is one of the following:
DeviceName.abort
DeviceName.getconfigure
DeviceName.sense
DeviceName.calibration
DeviceName.initiate
DeviceName.status
DeviceName.configure
DeviceName.input
DeviceName.system
DeviceName.display
DeviceName.measure
DeviceName.fetch
DeviceName.read

Each of the attributes can have their own attributes, example to change the brightness of the dispace use DeviceName.display.brightness = 0.8
@author: Yaqub Jonmohamadi
June 24, 2016
'''


from ThorlabsPM100 import ThorlabsPM100, USBTMC
import os
import time


class DetectPM100D:
    '''
    Initialization and detection of the Thorlab device
    '''
    def __init__(self):
        # Open first found LabJack
        try:
            USBTMC(device="/dev/usbtmc0")
            inst = USBTMC(device="/dev/usbtmc0")
            self.Handle = ThorlabsPM100(inst=inst)
        except OSError, er0:
            print ('er0:%s' % er0)
            if er0.errno == 13:				# ==> Permission denied: '/dev/usbtmc0'
                os.system('sudo chmod 777 /dev/usbtmc0')
                inst = USBTMC(device="/dev/usbtmc0")
                self.Handle = ThorlabsPM100(inst=inst)
            elif er0.errno == 2:			# ==> [Errno 2] No such file or directory: '/dev/usbtmc0'
                try:
                    USBTMC(device="/dev/usbtmc1")
                    inst = USBTMC(device="/dev/usbtmc1")
                    self.Handle = ThorlabsPM100(inst=inst)
                except OSError, er1:
                    print ('er1:%s' % er1)
                    if er1.errno == 13:		       # ==> Permission denied: '/dev/usbtmc1'
                        os.system('sudo chmod 777 /dev/usbtmc1')
                        inst = USBTMC(device="/dev/usbtmc1")
                        self.Handle = ThorlabsPM100(inst=inst)
                    elif er1.errno == 2:	# ==> [Errno 2] No such file or directory: '/dev/usbtmc1'
                        try:
                            USBTMC(device="/dev/usbtmc2")
                            inst = USBTMC(device="/dev/usbtmc2")
                            self.Handle = ThorlabsPM100(inst=inst)
                        except OSError, er2:
                            print ('er2:%s' % er2)
                            if er2.errno == 13:		# ==> Permission denied: '/dev/usbtmc2'
                                os.system('sudo chmod 777 /dev/usbtmc2')
                                inst = USBTMC(device="/dev/usbtmc2")
                                self.Handle = ThorlabsPM100(inst=inst)
                            elif er2.errno == 2:	# ==> [Errno 2] No such file or directory: '/dev/usbtmc2'
                                self.Error = 1
                                print ("Power meter is not connected! \n")
                                return

        print ("A Thorlabs PM100 device is opened.")
        self.Error = 0
        return

    def readPower(self):
        ''' This function returns the analogue value recorde on one of the AIN ports (e.g., 'AIN0') '''
        return self.Handle.read, time.time()
