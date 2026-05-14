# -*- coding: utf-8 -*-
"""
@author: Francois
"""

'''
Communication with differential pressure SENSORS.
The sensor must be connected to an arduino see doc : 
'''


import serial
import time as time
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#from lab import *


def acquisition(PRESSURE_COM_PORT = '/dev/ttyACM1', baud_rate = 9600, timeout=10, timestep = 0.9):
    
    
    pressure_board = serial.Serial( PRESSURE_COM_PORT , baudrate = baud_rate, timeout = timeout )   
    time.sleep(0.1)
    
    a = balance('Explorer35','/dev/ttyUSB0')

    
    
    
    fname='piezoData'
    
    output_data_file = './' + fname + '_' + str(int(time.time())) + '.csv'
       
    start = time.time() 
    
    ################ Initiate data file
    
    header = "loop,time,pressure,mass\n"
    
    
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
                valWa,bytesread=a.GetWeight()
    
                output_data =  str(loop_count)+ ',' + str(t) + "," +  str( pressure_digit)+ ","  + str(valWa)  + "\n"
                
                with open( output_data_file, 'a') as output_file:
                    output_file.write( output_data)    
    
                print( output_data )
                
    
            except: 
                print("communication with arduino failed")
        
            time.sleep(timestep)
            loop_count += 1
    
    
    pressure_board.close() 


def pressure_acquisition(PRESSURE_COM_PORT = '/dev/ttyACM0', baud_rate = 9600, timeout=10, timestep = 0.9):

    pressure_board = serial.Serial( PRESSURE_COM_PORT , baudrate = baud_rate, timeout = timeout )   
    time.sleep(0.1)
    
    
    fname='MariotteData'
    
    output_data_file = './' + fname + '_' + str(int(time.time())) + '.csv'
       
    start = time.time() 
    
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
               
                output_data =  str(loop_count)+ ',' + str(t) + "," +  str( pressure_digit) + "\n"
                
                with open( output_data_file, 'a') as output_file:
                    output_file.write( output_data)    
    
                print( output_data )
                
    
            except: 
                print("communication with arduino failed")
        
            time.sleep(timestep)
            loop_count += 1
    
    
    pressure_board.close() 
    

def reservoir_weight_control(fname, dt = 300):
    """
    tracks the weight of the reservoir and stores data in file fname
    input: fname name of the file in which to store the data
    
    Parameters
    ----------
        fname: string, output filename
        dt: int, default=300s, time interval in seconds
    """

    a = balance('Explorer35','/dev/ttyUSB0')

    #~ plt.ion()
    #~ fig = plt.figure()
    #~ ax = fig.add_subplot(111)
    #~ fig.canvas.draw()
    f=open(fname,'w')
    f.write('T,M\n')
    f.close()
    
    #~ valWa,bytesread=a.GetWeight()
    #~ listTot=[]
    while 1:
        #~ valList=[]
        #~ for i in range(5):        
        valWa,bytesread=a.GetWeight()
        #~ time.sleep(1)
            #~ if valWa>=0:
                #~ valList.append(valWa)
            #~ print( valWa )
        
        t=time.time()
        #~ print( t, np.mean(valList), np.std(valList) )
        print( t, valWa )
        #~ plt.plot(t,np.mean(valList),'ro')
        f=open(fname,'a')
        #~ f.write('%f,%f\n' % (t,np.mean(valList)))
        f.write('%f,%f\n' % (t,valWa))
        #~ listTot.append(np.mean(valList))
        f.close()
        #~ plt.title("%.3f; %.3f" % (np.mean(listTot), np.std(listTot)))
        #~ fig.canvas.draw()
        time.sleep(dt)    

def plot_reservoir(fname):
    """
    Plot reservoir data from file fname
    """
    
    dfl=pd.read_csv(fname)
    df = dfl[dfl['T']>0]

    plt.figure()
    plt.plot(df['T'],df['M'],'-')
    plt.xlabel('Time (s)')
    plt.ylabel('Mass (kg)')
    
    
    T = np.array(df[df['M']>0]['T'].tolist())
    M = np.array(df[df['M']>0]['M'].tolist())
    
    c = np.polyfit(T,M,1) # M = c[0]*T + c[1]
    p = np.poly1d(c) # cree la fonction p(x) = C[0]*x + c[1]
    
    print(p(5))
    Ttot = np.array(df['T'].tolist())
    
    plt.plot(Ttot,p(Ttot),'r--')
    
    print(c)
    
    A = (8*2.54*10)**2 * np.pi / 4
    VR = -1 * c[0] * 1000 * 1000 * 60
    RR = VR/A
    print(A,VR,RR)
    dm = -1*np.diff(np.array(M))
    #~ print(dm)
    
    moy=[]
    c=0
    for m in dm:
        if m > 2e-3 and m < 0.1:
            moy.append(m)
            
    #~ print(moy)
    print(np.mean(moy))
    

    
def plot_calib(fname, D=0.09):
    """
    Plot reservoir data from file fname
    """
    
    df=pd.read_csv(fname)
    
    
    A = D**2 * np.pi / 4 #m2
    VolMass = 1e-3 #m3/kg
    m_to_mm = 1e3
    plt.figure()
    plt.plot(df['pressure'],df['mass'] * VolMass / A * m_to_mm ,'-')
    plt.xlabel('Pressure')
    plt.ylabel('Height (mm)')
    
    

    plt.show()
    

if __name__ == '__main__':
    # reservoir_weight_control("Mariotte3.txt", 30)
    # plot_reservoir("Mariotte3.txt")
    acquisition()
    # fname="piezoData_1751303674.csv"
    # plot_calib(fname)
    
