import types
import inspect
import operator
import time
import threading


class Plugins:
    #all references to self are relative to the ciscrea instance we will
    #bind these methods to, NOT to a Plugins instance which should never be
    #instanciated anyway.
    
    @staticmethod
    def pwm(self, motor_idx, speed):
        try: 
            self.pwm_started
        except:
            #watchod thread, one per motor
            def __pwm_update(self, motor_idx):
                while not self.exit:  
                    self.pwmlock[motor_idx].acquire()
                    pwm_cmd=self.pwm_cmd[motor_idx]
                    self.pwmlock[motor_idx].release()
                    #pwm_cmd integer [-100:100]
                    #100 means dt for motor on will be equal to 1/pwm_freq
                    #pwm_freq is 10hz
                    
                    pwm_freq=2
                    
                    if pwm_cmd==0:
                        self.motor_speed(motor_idx, 0)
                        time.sleep(0.1)
                    else:

                        sgn=int(abs(pwm_cmd)/pwm_cmd)
                        dt=pwm_cmd/100./pwm_freq
                        print dt, 1./pwm_freq-dt, sgn*255
                        self.motor_speed(motor_idx, sgn*255)
                        time.sleep(dt)
                        self.motor_speed(motor_idx, sgn)
                        time.sleep(1./pwm_freq-dt)
                    
            #bind __pwm_update to this ciscrea instance
            self.__pwm_update=types.MethodType(__pwm_update, self)
            
            #list of pwm commands, one per motor
            self.pwm_cmd=[0,0,0,0,0]
            
            #we need as much threads as motors
            self.pwmlock=[]
            for idx in range(5):
                #pwm synchro mutex
                self.pwmlock.append(threading.Lock())
                threading.Thread(target=self.__pwm_update, args=(idx,)).start()

            #raise flag
            self.pwm_started=True

            pass

        print "COMMANDE RECU POUR MOTEUR %d VALEUR %d"%(motor_idx, speed)
        self.pwmlock[motor_idx].acquire()
        self.pwm_cmd[motor_idx]=speed
        self.pwmlock[motor_idx].release()
        
        
        
        
def add_module(ciscrea, fname):
    #get all available plugin methods
    avail=zip(*inspect.getmembers(Plugins, operator.isCallable))
    if fname in avail[0]:
        #bind the method to this ciscrea instance
        new_method=types.MethodType(avail[1][avail[0].index(fname)], ciscrea)
        #assign the method to the instance
        setattr(ciscrea,fname,new_method)
