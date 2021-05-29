// myfimulti.h

#ifndef MYFI_MULTI_H
#define MYFI_MULTI_H

/****
TODO:  if you connected to the mobile hotspot last time, don't wait for it next time also, ignoring the router;
    The router, if present, should get precedence over mobile hotspot.
TODO: Scan for wifi networks and connect to the one available (and the one with max RSSI)
TODO: keep doubling the tick interval from 1 sec, 2,4,8..128 seconds. (Then reboot ?). This will take care
   of the case where the device is running at a remote farm, and will get WiFi only when we visit the
   place and switch on our mobile hot spot.

WiFi status issues:
Wifi.status() always shows WL_CONNECTED even when the router is turned off:
https://github.com/esp8266/Arduino/issues/4352
https://github.com/esp8266/Arduino/issues/2593
https://github.com/esp8266/Arduino/issues/2186 
***/

#include <ESP8266WiFi.h>
#include "keys.h"
#include "common.h"

class MyfiMulti {
public:
    bool init();  // This does not return for almost 1 minute *
    bool init(int octet3, int octet4); // for static IP of the form 192.168.x.x
    bool re_init();
    int scan();  // scan for wifi networks

    void set_static_IP (int octet3, int octet4); 
    void set_host_name();  // auto generated name from MAC address
        
    bool is_connected (); 
    void update ();  // You are supposed to call this every second from the main app! (TODO:our own timer)
    void dump(); 

    bool ON = 0;  // for an active low LED; reverse them for active high
    bool OFF= 1;
    
    const char *HOST_NAME_PREFIX = "intof";
    int TICK_INTERVAL = 1000;    // millisec;   TODO: keep doubling this interval
    int ATTEMPT_DELAY =  250;    // millisec
    int MAX_ATTEMPTS  =  100;    // 100*250 = 25 seconds
    int MAX_CONNECTIONLESS_TIME = 180;  // NOTE: this is in units of TICK_INTERVAL
    // at 1 second tick interval, this will trigger reinitialization if connection is lost for 3 minutes
    // TODO: keep doubling TICK_INTERVAL, and this will automatically double.
private:

    bool connect_secondary();
    bool connect_primary();
    bool connect_auto();
    bool configure_wifi();
    void blink();
    void led_off();
    void led_on(); 
    bool vote_connected (int stage); 
    
    byte LED = 2;
    unsigned long last_update = 0;  // timestamp
    int connectionless_time = 0;    // how long we have been without wifi
    int octet3 = 0;  // the first two octets are assumed to be 192, 168
    int octet4 = 0;
};

#endif
