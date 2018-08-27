
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import SeaBreeze_Objective as SBO
import DAQT7_Objective as DAQ
import bisect

Spec = SBO.DetectSpectrometer()
Spec.setTriggerMode(0)
Spec.setIntegrationTime(40000)
WaveLength = Spec.readWavelength()

DAQ1 = DAQ.DetectDAQT7()
shut_port = "DAC0"
PhotoDiod_Port = "AIN1"
DAQ1.writePort(shut_port, 5)
def update_line(num, data, line):
    line.set_data(WaveLength,Spec.readIntensity(True, True)[0])
    print(max(Spec.readIntensity(True, True)[0]))
    return line,

fig1 = plt.figure()

data = np.random.rand(2, 25)
l, = plt.plot([], [])

#plt.xlim(0, 1100)
#plt.ylim(0, 16000)
plt.axis([450, 650, 0, 10000])
plt.grid()
plt.xlabel('Wavelength (nm)')
plt.ylabel("Intensity (Arb. Units)")
plt.title('Live Spectrometer Feed')
try:
	line_ani = animation.FuncAnimation(fig1, update_line, frames=60, fargs=(data, l), interval=1, blit=True)
except KeyboardInterrupt:
	DAQ1.writePort(shut_port, 0)
	DAQ1.close()
	Spec.close()
# To save the animation, use the command: line_ani.save('lines.mp4')
timeLimit = 100
DAQSIG = np.zeros(timeLimit)
DAQT = np.arange(0,timeLimit)


fig2 = plt.figure()
def update_line2(num, data, line):
	DAQ_Signal, DAQ_Time = DAQ1.readPort(PhotoDiod_Port)
	#print(DAQ_Signal,DAQ_Time)
	DAQSIG[num] = DAQ_Signal
	#count+=1
	line.set_data(DAQT,DAQSIG)
	return line,
count=0
z, = plt.plot([], [])

#plt.xlim(0, 1100)
#plt.ylim(0, 16000)
plt.axis([0, timeLimit, -1, 5])
plt.xlabel('Time')
plt.ylabel("Voltage (V)")
plt.title('PhotoDiode Live Voltage')
line_ani2 = animation.FuncAnimation(fig2, update_line2, np.arange(0, timeLimit), fargs=(data, z), interval=1, blit=True)
plt.show()
