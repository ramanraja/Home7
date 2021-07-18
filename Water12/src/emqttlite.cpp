// emqttLite.cpp
// Uses Ethernet transport

#include "emqttLite.h"

EthernetClient   ethernet_client;
PubSubClient pubsub_client (ethernet_client);

extern void  app_callback (const char* msg);  // defined in the main .ino file
   
//------------------------------------------------------------------------------------------------
// Make a copy of the incoming message, since the internal buffer of PubSubClient will be
// reused at any time for Publish operations !
char rx_payload_string [MAX_MSG_LENGTH]; 

// static callback to handle mqtt command messages
void mqtt_callback (char* topic, byte* payload, unsigned int length) {
    SERIAL_PRINT (F("Rx msg @ "));
    SERIAL_PRINTLN (topic);
    if (length >= MAX_MSG_LENGTH) {
        SERIAL_PRINTLN (F("* Mqtt Rx message is too long ! *"));
        return;  // Just drop the incoming message 
    }
    char *ptr = rx_payload_string;
    for (int i = 0; i < length; i++) {   // ugly, but needed. TODO: find another way (memcpy?) 
       *ptr++ = (char)payload[i];        // ASSUMPTION: sizeof(char)==sizeof(byte) 
    }
    *ptr= '\0';
    //SERIAL_PRINTLN (rx_payload_string);  
    app_callback ((const char*)rx_payload_string);  
}
//------------------------------------------------------------------------------------------------
// class methods

EmqttLite::EmqttLite() {
}

void EmqttLite::init (Config *config_ptr) {
    this->pC = config_ptr;
    generateClientID ();
    SERIAL_PRINT (F("MQTT client id: "));
    SERIAL_PRINTLN (mqtt_client_id);  
    if (reconnect ())  // initial connection
        subscribe (pC->sub_topic);  // TODO: is this a sticky subscription ?
} 

// you must periodically call this function; othewise the MQTT pump will starve
void EmqttLite::update () {
    pubsub_client.loop ();       // keep the message pump running
}

bool EmqttLite::isConnected () {
    return (pubsub_client.connected ());
}

// NOTE: The main program must attempt to reconnect once in, say, 15 seconds
bool EmqttLite::checkConnection () {
    if (pubsub_client.connected ())
        return true;
    if (reconnect()) {
        subscribe (pC->sub_topic); 
        return true;
    }          
    return false;
}

//connect to mqtt broker
bool EmqttLite::reconnect () {
    SERIAL_PRINTLN (F("(Re)connecting to MQTT server..."));
    if (pubsub_client.connected())  
        pubsub_client.disconnect ();  // to avoid leakage ?
    pubsub_client.setServer (pC->mqtt_server, pC->mqtt_port);
 
 #ifdef USE_MQTT_CREDENTIALS
    if (pubsub_client.connect (mqtt_client_id, pC->mqtt_user, pC->mqtt_password)) {
 #else
    if (pubsub_client.connect (mqtt_client_id)) {
 #endif
        SERIAL_PRINTLN (F("Connected to MQTT broker."));     
        return true;
    } else {
        SERIAL_PRINT (F("MQTT connection failed, rc="));
        SERIAL_PRINTLN (pubsub_client.state());
        return false;
    }
}

//generate random mqtt clientID
void EmqttLite::generateClientID () {
    snprintf (mqtt_client_id, (TINY_STRING_LENGTH-1), "%s%X", MQTT_CLIENT_PREFIX, random(0xffff));  
}

//subscribe to the mqtt command topic
bool EmqttLite::subscribe (const char* topic) {
    SERIAL_PRINT (F("Subscribing to topic: "));
    SERIAL_PRINTLN (topic);  
    pubsub_client.setCallback (mqtt_callback);   // static function outside of the class
    bool result = pubsub_client.subscribe (topic, QOS);  
    if (result) 
        SERIAL_PRINTLN (F("Subscribed."));    
    else
        SERIAL_PRINTLN (F("Subscription failed."));
    return(result);
}

//send a message to the primary mqtt publish topic
bool EmqttLite::publish (const char* topic, const char *msg) {
    SERIAL_PRINT (F("Publishing: "));    
    SERIAL_PRINTLN (msg);
    int result = pubsub_client.publish (topic, msg);
    if (!result) 
        SERIAL_PRINTLN (F("Publishing failed."));    
    return ((bool)result);  // true: success, false:failed to publish
}


 
