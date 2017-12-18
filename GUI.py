import socket
import subprocess
import time
import struct
import os
import sys
import tempfile
import glob
import datetime
import time
from multiprocessing import Process, Value, Array
from Tkinter import Tk, Text, BOTH, W, N, E, S, RAISED, Frame, Message, LEFT, TOP, BOTTOM, DISABLED, NORMAL, PhotoImage, StringVar, Toplevel
from ttk import Button, Style, Label, Entry, Notebook, Scale
from tkFileDialog import askopenfilename
from PIL import Image, ImageTk

import h5py
import DAQT7_Objective as DAQ
import SeaBreeze_Objective as SBO
import ThorlabsPM100_Objective as P100
import numpy as np
import matplotlib.pyplot as plt
import os.path

def setup():

    # Check that parameters are appropriate
    Spec1 = SBO.DetectSpectrometer()
    DAQ1 = DAQ.DetectDAQT7()

    MIN_INT_TIME = 2
    MAX_INT_TIME = 2000
    MIN_REC_TIME = 10
    MAX_REC_TIME = 3600
    MIN_WAVE_LEN = 100
    MAX_WAVE_LEN = 1000

    if Spec1.Error == 1:
        print("ERROR: Cession failed, could not detect spectrometer.")
        error_msg.set("ERROR: Cession failed, could not detect spectrometer.")
    elif DAQ1.Error == 1:
        print("ERROR: Cession failed, could not detect DAQ.")
        error_msg.set("ERROR: Cession failed, could not detect DAQ.")
    elif not is_number(int_time.get()):
        print("ERROR: Integration duration is not a number.")
        error_msg.set("ERROR: Integration duration is not a number.")
    elif int(int_time.get()) < MIN_INT_TIME:
        print("ERROR: Integration duration is smaller than " + str(MIN_INT_TIME) + ".")
        error_msg.set("ERROR: Integration duration is smaller than " + str(MIN_INT_TIME) + ".")
    elif int(int_time.get()) > MAX_INT_TIME:
        print("ERROR: Integration duration is greater than " + str(MAX_INT_TIME) + ".")
        error_msg.set("ERROR: Integration duration is greater than " + str(MAX_INT_TIME) + ".")
    elif not is_number(rec_time.get()):
        print("ERROR: Recording duration is not a number.")
        error_msg.set("ERROR: Recording duration is not a number.")
    elif int(int_time.get()) < MIN_REC_TIME:
        print("ERROR: Recording duration is smaller than " + str(MIN_REC_TIME) + ".")
        error_msg.set("ERROR: Recording duration is smaller than " + str(MIN_REC_TIME) + ".")
    elif int(int_time.get()) > MAX_REC_TIME:
        print("ERROR: Recording duration is greater than " + str(MAX_REC_TIME) + ".")
        error_msg.set("ERROR: Recording duration is greater than " + str(MAX_REC_TIME) + ".")
    elif not is_number(min_len.get()):
        print("ERROR: Minimum wavelength is not a number.")
        error_msg.set("ERROR: Minimum wavelength is not a number.")
    elif int(min_len.get()) < MIN_WAVE_LEN:
        print("ERROR: Minimum wavelength is smaller than " + str(MIN_WAVE_LEN) + ".")
        error_msg.set("ERROR: Minimum wavelength is smaller than " + str(MIN_WAVE_LEN) + ".")
    elif int(min_len.get()) > MAX_WAVE_LEN:
        print("ERROR: Minimum wavelength is greater than " + str(MAX_WAVE_LEN) + ".")
        error_msg.set("ERROR: Minimum wavelength is greater than " + str(MAX_WAVE_LEN) + ".")
    elif not is_number(max_len.get()):
        print("ERROR: Maximum wavelength is not a number.")
        error_msg.set("ERROR: Maximum wavelength is not a number.")
    elif int(min_len.get()) < MIN_WAVE_LEN:
        print("ERROR: Maximum wavelength is smaller than " + str(MIN_WAVE_LEN) + ".")
        error_msg.set("ERROR: Maximum wavelength is smaller than " + str(MIN_WAVE_LEN) + ".")
    elif int(min_len.get()) > MAX_WAVE_LEN:
        print("ERROR: Maximum wavelength is greater than " + str(MAX_WAVE_LEN) + ".")
        error_msg.set("ERROR: Maximum wavelength is greater than " + str(MAX_WAVE_LEN) + ".")
    elif int(min_len.get()) >= int(max_len.get()):
        print("ERROR: Minimum wavelength is smaller than maximum wavelength.")
        error_msg.set("ERROR: Minimum wavelength is smaller than maximum wavelength.")

    else:

        print "STARTING..."
        # Start Process
        if filename.get() == "":
            filename.set("OptrodeData")

        Green_Shutter = "DAC0"
        Blue_Shutter = "DAC1"

        DAQ1.writePort(Green_Shutter, 0)
        DAQ1.writePort(Blue_Shutter, 0)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

