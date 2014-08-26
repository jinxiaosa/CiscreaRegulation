from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
import numpy as np
import sys
import time
import threading
import inspect
import operator
import types
import struct
import os
from Queue import Queue, Empty



                
class Ciscrea(object):
    def __init__(self, remote, timeout=0.01):
        if len(remote.split("."))==3:
            #we probably have a TCP request
            print "TCP connection to: ", remote
            self.client=ModbusTcpClient(remote, 502)
            self.__modbus_timeout=timeout
        else:
            if os.name!="posix" and timeout<0.03:
                print "RS485 timeout too low, using 0.03 seconds"
                self.__modbus_timeout=0.03
            else:
                self.__modbus_timeout=timeout
                
            print "RS485 connection to: ", remote
            self.client=ModbusSerialClient(method="rtu", port=remote, stopbits=1,bytesize=8,
                    parity="N",baudrate=38400, timeout=self.__modbus_timeout)

            #print self.client.connect()
                
        #motor tresholds, use default values unless a calibration file is loaded
        self.neutral=125*np.ones(5, dtype='int8')
        self.min_fwd=1*np.ones(5, dtype='int8')
        self.min_bwd=-1*np.ones(5, dtype='int8')
        self.motor_max=80#seems constant across all AUVs
        #flag for motors mounted the wrong way
        self.motor_spin=1*np.ones(5, dtype='int8')
        
        
        #flag if the motors are calibrated
        self.calib=False
        
        #flag to exit watchdog thread
        self.exit=False
        

        
        self.alarms_byte=0
        self.__status=[0 for _ in range(16)]
        self.alarms_list=[[False]*12,
                          ['Water ingress main compartment',
                          'Water ingress left battery',
                          'Water ingress right battery',
                          'Overheating',
                          'Low power',
                          'Over consumption',
                          'Maximum depth',
                          'Start error',
                          'SPI error',
                          'I2C error'
                          ]]

        self.rwlock=threading.Lock()
        self.statuslock=threading.Lock()

        self.__motors_values=[0,0,0,0,0]
        self.modbus_write(1, 0xC000)#wtf ?!
        print "rock'n roll baby"
        
        #launch watchdog thread and exit __init__
        threading.Thread(target=self.__keep_alive).start()
    
    def get_modbus_timeout(self):
        return self.__modbus_timeout

    def modbus_read(self, reg, nb):
        """
        Lock rw mutex and read nb registers starting at register reg
        Argument 1: register index to start to read from
        Argument 2: number of registers to read
        Return value: ciscrea answer or None on error
        """      
        
        
        with self.rwlock:
            try:
                val=self.client.read_holding_registers(reg,nb,unit=16)
            except Exception,e:
                val=None
                print e
                print "Error reading from modbus"
        return val
    
    
    def modbus_write(self, reg, value):
        """
        Lock rw mutex and write value at register reg.
        Print an error message if ciscrea does not acknowledge
        Argument 1: register index to write to
        Argument 2: value to write
        Return value: modbus answer or None on error
        """
        with self.rwlock:
            try:
                answer=self.client.write_register(reg, value, unit=16)
            except:
                print "Error writing on modbus"
                answer=None
                pass
        return answer
