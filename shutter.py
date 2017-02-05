#This code allows control of only the shutter.

import DAQT7_Objective as DAQ
shut_port = "DAC0"
DAQ1 = DAQ.DetectDAQT7()
print("Enter 1 to open the shutter, 0 to close. q to quit which closes the shutter too.")
while True:
	user_in = raw_input("\n>: ")
	if user_in == "1":
		DAQ1.writePort(shut_port,5)
	elif user_in =="0":
		DAQ1.writePort(shut_port,0)
	elif user_in == "q":
		DAQ1.writePort(shut_port,0)
		break
