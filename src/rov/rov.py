# -*- coding: iso-8859-15 -*-
import pygame
import math
import sys
sys.path.append("../base")

import numpy as np

from rov_support import *
from ciscrea import AsynCrea
from camcrea import CamCrea
from regulations import z_control, psi_control,psi_hinf_control,psi_hinf_nonlin_kalmf

import os
import time

#in case of SIGINT close everything nicely
import signal

def close_all(signal, frame):
    cam.stop_movie()
    ciscrea.quit()
    pygame.quit()   
    
def update_ciscrea(motors, tilt):
    ciscrea.cam_tilt(tilt)
    ciscrea.fast_motor_update(list(motors))
    
#in case of SIGINT (kill, etc) perform a nice shut down    
signal.signal(signal.SIGINT, close_all)


if len(sys.argv)>2:
    ciscrea=AsynCrea(sys.argv[1])
else:
    print "Need an IP or serial port to connect to"
    sys.exit(1)

ciscrea.load_calibration(sys.argv[2])
if not ciscrea.calib:
    print "Run calibrea.py first !"

#video buffer, seems useless now
video_buf_len=1

#start SDL stuff

pygame.init()
pygame.joystick.init()
pygame.joystick.Joystick(0).init()
cam=CamCrea()

#need a timer in order not to u ciscrea with modbus requests
ciscrea_update=pygame.USEREVENT
update_timeout=10*ciscrea.get_modbus_timeout()
pygame.time.set_timer(ciscrea_update, int(update_timeout*1000))

#without this timer a hat event generates only a 1 or a 0, this timer
#is used to generate an event as long as the hat is kept pressed
hat_tick=pygame.USEREVENT+1
pygame.time.set_timer(hat_tick, 150)


#switch to 800*600 fullscreeen
if cam.is_connected():
    pygame.display.set_caption('Ciscrea ROV')
    screen = pygame.display.set_mode((800,600))
    #screen = pygame.FULLSCREEN | pygame.HWSURFACE
    imbuf=[cam.get_image() for _ in range(video_buf_len)]
else:
    print "No camera detected, UI will not start"
    
    

done=False

hat_value=0 #allow constant update while hat is pressed
#center the camera
ciscrea.cam_tilt(127)

#idx for image buffer if used
img_idx=0

#flag to remember wether the light is on or off
light_on=False

#integer to control light level, change with up or down arrow keys
light_intensity=255

#counter for camera tilt
cam_tilt=0

#read ciscrea status for the first UI redraw
status=ciscrea.get_status()


#list to store joystick orders
motors=[0,0,0,0,0]
joy_cmd=[0,0,0,0]

#switch off auto depth by default
auto_depth=False
auto_pid_depth=False
auto_heading=False
target1=False
joystick_rotation=False
target_z="xxx"
target_psi="xxx"
controller="xxx"

