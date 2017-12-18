# PhysicsLabPythonCodes
This repository is for devices used in the physics lab such as Spectrometers, DAQ card or P100 power meter.


Just to clarify that in above repository there are two types of codes: 1) library codes which are necessary to be used in any codes written for the spectrometer or other devices and 2) example codes which shows how the library codes are used.

The library codes include: DAQT7_Objective.py, SeaBreeze_Objective.py and ThorlabsPM100_Objective.py.

The example codes include: Spectrometer_Reader.py, DAQT7_AnalogueToDigitalReading.py,  ThorelabsPM100_PowerReader.py and Simultaneous_PM100_Spec_DAQ_Reading.py. The last code (as the names says) is for reading all the three devices simultaneously. Theses 4 codes are examples to show how to: 1) use the devices, 2) plot their output and 3) save the data in HDF5 format. You can use them as templates for your work and modify them, I can help you when you have problems.

To run the above codes (example Spectrometer_Reader.py):
1) Download them and put them in your working space
2) Open a terminal and use 'cd' to navigate to the directory where the codes are
3) type 'python Spectrometer_Reader.py' to run Spectrometer_Reader.py

You can also use below steps instead of step 3:
3) type 'ipython --pylab' on the terminal (which takes you to the ipython environment)
4) type '%run Spectrometer_Reader.py' to run the code. 
