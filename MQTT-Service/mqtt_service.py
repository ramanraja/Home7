# Connects to an AWS IoT end point and prints incoming messages.
# This version works well: See the published messages on AWS IoT console under Test tab on the left nav bar.
# You can use this program to send health check queries to Tasmota devices and print their response.
# Uses certificates generated using AWS Console
# https://aws.amazon.com/blogs/iot/how-to-implement-mqtt-with-tls-client-authentication-on-port-443-from-client-devices-python/
# https://aws.amazon.com/jp/blogs/iot/mqtt-with-tls-client-authentication-on-port-443-why-it-is-useful-and-how-it-works/

# IMPORTANT: 
# You MUST: (1) Download the CA and client certificates (2) enable the certificates on AWS console and (3) attach a policy with IoT permissions to the certificates.

import sys
import ssl
import time
import json
import datetime
from random import randint
import paho.mqtt.client as paho_mqtt
from mqtt_config  import MqttConfigurator

# globals
mqtt = None  # this is essential, since we are not implementing this as a class 
mqcon = MqttConfigurator()
subscribe_topics = {}  # list of topics to subscribe after every reconnect

#------------------------------ MQTT callbacks ----------------------------------------- 

def on_connect (client, userdata, flags, rc):
    print('\n*** Connected to MQTT broker. ***\n')
    # on reconnection, subscriptions should be automatically renewed:
    for key in subscribe_topics.keys():
        topic = key
        qos = subscribe_topics[topic]
        print (f'subscribing to {topic}, QOS={qos}')
        client.subscribe (topic, qos=qos)
 
def on_disconnect (client, userdata, rc):
    print('MQTT broker disconnected: ', aws_iot_endpoint)
    
def on_publish (client, userdata, mid):
    print(f'Published msg id: {mid}')   

def on_subscribe (client, userdata, mid, granted_qos):
    print(f'Subscribed; mid={mid}, granted QOS={granted_qos}')
    
def on_message_all  (client, userdata, msg):
    payload = msg.payload.decode ('UTF-8')
    print (f' << {msg.topic} <- {payload}') 
  
#---------------------------------------------- API ---------------------------------------- 
  
def init():
    global mqtt  # this is essential, since we are not using 'self.loop()' in a class 
 
    mqtt = paho_mqtt.Client (mqcon.get_client_id(), clean_session=mqcon.clean_session)   
    if mqcon.use_aws_broker:
        mqtt.tls_set_context (mqcon.get_ssl_context())
    mqtt.on_connect = on_connect
    mqtt.on_disconnect = on_disconnect
    mqtt.on_publish = on_publish
    mqtt.on_subscribe = on_subscribe
    ##mqtt.on_message = on_message_all
    # message callbacks will be added through register_callback()
    
def connect():    
    global mqtt
    print (f'Connecting to MQTT broker...')
    try:
        mqtt.connect (mqcon.mqtt_broker, 
            port = mqcon.mqtt_port, 
            keepalive = mqcon.keep_alive)  
    except Exception as e:                  
        # catching and burying this exception is essential: 
        # you can just ignore it, and mqtt will reconnect later   
        print ('\n*** MQTT Connection failed: ', str(e), '  ***\n')    

def loop():    #  do NOT call this in an async program!
    global mqtt  # this is essential
    # blocking call - reconnects automatically (useful esp. for mqtt listeners)
    print ('Starting a BLOCKING loop...')
    mqtt.loop_forever()    # blocking call; do NOT call this in an async program!

def start(): 
    global mqtt
    # Non-blocking mode (useful if you are also doing other business);
    # must have a matching loop_stop()
    print ('Starting a non-blocking MQTT loop...')
    mqtt.loop_start()       # starts a background thread
    time.sleep (1)
        
def stop():
    global mqtt
    print ('Stopping MQTT loop...')
    mqtt.loop_stop()   # kill the background thread     

def publish (topic, payload, qos=0):
    global mqtt  
    print (f' >> {topic} -> {payload}')
    if isinstance (payload, dict):
        payload = json.dumps(payload) # TODO: revisit the need for this
    mqtt.publish (topic, payload=payload, qos=qos, retain=False)    

def register_callback (topic, handler, qos=0):
    global mqtt
    subscribe_topics [topic] = qos
    mqtt.message_callback_add (topic, handler)
    print (f'Handler added: {topic}, QOS={qos}')
#-------------------------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------------------------
        
if (__name__ == '__main__'):
    print ('MQTT test runner starting..')
    # MQTT: The flow init-register-connect-start must be followed
    try:
        init()
        register_callback ('#', on_message_all)
        connect()
        start()
        count = 0
        while True:
            count += 1
            publish ('test/topic', f'Hello-{count}')
            time.sleep(30)
    except KeyboardInterrupt:
        stop()
    print ('Main thread quits.')  
        