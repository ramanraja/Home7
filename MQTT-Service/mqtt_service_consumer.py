import mqtt_service as mqtt
import time

def on_message_handler  (client, userdata, msg):
    payload = msg.payload.decode ('UTF-8')
    print (f'<< {msg.topic} <- {payload}') 
    
# MAIN
if (__name__ == '__main__'):
    print ('AWS MQTT tester starting..')
    # MQTT: The flow init-register-connect-start must be followed
    try:
        mqtt.init()
        mqtt.register_callback ('#', on_message_handler)
        mqtt.connect()        
        mqtt.start()
        count=0
        while True:
            count+=1 
            mqtt.publish ('raja/test/topic',  f'Hello, World-{count}')
            time.sleep(30)        
    except KeyboardInterrupt:
        mqtt.stop()
    print ('Main thread quits.')    
    
    
    