import inspect
import operator
import types

class Console:
    def __init__(self, auv):
        self.auv=auv
        print "Type help to get help"
        #get all known console and auv commands
        cmds=inspect.getmembers(self.auv, operator.isCallable)+\
            inspect.getmembers(self, operator.isCallable)
        self.commands=zip(*cmds)
        
        #ugly but it works...
        while not self.auv.exit:
            input_cmd=(raw_input('Ciscrea shell:> ')).split()
            if len(input_cmd)==0 or input_cmd[0][0]=="_":
                continue
            
            user_cmd=input_cmd[0]
            user_args=[]

            try:
                for i in range(1,len(input_cmd[1:])+1):
                    if not '"' in input_cmd[i]:
                        to_add=int(input_cmd[i])
                    else:
                        to_add=input_cmd[i][1:-1]
                    user_args.append(to_add)
            except Exception, e:
                print "Arguments can only be integers or double quoted strings"
                print e
                continue
            
            if user_cmd in self.commands[0]:
                methodToCall=self.commands[0].index(user_cmd)
            else:
                print "I'm afraid I can't do that"
                continue
            
            try:
                res=self.commands[1][methodToCall](*user_args)
            except Exception, e:
                print "Something went wrong with your arguments"
                print e
                continue
            
            if res is not None:
                print res
            else:
                print "OK"
 
    
    def help(self, str=None):
        """
        Print default help string
        Optionnal argument: command to get help string from, quoted string
        Return value: help string
        """
        
        if str in self.commands[0]:
            cmd=self.commands[0].index(str)
            help_str=self.commands[1][cmd].__doc__
        else:
            help_str="Known commands are:\n"
            nb_found=1
            for cmd in self.commands[0]:
                if cmd[0] is not "_":
                    help_str+="[%d] %s\n"%(nb_found,cmd)
                    nb_found+=1
                    
            help_str+="Type help \"command name\" to get command specific help"
        return help_str
    #below some dumb open loop commands to check the motors    
    def forward(self, value):
        """
        Dumb open loop forward command
        Argument: motors voltage, integer between 0 and 255
        Return value: None
        """
        
        for i in range(4):
            self.auv.motor_speed(i, value*(-1)**(i<2))
            
    def backward(self, value):
        """
        Dumb open loop backward command
        Argument: motors voltage, integer between 0 and 255
        Return value: None
        """
        self.forward(-value)
        
    def down(self, value):
        """
        Dumb open loop down command
        Argument: motors voltage, integer between 0 and 255
        Return value: None
        """
        self.auv.motor_speed(4, value)
            
    def up(self, value):
        """
        Dumb open loop up command
        Argument: motors voltage, integer between 0 and 255
        Return value: None
        """
        self.down(-value)
        