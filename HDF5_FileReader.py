# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 16:25:43 2016

@author: yjon701
"""

import h5py
import matplotlib.pyplot as plt
import Get_File_Path as GetFile


class HDF5_Data:
    def __init__(self, Data):
        #self.data = Data
        if   len((Data).keys()) == 3:
            print('Optrode version 1 (old)')
            self.allocator(Data)
        elif len(Data.keys()) == 2:
            print('Optrode version 2 (new)')
            self.allocator(Data)
                  
    def allocator(self, Data):                          # This function creats the variable from the loaded data set
        print('\nYour variables are \'Splitted_Data.\' + following attributes: \n')
        for I  in range(len(Data.keys())):
            for II in range(len(Data[Data.keys()[I]].keys())):
                exec((Data.keys()[I] + '_' + Data[Data.keys()[I]].keys()[II]) + "=Data[Data.keys()[I]].values()[II]")   
                setattr(self, Data.keys()[I] + '_' + Data[Data.keys()[I]].keys()[II], Data[Data.keys()[I]].values()[II])
                print(Data.keys()[I] + '_' + Data[Data.keys()[I]].keys()[II])


def GUI_GetData():
    Record = GetFile.Input_Window()
    Record_address = Record.get_address()
    Data = h5py.File(Record_address,'r')
    return Data



if __name__ == "__main__":


    Data = GUI_GetData()
    Splitted_Data = HDF5_Data(Data)
    
    # sample demonstration of the data   
    # plt.figure()    
    # plt.plot(Splitted_Data.DAQT7_PhotoDiode) 
    
    
