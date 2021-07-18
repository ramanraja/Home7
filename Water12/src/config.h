// config.h

#ifndef CONFIG_H
#define CONFIG_H

#include <Ethernet.h>

#define  MQTT_CLIENT_PREFIX  "INTOF_"

class Config {
  public:
    void init();
    
    char *mqtt_server = "192.168.0.99"; 
    int mqtt_port = 1883;
    //char *mqtt_user = "";
    //char *mqtt_password = "";
    
    // Enter any unique MAC address for your controller below.
    // Newer Ethernet shields have a MAC address printed on them
    byte mac[6] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0x01 };
    
    // Specify a static IP address, in case DHCP fails 
    // Maithri
    IPAddress device_ip = IPAddress(192, 168, 0, 177);
    IPAddress router_ip = IPAddress(192, 168, 0, 1);
    
    // Mithila
    //IPAddress device_ip = IPAddress(192, 168, 1, 177);
    //IPAddress router_ip = IPAddress(192, 168, 1, 1);
    
    char *pub_topic = "intof/tank/status";
    char *sub_topic = "intof/tank/cmnd";
};

#endif