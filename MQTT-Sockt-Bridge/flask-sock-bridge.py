# This is a based on the example at:
# https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/example/app.py

import json
from threading import Lock
import mqtt_service as mqtt # our own shrink-wrapped MQTT service
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, send, emit, disconnect # 'connect' is not there !
from flask_socketio import join_room, leave_room, close_room, rooms

# pip install flask-socketio
# pip install gevent gevent-websocket

# config
lwt_topic = "tele/+/+/LWT"     # tele/IN-123/TOF-456/LWT
status_topic = "stat/#"        # stat/IN-123/TOF-456/POWER1
universal_topic = '#'
CMD_PREFIX = 'cmnd'                      
STATUS_PREFIX = 'stat'
TELE_PREFIX = 'tele'

# globals
# Set the async mode to "threading", "eventlet" or "gevent". 
# leave it as None for the application to choose the best option based on installed packages.
a_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-little-secret!'
# enable logger and engineio_logger for detailed connection issue messages
socketio = SocketIO(app, async_mode=a_mode, cors_allowed_origins="*")  #, logger=True, engineio_logger=True)

#-------------------------------------------------------------------------------------------------
bgnd_thread = None
thread_lock = Lock()

def worker_thread():
    print ('Worker thread starts..')
    for i in range (5):
        print ('---Tick!----')
        socketio.sleep(1) # coroutine!
    print ('Worker thread exits.')
        
def init_bgnd_thread():        
    global bgnd_thread
    with thread_lock:
        if bgnd_thread is None:
            print ('Starting background thread...')
            bgnd_thread = socketio.start_background_task (worker_thread)
#-------------------------------------------------------------------------------------------------
# SocketIO
#-------------------------------------------------------------------------------------------------         
@socketio.event
def connect():  # function name is taken as the event name
    print('\nA client has connected. SID=', request.sid)
    socketio.emit ('message', f'User {request.sid} is connected.')  

@socketio.on('disconnect')
def disconnect():
    print(f'A client disconnected. SID={request.sid}')
    socketio.emit ('message', f'User {request.sid} has disconnected.')   
    
@socketio.on('message')
def on_message(msg):
    print(f'Default handler: {msg}. SID={request.sid}')
    
@socketio.on('button_event')
def iot_event (jpayload):
    try:
        print(f'Command: {jpayload} from SID={request.sid}')
        #print (type(jpayload)) # dict
        topic = f"{CMD_PREFIX}/{jpayload['intof_id']}/{jpayload['device_id']}/{jpayload['relsen_id']}"
        mqtt.publish (topic, jpayload['desired_state'])    
    except Exception as e:
        print ('ERROR publishing to MQTT: ',str(e))
#-------------------------------------------------------------------------------------------------  
# app routes    
#-------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

# For testing: push any arbirary message to websocket clients
@app.route('/send/socket')
def send_to_socket (): 
    print (request.args)
    event = request.args.get('event', 'message')
    jpayload = request.args.get('msg', {'data':'NONE'})
    socketio.emit(event, jpayload)
    return {'result' : 'OK'}
    
# For testing: push any arbirary message to mqtt broker
@app.route('/send/mqtt')
def send_to_mqtt (): 
    print (request.args)
    topic = request.args.get('topic', 'intof/test/topic')
    jpayload = request.args.get('msg', {'data':'NONE'})
    mqtt.publish (topic, jpayload)
    return {'result' : 'OK'}    
#-------------------------------------------------------------------------------------------------
# MQTT
#-------------------------------------------------------------------------------------------------   
   
def lwt_handler (client, userdata, msg):
    payload = msg.payload.decode ('UTF-8')
    print (f' << {msg.topic} <- {payload}') 
    process_lwt (msg.topic, payload)
    
def status_handler (client, userdata, msg):
    payload = msg.payload.decode ('UTF-8')
    print (f' << {msg.topic} <- {payload}')   
    process_status (msg.topic, payload)
   
#------------------------------ business logic ----------------------------------------- 
    
# format: tele/IN-123/TOF-456/LWT   Online
def process_lwt (topic, payload):    
    sp = topic.split('/')
    if (len(sp) < 4):
        print ('\n* Malformed topic name!')
        return False
    prefix = sp[0]
    if (prefix != TELE_PREFIX):
        print ('Not an LWT message.')
        return False
    intof_id = sp[1]
    device_id = sp[2]
    msg = f'Device {intof_id}/{device_id} is {payload}!'
    print (msg)
    socketio.emit('from_bridge', msg)
    return True
    
# format: tele/IN-123/TOF-456/POWER1   ON   
def process_status (topic, payload):
    sp = topic.split('/')
    if (len(sp) < 4):
        print ('\n* Malformed topic name!')
        return False
    prefix = sp[0]
    if (prefix != STATUS_PREFIX):
        print ('Not a status report.')
        return False
    intof_id = sp[1]
    device_id = sp[2]
    relsen_id = sp[3]
    msg = f'Relay {intof_id}/{device_id}/{relsen_id} is {payload}.'
    print (msg)
    jpayload = {'intof_id':intof_id, 'device_id':device_id, 'relsen_id':relsen_id, 'current_state':payload}
    socketio.emit('from_bridge', jpayload)
    return True
    
#-------------------------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------------------------
           
if __name__ == '__main__':
    PORT = 5000
    print ('Shrink-wrapped MQTT client initializing..')
    init_bgnd_thread()  # dummy task, just for testing
    # mqtt is an imported global name, not an object created here
    # MQTT: The flow init-register-connect-start must be followed
    mqtt.init()   
    mqtt.register_callback (lwt_topic, lwt_handler, qos=1)
    mqtt.register_callback (status_topic, status_handler)
    mqtt.connect()        
    print ('Starting MQTT background job..')
    mqtt.start()
    print (f'Flask-SocketIO server listening on port {PORT}...')
    try:
        socketio.run(app, host='0.0.0.0', port=PORT)
    except KeyboardInterrupt:
        mqtt.stop()
    print ('Main thread quits.')     
     
#-------------------------------------------------------------------------------------------------
'''
TESTS:
http://localhost:5000/send/socket?event=message&msg={"data":"Hello...world"}
http://localhost:5000/send/mqtt?topic=intof/test/topix&msg={"data":"Hello, world"}
'''     