#        try:    
#            echo_value=int(str(answer).split()[-1])
#            if echo_value != value:
#                print "Something went wrong writing register %d with value %d"%(reg, value)
#                print answer
#        except Exception, e:
#            print "Error on modbus write"
#            print e

    def modbus_writes(self, reg, values):
        """
        As modbus_write but writes several registers at once, starts from reg
        and ends as reg+len(values)-1
        Argument 1: register index to start to write to
        Argument 2: values to write
        Return value: modbus answer or None on error
        """
        with self.rwlock:
            try:
                answer=self.client.write_registers(reg, values, unit=16)
            except:
                print "Error writing on modbus"
                answer=None
                pass
        return answer
        
    def __keep_alive(self):
        """
        Watchdog thread to keep the ciscrea online.
        Arguments: None
        Return value: None
        Will update every 0.1 second OR 5*modbus_timeout depending on which one is the biggest
        """
        sleep_time=max(0.1, 5*self.__modbus_timeout)
        fail=0
        while not self.exit:
            result = self.modbus_read(32,17)
            if result is not None:
                try:
                    self.alarms_byte=result.getRegister(0)
                except:
                    self.alarms_byte=0
                    continue
                fail=0
                with self.statuslock:
                    for i in range(16):
                        self.__status[i]=result.getRegister(i+1)
                time.sleep(sleep_time)
            else:
                fail+=1
                if fail>10:
                    print "keepalive() unable to communicate with Ciscrea"
                    self.exit=True

            
    def __get_status(self):
        """raw copy of the status list, no conversion to SI units"""
        with self.statuslock:
            status=list(self.__status) #make a copy
        return status

    def get_status(self):
        """returns the current status in SI units"""
        #ugly code...
        status=self.__get_status()
        status_dict={}
        status_dict["depth"]=status[0]/100.
        status_dict["heading"]=np.deg2rad(status[1]/10.)
        status_dict["voltage 1"]=status[2]/1000.
        status_dict["voltage 2"]=status[3]/1000.
        status_dict["current 1"]=status[4]/1000.
        status_dict["current 2"]=status[5]/1000.
        status_dict["main temp"]=status[6]*0.0625
        status_dict["external temp"]=status[7]*0.0625
        status_dict["temp add 1"]=status[8]*0.0625
        status_dict["temp add 2"]=status[9]*0.0625
        status_dict["temp add 3"]=status[10]*0.0625
        status_dict["total cons 1"]=status[11]/1000.
        status_dict["total cons 2"]=status[12]/1000.
        return status_dict
    
    def alarms(self):
        """Decode the alarm byte
        Arguments: None
        Return value: True and alarm string or False and None
        """
        
        self.alarms_list[0]=[True if int(_) else False for _ in bin(self.alarms_byte)[2:]]
        if any(self.alarms_list[0]):
            alarms_string=[self.alarms_list[1][_] 
                        for _,val in enumerate(self.alarms_list[0]) if val==True]
            return True, alarms_string
        else:
            return False, None
        
    def light_on(self, intensity=255):
        """
        Switch on ciscrea lights at full intensity 
        Optional arguments: light intensity, integer between 0 and 255
        Return value: None
        """
        
        self.modbus_write(5, min(intensity,255))
        if not hasattr(self, "cmd_byte"):
            result=self.modbus_read(1,1)
            if result is None:
                return None
            else:
                self.cmd_byte = result.getRegister(0)
        #turn on light if not already on, do not touch otherwise
        #anyway the light byte has to be validated on each
        #intensity change
        self.cmd_byte|=0x1
        self.modbus_write(1, self.cmd_byte)
        
    def cam_tilt(self, tilt):
        """
        Tilt camera
        Arguments: tilt in [0:255] 127 is straight
        Return value: None
        """
        if tilt>255:
            tilt=255
        elif tilt<0:
            tilt=0
        self.modbus_write(6, int(tilt)<<8)
        
         
    
    def light_off(self):
        """
        Switch off ciscrea lights
        Arguments: none
        Return value: None
        """
        result = self.modbus_read(1,1)
        if result is not None:
            self.modbus_write(1, result.getRegister(0)&0xfffe)
        
    def average_current(self, steps=10):
        """
        Monitors battery current and averages it after 10 readings
        Optionnal argument: number of readings, integer
        Return value: current drawn by the AUV
        """
        
        val=np.zeros(2)
        cpt=0
        while cpt<steps:
            result = self.modbus_read(37,2)
            if result is None:
                return 0
            val+=result.getRegister(0),result.getRegister(1)
            cpt+=1
        return val/(float(steps))
    
    def full_stop(self):
        """
        Switch off all motors
        Argument: None
        Return value: None
        """
        return self.fast_motor_update([0,0,0,0,0])
    
    def __command_to_byte(self, idx, cmd):
        """
        Convert an absolute motor command -127/127 to a
        0-255 motor byte shifted by calibration values
        Argument 1: motor idx
        Argument 2: 
        """
        cmd=cmd*self.motor_spin[idx]
        if cmd>0:
            cmd+=self.min_fwd[idx]-1
        elif cmd<0:
            cmd+=self.min_bwd[idx]+1
        cmd=int(cmd*self.motor_max/127.)
        cmd+=self.neutral[idx]
        
        byte=max(min(cmd,255),0)
        return byte
    

    def fast_motor_update(self, values):
        """
        Erase all motors control bytes with new ones from values
        Argument 1: values, list or table with 5 motor bytes
        Return value: False if values is not suitable for all 5 motors,
        None on modbus error, modbus answer otherwise
        """
        if len(values)!= 5:
            return False

        #update stored motor values if one needs to perform
        #incremental motor control, eg speed+=1
        self.__motors_values=list(values) #object copy()
        
        motor_regs=[]
        
        for i in range(2):
            b1=self.__command_to_byte(i*2, values[i*2])
            b2=self.__command_to_byte(i*2+1, values[i*2+1])
            motor_regs.append((b1<<8)+b2)
        
        motor_regs.append(self.__command_to_byte(4,values[4])<<8)
        return self.modbus_writes(2,motor_regs)
        
    
    def motor_speed(self, idx, cmd):
        """
        Switch on the specified motor at the given voltage
        Argument 1: motor number, integer between 0 and 4
        Argument 2: voltage, integer between -127 and 127
        Return value: False if cmd is not suitable, None on modbus error, 
        modbus answer otherwise
        Should be thread safe
        """
        if idx<=4 and idx>=0:
            self.__motors_values[idx]=cmd
            return self.fast_motor_update(self.__motors_values)

    def speed_vector(self, *args):
        if len(args)!=5:
            return False
        else:
            return self.fast_motor_update(args)
