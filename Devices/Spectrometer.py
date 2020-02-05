"""Develop edition, porting original code hopefully to python3, and making it less spaghetti"""

import Devices.req.SeaBreeze_Objective as SBO

class Spectrometer:

    def __init__(self):
        self.device = SBO.DetectSpectromter()
        self.wavelengths = self.device.readWavelength()
    
    def spec_init_process(self, integration_time, trigger_mode):
        '''
        A function for initializing the spectrometer (integration time and triggering mode
        Integration_Time is given in milliseconds
        '''
        self.device.setTriggerMode(trigger_mode)
        time.sleep(0.01) #verify if this is necessary
        self.device.setIntegrationTime(integration_Time*1000)          # Conversting it to Microseconds
        time.sleep(0.01)


    def spec_speed_test(self, no_spec_tests):
        '''
        A function for testing the spectrometer speed in free running mode, 
        THIS FUNCTION HAS NOT BEEN REWRITTEN, WILL NOT WORK WITHOUT MODIFICATION
        '''
        Test_Integration_Time = self.device.Handle.minimum_integration_time_micros/float(1000)
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
                Test_Integration_Time = Test_Integration_Time + self.device.Handle.minimum_integration_time_micros/float(2000)
                Spec_Init_Process(Test_Integration_Time, 0)
                #I = 0

        print ('Spectrometer minimum integration time is %f ms and the practical minimum integration time is %f ms \n' %(self.device.Handle.minimum_integration_time_micros/float(1000), Test_Integration_Time))

        return Test_Integration_Time

    def spec_read_process(self, no_spec_sample, min_wave_index, max_wave_index,  spec_data_array, spec_time_array):
        '''
        Reads specified no. samples between a wavelength range
        '''

        records = np.zeros(shape=(wave_len, No_Spec_Sample ), dtype = float )
        
        for i in range(no_spec_sample):
            a,b = self.device.readIntensity(True, True)
            spec_data_array[i,:] = a[min_wave_index:max_wave_index]
            spec_time_array = b