# -*- coding: utf-8 -*-
"""
This is a small GUI to read the files.
@author: Yaqub Jonmohamadi
"""

from Tkinter import Tk
from tkFileDialog import askopenfilename

import os.path

#Path_to_Fred_Codes = os.path.abspath(os.path.join( os.getcwd(), os.pardir))
#os.chdir(Path_to_Fred_Codes)
#os.chdir(Path_to_Records)
#File_name2 = File_name + "Bead" + str('%s' %CroppIndex)+ ".jpg"
#File_name = File_name_PreFix + '-' + File_name_Suffix    
class Input_Window:
    def __init__(self):
        self.CurrentAddress = os.path.abspath(os.path.join( os.getcwd()))
    def get_address(self):
        os.chdir(os.path.abspath(os.path.join( os.getcwd(), os.pardir)))
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        self.filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
        os.chdir(self.CurrentAddress)  
        return self.filename
