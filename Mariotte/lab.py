#!/usr/local/bin/python
# coding: utf-8
#
# This work is licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
# http://creativecommons.org/licenses/by-sa/3.0/
#
# 11/04/2012
# F. M�tivier

# libs
# hardware
import serial
from time import sleep
from sys import stdout
from pyfirmata import Arduino, util



class balance:
    """ A simple class to control a weighting device
            specifies the parameters of three common weighting devices
            enables to get the weight using a simple function call
    """
    def __init__(self,bal='Ohaus50',com='/dev/ttyUSB0'):
        """ initilize the scale (balance in french): specify it type and the com port to be used

        Parameters
        ----------
        bal : str, optional
            scale name, by default 'Ohaus50'
        com : str, optional
            com port of the scale, by default '/dev/ttyUSB0'
        """
        self.PortComm=serial.Serial()
        self.PortComm.timeout = 5
        self.PortComm.port=com

        # sets the parameters for acquisition
        # checked for the Ohaus 50 and the Explorer 35
        self.bal=bal
        if self.bal == 'Ohaus50':
            print( self.bal )
            self.PortComm.baudrate = 9600
            self.PortComm.parity = serial.PARITY_NONE
            self.PortComm.stopbits = serial.STOPBITS_TWO
            self.PortComm.bytesize = serial.SEVENBITS
            self.Ordre = "P\r\n" 
            self.Ilength = 8
        elif self.bal=='Explorer35':
            print( self.bal )
            self.PortComm.baudrate = 9600
            self.PortComm.parity = serial.PARITY_NONE
            self.PortComm.stopbits = serial.STOPBITS_TWO
            self.PortComm.bytesize = serial.SEVENBITS
            self.Ordre = "SI\r\n" 
            self.Ilength = 19
        elif self.bal=='Explorer22':
            print( self.bal )
            self.PortComm.baudrate = 9600
            self.PortComm.parity = serial.PARITY_NONE
            self.PortComm.stopbits = serial.STOPBITS_TWO
            self.PortComm.bytesize = serial.SEVENBITS
            self.Ordre = "P\r" 
            self.Ilength = 8
        elif self.bal=='KERN':
            print( self.bal )
            self.PortComm.baudrate  = 9600
            self.PortComm.parity = serial.PARITY_NONE
            self.PortComm.stopbits = serial.STOPBITS_ONE
            self.PortComm.bytesize = serial.EIGHTBITS
            self.Ordre=""
        elif self.bal=='ExplorerPro':
            print( self.bal )
            self.PortComm.baudrate  = 9600
            self.PortComm.parity = serial.PARITY_NONE
            self.PortComm.stopbits = serial.STOPBITS_ONE
            self.PortComm.bytesize = serial.EIGHTBITS
            self.Ordre="P"
            self.Ilength = 12
        if self.PortComm.isOpen():
            self.PortComm.close()
        self.PortComm.open()

    def GetWeight(self):
        """retrieves the current weight of the balance

        Returns
        -------
        poids: float, weight measured
        bytesread: bytes, raw serial message
        """

        if self.Ordre!="":
            self.PortComm.flushInput()
            self.PortComm.write(self.Ordre.encode())
            bytesread=self.PortComm.read(self.Ilength)
            
        else:
            self.PortComm.flushInput()
            bytesread=self.PortComm.readline()

        #~ print bytesread
        if self.bal == 'Explorer22':
            poids = bytesread[1:8]
        elif self.bal== 'Ohaus50':
            poids = bytesread
        elif self.bal == 'Explorer35':
            poids = bytesread[6:13]
        elif self.bal == 'KERN':
            poids= str(bytesread)[:-6]
        elif self.bal == 'ExplorerPro':
            if len(bytesread)>=8:
                poids= str(bytesread)[:5]+'.'+str(bytesread)[7]
            else:
                poids=''
        # if a value of weight is returned convert to float
        if poids!='':
            try: 
                poids = float(poids)        
            except:
                poids = -999
        else:
            poids=0
            
        return poids, bytesread

    def close(self):
        """ close COM port"""
        self.PortComm.close()
        
    def Send_and_Receive(self, Ordre = '?'):
        self.PortComm.flushInput()
        self.PortComm.write(self.Ordre)
        bytesread=self.PortComm.readline()
        return bytesread

