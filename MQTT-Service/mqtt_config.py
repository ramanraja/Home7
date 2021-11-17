# Configures MQTT client to use either a regular broker or AWS broker with TLS
# Uses certificates generated using AWS Console:
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

# Environmentals (TODO: get these from .env, OS etc)

USE_AWS_BROKER = False # True # 
AWS_REGION = 'eu-east-3'   
AWS_USER_ID = 'xxxxxxxxxxx'
AWS_CREDENTIALS_BASE_DIR = 'C:/users/user/aws_credentials'
MQTT_TLS_PORT = 443  # port 443 works fine; no need for 8883; since this is a DIY implementation using ALPN  

MQTT_BROKER = '192.168.0.100'  # non-TLS broker
MQTT_PORT = 1883
MQTT_USER_ID = None
MQTT_PASSWORD = None
KEEP_ALIVE = 60

DEBUG_ENABLED = True  # disable this for production
VERSION = '1.0'
CLEAN_MQTT_SESSION = True

class MqttConfigurator ():
    def  __init__ (self):
        self.use_aws_broker = USE_AWS_BROKER
        self.clean_session = CLEAN_MQTT_SESSION
        self.keep_alive = KEEP_ALIVE
        self.user_id = MQTT_USER_ID
        self.password = MQTT_PASSWORD
        if self.use_aws_broker:
            self.configure_aws()
        else:
            self.configure_simple()
        self.print_config()
            
    def configure_aws (self):
        self.aws_region = AWS_REGION
        self.mqtt_broker = f'{AWS_USER_ID}-ats.iot.{AWS_REGION}.amazonaws.com'
        self.mqtt_port = MQTT_TLS_PORT
        self.ca  = f'{AWS_CREDENTIALS_BASE_DIR}/AmazonRootCA1.pem'
        self.certificate = f'{AWS_CREDENTIALS_BASE_DIR}/{AWS_REGION}/certificate.pem'
        self.private_key = f'{AWS_CREDENTIALS_BASE_DIR}/{AWS_REGION}/private.key'
    
    def configure_simple (self):    
        self.mqtt_broker = MQTT_BROKER
        self.mqtt_port = MQTT_PORT   
        
    def print_config (self):
        print (f'Shrink wrapped MQTT service V.{VERSION}')
        if not DEBUG_ENABLED :  
            print ('\n* Debug display of MQTT configuration objects disabled! *')
            return
        if USE_AWS_BROKER:
            print ('Using AWS-TLS client.')
            print (f'Open ssl version: {ssl.OPENSSL_VERSION}')
            print (f'AWS region: {self.aws_region}')
            print (f'AWS MQTT endpoint: {self.mqtt_broker}')    
            print (f'MQTT port: {self.mqtt_port}')  
            print (f'Root CA: {self.ca}')
            print (f'Client certificate: {self.certificate}') 
            print (f'Private key: {self.private_key}') 
            print (f'clean_session: {self.clean_session}')
        else:
            print ('Using simple non-TLS client.')
            print (f'MQTT broker: {self.mqtt_broker}')  
            print (f'MQTT port: {self.mqtt_port}') 
            print (f'user_id: {self.user_id}')
            if self.password: x='***'  # mask it, but indicate that a passwd exists
            else: x='None'
            print (f'password: {x}')    
   
    # SSL ALPN handshake -------------------------------------

    def get_ssl_context (self):
        if not USE_AWS_BROKER:
            print ('No SSL context: Not using TLS enabled broker.')
            return None
        try:
            ssl_context = ssl.create_default_context()
            protocol = "x-amzn-mqtt-ca"  # ALPN protocol
            ssl_context.set_alpn_protocols ([protocol])
            ssl_context.load_verify_locations (cafile = self.ca)
            ssl_context.load_cert_chain (certfile = self.certificate, keyfile = self.private_key)
            print ('Successfully created SSL context.')
            return  ssl_context
        except Exception as e:
            print("\n* ERROR: Failed to create SSL context! *\n")
            print (e)
        return None
         
    # API ------------------------------------------------------- 

    # Note: If client ID is constant, earlier subscriptions will still linger * 
    #       More seriously, you must not run more than one copy of this program at a time!
    # TODO: since this is going to be only a single instance of this app, make this a constant
    #       client ID with sticky sessions  
    def get_client_id (self, generate_random=True):
        if generate_random:
            client_id = f'intof-mqclient-{randint(1000,100000)}'
        else:
            client_id = 'intof-mqtt-client-Nov-2021'
        print (f'MQTT client ID: {client_id}')
        return client_id

#-------------------------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------------------------
        
if (__name__ == '__main__'):
    print ('AWS MQTT Configurator..')
    mqcon = MqttConfigurator()
    #mqcon.print_config()
    print()
    print ('Client ID: ', mqcon.get_client_id()) # False
    print ('SSL Context: ', mqcon.get_ssl_context())
    print ('clean session: ', mqcon.clean_session)
    print ('MQTT user id: ', mqcon.user_id)
    if mqcon.password: x='***'
    else: x='None'
    print (f"password: {x}")       
    print ('Done!')  
        