#    def motor_speed(self, idx, value):
#        """
#        Switch on the specified motor at the given voltage
#        Argument 1: motor number, integer between 0 and 4
#        Argument 2: voltage, integer between -127 and 127
#        Return value: None
#        Should be thread safe
#        WARNING: this method is not suitable for realtime
#        code
#        """
#        
#        try: self.motors_lock
#        except:
#            self.motors_lock=[threading.Lock() for _ in range(3)]
#            pass
#        
#        #motor 0 and 1 share the same control byte, 2 and 3 have the same behaviour
#        #byte for motor 4 is not explicitly shared with anything else according
#        #to the doc but you never know...
#         
#        self.motors_lock[idx/2].acquire()
#        value=self.__command_to_byte(idx, value)
##        if value>0:
##            value+=self.min_fwd[idx]-1
##        elif value<0:
##            value+=self.min_bwd[idx]+1
##        value+=self.neutral[idx]
##        
##        
##        value=min(255, value)
##        value=max(0,value)
#
#        
#        #get motor bytes
#        result = self.modbus_read(2+idx/2,1)
#        if result is None:
#            self.motors_lock[idx/2].release()
#            return None
#        motor_byte=result.getRegister(0)
#        
#        #put zeros on the byte for motor idx
#        motor_byte &= (0xff<<8*(idx%2))
#
#        #update byte for motor idx
#        motor_byte|=value<<8*((idx+1)%2)
#        
#        self.modbus_write(2+idx/2,motor_byte)
#        self.motors_lock[idx/2].release()
        
    def save_calibration(self, filename):
        """
        Save the current ciscrea calibration
        Argument: filename, quoted string
        Return value: None
        """
        
        #avoid the annoying .npy extenstion
        fd=open(filename, 'wb')
        np.save(fd, (self.neutral, self.min_fwd, self.min_bwd, self.motor_spin))
    
    def load_calibration(self, filename):
        """
        Load a ciscrea calibration file, raise calibrated flag on success
        Argument: filename, quoted string
        Return value: None on success, error string on failure
        """
        try:
            self.neutral, self.min_fwd,\
                self.min_bwd, self.motor_spin=np.load(filename)
            self.calib=True
        except IOError, e:
            return e
        
    def quit(self):
        """
        Raise the exit flag to finish watchdog thread
        Arguments: None
        Return value: goodbye string
        """
        
        self.exit=True
        return "Bye !"
    

class AsynCrea(Ciscrea):
    def __init__(self, remote):
        """remote: remote address (tcp) or RS485 port
        queue_timeout: blocking time for queue get (s)
        timeout: RS485 timeout (s) default to 0.01
        """
        if os.name=="posix":
            print "POSIX compliant OS detected, using 0.01 second timeout on RS485 modbus"
            modbus_timeout=0.01
        else:
            print "WARNING ! Windows detected, will try to use a long RS485 timeout, use at your own risks"
            modbus_timeout=0.03
        print "The above can be safely ignored if using TCP modbus"

        self.writeq=Queue(0)
        super(AsynCrea, self).__init__(remote, modbus_timeout)
        self.__queue_timeout=10*modbus_timeout
        threading.Thread(target=self.__async_modbus_write).start()

    def modbus_writes(self, reg, value):
        """
        As modbus_write but asynchronously writes several registers
         at once, starts from reg and ends as reg+len(values)-1
        Argument 1: register index to start to write to
        Argument 2: values to write
        Return value: None
        """
        self.writeq.put([[reg, value, False]], False)


    def modbus_write(self, reg, value):
        """
        asynchronously write value at register reg.
        Print an error message if ciscrea does not acknowledge
        Argument 1: register index to write to
        Argument 2: value to write
        Return value: None
        """

        self.writeq.put([[reg, value, True]], False)

    def __async_modbus_write(self):
        """
        Support function for asynchronous modbus write/writes, runs as a 
        thread
        Argument 1: register index to write to
        Argument 2: value to write
        Return value: None
        """
        while not self.exit:
            try:
                for reg, value, single in self.writeq.get(True,self.__queue_timeout):
                    #print "writes", reg, value
                    #if reg==2:
                    #    print reg, value
                    if single:
                        super(AsynCrea, self).modbus_write(reg, value)
                    else:
                        super(AsynCrea, self).modbus_writes(reg, value)
            except Empty: 
                #will evaluate self.exit after this and then
                # retry to get an element in queue
                print "Command queue empty, master thread is too slow"
                pass    
