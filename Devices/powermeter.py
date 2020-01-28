#PowerMeter.py
import req.ThorlabsPM100_Objective as P100

class PM:

    def __init__(self):
        self.PM1 = P100.DetectPM100D()
        
    def Power_Speed_Test(self, no_power_tests):
        '''
        A function for testing the speed of the Power meter LabJack
        '''
        Scratch_Signal = 0
        Mean_Time = 0
        I = 0
        Start_Time = time.time()
        while I < no_power_tests:
            Scratch_Signal, Scratch_Time = Power_meter.readPower()
            I = I + 1
        Duration = time.time() - Start_Time
        Mean_Time = Duration/float(no_power_tests)
        print ('Power meter reading requires %f s per sample \n' %Mean_Time)

        return Mean_Time

    def Power_Read_Process(self, no_power_sample):
        '''
        A function for reading the Power meter
        '''
        while Power_Index[0] < no_power_sample:
            Power_Signal[Power_Index[0]], Power_Time[Power_Index[0]] = Power_meter.readPower()
            Power_Index[0] = Power_Index[0] + 1
        Power_Is_Read.value = 1
