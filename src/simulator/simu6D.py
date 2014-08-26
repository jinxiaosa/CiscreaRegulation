import numpy as np
from numpy import pi
from dynamics import dx
import pylab as p
from scipy.integrate import ode
import numpy as np

M=40 #kg

#water density
rho=1000 #kg/m3

#drag coefficients
Cd=1 #dimensionless, 3D cubic shape
CE=0.438 #eddies

#propellers base angle
Theta0=pi/12

#propellers angle from 0 to 3
Theta=[Theta0, 2*pi-Theta0, pi-Theta0, pi+Theta0]

#propellers position
xprop=[0.2,0.2,-0.2,-0.2]
yprop=[0.2,-0.2,0.2,-0.2]

#ai (propellers force)
u=[10,-10,0,0,0]

#AUV l*w*h
dims=[0.6,0.6,0.2]

#initial conditions
x0=[0,0,0,0,0,0,0,0,0,0]

###precompute as much as possible###
cost=np.cos(Theta)
sint=np.sin(Theta)
rhocd=rho*Cd/2.
rhocdplh=rho*dims[2]*CE/128.
hw=dims[2]*dims[1]
lh=dims[2]*dims[0]
lw=dims[1]*dims[0]
Jd=M*(dims[0]**2+dims[1]**2)/12.
invM=1./M
Cdw=(CE/8.)*rho*dims[2]*(dims[0]+dims[1])*(dims[0]**2+dims[1]**2)**(3/2.)
Cdl=-0.5*(dims[0]*dims[1]+dims[1]*dims[2]+dims[2]*dims[0])/3
xprop=np.array(xprop)
yprop=np.array(yprop)
#pack these values for ODE
params_c=M,invM, xprop,yprop,cost,sint,rhocd, rhocdplh, hw, lh, lw, Cdw, Jd
r = ode(dx)#.set_integrator('dop853')
r.set_initial_value(x0,0).set_f_params((u,params_c))
t1=600
dt=0.01
res=[]
t=[]
while r.successful() and r.t < t1:
    params=u,params_c
    r.set_f_params(params)
    r.integrate(r.t+dt)
    res.append(r.y)
    t.append(r.t)
    if r.t>100:
        u=[10,10,0,0,0]
    if r.t>300:
        u=[0,0,0,0,0]
res=np.array(zip(*res))
x=res[8]
y=res[9]

p.figure()
p.subplot(411)
p.plot(x, y,label="trajectoire")
p.legend()
p.subplot(412)
p.plot(t,x, label="x")
p.legend()
p.subplot(413)
p.plot(t,y, label="y")
p.legend()
p.subplot(414)
p.plot(t,res[2], label="z")
p.legend()

p.figure()
p.subplot(311)
p.plot(t,res[4], label="dx")
p.legend()
p.subplot(312)
p.plot(t,res[5], label="dy")
p.legend()
p.subplot(313)
p.plot(t,res[6], label="dz")
p.legend()


p.figure()
p.plot(t,np.rad2deg(res[3])%360, label="cap")
#p.plot(np.rad2deg(np.arctan2(res[4],res[5])+np.pi/2), label="cap xy")


p.legend()
p.show()

print res[7][-1]

