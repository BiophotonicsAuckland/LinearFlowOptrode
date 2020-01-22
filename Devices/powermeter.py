#PowerMeter.py
import req.ThorlabsPM100_Objective as P100

class PM:

    def __init__(self):
        self.PM1 = P100.DetectPM100D()
        
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
