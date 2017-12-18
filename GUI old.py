import socket
import subprocess
import time
import struct
import os
import sys
import tempfile
import glob
from multiprocessing import Process, Value
from Tkinter import Tk, Text, BOTH, W, N, E, S, RAISED, Frame, Message, LEFT, TOP, BOTTOM, DISABLED, NORMAL, PhotoImage, StringVar, Toplevel
from ttk import Button, Style, Label, Entry, Notebook, Scale
from tkFileDialog import askopenfilename
from PIL import Image, ImageTk
from datetime import datetime

class GUI:

    def __init__(self):
        self.root = Tk()
        self.root.geometry("400x500+150+150")

        self.initVars()

        self.initUI()

        self.root.mainloop()


    def initVars(self):
        self.filename = StringVar(value="")
        self.record_time = StringVar(value="300")
        self.int_time = StringVar(value="15")
        self.min_freq = StringVar(value="500")
        self.max_freq = StringVar(value="600")

    def initUI(self):

        small_entry = 6
        large_entry = 19

        self.root.grid_columnconfigure(0, weight=1)

        ##### Title frame #####
        self.frame1 = Frame(self.root)
        self.frame1.grid(row=0, column=0)

        self.title = Label(self.frame1, text="Linear Flow Fluorescense", font=(None, 13))
        self.title.grid(row=0, column=1, padx=10, pady=10)


        ##### Parameter frame #####
        self.frame2 = Frame(self.root, relief=RAISED, borderwidth=1)
        self.frame2.grid(row=1, column=0, padx=4, pady=4)

        rowfn = 2   # Filename row
        rowrd = 3   # Recording duration row
        rowit = 4   # Integration time row
        rowwr = 5   # Wavelength range row

        self.fnlbl = Label(self.frame2, text="Select Filename", font=(None, 11))
        self.fnlbl.grid(row=rowfn, column=1, padx=6, pady=6, sticky=E)
        self.fntxt = Entry(self.frame2, textvariable=self.filename, width=large_entry)
        self.fntxt.grid(row=rowfn, column=2, padx=6, pady=6, columnspan=3)

        self.rdlbl = Label(self.frame2, text="Recording duration (s)", font=(None, 11))
        self.rdlbl.grid(row=rowrd, column=1, padx=6, pady=6, sticky=E)
        self.rdtxt = Entry(self.frame2, textvariable=self.record_time, width=large_entry)
        self.rdtxt.grid(row=rowrd, column=2, padx=6, pady=6, columnspan=3)

        self.itlbl = Label(self.frame2, text="Integration time (ms)", font=(None, 11))
        self.itlbl.grid(row=rowit, column=1, padx=6, pady=6, sticky=E)
        self.ittxt = Entry(self.frame2, textvariable=self.int_time, width=large_entry)
        self.ittxt.grid(row=rowit, column=2, padx=6, pady=6, columnspan=3)

        self.wrlbl = Label(self.frame2, text="Wavelength range (nm)", font=(None, 11))
        self.wrlbl.grid(row=rowwr, column=1, padx=6, pady=6, sticky=E)
        self.wrtxt = Entry(self.frame2, textvariable=self.min_freq, width=small_entry)
        self.wrtxt.grid(row=rowwr, column=2, padx=6, pady=6)
        self.wrlbl = Label(self.frame2, text="to", font=(None, 11))
        self.wrlbl.grid(row=rowwr, column=3, padx=0, pady=6, sticky=E)
        self.wrtxt = Entry(self.frame2, textvariable=self.max_freq, width=small_entry)
        self.wrtxt.grid(row=rowwr, column=4, padx=6, pady=6)


        ##### Button frame #####
        self.frame3 = Frame(self.root, relief=RAISED, borderwidth=1)
        self.frame3.grid(row=2, column=0)

        self.but1 = Button(self.frame3, text="Prepare")
        self.but1.grid(row=1, column=1)

        self.but1 = Button(self.frame3, text="Begin")
        self.but1.grid(row=1, column=2)

haha = GUI()
