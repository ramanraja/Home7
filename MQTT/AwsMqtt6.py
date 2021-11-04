# This simple example creates a connection to the AWS IoT endpoint and publishes a message to it.
# This version works well: See the published messages on AWS IoT console under Test tab on the left nav bar.
# You can use this program to send health check queires to Tasmota devices and print their response.
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
import paho.mqtt.client as paho_mqtt

'''
# Alexa enabled lambda in EU-West1 (Ireland) 
aws_region = 'eu-west-1'
aws_iot_endpoint = "xxxxxxxxx-ats.iot.eu-west-1.amazonaws.com"    # NOTE: this is without any protocol indicator like https://
ca = "../credentials/AmazonRootCA1.pem" 
cert = "../credentials/Ireland-certificate.pem" 
private = "../credentials/Ireland-private.key" 
'''

#  US-East2 (Ohio) 
aws_region = 'us-east-2'
aws_iot_endpoint = "xxxxxxxxx-ats.iot.us-east-2.amazonaws.com"    # NOTE: this is without any protocol indicator like https://
ca = "../credentials/AmazonRootCA1.pem" 
client_certificate = "../credentials/Ohio-certificate.pem" 
private_key = "../credentials/Ohio-private.key" 

# globals
terminate = False
mqtt = None
pub_topic = "cmnd/IN-999999/TOF-888888/POWER2"     # publish on this
sub_topic_lwt = "tele/+/+/LWT"                     # listen on this
sub_topic_status = "stat/#"     
CMD_PREFIX = 'cmnd'                      
STATUS_PREFIX = 'stat'
TELE_PREFIX = 'tele'

#---------------------------------- SSL handshake -------------------------------------
def get_ssl_context():
    try:
        ssl_context = ssl.create_default_context()
        protocol = "x-amzn-mqtt-ca"  # ALPN protocol
        ssl_context.set_alpn_protocols ([protocol])
        ssl_context.load_verify_locations (cafile=ca)
        ssl_context.load_cert_chain (certfile=client_certificate, keyfile=private_key)
        return  ssl_context
    except Exception as e:
        print("* Could not get SSL context! *")
        raise e
         
#------------------------------ MQTT callbacks ----------------------------------------- 

def on_connect (client, userdata, flags, rc):
    print('Connected to MQTT broker.')
    # on reconnection, subscriptions should be automatically renewed:
    client.subscribe (sub_topic_lwt, qos=1)
    client.subscribe (sub_topic_status, qos=0)  
 
def on_disconnect (client, userdata, flags, rc):
    print('MQTT server connection lost: ', aws_iot_endpoint)
    
def on_publish (client, userdata, mid):
    print("Published msg id: "+str(mid))  #  msg.payload.decode ('UTF-8')

def on_subscribe (client, userdata, mid, granted_qos):
    print("Subscribed; mid="+str(mid)+", granted QOS="+str(granted_qos))
    
def on_message_lwt (client, userdata, msg):
    payload = msg.payload.decode ('UTF-8')
    print (f' <<< {msg.topic} --> {payload}') 
    handle_lwt (msg.topic, payload)
    
def on_message_status (client, userdata, msg):
    payload = msg.payload.decode ('UTF-8')
    print (f' <<< {msg.topic} -> {payload}')   
    handle_message (msg.topic, payload)
    
#------------------------------ business logic ----------------------------------------- 
    
def handle_lwt (topic, payload):    
    sp = topic.split('/')
    if (len(sp) < 4):
        print ('\n** Malformed topic name! **\n')
        return False
    prefix = sp[0]
    if (prefix != TELE_PREFIX):
        print ('Not an LWT message.')
        return False
    intof_id = sp[1]
    device_id = sp[2]
    print (f'({intof_id}:{device_id}) is {payload}')
    
def handle_message (topic, payload):
    sp = topic.split('/')
    if (len(sp) < 4):
        print ('\n** Malformed topic name! **\n')
        return False
    prefix = sp[0]
    if (prefix != STATUS_PREFIX):
        print ('Not a status report.')
        return False
    intof_id = sp[1]
    device_id = sp[2]
    relsen_id = sp[3]
    print (f'({intof_id}:{device_id})/{relsen_id} is {payload}')
    
#-------------------------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    print ('Device Simulator V 1.0 starting...')
    print ("open ssl version:{}".format (ssl.OPENSSL_VERSION))
    print ('AWS region: {}'.format (aws_region))
    print ("AWS end point: {}".format (aws_iot_endpoint))
    print ("Publishing topic: {}".format(pub_topic))

    mqtt = paho_mqtt.Client()
    context= get_ssl_context()
    mqtt.tls_set_context (context)
    mqtt.on_connect = on_connect
    mqtt.on_disconnect = on_disconnect
    mqtt.on_publish = on_publish
    mqtt.on_subscribe = on_subscribe
    ##mqtt.on_message = on_message
    mqtt.message_callback_add (sub_topic_lwt, on_message_lwt)
    mqtt.message_callback_add (sub_topic_status, on_message_status)
        
    try:
        print ("\nConnecting to AWS...")
        # port 443 works fine; no need for 8883; since this is a DIY implementation using ALPN
        mqtt.connect(aws_iot_endpoint, port=443, keepalive=60)  
        print (f"\n*** Connected to AWS MQTT broker {aws_iot_endpoint}, port {443}. ***\n")
    except Exception as e:  # catching this exception is essential *
        print ('\n** MQTT Connection failed: ', str(e), '  **\n') # ignore the exception, it will reconnect later

    #mqtt.loop_forever()    # blocks the main thread; useful for listener-only applications

    # Non-blocking mode (useful if you are also doing other business);
    # must have a matching loop_stop()
    mqtt.loop_start()       # starts a background thread
    time.sleep (1)
        
    print ('\nStarting main loop..')
    print ('Press ^C to quit')
    try:
        count = 0
        while not terminate:  # the main loop
            count += 1
            #now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            #jnow = {"Time" : now}
            #print ("Heart beat: {}".format(jnow))
            if (count%2==0) : command = 'OFF'
            else: command = 'ON'
            print (f'Publishing:{pub_topic} -> {command}')
            mqtt.publish (pub_topic, command)
            time.sleep (10)  
    except KeyboardInterrupt :
        print ('^C Pressed.')
    terminate = True
    mqtt.loop_stop()   # kill the background thread   
    time.sleep(1)   
    print ('Main thread ends.')    
        