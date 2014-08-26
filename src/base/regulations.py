import numpy as np
from scipy.integrate import ode
import time
from numpy import linalg as LA

from collections import deque
moto_limit=5.8 #or we call it 120
moto_cmd_limit=120 #or we call it 120
P=0
D=0
I=0
#y=0
yold=0
v=0
klmf_moto_ctrl=0 # save the Hinf controller output for kalman filter
comp_damp=0# Record the nonlinear damping compensation
fedfwd=1# reserved for damping compensator
DN=0.35 # reserved for nonlinear damping paras
psi_comp=0 # reserved for compensation
campass_comp_para=0.2# reserved for the paras of compensation 0.5 is good and precise
ang_vel=0 # reserved for the velocity of kalman
kalmfinput=0 # reserved for the input to kalman
not_initial=True
xk=np.matrix("0;0;0;0;0") # reserved by hinf controller
kalxk=np.matrix("0;0")# reserved by kalman fitler
smith_xk=np.matrix("0;0")# reserved by smith compensator 
kalmf_ang=0 #reserved for kalman angle 
psilist=deque([0])
smithlist=deque([0, 0 ,0 ,0 ])
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

def psi_control(psi, target_psi):
    #global variable
    global P
    global D
    global I
    global yold
    global psilist
    
    if not hasattr(psi_control, "outfile"):
        psi_control.outfile=open("logs/pid/PID_log_psi_ctrl"+str(time.strftime("%y-%m-%d-%H-%M"))+".txt", "w+")
        
    #2014-3-31 edit by yangrui write a PID contorller here 
   
    #    psi: the yaw angle in rad
    #    target_psi: the expected orientation in rad
    # psilist.append(psi)
    y=psi#psilist.popleft()
    r=target_psi
    psi_err=r-y
    # Pre compute PID controller parameters
    #gain
    kp=15
    ki=0.6
    kd=10
    N=2.59
    #interval 0.1s
    h=0.1
    bi=ki*h
    Tf=kd/(kp*N)
    ad=Tf/(Tf+h)
    bd=kd/(Tf+h)
    #br=h/Tt
    
    P=kp*psi_err
    
    #yang rui solve the turning shaking problem, tell why next time
    
    if y-yold<-3 or y-yold>3:
        yold=y
    
    D=ad*D-bd*(y-yold)
    v=P+I+D
    #u=sat(v,ulow,uhigh)
    I=I+bi*(psi_err)#+br*(u-v)
    yold=y
   
    #write campass and control command 
    psi_control.outfile.write("Psi: "+str(psi)+" ,ctrl_cmd: "+str(v)+" ,P: "+str(P)+" ,I: "+str(I)+" ,D: "+str(D)+"\n")
    psi_control.outfile.flush()
    
    #add a dead zone and saturation
#    if v>120:
#        v=120
#    elif v<-120:
#        v=-120
#    elif v>-2 and v<2:
#        if v>0:
#            v=0
#        else:
#            v=0
     
    moto_ref_psi =v
    print("PID:",psi, target_psi, moto_ref_psi)
    return moto_ref_psi



#   Kalman filter: estimation of angular velocity
def kalmf_ang_vel(psi, moto_ctrler,comp_damp):
    global ang_vel
    global moto_limit
    global kalxk
    global kalmf_ang
    global kalmfinput
    if not hasattr(kalmf_ang_vel, "outfile"):
        kalmf_ang_vel.outfile=open("logs/kalmf/Kalman"+str(time.strftime("%y-%m-%d-%H-%M"))+".txt", "w+")
    
    
    # use compensation  and moto limit calculate the kalman input
    moto_max=moto_limit
    moto_min=-moto_limit
    
    kalmfinput=moto_ctrler
    
    Motoinput=moto_ctrler-comp_damp
    if Motoinput>moto_max:
        kalmfinput=moto_max+comp_damp
    elif Motoinput<moto_min:
        kalmfinput=moto_min+comp_damp
        
    #kalman iteration
