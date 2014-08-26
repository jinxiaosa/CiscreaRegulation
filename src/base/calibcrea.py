from ciscrea import Ciscrea
import sys
import time
import numpy as np

def calibration(ciscrea):
    """
    Increase voltage on each motor one by one and monitor power consumption.
        When the consumption increases the motor is started.
        Do this forward and backward for each motor. 
        Raise calibrated flag when done
    Arguments: None
    Return Value: False on error, True otherwise
    """
    
    #are we connected ?
    if ciscrea.full_stop() is None:
        return False
    
    #erase previous calibration values
    if ciscrea.calib:
        ciscrea.neutral=125*np.ones(5, dtype='int8')
        ciscrea.min_fwd=1*np.ones(5, dtype='int8')
        ciscrea.min_bwd=-1*np.ones(5, dtype='int8')
        ciscrea.calib=False
        
    fwd_treshold=calibrate_motors(ciscrea, 'F')
    bwd_treshold=calibrate_motors(ciscrea, 'B')
    ciscrea.neutral=125*np.ones(5, dtype='int')+fwd_treshold+bwd_treshold
    ciscrea.min_fwd=125*np.ones(5, dtype='int')+fwd_treshold-ciscrea.neutral
    ciscrea.min_bwd=125*np.ones(5, dtype='int')+bwd_treshold-ciscrea.neutral
    
    ciscrea.full_stop()        
    ciscrea.calib=True
    return True

def calibrate_motors(ciscrea, heading='F', nb_motors=5, start_current=60):
    if heading=='F':
        incr=1
    elif heading=='B':
        incr=-1

    ciscrea.full_stop()
    
    time.sleep(1)
    #read consumption
    rest=ciscrea.average_current()
    treshold=np.zeros(5, dtype='int8')
    for i in range(nb_motors):
        motor_start=False
        treshold[i]=0
        while not motor_start:
            print "motor %d voltage %d"%(i, treshold[i])
            ciscrea.motor_speed(i, treshold[i])
            consumption=ciscrea.average_current(20)
            if sum(consumption-rest)>start_current: #mA
                motor_start=True
            else:
                treshold[i]+=incr         
        ciscrea.full_stop()
        time.sleep(1)
        rest=ciscrea.average_current()
    return treshold

def motor_spin(ciscrea):
    ciscrea.full_stop()
    msg=["through the bow", "through the prow", "up"]
    valid_ans=['y', 'n']
    for i in range(5):
        ciscrea.motor_speed(i,127)
        ans=None
        while ans not in valid_ans:
            input_str="Is motor %d blowing %s? (y/n) "%(i, msg[i/2])
            ans=raw_input(input_str)
        ciscrea.full_stop()
        if ans=='n':
            ciscrea.motor_spin[i]=-1

if len(sys.argv)>2:
    bot=Ciscrea(sys.argv[1])
else:
    print "Usage: %s [IP or serial port] [configuration file]"%(sys.argv[0])
    sys.exit(1)


if calibration(bot):
    motor_spin(bot)
    bot.save_calibration(sys.argv[2]+".calib")
else:
    print "Can not connect to "+sys.argv[1]

bot.quit()