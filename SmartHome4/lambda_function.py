# Alexa enabled Smart Home. Supported by an OEM Device Cloud (MariaDB database).
# For Alexa smat Home to work, create your lambda etc in eu-west-1 (Ireland).
# Register your devices through the Intof App and enter them in the Device DB.
# Ask Alexa to discover them. You can rename them using Intof App or the Amazon Alexa app.

##import uuid
import boto3
import json
import random
from alexa.skills.smarthome import AlexaResponse
import dataset
from user import UserMap
from device import Device

# Global variables

umap = None
device = None
lambda_region = 'eu-west-1'
CMD_PREFIX = 'cmnd'

def get_error_response (error_type, error_msg):
    response = AlexaResponse (
                    name = 'ErrorResponse',
                    payload = { 
                        'type': error_type, 
                        'message': error_msg
                    })
    return response
  
        
def validate_request (request):
    if 'directive' not in request:
        response = AlexaResponse (
                        name = 'ErrorResponse',
                        payload = { 
                            'type': 'INVALID_DIRECTIVE', 
                            'message': 'Invalid Alexa request; Missing key: directive'
                        })
        return response
    # payload version must be 3
    payload_version = request['directive']['header']['payloadVersion']
    if payload_version != '3':
        response = AlexaResponse (
                        name = 'ErrorResponse',
                        payload = {
                            'type': 'INTERNAL_ERROR', 
                            'message': 'Only Smart Home API version 3 is supported.'
                        })
        return response
    print ('-  Request validated.')
    return (None) # None = no error response; successfully validated
    
    
def get_name_and_space (request)    :
    # see what is being requested
    namespace = request['directive']['header']['namespace']
    name = request['directive']['header']['name']
    print ('-  Namespace: {}, Name: {}'.format (namespace, name))
    return (tuple((namespace, name)))
    
    
# https://developer.amazon.com/en-US/docs/alexa/account-linking/configure-authorization-code-grant.html    
# https://developer.amazon.com/en-US/docs/alexa/device-apis/alexa-authorization.html#directives
def handle_grant (request):
    print ('-  Code grant triggered!')
    # Note: This sample accepts any grant request
    # Use the Grant-Code and Grantee-Token to get Access-Token and Refresh-Token and save them in a DB
    grant_code = request['directive']['payload']['grant']['code']
    grantee_token = request['directive']['payload']['grantee']['token']
    print ('-  Grant code: ', grant_code)
    print ('-  Grantee token: ', grantee_token)
    result = save_grant (grant_code, grantee_token)
    if (result == False):
        response = AlexaResponse (
                        name = 'ErrorResponse',
                        payload = {
                            'type': 'INTERNAL_ERROR', 
                            'message': 'Failed to save grant code & token in DB.'
                        })
        return response 
    response = AlexaResponse (namespace='Alexa.Authorization', name='AcceptGrant.Response')
    return response


def handle_discovery (request):
    print ('-  Discovery initiated!')
    token = request['directive']['payload']['scope']['token']
    intof_id = umap.token_intof_map (token)
    if (intof_id == None):
        response = get_error_response ('REGISTRATION_ERROR', 'Unable to get the Intof user id.') # INVALID_AUTHORIZATION_CREDENTIAL / EXPIRD
        #return send_response (response.get())
        return response
    devices = device.get_devices (intof_id)
    if (devices == None):
        response = get_error_response ('DISCOVERY_ERROR', 'Unable to get your registered devices.')
    if  len(devices) == 0:
        response = get_error_response ('DISCOVERY_ERROR', 'You do not have any registered devices.')        
        return send_response (response.get())
    response = AlexaResponse (namespace='Alexa.Discovery', name='Discover.Response')
    # create a basic alexa capability...
    capability_alexa = response.create_payload_endpoint_capability()              
    # .. and a more specific capability
    capability_powercontroller = response.create_payload_endpoint_capability (   
                                       interface='Alexa.PowerController',
                                       supported=[{'name': 'powerState'}]) 
    for i in range (len(devices)): 
        response.add_payload_endpoint (
                    friendly_name = devices[i][1],
                    endpoint_id = devices[i][0],
                    capabilities= [capability_alexa, capability_powercontroller])                  
    return response    
    
    
