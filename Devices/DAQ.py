import req.DAQT7_Objective as daq

class DAQ:

    def __init__(self, shutter):
        self.device = DAQ.DetectDAQT7()
        self.shutter = shutter
        
    def DAQ_Read_Process(self, No_DAC_Sample):
        '''
        A function for reading the DAQ analogue inpute on AINX
        '''
        while DAQ_Index[0] < No_DAC_Sample:
            DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = self.device.readPort(PhotoDiod_Port)
            DAQ_Index[0] = DAQ_Index[0] + 1
        DAQ_Is_Read.value = 1

    def DAQ_Speed_Test(self, No_DAQ_Tests):
        '''
        A function for testing the speed of the DAQ analogue inpute on AINX
        '''
        Scratch_Signal = 0
        Mean_Time = 0
        I = 0
        Start_Time = time.time()
        while I < No_DAQ_Tests:
            Scratch_Signal, Scratch_Time = self.device.readPort(PhotoDiod_Port)
            I = I + 1
        Duration = time.time() - Start_Time
        Mean_Time = Duration/float(No_DAQ_Tests)
        print ('DAQ Analogue reading requires %f s per sample \n' %Mean_Time)

        return Mean_Time
        
    def close():
        self.self.device.writePort(self.shutter, 0)
  
