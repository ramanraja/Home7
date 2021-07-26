# Motsen V 3.0
# Motesen.py 
# Motor and Sensor monitor

# TODO: use a timer instead of sleep()

class Motsen ():
    ALL_OK = 0
    COMM_FAIL = 1
    INFLOW_FAIL = 2
    OVERFLOW = 3
    HALFWAY_CROSS = 4
    NOT_MONITORING = 5
    
    MAX_INFLOW_COUNTER = 10
    MAX_COMM_COUNTER = 7
    
    def __init__ (self, name):
        self.name = name
        self.motor_on = False
        self.inflow_on = False
        self.overflow_on = False
        self.halfway_on = False
        
        self.inflow_failure = False
        self.comm_failure = False      
        self.inflow_counter = 0
        self.comm_counter = 0
        
    def getName (self):
        return self.name
    
    def isMotorOn (self):
        return self.motor_on
        
    def isCommFailure (self):
        return self.comm_failure
        
    def isInflowFailure (self):
        return self.inflow_failure
        
    def isOverflow (self):
        return self.overflow_on
    
    # status notifications from tank controller
    def onTankMessage (self, inflow, overflow, halfway):
        self.comm_failure = False
        self.comm_counter = self.MAX_COMM_COUNTER       # fill the leaky bucket  
        self.inflow_on = inflow
        self.overflow_on = overflow
        self.halfway_on = halfway
        
     
    # notifications from pump motor controller   
    def onMotorMessage (self, motor):    
        self.motor_on = motor
        if (self.motor_on == False):    # the motor was just stopped and we got notified
            self.overflow_on = False    # avoid false triggering at the beginning of the next cycle
            self.inflow_on = True       # prepare for when the motor is started again 
            print ("{} tank: monitoring is OFF.".format(self.name))   
            return                      #  no need for watching anything any more
        # start monitoring vital parameters
        print ("{} tank: monitoring is ON..".format(self.name))
        self.comm_counter = self.MAX_COMM_COUNTER      
        self.inflow_counter = self.MAX_INFLOW_COUNTER
        
        
    def onHalfwayMessage (self, halfway):
        self.halfway_on = halfway
        self.display()
        # self.halfway_crossed = True
        # TODO: automatically start motor if water goes below half way mark
        
        
    # the project main thread allots CPU time slice to each Motsen object for its processing
    # You MUST call this periodically (typically, once every second) from the program's main loop
    def process (self):
        if (self.motor_on == False):
            return self.NOT_MONITORING
        # Case 1: overflow; just raise an alarm immediately
        if (self.overflow_on):        
            print ("{} tank: OVERFLOW!".format(self.name))        
            return self.OVERFLOW
        # Case 2: motor ON, but no status from the tank
        if (self.comm_counter > 0):  
            self.comm_counter -= 1
            if (self.comm_counter == 0):
                self.comm_failure = True
                print ("{} tank: sensor is offline!".format(self.name))
                self.comm_counter = self.MAX_COMM_COUNTER  # restart comm-monitoring; keep alarming
                return self.COMM_FAIL
        # Case 3: motor ON, but inflow is absent
        if (self.inflow_on == True):
            return self.ALL_OK
        if (self.inflow_counter > 0):  
            self.inflow_counter -= 1
            if (self.inflow_counter == 0):
                self.inflow_failure = True
                print ("{} tank: inflow failure!".format(self.name))
                self.inflow_counter = self.MAX_INFLOW_COUNTER  # usually the motor will be stopped now, but
                return self.INFLOW_FAIL                        # keep the vigil on; restart monitoring inflow
        return self.ALL_OK       
                            
    
    # display status on LEDs or I2C display  
    def display (self):
        pass   #  TODO: implement
        
        
        
        