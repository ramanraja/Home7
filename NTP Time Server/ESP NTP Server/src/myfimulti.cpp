// myfimulti.cpp

/***
WiFi status issues:
Wifi.status() always shows WL_CONNECTED even when the router is turned off:
https://github.com/esp8266/Arduino/issues/4352
https://github.com/esp8266/Arduino/issues/2593
https://github.com/esp8266/Arduino/issues/2186 
Under some conditions (in code) the initial auto reconnect does not work and it times out. What contributes
to this? Possible suspects:
  WiFi.mode(WIFI_OFF); 
  WiFi.disconnect();  //to prevent connecting to wifi based on previous configuration? 
  WiFi.persistent(false);   
Observation: dump() shows that static IP has been set, but the router table still shows a dynamic IP.
Investigate: While setting up a static IP, what DNS server to set? Router IP ? Mobile phone IP ? Or just omit it?

Static IP: *
https://circuits4you.com/2018/03/09/esp8266-static-ip-address-arduino-example/
static IP: The router does not show the device in its DHCP client list.
Just ping the IP or connect a client (if it is running a web/time server).
***/

#include "myfimulti.h"

const char* WIFI_STATUS_STR[] = {
    "WL_IDLE_STATUS", 
    "WL_NO_SSID_AVAIL", 
    "WL_SCAN_COMPLETED", 
    "WL_CONNECTED", 
    "WL_CONNECT_FAILED", 
    "WL_CONNECTION_LOST",
    "WL_DISCONNECTED" 
};

bool MyfiMulti::init (int octet3, int octet4) {
    this->octet3 = octet3;
    this->octet4 = octet4;
    SERIAL_PRINT (F("Requesting Wifi static IP: 192.168."));
    SERIAL_PRINT (octet3);
    SERIAL_PRINT (F("."));
    SERIAL_PRINTLN (octet4);
    init();
}

// This does not return for almost 1 minute *
// TODO: make this a state machine without the delay() statements
bool MyfiMulti::init () {
    SERIAL_PRINT (F("Primary AP: "));
    SERIAL_PRINTLN (AP_SSID1);
    SERIAL_PRINT (F("Backup AP: "));
    SERIAL_PRINTLN (AP_SSID2);
    if (connect_auto()) {
        configure_wifi();
        return true;
    }
    return (re_init());
}
        
bool MyfiMulti::re_init () {        
    if (connect_primary()) {
        configure_wifi();
        return true;
    }
    if (connect_secondary()) {
        configure_wifi();
        return true;
    }
    return false;
}

bool MyfiMulti::connect_auto () {
    ////////WiFi.mode (WIFI_OFF);   // this line prevents the ESP from auto-connecting ??  *
    WiFi.mode (WIFI_STA);   // the default is AP+STA
    pinMode (LED, OUTPUT); // active low
    led_off();
    delay (1000);
    SERIAL_PRINTLN (F("\nInitial status: "));
    vote_connected (1);
    SERIAL_PRINTLN (F("\nAuto-connecting to wifi.."));
    int attempts = 0;
    while (!is_connected())
    {
      delay (ATTEMPT_DELAY);
      SERIAL_PRINT (".");
      attempts++;
      if (attempts > MAX_ATTEMPTS)
          break;
    }  
    vote_connected (2);
    return (is_connected());  
}

// connect to the primary router
bool MyfiMulti::connect_primary () {
    SERIAL_PRINTLN (F("\nInitializing AP 1..")); 
    //WiFi.disconnect();  //Prevent connecting to wifi based on previous configuration 
    //WiFi.persistent(false);  // TODO: investigate; this may prevent from auto connecting next time?
    WiFi.mode (WIFI_OFF);   // 'this is a temporary fix'
    WiFi.mode (WIFI_STA);
    delay (1000);
    ///set_static_IP (octet3, octet4); // this makes the device invisible to the router's DHCP table; ping the device to verify it exists.
    ///set_host_name();                
    WiFi.begin (AP_SSID1, AP_PASSWD1); // set-static-ip has to be done befor wifi.begin() *
    WiFi.mode (WIFI_STA);
    int attempts = 0;
    while (!is_connected())
    {
      delay (ATTEMPT_DELAY);
      SERIAL_PRINT("+");
      attempts++;
      if (attempts > MAX_ATTEMPTS)
          break;   
    }
    vote_connected (3);
    return (is_connected());  
}

