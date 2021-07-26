# MonitorX.py
# Monitors Arduino water level controller & coordinates with pump motors
# uses classical Paho MQTT library with its own event loop
# New: Motsen class introduced
# pip install paho-mqtt
# Paho MQTT API doc:
# https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php

from Motsen import Motsen
import paho.mqtt.client as mqtt
import json
import time
import sys

#------------------------------ globals -------------------------------------------------------
server  = "192.168.0.99"  
port    = 1883
QOS     = 1
client  = None

# tank controller
pub_topic_tank   = "intof/tank/cmnd"               
sub_topic_tank   = "intof/tank/status"          

# pump motor
pub_topic_motor_prefix = "cmnd/blynk/POWER"   # suffix with 1-3 for the 3 motors
sub_topic_motor  = "stat/blynk/+"             

#------------------------------ callbacks ----------------------------------------------------- 

def on_connect (client, userdata, flags, rc):
    print ('Connected to MQTT server: ' +server)
    # on reconnection, will be automatically renewed
    client.subscribe ([(sub_topic_tank,QOS),(sub_topic_motor,QOS)])  

def on_publish (client, userdata, mid):
    #print ("Published msg id: "+str(mid))
    pass

def on_subscribe (client, userdata, mid, granted_qos):
    print ("Subscribed. Granted QOS=" +str(granted_qos))
    
def on_unsubscribe (client, userdata, mid):
    print ("Unsubscribed: " +str(mid))
        
def on_message_tank (client, userdata, msg):
    dmsg = msg.payload.decode ('UTF-8')
    print (msg.topic +" >>> " + dmsg) 
    parse_msg_tank (msg.topic, dmsg)
    
def on_message_motor (client, userdata, msg):
    dmsg = msg.payload.decode ('UTF-8')
    print (msg.topic +" >>> " + dmsg) 
    parse_msg_motor (msg.topic, dmsg)    
    
#---------------------------- business logic --------------------------------------------------
'''
Design Notes:
1) When the tank sensor is offline, just keep reminding it is offline. But do not switch off the motors:
    In case of sensor trouble, you can switch it off and at least use the motor manually.
2) If only one motor is ON, just enable the corresponding sensor (A or B type). Get C type packet only when 
    both the motors are ON.
      
TODO:
Use timers instead of sleep(1)

You send A 1 command. No 'A' packets are coming even after 6 seconds. Resend A 1 command.
You send A 0 command. Still the 'A' packets are coming. Resend the A 0 command.
Raise audible alarms.
Staus display on OLED I2C device or plain LEDs
When 'D' packets stop coming after 6 minutes, raise comm-failure alarm
Request for an 'O' packet once in 15 minutes and update the LED display.
-------------------------------------------------------------------------------------------------'''

def parse_msg_tank (topic, msg):
    ## jmsg = json.loads (msg)              #  if it is JSON
    if (msg[1] != ' '):
        print ('\n******* Invalid payload ! *******\n')  # TODO: remove this later
        return
    inflow = False
    overflow = False
    halfway = False
    if (msg[0] == 'A'):
        if (msg[2] == '1') : inflow = True
        if (msg[3] == '1') : overflow = True
        if (msg[4] == '1') : halfway = True
        drink_ms.onTankMessage (inflow, overflow, halfway)
    elif (msg[0] == 'B'):
        if (msg[2] == '1') : inflow = True
        if (msg[3] == '1') : overflow = True
        if (msg[4] == '1') : halfway = True    
        salt_ms.onTankMessage (inflow, overflow, halfway)    
    elif (msg[0] == 'C' or msg[0] == 'R'):
        if (msg[2] == '1') : inflow = True
        if (msg[3] == '1') : overflow = True
        if (msg[4] == '1') : halfway = True    
        drink_ms.onTankMessage (inflow, overflow, halfway)
        inflow = False
        overflow = False
        halfway = False        
        if (msg[6] == '1') : inflow = True
        if (msg[7] == '1') : overflow = True
        if (msg[8] == '1') : halfway = True
        salt_ms.onTankMessage (inflow, overflow, halfway)  
        if (msg[0] == 'R'):
            print ('\n* Tank controller rebooted! *\n')
            ping_sensors()   # prime the tank controller
            ping_motors()    # refresh the motor status; this will call operate_sensors()
    elif (msg[0] == 'D'):
        halfway1 = False
        halfway2 = False
        if (msg[2] == '1') : 
            halfway1 = True
        if (msg[3] == '1') : 
            halfway2 = True
        drink_ms.onHalfwayMessage (halfway1)
        salt_ms.onHalfwayMessage (halfway2)
    elif (msg[0] == 'E'):
        print ('\n* Data error! *\n') # TODO: resend request/cmd
        
        
