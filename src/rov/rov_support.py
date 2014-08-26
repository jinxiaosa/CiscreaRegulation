# -*- coding: iso-8859-15 -*-
import pygame
import os
from regulations import newton2motors
import numpy as np

def decode_joystick(axis, value, max_thr=1.5):
    if not hasattr(decode_joystick, "previous_orders"):
        decode_joystick.previous_orders=[0,0,0,0]
        if os.name=="posix":
            decode_joystick.updown_axis=3
            decode_joystick.psi_axis=2
        else:
            decode_joystick.updown_axis=2
            decode_joystick.psi_axis=3


    if os.name!="posix": #to be cleaned later
        if value<0:
            sgn=-1
        else:
            sgn=+1
        if axis==decode_joystick.psi_axis:
            if abs(value)<0.2:
                value=0
            else:
                value=sgn*(abs(value)-0.2)/0.8
        else:
            if abs(value)<0.1:
                value=0
            else:
                value=sgn*(abs(value)-0.1)/0.9
        
    lr, fw, psi, z=decode_joystick.previous_orders
    if axis==0:
        T_lr=max_thr*value
        lr=newton2motors(T_lr)
    elif axis==1:
        T_fw=max_thr*value
        fw=newton2motors(T_fw)
    elif axis==decode_joystick.psi_axis:
        T_psi =max_thr*value
        psi=newton2motors(T_psi)
    elif axis==decode_joystick.updown_axis:
        T_z = max_thr*value
        z=newton2motors(T_z)

    #motors[0]=fw-lr-psi
    #motors[1]=fw+lr+psi
    #motors[2]=-fw-lr-psi
    #motors[3]=-fw+lr+psi
    decode_joystick.previous_orders=lr, fw, psi, z
    return [lr, fw, psi, z]

def update_psi(motors, psi):
    motors[0]-=psi
    motors[1]+=psi
    motors[2]+=psi
    motors[3]-=psi
    return motors

def joystick2motors(lr, fw, psi, z):
    """
    Translates joystick orders into motors' registers
    values
    Arguments: joystick orders ForWard, LeftRight, heading (Psi)
    and Z as integers from -127 to +127
    Return values: motors registers from 127 (full fowarard)
    to -127 (full backward). Forward/Backward as defined in the ciscrea
    model.
    """
    
    #  target_z = int(10*2.5*(1+value))/10.
    
    # yang rui edit here to slow the psi motion
    psi=psi/2

    motors=[-fw-lr-psi,
            -fw+lr+psi,
            fw-lr+psi,
            fw+lr-psi,
            z
            ]
    
    M=0
    #we want to find the maximum absolute value, min/max 
    #on lists are of little help here 
    
    for val in motors:
        if abs(val)>M:
            M=abs(val)
    if M>127:
        for idx in range(len(motors)-1):#do not change Z
            motors[idx]=int(127*motors[idx]/float(M)) 

    return motors

def joyhat(value, tilt):
    if value!=0:
        tilt+=value*10
        if tilt>180:
            tilt=180
        elif tilt<30:
            tilt=30
    return tilt
        
    

def draw_ui(screen,status, target_z, target_psi, cam, controller,joyrote):
        pygame.draw.polygon(screen,(0,0,0),((0,475),(635,475),(635,0),(800,0),
                (800,600),(0,600)))
        font = pygame.font.Font(None, 36)
        
        pygame.draw.rect(screen,(255,0,0),(645,5,150,100), 2)
        text = font.render("Depth:", 1, (255, 255, 255))
        screen.blit(text,(650,10))
        text = font.render(str(status["depth"])+" / "+str(target_z), 1, (255, 255, 255))
        screen.blit(text,(650,40))
        
        
        
        pygame.draw.rect(screen,(255,0,0),(645,5+120,150,100), 2)
        text = font.render("Heading:", 1, (255, 255, 255))
        screen.blit(text,(650,10+120))
        if target_psi != "xxx":
            target_psi=np.rad2deg(target_psi)
        text = font.render(str(np.rad2deg(status["heading"]))+" / "+str(target_psi)+"°", 1, (255, 255, 255))
        screen.blit(text,(650,40+120))    
        
        
        # draw controller
        
        
        pygame.draw.rect(screen,(255,0,0),(645,5+240,150,100), 2)
        text = font.render("Controller:", 1, (255, 255, 255))
        screen.blit(text,(650,10+240))
        if joyrote!= "xxx":
            text = font.render(str(controller), 1, (255, 255, 255))
            screen.blit(text,(650,40+240))
            text = font.render(str(joyrote), 1, (255, 255, 255))
        else:
            text = font.render(str(controller), 1, (255, 255, 255))
     
        screen.blit(text,(650,70+240))  
        
        #draw red circle when recording
        if cam.is_recording():
            flash=int(pygame.time.get_ticks()/1000.)%2
            if flash:
                pygame.draw.circle(screen, (255,0,0), (720,550), 40,0)
