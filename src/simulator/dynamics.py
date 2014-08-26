import numpy as np

def dx(t,x,args):    
    u, params_c=args
    M,invM, xprop,yprop,cost,sint,rhocd, rhocdplh, hw, lh, lw, Cdw, Jd=params_c
    u=np.array(u)
    #heading
    psi=x[3]
    spsi=np.sin(psi)
    cpsi=np.cos(psi)
    
    #speeds
    sp_x2=np.abs(x[4])*x[4]
    sp_y2=np.abs(x[5])*x[5]
    #sum ai*cos/sin
    Sac=np.sum(u[:-1]*cost)
    Sas=np.sum(u[:-1]*sint)
    
    dx4b=invM*(Sac-rhocd*hw*sp_x2)
    dx5b=invM*(-Sas-rhocd*lh*sp_y2)
    dx6b=invM*(u[-1]-rhocd*lw*np.abs(x[6])*x[6])

    dx7=Jd*(np.sum(u[:-1]*(-xprop*sint-yprop*cost))-
            Cdw*abs(x[7])*x[7])
        #rhocdplh*abs(x[7])*x[7]*l4w4)
    
    if abs(x[7])<1e-3:
        x[7]=0
    
    dxr=cpsi*x[4]+spsi*x[5]
    dyr=-spsi*x[4]+cpsi*x[5]
    
    return [x[4],x[5],x[6],x[7],dx4b,dx5b,dx6b,dx7, dxr, dyr]