def parse_msg_motor (topic, msg):
    ## jmsg = json.loads (msg)               #  if it is JSON
    if (topic.endswith ('RESULT')):
        return  # TODO: use the pattern filters of MQTT client!
    motor_status = False
    tank = 0
    if (msg == 'ON'):
        motor_status = True
    elif (msg != 'OFF'):
        print ('\n******* Invalid payload !. *******\n')  # TODO: remove this later
        return                
    if (topic.endswith ('POWER1')):
        tank = 1
        drink_ms.onMotorMessage (motor_status)
    elif (topic.endswith ('POWER2')):
        tank = 2
        salt_ms.onMotorMessage (motor_status)
    else:
        print ('\n******* Invalid payload !.. *******\n')  # TODO: remove this later
        return         
    operate_sensors ()   # send an appropriate data request to the sensor      


# Get both motor motor_statuses from the motsen, and decide if you want a C type packet (tank=3)
def operate_sensors ():
    motor1 = drink_ms.isMotorOn()
    motor2 = salt_ms.isMotorOn()
    if (motor1==True and motor2==True):
        start_sensor (3)   # C 1 command
        return
    if (motor1==False and motor2==False):
        stop_sensor (3)    # C 0
        return        
    if (motor1==True and motor2==False):
        start_sensor (1)   # A 1
        return  
    if (motor1==False and motor2==True):
        start_sensor (2)   # B 1
        return  


# TODO: call this when water goes just below halfway mark
def start_motor (tank_number):     
    topic = '{}{}'.format (pub_topic_motor_prefix, tank_number)
    cmd = 'ON'
    print ('Sending cmd:  {} >> {}'.format (topic, cmd))
    client.publish (topic, cmd)     
        
    
def stop_motor (tank_number):
    topic = '{}{}'.format (pub_topic_motor_prefix, tank_number)
    cmd = 'OFF'
    print ('Sending cmd:  {} >> {}'.format (topic, cmd))
    client.publish (topic, cmd)      
    

# request for motot status
def ping_motors ():
    print ('Pinging motors..')
    topic = '{}{}'.format (pub_topic_motor_prefix, '0')
    cmd = ''
    print ('Sending cmd:  {} >> {}'.format (topic, cmd))
    client.publish (topic, cmd)  
        
'''--------------------------------------
tank_number: 1,2 or 3
1 : drinking water (A type packet)
2 : salt water (B type packet)
3 : both tanks (C type packet)
--------------------------------------'''
def start_sensor (tank_number):
    if (tank_number == 1):
        cmd = 'A 1'
    elif (tank_number == 2):
        cmd = 'B 1'  
    else:
        cmd = 'C 1'
    print ('Sending request: ', cmd)
    client.publish (pub_topic_tank, cmd) 
    
 
# tank_number: 1,2 or 3
# 'A 0' and 'B 0' will not be normally called; included here only for completion
# NOTE: all the 3 calls below have identical effect: they move the sensor status to 'D 1'
def stop_sensor (tank_number):
    if (tank_number == 1):
        cmd = 'A 0'
    elif (tank_number == 2):
        cmd = 'B 0'  
    else:
        cmd = 'C 0'
    print ('Sending request: ', cmd)
    client.publish (pub_topic_tank, cmd)
    
    
# request for a one-off packet of type 'C' 
def ping_sensors ():
    cmd = 'O 1'    # the '1' is redundant, but kept for uniformity
    print ('Sending cmd: ', cmd)
    client.publish (pub_topic_tank, cmd)
    
