import SeaBreeze_Objective as SBO
import matplotlib.pyplot as plt
import DAQT7_Objective as DAQ

DAQ1 = DAQ.DetectDAQT7()
Spec = SBO.DetectSpectrometer()

Spec.setTriggerMode(0)                                      
Spec.setIntegrationTime(40000)   #100000 Not sure what amount of time this corresponds to                      

WaveLength = Spec.readWavelength()
Time_Index =[]                                          
Intensities = []

plt.axis([300, 900, -500, 30000])
plt.ion()
plt.xlabel('WaveLength')
plt.ylabel('Intensity')
shut_port = "DAC0"
DAQ1.writePort(shut_port, 5)

try:
    while True:
        Intensities, Time_Index =  Spec.readIntensity(True, True)
        
        plt.plot(WaveLength, Intensities)
        plt.pause(0.001)
        plt.clf()
        print(max(Intensities))
        
except KeyboardInterrupt:
    print("Exiting")
    DAQ1.writePort(shut_port, 0)
    Spec.close()