#    a=
#    0.817434207010430        -0.0270295049541631
#    0.0905652303625428    0.917467766665371
#    b=
#    0.182565792989570         0.0270295049541631
#    0.00943476963745717    0.0825322333346289
#    
#    
#    c=
#    0    0.920462421552291
#    1    -0.0330662758205544
#    0    0.920462421552291
#    
#    d=
#    0    0.0795375784477090
#    0    0.0330662758205544
#    0    0.0795375784477090
    a=np.matrix(" 0.817434207010430 -0.0270295049541631; 0.0905652303625428 0.917467766665371")
    b=np.matrix(" 0.182565792989570 0.0270295049541631; 0.00943476963745717 0.0825322333346289")
    c=np.matrix("0 0.920462421552291; 1 -0.0330662758205544; 0 0.920462421552291")
    d=np.matrix(" 0 0.0795375784477090; 0 0.0330662758205544; 0 0.0795375784477090")
  
    uk=np.matrix([kalmfinput, psi])
    uk=uk.transpose()
    xkk=a*kalxk+b*uk
    yk=c*kalxk+d*uk
    kalxk=xkk
    #write campass and control command 
    
    ang_vel=yk[1,0]
    kalmf_ang=yk[0,0]
    # write a log of kalman filter
   
    kalmf_ang_vel.outfile.write("Kal_Ang_Vel: "+str(yk[1,0])+" ,Psi_kal: "+str(yk[0,0])+" ,Psi_Input: "+str(psi)+" ,Moto_input: "+str(kalmfinput)+"\n")
    kalmf_ang_vel.outfile.flush()
    
    #print on screen
    print("Input",kalmfinput,"Psi:",psi,"y", yk[0,0], "Ang_Vel:",yk[1,0],"x2:", yk[2,0])
    
    return ang_vel
#   Nonlinear Compensator
def nonlin_compensator(ang_vel):
    global comp_damp
    global fedfwd
    global DN
    # make a feed back
    comp_damp=fedfwd*ang_vel-DN*abs(ang_vel)*ang_vel
    return comp_damp

def psi_hinf_control(psi, target_psi):
    global xk
    global v
    #    Control log
    if not hasattr(psi_hinf_control, "outfile"):
        psi_hinf_control.outfile=open("logs/hinf/Hinf_log_psi_ctrl"+str(time.strftime("%y-%m-%d-%H-%M"))+".txt", "w+")
        
    #    psi: the yaw angle in rad
    #    target_psi: the expected orientation in rad
    y=psi#psilist.popleft()
    r=target_psi
    psi_err=r-y
    uk=np.matrix(psi_err)
    #hinf controller
    #a= 
    #0.197256482648792    1.59540314598849    4.49798010253664    -3.71776829599392    0.300123924813506
    #-0.00621131141495130    0.759731533313859    -0.685176910215340    0.547387817981330    -0.0450683664607837
    #0.0146347815053511    -0.170901816165014    0.550453855157298    0.0406100731570936    -0.0155990464674315
    #-0.00153580351247490    -0.0362653741260259    -0.0211178973384089    0.305283481543664    0.0296900874424064
    #0.000293001798299378    0.000255776045928881    0.000246755112570867    0.0276890693987905    0.998376332616215
    #
    #b=
    #0.273103219717465
    #-0.0179292130016475
    #0.206521330295216
    #0.110601840954218
    #0.000521323997792441
    #
    #c=
    #-16.0062512802928    58.3996253615540    178.658222489516    -258.946581201241    16.8045790623509
    #
    #d
    a=np.matrix("0.197256482648792    1.59540314598849    4.49798010253664    -3.71776829599392    0.300123924813506; -0.00621131141495130    0.759731533313859    -0.685176910215340    0.547387817981330    -0.0450683664607837; 0.0146347815053511    -0.170901816165014    0.550453855157298    0.0406100731570936    -0.0155990464674315; -0.00153580351247490    -0.0362653741260259    -0.0211178973384089    0.305283481543664    0.0296900874424064; 0.000293001798299378    0.000255776045928881    0.000246755112570867    0.0276890693987905    0.998376332616215")
    b=np.matrix("0.273103219717465; -0.0179292130016475; 0.206521330295216; 0.110601840954218; 0.000521323997792441")
    c=np.matrix("-16.0062512802928    58.3996253615540    178.658222489516    -258.946581201241    16.8045790623509")
    
    xkk=a*xk+b*uk
    yk=c*xk
    xk=xkk
    #write campass and control command 
    
    moto_ref_psi=yk[0,0]
    
    psi_hinf_control.outfile.write("Psi: "+str(psi)+" ,ctrl_cmd: "+str(moto_ref_psi*moto_cmd_limit/moto_limit)+" ,ctrl_force: "+str(moto_ref_psi)+"\n")
    psi_hinf_control.outfile.flush()
    
    #add a dead zone and saturation
    if moto_ref_psi>moto_limit:
        moto_ref_psi=moto_limit
    elif moto_ref_psi<-moto_limit:
        moto_ref_psi=-moto_limit
     
    print('psi:', psi, 'tar:', target_psi, 'ctrl:', moto_ref_psi*moto_cmd_limit/moto_limit)
    return moto_ref_psi

# add a smith compensator

