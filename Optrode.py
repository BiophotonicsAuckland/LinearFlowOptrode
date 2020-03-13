#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rewrite of originally spaghetti.

"""
import sys, os

    
from Devices.Spectrometer import Spectrometer
from Devices.DAQ import DAQ

import matplotlib, socket, subprocess, struct, tempfile, glob, datetime, time, bisect, os.path, h5py
from multiprocessing import Process, Value, Array
import numpy as np
import tkinter as tk
from GUI import View

time_start =  time.time()

BLUE_LASER = "FIO1"
BLUE_SHUTTER = "DAC0"
PhotoDiod_Port = "AIN1"

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def close(root, DAQ1, Spec1):
    try:
  
            DAQ1.close()
            Spec1.close()
    except:
        print("Failed to close devices properly, please replug them")
    finally:
        root.destroy()

class Observable:
    def __init__(self, initial_value=None):
        self.data = initial_value
        self.callbacks = {}

    def add_callback(self, func):
        self.callbacks[func] = 1

    def del_callback(self, func):
        del self.callback[func]

    def _do_callbacks(self):
        for func in self.callbacks:
             func(self.data)

    def set(self, data):
        self.data = data
        self._do_callbacks()

    def get(self):
        return self.data

    def unset(self):
        self.data = None

class DeviceIOError(Exception):
    pass
    
class InvalidUserInput(Exception):
    pass
    
class Model:

    def __init__(self, view_settings):
    
        self.settings = {
            "directory": Observable(),
            "filename": Observable(),
            "bool_suffix": Observable(),
            "int_time": Observable(),
            "rec_time": Observable(),
            "min_wav" : Observable(),
            "max_wav" : Observable()
        }
        
        for key, val in view_settings.items():
            self.settings[key].set(val)
        
        self.status = Observable("")
        self.spec = Spectrometer()
        self.daq = DAQ(BLUE_SHUTTER)
        
        
    def start_test(self):
        
        self.status.set("Setting Up...")
        
        self.spec.spec_init_process(self.settings["int_time"].get(), 0)
        
        self.wavelengths = self.spec.device.readWavelength()
        min_wave_index = max(bisect.bisect(self.wavelengths, float(self.settings["min_wav"].get())-1), 0)
        max_wave_index = bisect.bisect(self.wavelengths, float(self.settings["max_wav"].get()))
        self.wavelengths = self.wavelengths[min_wave_index:max_wave_index]
        
        """
            import ctypes as c
            import numpy as np
            import multiprocessing as mp

            n, m = 2, 3
            mp_arr = mp.Array(c.c_double, n*m) # shared, can be used from multiple processes
            # then in each new process create a new numpy array using:
            arr = np.frombuffer(mp_arr.get_obj()) # mp_arr and arr share the same memory
            # make it two-dimensional
            b = arr.reshape((n,m)) # b and arr share the same memory
        """
        #https://stackoverflow.com/questions/44704086/eoferror-ran-out-of-input-inside-a-class
        
        no_spec_samples = int(1000*float(self.settings["rec_time"].get())/float(self.settings["int_time"].get()))
        spectrum_data = Array('d', np.zeros(shape=(no_spec_samples* len(self.wavelengths),1), dtype= float))
        spectrum_time_data = Array('d', np.zeros(shape=(no_spec_samples ,1), dtype = float ))
        
        daq_sampling_rate = 1 #Hz, temporary valuem should be determiend by daq speed test somehow
        no_daq_samples = int(float(self.settings["rec_time"].get())*daq_sampling_rate)
        daq_data = Array('d', np.zeros(shape=(no_daq_samples,1), dtype= float))
        daq_time = Array('d', np.zeros(shape=(no_daq_samples,1), dtype = float ))
        
        spec_read_process = Process(target=self.spec.spec_read_process, args=(no_spec_samples, min_wave_index, max_wave_index, spectrum_data, spectrum_time_data ))
        daq_read_process = Process(target=self.daq.DAQ_Read_Process)
        
        self.status.set("Measuring...")
        self.daq.device.writePort(BLUE_SHUTTER, 5)

        #start the two processes 
        spec_read_process.start()
        daq_read_process.start()
        
        
        #finishing code
        self.daq.device.writePort(BLUE_SHUTTER, 0)
        self.save_data(spectrum_data, spectrum_time_data, daq_data, daq_time)
        self.status.set("Complete!")
        
        #pass
		
    def abort_test(self):
        self.status.set("Aborting Measurement...")
        self.daq.device.writePort(BLUE_SHUTTER, 0)
        
           
    def save_data(self, spec_dat, spec_time, daq_dat,daq_time):
        os.chdir(self.settings["directory"])
        
        filename = self.settings["filename"]
        if self.settings["bool_suffix"]:
            filename_suffix = str('%s' %datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))
            filename+= ('-' + filename_suffix)
        
        filename+=".hdf5"
        f = h5py.File(filename, "w")

        # Saving the recorded signals in HDF5 format
        Optrode_DAQ = f.create_group('DAQT7')
        f.create_dataset('DAQT7/PhotoDiode', data = np.asanyarray(DAQ_Signal[:]))
        f.create_dataset('DAQT7/TimeIndex', data = np.asanyarray(DAQ_Time[:]))
        Optrode_DAQ.attrs['DAQT7 Details'] = np.string_(DAQ_Details)

        Optrode_Spectrometer = f.create_group('Spectrometer')
        f.create_dataset('Spectrometer/Intensities', data = np.asanyarray(spec_dat))
        f.create_dataset('Spectrometer/Time_Index', data = np.asanyarray(Spec_Time))
        f.create_dataset('Spectrometer/WaveLength', data = np.asanyarray(Wavelengths))
        Optrode_Spectrometer.attrs['Spectrometer Details'] = np.string_(Spec_Details)

        if (Power_meter.Error == 0):
            Optrode_Power = f.create_group('PM100_PowerMeter')
            f.create_dataset('PM100_PowerMeter/Power', data = np.asanyarray(Power_Signal[:]))
            f.create_dataset('PM100_PowerMeter/TimeIndex', data = np.asanyarray(Power_Time[:]))
            #Optrode_DAQ.attrs['PowerMeter Details'] = np.string_(DAQ_Details)

        f.close()
        
    def validation(self):
        '''
        Test if parameters are appropriate, raises error if not
        '''
        MIN_INT_TIME = 5#Spec1.Handle.minimum_integration_time_micros/1000.0   
        MAX_INT_TIME = 2000
        MIN_REC_TIME = 1
        MAX_REC_TIME = 3600
        MIN_WAVE_LEN = 100
        MAX_WAVE_LEN = 10000

        
        if not is_number(self.settings["int_time"].get()):
            raise InvalidUserInput("ERROR: Integration duration is not a number.")
        elif float(self.settings["int_time"].get()) < MIN_INT_TIME:
            raise InvalidUserInput("ERROR: Integration duration is smaller than " + str(MIN_INT_TIME) + ".")
        elif float(self.settings["int_time"].get()) > MAX_INT_TIME:
            raise InvalidUserInput("ERROR: Integration duration is greater than " + str(MAX_INT_TIME) + ".")
        elif not is_number(self.settings["rec_time"].get()):
            raise InvalidUserInput("ERROR: Recording duration is not a number.")
        elif float(self.settings["int_time"].get()) < MIN_REC_TIME:
            raise InvalidUserInput("ERROR: Recording duration is smaller than " + str(MIN_REC_TIME) + ".")
        elif float(self.settings["int_time"].get()) > MAX_REC_TIME:
            raise InvalidUserInput("ERROR: Recording duration is greater than " + str(MAX_REC_TIME) + ".")
        elif not is_number(self.settings["min_wav"].get()):
            raise InvalidUserInput("ERROR: Minimum wavelength is not a number.")
        elif float(self.settings["min_wav"].get()) < MIN_WAVE_LEN:
            raise InvalidUserInput("ERROR: Minimum wavelength is smaller than " + str(MIN_WAVE_LEN) + ".")
        elif float(self.settings["min_wav"].get()) > MAX_WAVE_LEN:
            raise InvalidUserInput("ERROR: Minimum wavelength is greater than " + str(MAX_WAVE_LEN) + ".")
        elif not is_number(self.settings["max_wav"].get()):
            raise InvalidUserInput("ERROR: Maximum wavelength is not a number.")
        elif float(self.settings["min_wav"].get()) < MIN_WAVE_LEN:
            raise InvalidUserInput("ERROR: Maximum wavelength is smaller than " + str(MIN_WAVE_LEN) + ".")
        elif float(self.settings["min_wav"].get()) > MAX_WAVE_LEN:
            raise InvalidUserInput("ERROR: Maximum wavelength is greater than " + str(MAX_WAVE_LEN) + ".")
        elif float(self.settings["min_wav"].get()) >= float(self.settings["max_wav"].get()):
            raise InvalidUserInput("ERROR: Minimum wavelength is smaller than maximum wavelength.")
        elif self.settings["filename"].get() == "":
            raise InvalidUserInput("ERROR: Please specify a filename")
        
        """
        if self.spec.spec.Error == 1:
            raise DeviceIOError("ERROR: Cession failed, could not detect spectrometer.")
        elif DAQ1.Error == 1:
            raise DeviceIOError("ERROR: Cession failed, could not detect DAQ, try unplugging and plugging back in.")
        """
class Controller:

    def __init__(self, root):
        self.model = None
        self.view = View(root)
        self.view.but_start.config(command=self.start_test)
        self.view.but_abort.config(command=self.abort_test)
        
    def set_message(self, msg):
        self.view.error_msg.set(msg)
  
    def get_settings(self):
        dict = {
            "directory": self.view.directory.get(),
            "filename": self.view.filename.get(),
            "bool_suffix": self.view.is_suff.get(),
            "int_time": self.view.int_time.get(),
            "rec_time": self.view.rec_time.get(),
            "min_wav" : self.view.min_len.get(),
            "max_wav" : self.view.max_len.get()
        }
        
        return dict
        
    def start_test(self):
        #Instantiate the model
        self.model = Model(self.get_settings())
        self.model.status.add_callback(self.set_message)
        
        #Validate the input
        try:
            
            self.model.validation()
        except DeviceIOError as e:
            self.set_message(e)#custom exception if spec or daq connection error and or paramter settings:
            return
            
        except InvalidUserInput as e:
            self.set_message(e)
            return
           
         
        #Disable UI
        self.view.toggle_ui(False)
        self.model.start_test()

        
    def abort_test(self):
        pass
        
if __name__ == "__main__":
    root = tk.Tk()
    con = Controller(root)
    root.mainloop()