def handle_power_state (request):
    # Note: This sample always returns a success response for either a request to TurnOff or TurnOn
    # TODO: handle other scenarios, other than on/off?
    endpoint_id = request['directive']['endpoint']['endpointId']
    name = name = request['directive']['header']['name']
    power_state_value = 'ON' if name == 'TurnOn' else 'OFF'
    correlation_token = request['directive']['header']['correlationToken'] # required in the response
    bearer_token = request['directive']['endpoint']['scope']['token']  # identifies the user
    
    intof_id = umap.token_intof_map (bearer_token)
    if (intof_id == None):
        response = get_error_response ('INTERNAL_ERROR', 'Unable to get the Intof user id.')    
        return send_response (response.get())
 
    # TODO: Check for device error in setting the state
    state_set = set_device_state (intof_id, endpoint_id, power_state_value)
    if (state_set == False):
        print ('-   Error setting the device state!')
        response = get_error_response ('ENDPOINT_UNREACHABLE', 'The device is not responding.') # TODO: use friendly name in the response
        return send_response (response.get())       
    response = AlexaResponse (correlation_token=correlation_token)
    response.add_context_property (namespace='Alexa.PowerController', name='powerState', value=power_state_value)
    return response


# https://developer.amazon.com/en-US/docs/alexa/account-linking/use-access-tokens.html
def set_device_state (intof_id, endpoint_id, power_state):
    print ('-  Setting device state to ' + power_state)
    #  NOTE: if the region name below is wrong, the MQTT message will be lost without warning
    client = boto3.client ('iot-data', region_name=lambda_region) # TODO: revisit this hard coded region!
    sp = endpoint_id.split('.')
    tasmota_topic = '{}/{}/{}/{}'.format (CMD_PREFIX, intof_id, sp[0], sp[1])
    print ('-  Publishing: {} -> {}'.format (tasmota_topic, power_state))
    mqtt_gateway_response = client.publish (topic=tasmota_topic, qos=0, payload=power_state) #  payload=json.dumps(payload)
    print ('-  MQTT result: ')
    print (mqtt_gateway_response)
    # TODO: revisit the following: is this enough indication of failure?
    if mqtt_gateway_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return True
    else:
        return False         

        
def create_user_id ():  # TODO: replace this with Intof ID
    return ('IN' + "%0.6d" % random.randint(0, 999999))
    # TODO: check for duplicate id and regenerate a new id, if necessary; or use uuid


def save_grant (grant_code, grantee_token):     # TODO: implement this !
    amazon_id = umap.token_amazon_map (grantee_token)
    print ('Amazon id for the grantee token: ', amazon_id)
    intof_id = umap.token_intof_map (grantee_token)
    if (intof_id == None):
        print (' *** Intof ID cannot be found from the grantee token. Creating my own ID.. ***')
        intof_id = create_user_id()
        print ('- Created intof ID: ', intof_id)
    else:
        print ('Intof id for the grantee token: ', intof_id)
    # TODO: save it in UserMap table
    db_result = umap.save_grant (intof_id, grant_code, grantee_token)
    return db_result


def send_response (response):
    # TODO Validate the response
    print('-  Lambda_handler response:')
    print(json.dumps(response))
    return response
