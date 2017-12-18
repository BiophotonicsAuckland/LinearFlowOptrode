"""Written by Liam Murphy, Nov 30 2017"""

import h5py
import numpy as np
import matplotlib.pyplot as plt

#Opening HDF5 File
file_dir = "/home/frederique/Desktop/microbead_data/"#"/home/frederique/PhysicsLabPythonCodes/Records/"
f = h5py.File(file_dir+"milliq.hdf5","r")

#Figuring out file structure and accessing spectrometer data
print(f.keys())
spec = f["Spectrometer"]
print(spec.keys())

#Plotting Code, uncomment to see plot, comment to reduce execution time

plt.plot(spec["WaveLength"],spec["Intensities"])#Spec group contains releavant data
plt.xlabel("Wavelength (nm)")
plt.ylabel("Intensity (arb.u)")
plt.title("Emission Spectra")

#plt.savefig("Emission_spec.pdf",format="PDF")

intense = np.array(spec["Intensities"])
wave = np.array(spec["WaveLength"])
avg_intense =np.zeros(intense.shape[0])

#plt.figure(1)

for integration in intense.T:
	avg_intense+=integration
		#print(i.shape)
avg_intense/=intense.shape[1]
plt.plot(wave,avg_intense)#Spec group contains releavant data
plt.xlabel("Wavelength (nm)")
plt.ylabel("Intensity (arb.u)")
plt.title("Emission Spectra")


#Photodiode stuff

daq = f["DAQT7"]
print(daq.keys())
pd = daq["PhotoDiode"]
time = daq["TimeIndex"]
#print(time.index(1.4*10**9))

print(time.shape)
#plt.plot(time,pd)
#shape
while True:
	plt.pause(0.1)
