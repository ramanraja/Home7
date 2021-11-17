/*
Intof SocketIO-MQTT bridge for AWS IoT
V1.0
November 2021 
Author: VR
*/
const socket = io();        
var button_states = [false, false, false, false]

socket.on('connect', function() {
	let msg = 'INF: Connected to MQTT bridge.';
	console.log(msg);
	//display_response (msg);
});

socket.on('disconnect', function() {
	let msg = 'INF: Disconnected from MQTT bridge.';
	console.log(msg);
	//display_response (msg);
});	

socket.on('error', function(msg) {
	console.log ('ERR: ' +msg);
	//display_response (msg);			
});

socket.on('message', function(msg) {
	console.log ('MSG: ' +msg);
	//display_response (msg);			
});

socket.on('from_bridge', function (jmsg) {
	msg = JSON.stringify(jmsg)
	console.log ('MQT: '+ msg);
	//display_response (msg);
	//jresponse = JSON.parse(msg);   /* resolve it into a json object */
	process_response (jmsg);      
});

function display_response (msg) {
	document.getElementById ("response_para").innerHTML = msg;
}

function process_response (jmsg) {
	button_id = jmsg.relsen_id;  /* TODO: revisit button naming convention: POWER1, POWER2 etc. */
	document.getElementById (button_id).innerHTML = jmsg.current_state; 
}

function send_to_socket (button_num) {
	let state = 'OFF';
	button_states[button_num-1] = !button_states[button_num-1]; // 1-based index is used
	if (button_states[button_num-1])
		state = 'ON';
	jpayload = {'intof_id' : 'IN-999999', 'device_id' : 'TOF-888888', 'relsen_id' : 'POWER'+button_num, 'desired_state' : state};
	console.log ('Sending to socket: ', jpayload);
    //socket.send (jpayload);                      /* this is valid */
	//socket.send (JSON.stringify (jpayload));     /* this is also valid */
	socket.emit ('button_event', jpayload);        /* only 'emit' can post to a custom event name */ 
}
 