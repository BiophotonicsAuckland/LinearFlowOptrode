# Uncomment the next two lines if you want to save the animation
#import matplotlib
#matplotlib.use("Agg")

import numpy
from matplotlib.pylab import *
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.animation as animation
import SeaBreeze_Objective as SBO
import DAQT7_Objective as DAQ

Spec = SBO.DetectSpectrometer()
Spec.setTriggerMode(0)
Spec.setIntegrationTime(40000)

DAQ1 = DAQ.DetectDAQT7()
shut_port = "DAC0"
PhotoDiod_Port = "AIN1"
DAQ1.writePort(shut_port, 5)


# Sent for figure
font = {'size':9}
matplotlib.rc('font', **font)

# Setup figure and subplots
fig1 = figure(num = 0, figsize = (12, 8))
fig1.suptitle("Live Data for Alignment", fontsize=12)
ax01 = subplot2grid((2, 1), (0, 0))
ax02 = subplot2grid((2, 1), (1, 0))

# Data Update
xmin = 0.0
xmax = 200.0

# Set x-limits
ax01.set_xlim(xmin, xmax)
ax02.set_xlim(300, 900)

# Set y-limits
ax01.set_ylim(0, 6)
ax02.set_ylim(-500, 10000)

# Turn on grids
ax01.grid(True)
ax02.grid(True)

# Set label names and titles
ax01.set_title("Live Spectrometer Feed")
ax01.set_xlabel("Wavelength (nm)")
ax01.set_ylabel("Intensity (unit)")

ax02.set_title("Photodiode Feed")
ax02.set_xlabel("Voltage (V)")
ax02.set_ylabel("Time (unit)")

# Data Placeholders
DAQdata = zeros(0)
yv1 = zeros(0)
t = zeros(0)
x = 0.0

# Set plots
p011, = ax01.plot(t,DAQdata,'b-', label="DAQdata")
p021, = ax02.plot(t,yv1,'b-', label="haha")

WaveLengths = Spec.readWavelength()

def updateData(self):
	global x
	global DAQdata
	global t

	specData = Spec.readIntensity(True, True)[0]
	newDAQ,_ = DAQ1.readPort(PhotoDiod_Port)

	DAQdata = append(DAQdata, newDAQ)
	t = append(t,x)

	x += 1

	p011.set_data(t,DAQdata)
	p021.set_data(WaveLengths, specData)

	if x >= xmax*0.8:
		p011.axes.set_xlim(x-xmax*0.8, x+xmax*0.2)
	p021.axes.set_ylim(1.2*np.amin(specData), 1.2*np.amax(specData))

	return p011, p021

simulation = animation.FuncAnimation(fig1, updateData, blit=False, interval=20, repeat=False)

# Uncomment the next line if you want to save the animation
#simulation.save(filename='sim.mp4',fps=30,dpi=300)

plt.show()