#---------------------------- main ------------------------------------------------------------

PING_INTERVAL = 1
     
drink_ms = Motsen ("Drink")
salt_ms =  Motsen ("Salt")
     
# note: if client ID is constant, earlier subscriptions will still linger *     
client = mqtt.Client ("Intof_water-monitor_2021", clean_session=False)    # true
# This is needed for Adafruit broker only:
# client.username_pw_set ("raman_raja", "d11809xxxxxxxxxxxxx...d4afe")    # AIO key

client.on_connect     = on_connect
client.on_publish     = on_publish
client.on_subscribe   = on_subscribe
client.on_unsubscribe = on_unsubscribe
###client.on_message     = on_message
client.message_callback_add (sub_topic_tank, on_message_tank)
client.message_callback_add (sub_topic_motor, on_message_motor)

client.connect (server, port, keepalive=60)         # blocking call
#client.connect_async (server, port, keepalive=60)  # non blocking call

# Blocking mode (useful for mqtt listeners). It will reconnec automatically 
#client.loop_forever()                              # blocks the main thread

# Non-blocking mode (useful if you are also an mqtt sender)
client.loop_start()                                 # starts a background thread
time.sleep (2)

print ('\nStarting main loop..')
print ('Press ^C to quit')

ping_sensors()  # priming read
  
terminate = False
try:
    while not terminate:
        #ping_motors ()  # TODO: enable this with a periodic counter
        #ping_sensors()
        
        # allocate a CPU slice to the Motsen objects, as Motsen doesn't have its own thread:
        result = drink_ms.process()   # first tank
        if (result == Motsen.OVERFLOW or result == Motsen.INFLOW_FAIL):
            stop_motor (1)
        elif (result == Motsen.COMM_FAIL):
            operate_sensors()

        result = salt_ms.process()    # second tank
        if (result == Motsen.OVERFLOW or result == Motsen.INFLOW_FAIL):
            stop_motor (2)        
        elif (result == Motsen.COMM_FAIL):
            operate_sensors()
                        
        time.sleep (PING_INTERVAL)    #  TODO: replace sleep() with a timer
except KeyboardInterrupt:
    print ('\n^C pressed.')

try:
    client.unsubscribe (sub_topic_tank, QOS)
    client.unsubscribe (sub_topic_motor,QOS)  
    time.sleep(1)
except Exception as e:
    print (str(e))       
client.loop_stop()                                  # kill the background thread   
time.sleep(1)   
print ('Main thread quits.')                        

'''============================================================================================

Public brokers:
 server = 'broker.mqtt-dashboard.com'  # http://www.hivemq.com/demos/websocket-client/
 server = 'm2m.eclipse.org'
 server = 'test.mosquitto.org'
 server = 'io.adafruit.com'  
 server = 'localhost'                  # mosquitto -v
 port   = 8000                         # 1883

Test:
  mosquitto_sub -h 192.168.0.99 -t intof/tank/+  -v
  mosquitto_sub -h 192.168.0.99 -t stat/blynk/+ -v
  
  To ping the motors:
  mosquitto_pub -h 192.168.0.99 -t cmnd/blynk/POWER0 -m  "" 
  Simulate motor status:
  mosquitto_pub -h 192.168.0.99 -t stat/blynk/POWER1 -m  "ON"
  mosquitto_pub -h 192.168.0.99 -t stat/blynk/POWER1 -m  "OFF"  
  start/stop tank status:  
  mosquitto_pub -h 192.168.0.99 -t intof/tank/cmnd -m "A 1"
  mosquitto_pub -h 192.168.0.99 -t intof/tank/cmnd -m "A 0"
  mosquitto_pub -h 192.168.0.99 -t intof/tank/cmnd -m "N 0"
  
  mosquitto_pub -h 192.168.0.99 -t intof/tank/status -m  "A 010"
  mosquitto_pub -h 192.168.0.99 -t intof/tank/status -m  "A 000"
  NOTE: For JSON payloads, you must escape the quotes around key-value strings
        
On MQTT broker (Raspberry Pi):
  sudo systemctl stop  mosquitto.service  
  sudo systemctl start mosquitto.service
============================================================================================'''