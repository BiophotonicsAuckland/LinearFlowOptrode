# Optrode Codes

This Repo contains modifications/additions to the Optrode Code created by YJonmo, the original work is located at the following repo: https://github.com/YJonmo/PhysicsLabPythonCodes

## Align 2
This program simply plots photodiode and the spectra in real time, fixed axis that is changeable in the source.

## Optrode Version 4.1.py
Author: 
This program can measure spectra at specified integration time for specified recording time alone with other sensor data stored in hdf5 file. This also has an align feature with slightly different y axis functionality.

## Data_process.py
This script processes a series of hdf5 files produced from optrodev4, takes in a background hdf5 file and a series of experiment data to plot spectra, calculate background avg, subtract, replot and also plotting fluorenscence over time.

## Fix Shutter
This script just forces the shutter to close in the case the program leaves the shutter open after closing/crashing.

