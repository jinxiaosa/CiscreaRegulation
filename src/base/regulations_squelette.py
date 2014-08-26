import numpy as np
from scipy.integrate import ode
import time

def newton2motors(T):
    """Returns the motor order needed for a given thrust, will
    return +/- 127 if T is above the power range of the motor"""
    sgn=1
    if T<0:
        sgn=-1
        T*=-1
    f=203.874*T
    g=65.6756*T+30.3781
    ret_val=sgn*int(np.min([127,f,g]))
    #ret_val=sgn*min(127,int(0.5*(14.9109*T+47.7123*np.sqrt(T))))
    return ret_val

def z_control(depth, target_depth, dt):
    """
    Returns vertical motors order as an integer between -127 and +127
    depth: current depth in meters
    target_depth: depth the AUV has to reach
    dt: time in seconds between two consecutive calls to z_control
    """

    #below is an ugly way to store variables between two consecutive calls
    #to z_control

    #First we check if this is first time z_control is called 
    if not hasattr(z_control, "foo"):  #does the variable called "foo" exists ?
        #if it does not exist it means this is the first call to z_control
        z_control.foo=42
        z_control.log=open("log"+str(time.time())+".txt", "w+")
        z_control.log.write("Depth Target_depth\n")
    #now z_control.foo exists, any value written to it will remain until the next call
    print z_control.foo
    z_control.foo+=1
    z_control.log.write("%f %f\n"%(depth, target_depth))
    z_control.log.flush()
    return 0

def psi_control(psi, target_psi, dt, fw):
    return 0