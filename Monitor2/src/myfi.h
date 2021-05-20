// myfi.h

#ifndef MYFI_H
#define MYFI_H

#include "common.h"
#include "keys.h"
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>

class MyFi {
public:
    MyFi();
    bool init ();
    bool init (int octet3, int octet4);
    bool reinit();
    void setStaticIP ();
    void disable();
    bool isConnected();
    bool reconnect();
    bool reconnect (bool switch_off);
    bool update();
    void dump();
private:
    bool set_static_ip = true;
    int oct3, oct4;
    ESP8266WiFiMulti wifi_multi_client;
};

#endif 