if __name__ == "__main__":

    # Creating GUI
    root = Tk()
    root.geometry("400x500+150+150")
    root.grid_columnconfigure(0, weight=1)

    # Setting variables
    filename = StringVar(value="")      # Filename of output data
    int_time = StringVar(value="15")    # Integration time of spectrometer (ms)
    rec_time = StringVar(value="300")   # Recording duration of spectrometer (s)
    min_len = StringVar(value="500")    # Minimum wavelength to record (nm)
    max_len = StringVar(value="600")    # Maximum wavelength to record (nm)

    error_msg = StringVar(value=" ")

    small_entry = 6
    large_entry = 19

    # Title frame
    frame1 = Frame(root)
    frame1.grid(row=0, column=0)

    title = Label(frame1, text="Linear Flow Fluorescense", font=(None, 13))
    title.grid(row=0, column=1, padx=10, pady=10)

    # Parameter frame
    frame2 = Frame(root, relief=RAISED, borderwidth=1)
    frame2.grid(row=1, column=0, padx=4, pady=4)

    rowfn = 1   # Filename row
    rowrd = 2   # Recording duration row
    rowit = 3   # Integration time row
    rowwr = 4   # Wavelength range row
    rower = 5   # Error message row

    fnlbl = Label(frame2, text="Select Filename", font=(None, 11))
    fnlbl.grid(row=rowfn, column=1, padx=6, pady=6, sticky=E)
    fntxt = Entry(frame2, textvariable=filename, width=large_entry)
    fntxt.grid(row=rowfn, column=2, padx=6, pady=6, columnspan=3)

    rdlbl = Label(frame2, text="Recording duration (s)", font=(None, 11))
    rdlbl.grid(row=rowrd, column=1, padx=6, pady=6, sticky=E)
    rdtxt = Entry(frame2, textvariable=rec_time, width=large_entry)
    rdtxt.grid(row=rowrd, column=2, padx=6, pady=6, columnspan=3)

    itlbl = Label(frame2, text="Integration time (ms)", font=(None, 11))
    itlbl.grid(row=rowit, column=1, padx=6, pady=6, sticky=E)
    ittxt = Entry(frame2, textvariable=int_time, width=large_entry)
    ittxt.grid(row=rowit, column=2, padx=6, pady=6, columnspan=3)

    wrlbl = Label(frame2, text="Wavelength range (nm)", font=(None, 11))
    wrlbl.grid(row=rowwr, column=1, padx=6, pady=6, sticky=E)
    wrtxt = Entry(frame2, textvariable=min_len, width=small_entry)
    wrtxt.grid(row=rowwr, column=2, padx=6, pady=6, sticky=W)
    wrlbl = Label(frame2, text="to", font=(None, 11))
    wrlbl.grid(row=rowwr, column=3, padx=0, pady=6)
    wrtxt = Entry(frame2, textvariable=max_len, width=small_entry)
    wrtxt.grid(row=rowwr, column=4, padx=6, pady=6, sticky=E)

    erlbl = Message(frame2, width=340, textvariable=error_msg, font=(None, 11))
    erlbl.grid(row=rower, column=1, columnspan=4)

    # Button frame
    frame3 = Frame(root, relief=RAISED, borderwidth=1)
    frame3.grid(row=2, column=0)

    but1 = Button(frame3, text="Setup", command=setup)
    but1.grid(row=1, column=1)

    but1 = Button(frame3, text="Start", command=lambda: start)
    but1.grid(row=1, column=2)

    root.mainloop()