#---------------------------------------------------------------------------------------------------           
def lambda_handler(request, context):
    global umap, device
    
    print('-  Lambda_handler request:')
    print(json.dumps(request))
    print('-  Lambda_handler context:')
    print(context)  

    response = validate_request (request)  # IF THERE IS NO ERROR, this returns a 'None' object 
    if response is not None:
        return send_response (response.get())
            
    #database_url = None     # use environment variable DATABASE_URL (defaults to 'sqlite:///:memory:')
    database_url = 'mysql://user:passwd@100.101.102.103:3306/customers'   
    print ('Using Database: ', database_url)
    
    try:
        if database_url is None:
            db = dataset.connect()   
        else:
            db = dataset.connect (database_url) 
    except Exception as e:
        print ("EXCAPTION: Could not connect to database; "+str(e))
        response = get_error_response ('DATABASE_ERROR', 'Could not connect to database.')
        return send_response (response.get())
    umap = UserMap (db)  # you must always call setup() after this
    table_exists = umap.setup()  
    if (not table_exists):
        response = get_error_response ('DATABASE_ERROR', 'User table is missing.')
        return send_response (response.get())
    device = Device (db)  # you must always call setup()  
    table_exists = device.setup() 
    if (not table_exists):
        response = get_error_response ('DATABASE_ERROR', 'Device table is missing.')
        return send_response (response.get())

    (namespace, name) = get_name_and_space (request) 
    
    if namespace == 'Alexa.Authorization':  # the user has just enabled the skill
        if name == 'AcceptGrant':
            response = handle_grant (request)
            return send_response (response.get())    
    
    if namespace == 'Alexa.Discovery':
        if name == 'Discover':   
            response = handle_discovery (request)
            return send_response (response.get())        

    if namespace == 'Alexa.PowerController':
        response = handle_power_state (request)
        return send_response (response.get())
    
    # None of the above
    response = get_error_response ('INVALID_DIRECTIVE', 'Invalid Alexa request; Unknown directive')
    return send_response (response.get())

#----------------------------------------------
# MAIN    
#----------------------------------------------
if (__name__ == '__main__'):
    discover = {
      "directive": {
        "header": {
          "namespace": "Alexa.Discovery",
          "name": "Discover",
          "payloadVersion": "3",
          "messageId": "1234567890"
        },
        "payload": {
          "scope": {
            "type": "BearerToken",
            "token": "dummy-access-token"
          }
        }
      }
    }
    lambda_handler(request=discover, context='CTX')
'''---------------------------------------------------------------------------------------------------
Test inputs
Grant:
{
  "directive": {
    "header": {
      "namespace": "Alexa.Authorization",
      "name": "AcceptGrant",
      "payloadVersion": "3",
      "messageId": "2233567890"
    },
    "payload": {
        "grant": {
           "code" : "this-grant-code-has-grandeur1"
        },
        "grantee": {
           "token": "a-generous-grant-token1"
      }
    }
  }
}            
------------------------            
Discovery:
{
  "directive": {
    "header": {
      "namespace": "Alexa.Discovery",
      "name": "Discover",
      "payloadVersion": "3",
      "messageId": "1234567890"
    },
    "payload": {
      "scope": {
        "type": "BearerToken",
        "token": "dummy-access-token"
      }
    }
  }
}
-------------------------
PowerState:
{
  "directive": {
    "header": {
      "namespace": "Alexa.PowerController",
      "name": "TurnOff",
      "correlationToken": "dummy-access-token",
      "payloadVersion": "3"
    },
    "endpoint": {
      "endpointId": "intof_856CD8.POWER1"
    }
  }
}
--------------------------
Error1:
{
  "misdirective": {
    "header": {
      "namespace": "Alexa.Discovery",
      "name": "Discover",
      "payloadVersion": "3",
      "messageId": "1234567890"
    },
    "payload": {
    }
  }
}
--------------------------
Error2:
{
  "directive": {
    "header": {
      "namespace": "Alexa.Discovery",
      "name": "Discover",
      "payloadVersion": "2",
      "messageId": "1234567890"
    },
    "payload": {
    }
  }
}
--------------------------
Error3:
{
  "directive": {
    "header": {
      "namespace": "Dummy.Name.Space",
      "name": "Dummy.Name",
      "payloadVersion": "3",
      "messageId": "1234567890"
    },
    "payload": {
    }
  }
}
----------------------------------------------------
Open Access policy for the lambda:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:Connect",
                "iot:Publish",
                "iot:Subscribe",
                "iot:Receive",
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
----------------------------------------------------------------------------------------------------'''