// connect to the backup mobile hotspot
bool MyfiMulti::connect_secondary () {
    SERIAL_PRINTLN (F("\nInitializing AP 2.."));  
    WiFi.persistent (false); // Is this necessary to prevent auto connecting the next time?
    WiFi.mode (WIFI_OFF);   // 'this is a temporary fix'
    WiFi.mode (WIFI_STA);
    delay (1000);
    // satic IP is NOT applicable to mobile hotspot *
    /////set_static_IP (octet3, octet4); // Do NOT call this for the backup AP !
    set_host_name();          
    WiFi.begin (AP_SSID2, AP_PASSWD2);
    WiFi.mode (WIFI_STA);
    int attempts = 0;
    while (!is_connected())
    {
      delay (ATTEMPT_DELAY);
      SERIAL_PRINT ("*");
      attempts++;
      if (attempts > MAX_ATTEMPTS)
          break;   
    }
    vote_connected (4);
    return (is_connected());  
}  
    
bool MyfiMulti::configure_wifi () {    
    bool connected = is_connected();
    if (connected) {
        SERIAL_PRINTLN (F("\nWifi connected."));
        // static IP is applicable only to the primary/router AP, not to the backup mobile hotspot; it may have different domain.
        // NOTE: the device with static ip is invisible to the router's DHCP table; ping the device instead!
        if (WiFi.SSID() == AP_SSID1)
            set_static_IP (octet3, octet4); 
        set_host_name();                
        dump();  
        led_off();
    } else {
        SERIAL_PRINTLN (F("\n--- Could not connect to Wifi. ---"));
        led_on(); // leave it ON, so that we can laer start wifi manager portal
    }
    last_update = millis();
    return connected; 
}

// You are supposed to call this in the main loop
void MyfiMulti::update () {    
    if (millis()-last_update < TICK_INTERVAL)
        return;
    last_update = millis();
    if (!is_connected()) {
        blink();
        connectionless_time++;
        if (connectionless_time >= MAX_CONNECTIONLESS_TIME) {
            SERIAL_PRINTLN (F("Connection timed out. Reinitializing WiFi.."));
            re_init(); // skip auto connect, it is not working for the past several minutes
            connectionless_time = 0;  // we want to re-initialize only at 3,6,9.. minute intervals
        }
    }
    else {
        connectionless_time = 0;
        led_off();
    }
}

// TODO: revisit; should you use vote_connected for this also?
bool MyfiMulti::is_connected () {
    return (WiFi.status() == WL_CONNECTED); // this is notoriously unreliable !
}  

// We check WiFi connection status using different methods and take a majority vote
bool MyfiMulti::vote_connected (int stage) {
    led_on();
    int vote = 0;
    SERIAL_PRINT (F("\nVoting: stage "));
    SERIAL_PRINTLN (stage);
    SERIAL_PRINT (F("WiFi.status()= "));
    SERIAL_PRINTLN (WIFI_STATUS_STR [WiFi.status()]);   
    if (WiFi.status() == WL_CONNECTED) // this is notoriously unreliable !
        vote++;
    String ip = WiFi.localIP().toString();
    SERIAL_PRINT (F("IPAddress= "));
    SERIAL_PRINTLN (ip.c_str());    
    if (WiFi.localIP().isSet())
        vote++;
    long rssi = WiFi.RSSI();
    SERIAL_PRINT (F("Signal strength (RSSI):"));
    SERIAL_PRINTLN (rssi);        
    if (rssi < -10)   // when unconnected, RSSI is positive(31), that is, garbage
        vote++;     
    SERIAL_PRINT (F("Total votes= "));
    SERIAL_PRINTLN (vote);    
    if (vote > 1)
        SERIAL_PRINTLN (F("Connected !"));
    else
        SERIAL_PRINTLN (F("Not Connected :("));
    return (vote > 1);  // TODO: revisit
}