def smith_compensation(control_input,psi):
    
    global smith_xk
    global smithlist
    #Gnew_a_DC =
    #
    #    0.8174         0
    #    0.0906    1.0000
    #
    #Gnew_b_DC =
    #
    #    0.1826
    #    0.0094
    #Gnew_c_DC =
    #
    #     0     1
    #Gnew_d_DC =
    #
    #     0

    a=np.matrix(" 0.8174 0;0.0906 1.0000")
    b=np.matrix(" 0.1826; 0.0094")
    c=np.matrix(" 0 1")
    d=np.matrix(" 0")
  
    uk=np.matrix(control_input)
    xkk=a*smith_xk+b*uk
    yk=c*smith_xk+d*uk
    smith_xk=xkk
    # TODO correct error using kalman
    
    # Delay the output
    smithlist.append(yk)
    comp_smith_psi=yk-smithlist.popleft()+psi
    return comp_smith_psi

#   Kalman nonlinear comensator and hinf controller
def psi_hinf_nonlin_kalmf(psi, target_psi):

    global klmf_moto_ctrl # 
    global comp_damp
    global kalmf_ang
    global not_initial
    global psi_comp
    global ang_vel
    
    #moto_fin=0
    #    set the initial TODO this part should be changed
    if not_initial:
        not_initial=not not_initial
        kalmf_ang=psi
        kalxk=np.matrix([0,psi])
        kalxk=kalxk.transpose()
        psi_comp=psi
    
    #    1. Estimate Angular Velocity & Compensate the campass deley
    
    
    #selection
    #using kalman velocity compensation 
    psi_comp=psi+campass_comp_para*ang_vel
    
    ang_vel=kalmf_ang_vel(psi_comp, klmf_moto_ctrl,comp_damp)
    #psi_comp=smith_compensation(kalmfinput,psi)
   
    
    
    #    2. Calculate control (use kalmf_ang or psi)
    
    # selection
    #klmf_moto_ctrl= psi_hinf_control(psi_comp, target_psi)
    klmf_moto_ctrl= psi_hinf_control(kalmf_ang, target_psi)
    
    
    
    #    3. Make a compensation
    comp_damp=nonlin_compensator(ang_vel)
    #moto_fin= klmf_moto_ctrl-Comp
    
    #     amplify the moto gain to 120
    moto_fin=(klmf_moto_ctrl-comp_damp)*moto_cmd_limit/moto_limit
#    if moto_fin>-2 and moto_fin<2:
#        moto_fin=0
    print("moto_fin",moto_fin)
    return moto_fin





#    YANG RUI 2014-4-25 OLD HINF CONTROLLER

#def psi_hinf_control(psi, target_psi):
#    #global variable
#    global P
#    global D
#    global I
#    global yold
#    global psilist
#    global xk
#    global v
#    if not hasattr(psi_hinf_control, "outfile"):
#         psi_control.outfile=open("logs/hinf/Hinf_log_psi_ctrl"+str(time.strftime("%y-%m-%d-%H-%M"))+".txt", "w+")
#        
#    #2014-3-31 edit by yangrui write a PID contorller here 
#   
#    #    psi: the yaw angle in rad
#    #    target_psi: the expected orientation in rad
#    
#   
#    y=psi#psilist.popleft()
#    r=target_psi
#    psi_err=r-y
#    uk=np.matrix(psi_err)
#    #hinf controller
#    a=np.matrix(" 0.6087    0.2024    0.2422    0.9682    0.3001;-0.0971    0.3359   -0.0264   -0.6901   -0.2185;   -0.0062    0.0268    0.9400   -0.4398   -0.1377;    0.0010    0.0591   -0.0849    0.4034   -0.1865;    0.0008    0.0192   -0.0280   -0.1855    0.9416")
#    b=np.matrix("0.3126;    0.4366;   -0.1440;   -0.0025;    0.0031")
#    c=np.matrix("-0.9402    4.9311    4.1302   30.0983    9.4274")
##    a=[
##    0.6087    0.2024    0.2422    0.9682    0.3001
##   -0.0971    0.3359   -0.0264   -0.6901   -0.2185
##   -0.0062    0.0268    0.9400   -0.4398   -0.1377
##    0.0010    0.0591   -0.0849    0.4034   -0.1865
##    0.0008    0.0192   -0.0280   -0.1855    0.9416
##    ];
##b= [
##    0.3126
##    0.4366
##   -0.1440
##   -0.0025
##    0.0031
##    ];
## 
##c=[-0.9402    4.9311    4.1302   30.0983    9.4274];
#
#    xkk=a*xk+b*uk
#    yk=c*xk
#    xk=xkk
#    #write campass and control command 
#    
#    v=yk[0,0]*120/5.8/2
#    psi_control.outfile.write("Psi: "+str(psi)+" :ctrl_cmd: "+str(v)+"\n")
#    psi_control.outfile.flush()
#    
#    #add a dead zone and saturation
#    if v>120:
#        v=120
#    elif v<-120:
#        v=-120
#    elif v>-2 and v<2:
#        if v>0:
#            v=v
#        else:
#            v=v
#     
#    moto_ref_psi =v
#    print(psi, target_psi, moto_ref_psi, P,I,D)
#    return moto_ref_psi