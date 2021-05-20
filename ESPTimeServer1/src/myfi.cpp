// myfi.cpp
// TODO: exponentially increase the retry time interval if you cannot connect to wifi. (And at some point, reboot ESP?)

#include "myfi.h"

MyFi::MyFi() {
}

bool MyFi::init () {
    return (init(0,0));
}
 
bool MyFi::init (int octet3, int octet4) {
    if (octet3==0 && octet4==0) {
        set_static_ip = false;
    }
    else {
        set_static_ip = true;
        oct3 = octet3;
        oct4 = octet4;
    }
    int MAX_ATTEMPTS = 20;  // 5 sec
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(250);
        SERIAL_PRINT ("."); 
        attempts++;
        if (attempts >= MAX_ATTEMPTS) {
            SERIAL_PRINTLN (F("\nMyFi did not auto-connect. Initializing again.."));
            break;
        }    
    }
    SERIAL_PRINTLN();
    if (WiFi.status() != WL_CONNECTED)  
        return reinit();
    
    // we are not connected to wifi
    if (set_static_ip)
        setStaticIP();
    dump();
    return true; // connected to saved AP, so return success
}
    
bool MyFi::reinit () {    
    // Initial connection failed, initialize wifi again
    // WiFi.disconnect();  // https://github.com/tzapu/WiFiManager/blob/master/WiFiManager.cpp
    WiFi.mode(WIFI_OFF);  // Prevents reconnection issue (taking too long to connect) ***
    delay(1000);
    // it is important to set STA mode: https://github.com/knolleary/pubsubclient/issues/138
    WiFi.mode(WIFI_STA);   // 8266 defaults to STA+AP mode !
    wifi_set_sleep_type(NONE_SLEEP_T);  // revisit & understand this
    //wifi_set_sleep_type(LIGHT_SLEEP_T);    
    
    SERIAL_PRINTLN(F("Enlisting SSIDs:"));  
    wifi_multi_client.addAP(AP_SSID1, AP_PASSWD1);
    SERIAL_PRINTLN(AP_SSID1);
    if (strlen(AP_SSID2) > 0) {
        wifi_multi_client.addAP(AP_SSID2, AP_PASSWD2); 
        SERIAL_PRINTLN(AP_SSID2);
    }  
    int MAX_ATTEMPTS = 40;  // 10 sec
    int attempts = 0;
    while (wifi_multi_client.run() != WL_CONNECTED) {   
        delay (250);
        SERIAL_PRINT ("+"); 
        attempts++;
        if (attempts >= MAX_ATTEMPTS) {
            SERIAL_PRINTLN (F("\nMyFi[1]: Could not connect to WiFi")); 
            return false;
        }
    }
    SERIAL_PRINTLN();
    if (set_static_ip)
        setStaticIP();    
    dump ();
    return true; 
} 

void MyFi::setStaticIP () {
    SERIAL_PRINT (F("Setting static IP: 192.168."));
    SERIAL_PRINT (oct3);
    SERIAL_PRINT (".");
    SERIAL_PRINTLN (oct4);
    IPAddress ip (192,168, oct3, oct4);
    IPAddress gateway (192,168,oct3,1);  // NOTE this assumption about octet3 !
    IPAddress subnet (255,255,255,0);
    WiFi.config (ip,gateway,subnet);
}

bool MyFi::isConnected() {
    return (WiFi.status() == WL_CONNECTED); 
}

// CAUTION: If there is no wifi, reconnect() takes > 10 seconds to return
bool MyFi::update() {
   if (WiFi.status() == WL_CONNECTED)  
      return true;
   return (reconnect());
}

// Do NOT call this in the main loop ! It takes 10 sec to time out.
bool MyFi::reconnect () {
    SERIAL_PRINTLN (F("MyFi: Reconnecting to Wifi.."));
    WiFi.mode (WIFI_STA);
    int MAX_ATTEMPTS = 40;  // 10 sec
    int attempts = 0;
    bool connected = true;
    while (wifi_multi_client.run() != WL_CONNECTED) {  // run() alone is not sufficient to reconnect ! sometimes it freezes !
        delay (250);
        SERIAL_PRINT ("."); 
        attempts++;
        if (attempts >= MAX_ATTEMPTS) {
            SERIAL_PRINTLN (F("\nMyFi[2]: Could not connect to WiFi")); 
            connected = false;
            break;
        }
    }
    SERIAL_PRINT("\nMyFi: Wifi connected? : "); 
    SERIAL_PRINTLN(connected);    
    if (connected)
        dump();  
    return(connected);
}

void MyFi::disable() {
    SERIAL_PRINTLN (F("\nSwitching off wifi.."));
    WiFi.disconnect(); 
    WiFi.mode(WIFI_OFF);
    WiFi.forceSleepBegin();
    delay(10); 
}

void MyFi::dump() {
  SERIAL_PRINT(F("\nConnected to WiFi SSID: "));
  SERIAL_PRINTLN(WiFi.SSID());

  // print the WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  SERIAL_PRINT(F("My IP Address: "));
  SERIAL_PRINTLN(ip);

  // print the received signal strength
  long rssi = WiFi.RSSI();
  SERIAL_PRINT(F("Signal strength (RSSI):"));
  SERIAL_PRINT(rssi);
  SERIAL_PRINTLN(F(" dBm"));
  SERIAL_PRINTLN();
}
