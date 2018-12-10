# Optrode Codes

This Repo contains programs used to interface the linear flow setup's hardware to take measurements, align and process data generated. Uses previously written code from the original work is located at the following repo: https://github.com/YJonmo/PhysicsLabPythonCodes

## Align 2
This program simply plots photodiode and the spectra in real time, fixed axis that is changeable in the source. 

## Optrode Version 4.2.py
Authors: YJonmo (original CLI version), Olivier G (GUI additions), Liam Murphy (Minor design and feature additions)
This program interfaces a spectrometer, DAC card and shutter. Records spectroscopic data into hdf5 file.
Has several requisite class files stored in /req/.

## Data_process3.py
This script processes a series of hdf5 files produced from optrodev4.2.
Requires a background and primary measurements to calculate background avg, subtraction calibration, simpsons integration.
Can optionally output a series of plots for each of these features. 

## Shutter.py
This script lets you just open/close the shutter for power measurements or photobleaching.