joyrote="xxx"
while not done and not ciscrea.exit:
    if cam.is_connected() and cam.query_image():
        imbuf[(img_idx+video_buf_len)%video_buf_len] = cam.get_image()
        img_idx=(img_idx+1)%video_buf_len
        screen.blit(imbuf[img_idx],(0,0))
        draw_ui(screen, status, target_z, target_psi, cam,controller,joyrote)
        pygame.display.flip()


    event=pygame.event.poll()
    if event.type==pygame.JOYAXISMOTION:
        joy_cmd=decode_joystick(event.axis, event.value)
        
    elif event.type==pygame.JOYHATMOTION:
        hat_value=event.value[1]
        
    elif event.type==hat_tick:        
        cam_tilt=joyhat(hat_value, cam_tilt)
        
    elif event.type==pygame.JOYBUTTONUP:
        if event.button==0:
            light_on=not light_on
            if light_on:
                ciscrea.light_on(light_intensity)
            else:
                ciscrea.light_off()
        elif event.button==1:
            cam_tilt=127
            

        #using joystick control orientation, button 3
        elif event.button==2:
            joystick_rotation=not joystick_rotation    
                
        elif event.button==6 and cam.is_connected() and os.name=="posix":
            if cam.is_recording():
                cam.stop_movie()
            else:
                cam.start_movie()
        elif event.button==7: #button 8 to open pid controller
            auto_pid_depth=not auto_pid_depth
        elif event.button==8: #button 9 to change target
            target1=not target1
            if target1:
                target_psi=4.8
            else:
                target_psi=2
        elif event.button==11:
            auto_depth=not auto_depth
            if auto_depth:
                target_z=status["depth"]
                motors_old_z=joy_cmd[3]
            else:
                target_z="xxx"
                joy_cmd[3]=motors_old_z
                #gruiiiiikkkkk

        
        elif event.button==10:#button 11 to open auto yaw control
            auto_heading=not auto_heading
            if auto_heading:
                #target_psi=status["heading"]
                
                # edit by yang rui  set a heading, read the 
                target_psi=2
                
            else:
                target_psi="xxx"
                joy_cmd[2]=0
             
                 
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            close_all(0,0)
            done=True
        
        elif event.key == pygame.K_UP and light_on:
            light_intensity=min(255, light_intensity+20)
            ciscrea.light_on(light_intensity)

        elif event.key == pygame.K_DOWN and light_on:
            light_intensity=max(100, light_intensity-20)  
            ciscrea.light_on(light_intensity)

    elif event.type==ciscrea_update:
        status=ciscrea.get_status()
        depth=status["depth"]
        psi=status["heading"]
        #overwrite joystick orders in case of z or psi control
        
        controller="joystick"
        
        if auto_depth:
            joy_cmd[3]=z_control(depth, target_z, update_timeout)

        motors=joystick2motors(*joy_cmd)

        if auto_heading:
            
            
            # yang rui solve the psi circle problem
              
                
            
            #kill joystick psi axis
            # DO NOT KILL IT YANG RUIjoy_cmd[2]=0
            
            # yang rui enable the joystick orientation control system
            if joystick_rotation:
                joyrote="joyrote"
                rotateincre=float(joy_cmd[2])/2000
                target_psi=target_psi+rotateincre
                #print(joy_cmd[2],target_psi)
                if target_psi>(3.1415926*2):
                    target_psi=target_psi-(3.1415926*2)
                elif target_psi<=0:
                    target_psi=target_psi+(3.1415926*2)
                #print((rotateincre),target_psi)
            else:
                joyrote="xxx" 
                       
                       
#            TODO 2014-4-28 this code is not compatible with kalman filter, this code is not correct: try to correct it.
#            psi rang from 0 to 6.28, we should make it a circle 6.28 is the same as 0
#            target_psi_circle=3.1415926*2-target_psi
#            band psi           
            if psi>=(3.1415926*2):
                psi=psi-(3.1415926*2)
            elif psi<0:
                psi=psi+(3.1415926*2)   
            if (psi-target_psi)>3.1415926 :
                psi=psi-3.1415926*2
            elif (psi-target_psi)< -3.1415926 :
                psi=psi+3.1415926*2
       
            if auto_pid_depth:
                
                controller="PID_Yaw"
                #compute the motors orders for the remaining axis
                motors=joystick2motors(0,joy_cmd[1]/2.,0,joy_cmd[3])
                #compute what is left for the heading control
                #margin=127-np.max(motors[:-1])
    
                motors_psi=psi_control(psi, target_psi )
    
                motors=update_psi(motors,motors_psi)
            else:
                
                controller="Hinf_Yaw"    
                #compute the motors orders for the remaining axis
                motors=joystick2motors(0,joy_cmd[1]/2.,0,joy_cmd[3])
                #compute what is left for the heading control
                #margin=127-np.max(motors[:-1])
    
                motors_psi=psi_hinf_nonlin_kalmf(psi, target_psi )
    
                motors=update_psi(motors,motors_psi)
        update_ciscrea(motors, cam_tilt)
    
    #blocking call to force release the GIL
    time.sleep(0) #0 is NOT a bug.
