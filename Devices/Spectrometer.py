"""Develop edition, porting original code hopefully to python3, and making it less spaghetti"""

import req.SeaBreeze_Objective as SBO

class Spectrometer:

    def __init__(self):
        self.spec = SBO.DetectSpectromter()
        self.wavelengths = self.spec.readWavelength()
    
    def Spec_Init_Process(self, Integration_Time, Trigger_mode):
        '''
        A function for initializing the spectrometer (integration time and triggering mode
        Integration_Time is given in milliseconds
        '''
        self.spec.setTriggerMode(Trigger_mode)
        time.sleep(0.01) #verify if this is necessary
        self.spec.setIntegrationTime(Integration_Time*1000)          # Conversting it to Microseconds
        time.sleep(0.01)
        Spec_Init_Done.value = 1

    def Spec_Speed_Test(self, no_spec_tests):
        '''
        A function for testing the spectrometer speed in free running mode
        '''
        Test_Integration_Time = self.spec.Handle.minimum_integration_time_micros/float(1000)
        Spec_Init_Process(Test_Integration_Time, 0)
        Mean_Time = 0
        #I = 0
        Threshold = 1.2
        while True:
            Start_Time = time.time()
            Spec_Read_Process(no_spec_tests)
            Spec_Index[0] = 0
            '''
            while I < no_spec_tests:
                Scratch_Signal, Mean_Time = self.spec.readIntensity(True, True)
                I = I + 1
            '''
            Duration = (time.time() - Start_Time)*1000
            Mean_Time = Duration/float(no_spec_tests)
            if (Mean_Time < Threshold*float(Test_Integration_Time)):
                print ('Finished. Duration: %f' %Duration)
                print ('Mean time %f' %Mean_Time)
                print ('Test_Integration_Time %f' %Test_Integration_Time)
                break
            else:         # The integration time was not enough for the spectromer so it is increased by 0.5 portion of the minimum integration time
                print ('Mean time %f' %Mean_Time)
                print ('Test_Integration_Time %f' %Test_Integration_Time)
                print ('Duration: %f' %Duration)
                Test_Integration_Time = Test_Integration_Time + self.spec.Handle.minimum_integration_time_micros/float(2000)
                Spec_Init_Process(Test_Integration_Time, 0)
                #I = 0

        print ('Spectrometer minimum integration time is %f ms and the practical minimum integration time is %f ms \n' %(self.spec.Handle.minimum_integration_time_micros/float(1000), Test_Integration_Time))

        return Test_Integration_Time

    def Spec_Read_Process(self, no_spec_sample, start_wavelength, end_wavelength):
        '''
        Reads specified no. samples between a wavelength range, returns a 2D array.
        '''
        min_wave_index = max(bisect.bisect(self.wavelengths, float(start_wavelength)-1), 0)
        max_wave_index = bisect.bisect(Wavelengths, float(end_wavelength))
        wavelengths = self.wavelengths[min_wave_index : max_wave_index]
        wave_len = len(wavelengths)
        records = np.zeros(shape=(wave_len, No_Spec_Sample ), dtype = float )
        
        for i in range(no_spec_sample):
            a,b = self.spec.readIntensity(True, True)
            records[Spec_Index[0]*Wave_len : (Spec_Index[0] + 1)*Wave_len] = a[Min_Wave_Index:Max_Wave_Index]
            Spec_Time[Spec_Index[0]] = b
            Spec_Index[0] = Spec_Index[0] + 1
            Spec_Is_Read.value = 1