// emqttlite.h
// Ethernet based MQTT client

#ifndef EMQTTLITE_H
#define EMQTTLITE_H

#include "ether.h"
#include "config.h"
#include "common.h"
#include <PubSubClient.h>   // https://github.com/knolleary/pubsubclient 

/////#define USE_MQTT_CREDENTIALS

class EmqttLite {
  public:
    EmqttLite();
    void init (Config *config_ptr);
    void update ();
    bool reconnect ();
    bool isConnected ();
    bool checkConnection ();
    void generateClientID ();
    bool subscribe (const char* topic);
    bool publish (const char *topic, const char *msg);
    
    int QOS=0; 
  private:    
    char mqtt_client_id [TINY_STRING_LENGTH];   
    Config *pC;
};

#endif