class ISM112:
    """ A simple class to control an ISM device for analogue input

            enables to get the voltage using a simple function call
    """
    def __init__(self,AIN="02",com='/dev/ttyUSB0'):
        """ initilize the ISM port: specify it type and the com por to be used

        Parameters
        ----------
        AIN : str, optional
            ISM port to use , by default "02"
        com : str, optional
            com port to which ISM is connected, by default '/dev/ttyUSB0'
        """
        self.PortComm=serial.Serial()
        self.PortComm.timeout = 0
        self.PortComm.port=com

        # sets the parameters for acquisition
        self.PortComm.baudrate = 9600
        self.PortComm.parity = serial.PARITY_EVEN
        self.PortComm.stopbits = serial.STOPBITS_ONE
        self.PortComm.bytesize = serial.EIGHTBITS
        self.Ordre = "$01R"+AIN+"\r" 
        self.Ilength = 10

        print( self.PortComm.baudrate )

        if self.PortComm.isOpen():
            self.PortComm.close()
        self.PortComm.open()

    def Getvoltage(self):
        """Retrieves the current weight of the balance

        Returns
        -------
        voltage: float
            voltage
        """
        self.PortComm.flushInput()
        self.PortComm.write(self.Ordre)
        bytesread=self.PortComm.read(self.Ilength)

        print( bytesread )

        voltage = bytesread[1:6]

        return voltage

    def close(self):
        """ close COM port"""
        self.PortComm.close()



################################### connection

def read_all( arduino, dt = 0.1 ) :
    """readline on arduino every dt

    Parameters
    ----------
    arduino : object
        board
    dt : float, optional
        times tep, by default 0.1

    Returns
    -------
    answer: str
        line read
    """
    answer = []
    
    while arduino.inWaiting() > 0 :
        answer += [ arduino.readline() ]
        sleep( dt )

    return answer
    
################################## stop

def find_arduino(arduino_id, timeout = .1, port_number_list = range(8) ):
    """looks for boards with name arduino_id.
    To be used when not using the board serial number
    
    Parameters
    ----------
    arduino_id : str
        name given to arduino board
    timeout : float, optional
        timeout of connection, by default .1
    port_number_list : list of int, optional
        list of ports to check, by default range(8)

    Returns
    -------
    board or none
        board if found, none if no board found
    """

    print( "Looking for Arduino with ID " + arduino_id + '.\n' )
    
    OK = False
    
    for port_i in port_number_list:
        
        try :
            port_address = '/dev/ttyACM' + str(port_i)
            arduino = serial.Serial( port_address , timeout = timeout )
            
            read_all( arduino )
            
            arduino.write("?"); sleep(1.)
            aname = arduino.readline()
            print(aname)
            
            if arduino_id in aname:
                
                print( 'Arduino on port ' + port_address + ' with ID ' + arduino_id + '.\n' )
                
                OK = True
                
                break
            
            else:
                print( 'Somebody else on port ' + port_address)
            
        except :
            print( 'Nobody on port ' + port_address)
            pass

    if OK :
        return arduino
    
    else :
        return None

####################################

def stop(arduino):
    
    read_all(arduino)

    print( "Send stop message." )

    arduino.write("s");

    while not 'Stopping' in arduino.readline() :
            stdout.write( '.' )
            stdout.flush()
    print( '' )

    read_all(arduino)

    print( 'Stopped.' )

################################# launch

def launch( arduino, dt, number_of_steps ):

    if dt in ( 0., 's' ) :
        stop(arduino)
    
    else :

        print( "Send dt = " + str(dt) )

        arduino.write( str(dt) );

        while not '?' in arduino.readline() :
                stdout.write( '.' )
                stdout.flush()
        print( '')
        
        print("Send number of steps = " + str(number_of_steps))

        arduino.write( str(number_of_steps) );
        
        while not str( number_of_steps ) in arduino.readline() :
                stdout.write( '.' )
                stdout.flush()
        print( '')
        minutes,seconds = divmod( abs( number_of_steps*dt*4/1000. ), 60 )
        print( "Launched. Estimated time: " + str( int(minutes) ) + "'" + str( int(seconds) ) + "''")

        read_all(arduino)
        

###############################################

def connect_arduino(): #obsolete FM 30/04/18
    
    port_base_name = '/dev/ttyACM'
    port_suffix_list = ['0','1','2','3','4']
    
    board_connected = False 
    
    for port_suffix in port_suffix_list :
        
        port = port_base_name + port_suffix
        
        try :
            print( 'Trying port ' + port)
            board = Arduino(port)
            board_connected = True
            break
        
        except :
            print( 'Failed on port ' + port)
    
    if board_connected :
        
        it = util.Iterator(board)
        it.start() # necessary for tension meausurements
    
        time.sleep(.1)
        
        print( 'Connected to Arduino at ' + port)
    
    else :
        
        print( 'Failed to connect to Arduino!')
    
    return board

#########################################

def get_discharge_new(board, nb_measures=10):
    # uses the sketch written for arduino by Francois
    # replace get_tension
    # 29/04/18
    t=[]
    for i in range(nb_measures):
        board.write("Q")
        time.sleep(1.)
        val=int(board.readline())
        
        if val >0 and val < 1023:
            t.append(tension2discharge(val*5./1023.))
    if len(t) > 1:
        return mean(t)
    else:
        return nan
        