// scan for wifi networks
int MyfiMulti::scan () {
    SERIAL_PRINTLN (F("Disconnecting WiFi.."));
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();  //ESP has tendency to store old SSID and PASSword and tries to connect
    delay(100);  
    vote_connected (0);
    SERIAL_PRINTLN (F("Scanning for WiFi networks..."));
    // WiFi.scanNetworks will return the number of networks found
    int n = WiFi.scanNetworks();
    SERIAL_PRINTLN (F("Scan finished."));
    if (n == 0) {
      SERIAL_PRINTLN (F("No Networks Found."));
      return 0;
    }
    SERIAL_PRINT(n);
    SERIAL_PRINTLN (F(" Networks found"));
    for (int i = 0; i < n; ++i)
    {
      SERIAL_PRINT(i + 1);  //Sr. No
      SERIAL_PRINT (F("] "));
      SERIAL_PRINT (WiFi.SSID(i));  
      SERIAL_PRINT (F(" ("));
      SERIAL_PRINT (WiFi.RSSI(i)); //Signal Strength
      SERIAL_PRINT (F(") MAC:"));
      SERIAL_PRINT(WiFi.BSSIDstr(i));
      SERIAL_PRINTLN ((WiFi.encryptionType(i) == ENC_TYPE_NONE)?" Unsecured":" Secured");
      delay (10);
    }
    SERIAL_PRINTLN ("");  
    led_off();
}

// Do not search for the device in your router's DHCP table; it will not be listed there!
// Just ping the static IP of the device, or connect a client (eg: NTP client) and observe data at that end.
void MyfiMulti::set_static_IP (int octet3, int octet4) {
    if (octet4 == 0)  // octet3 can be zero
        return;
    SERIAL_PRINT (F("Setting static IP: 192.168."));
    SERIAL_PRINT (octet3);
    SERIAL_PRINT (".");
    SERIAL_PRINTLN (octet4);
    IPAddress ip (192,168, octet3, octet4);
    IPAddress gateway (192,168,octet3,1);  // NOTE this assumption about octet3 !
    IPAddress subnet (255,255,255,0);
    WiFi.config (ip,gateway,subnet);
    //WiFi.config (ip,gateway,subnet,gateway); // the 4th one is the DNS server
    // Investigate: While setting up a static IP, what DNS server to set? Router IP ? Mobile phone IP ? 
    // google 8.8.8.8 ? Or just omit it?
    
}

void MyfiMulti::set_host_name () {
   SERIAL_PRINT (F("MAC address: "));
   SERIAL_PRINTLN (WiFi.macAddress());  
   unsigned char mac[6];
   WiFi.macAddress (mac);
   // Take the 13 LSBs; they will make a decimal of 4 digits
   // NOTE: The << operator has lower precedence than +, so the parenthesis is necessary !
   int suffix = ((mac[4]&0x1F) << 8) + mac[5];
   char temp[32];
   sprintf (temp, "%s-%d", HOST_NAME_PREFIX, suffix);
   WiFi.hostname (temp);  // set the host name
   SERIAL_PRINT (F("Setting host name to: "));
   SERIAL_PRINTLN (WiFi.hostname());
}

void MyfiMulti::disable() {
    SERIAL_PRINTLN (F("\nSwitching off wifi.."));
    WiFi.disconnect(); 
    WiFi.mode(WIFI_OFF);
    WiFi.forceSleepBegin();
    delay(10); 
}

void MyfiMulti::dump() {
    SERIAL_PRINT (F("\nConnected to WiFi SSID: "));
    SERIAL_PRINTLN (WiFi.SSID());
    IPAddress ip = WiFi.localIP();
    SERIAL_PRINT (F("My IP Address: "));
    SERIAL_PRINT (ip);
    ///SERIAL_PRINTLN (octet4==0 ? " (DHCP)" : " (STATIC)");
    SERIAL_PRINT (F("Host name: "));
    SERIAL_PRINTLN (WiFi.hostname());
    long rssi = WiFi.RSSI();
    SERIAL_PRINT (F("Signal strength (RSSI):"));
    SERIAL_PRINT (rssi);
    SERIAL_PRINTLN (F(" dBm"));
    SERIAL_PRINTLN();
}

bool led_status = false;
void MyfiMulti::blink () {
    digitalWrite (LED, led_status);
    led_status = !led_status;
}

void MyfiMulti::led_off () {
    digitalWrite (LED, OFF);   
}

void MyfiMulti::led_on () {
    digitalWrite (LED, ON); // active low   
}
