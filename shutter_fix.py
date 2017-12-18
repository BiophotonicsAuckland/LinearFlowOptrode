#This code closes the shutter if it gets stuck open
import DAQT7_Objective as DAQ
shut_port = "DAC0"
DAQ1 = DAQ.DetectDAQT7()
DAQ1.writePort(shut_port, 0)