def get_tension(board, pin_number, nb_measures = 10 ) : # obsolete 

    board.analog[pin_number].enable_reporting()
    time.sleep(.1)
    
    tension = []

    for n in range(nb_measures) :
        tension = tension + [ board.analog[pin_number].read() ]
    
    tension = array(tension)
    
    if ( abs(tension) > 1.0 ).any() :
        return nan
    
    else :
        return mean(tension)*5. # volts

#########################################

def tension2discharge(tension,     range_intensity = [ 4e-3, 20e-3],     range_discharge = [ 0, 1.001 ], resistance=217 ):
    """Transforms the tension read on a Kobold flow meter to a discharge using a linear correlation

    Parameters
    ----------
    tension : float
        voltage measured
    range_intensity : list, optional
        min and max intensity retured by the flow meter, by default [ 4e-3, 20e-3]
    range_discharge : list, optional
        discharge range of the flow meter, by default [ 0, 1.001 ]
    resistance : int, optional
        circuit resistance used to measure the voltage, by default 217

    Returns
    -------
    float
        discharge in l/mn
    """
    
    intensity = tension/resistance # ampere
    
    coeff=(range_discharge[1] - range_discharge[0])/(range_intensity[1] -range_intensity[0])
    
    return range_discharge[0] + ( intensity - range_intensity[0]) * coeff

#########################################

def get_discharge(board) :
    """returns average of 10 discharge measurements

    Parameters
    ----------
    board : object
        arduino board

    Returns
    -------
    float
        discharge
    """
    
    return tension2discharge(get_tension_new(board,10))

#########################################

def light( light_board, switch ) :
    """switches ligh on and off

    Parameters
    ----------
    light_board : object
        light board
    switch : str
        on=High and off=Low
    """
    
    if switch == 'on' :
        light_board.digital[3].write(1)
    
    elif switch == 'off' :
        light_board.digital[3].write(0)
     
    else :
        print( 'Error light.')
        
#########################################

def electrovalve( board, switch ) :
    """switches digital pin 2 to high or low
    used to opena nd close an electrovalve

    Parameters
    ----------
    board : object
        arduino board
    switch : str
        on for high, off for low
    """

    
    if switch ==  'on' :
        board.digital[2].write(1)
        
    elif switch == 'off' :
        board.digital[2].write(0)
         
    else : 
        print( 'Error electrovalve.')
        
###########################################

def lightpanel (board, switch) :
    """switches ligh on and off. Same as light but for two panels connected on dgitial pins 2 and 3

    Parameters
    ----------
    board : object
        light board
    switch : str
        on=High and off=Low
    """
    if switch == 'on' :
        board.digital[2].write(1)
        board.digital[3].write(1)
        
    elif switch == 'off' :
        board.digital[2].write(0)
        board.digital[3].write(0)
    
    else :
        print( 'Error light.'    )

###########################################

def getval(TimeStep,filename,stop_event):

    device=lab.balance(balname,porttype)
    t0=time.time()

    while (not stop_event.is_set()):
        #get weight
        ValMass=device.GetWeight()
        #ValMass=random()
        MeasMass.append(ValMass)
        # register time
        ValTime=time.time()
        MeasTime.append(ValTime-t0)
        st='Temps = %4.2f\n Masse mesuree = %4.2f\n' % (ValTime-t0,ValMass)
        #Affiche les valeurs dans une petite fenetre
        prompt= st
        lbl.config(text=prompt)

        with open(filename,'a') as f:
            st="%f\t%f\n" % (ValTime-t0,ValMass)
            f.write(st)
        time.sleep(TimeStep)
        
#########################################

def param(iso=500, shutterspeed= 20, aperture= 21):
    """set camera parameters

    Parameters
    ----------
    iso : int, optional
        camera iso, by default 100
    shutterspeed : int, optional
        shutter speed , by default 20
    aperture : int, optional
        lense aperture, by default 21
    """
    os.system('gphoto2 --set-config-index iso=%i'%iso)
    os.system('gphoto2 --set-config-index shutterspeed=%i'%shutterspeed)
    os.system('gphoto2 --set-config-index aperture=%i'%aperture)
    time.sleep(2)
    os.system('gphoto2 --get-config iso=%i'%iso)
    os.system('gphoto2 --get-config shutterspeed=%i'%shutterspeed)
    os.system('gphoto2 --get-config aperture=%i'%aperture)
    
    
##########################################

def vanne( board, tsleep ) :
    """opens valve for tsleep seconds

    Parameters
    ----------
    board : object
        arduino
    tsleep : int (can be float but will be truncated)
        duration of opening
    """
    
    while True : 
        electrovalve(board, 'on')
        time.sleep(int(tsleep))
            
        # fermeture de la vanne
        electrovalve(board, 'off')
        time.sleep(int(tsleep))


def set_sediment_feed():
    """
    launch sediment feed interactive control 
    """
    sedfeeder = find_arduino('Sediment')
    
    go_on=True
    if sedfeeder:
        while go_on:
            dt = input('Delay [s] ? ')    
            sedfeeder.write( str(dt) )
            if int(dt)==0:
                go_on=False
        
