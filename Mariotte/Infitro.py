# -*- coding: utf-8 -*-
"""
@author: Francois
"""

'''
Communication with SENO343 differential pressure SENSOR.
The sensor must be connected to an arduino see doc : 
'''


import serial
import time as time
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def infiltration():
    ################ PARAMETERS
    
    timestep = 0.9 # acquisition time step (s)
    
    PRESSURE_COM_PORT = 'COM8'

    timeout=10
    baud_rate = 9600
    
    
    pressure_board = serial.Serial( PRESSURE_COM_PORT , baudrate = baud_rate, timeout = timeout )   
    time.sleep(0.1)
    print("Board connected")
    
    fname='InfiltrationMayotte'
    
    output_data_file = '../data/' + fname + '_' + str(int(time.time())) + '.csv'
       
    start = time.time() 
    print(start)
    ################ Initiate data file
    
    header = "loop,time,pressure\n"
    
    
    with open( output_data_file, 'w') as output_file:
        output_file.write(header)    

    if pressure_board:
    
        loop_count = 0
    
        while True :
              
            try:
                pressure_board.flushInput()
                time.sleep(0.1)
                
                t = time.time() - start
                
                pressure_digit = int(pressure_board.readline().decode())
                
                output_data =  str(loop_count)+ ',' + str(t) + "," +  str( pressure_digit)+"\n"
                
                with open( output_data_file, 'a') as output_file:
                     output_file.write( output_data)    
    
                print( output_data )
                
    
            except: 
                print("communication with arduino failed")
        
            time.sleep(timestep)
            loop_count += 1
    
    
    pressure_board.close() 
    
if __name__ == '__main__':
	infiltration()
	
	
