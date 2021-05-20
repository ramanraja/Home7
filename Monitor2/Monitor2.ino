// splice or RTC4.ino and ESPTimeServer1.ino
/**
 * Issues:
 * (1) (WiFi.status() == WL_CONNECTED) always true even when the modem is switched off
 * Need to study wifimulticonnect.run()
 * See also 'rainy days' event handling in:
 * https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/wifi.html
 * https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/wifi.html#esp32-wi-fi-api-error-code
 * Write robust error recovery routines !!!
 * 
 * (2) HttpPoster issue:
 * When the web server is another ESP8266( Tasmota in my case) and you call 
 * HttpClient.close() or just exit the function without closing, ESP crashes !
 * There is no issue when the server is not ESP, for example, a web server running on PC.
 * 
 * (3) Even after WiFi is restored, the HTTPPoster is unable to connect. It returns code 3 (connection refused)
 * forever afterwards.
 * **/
#include "src/main.h"

#define  CONNECTION_ATTEMPTS1   3
#define  CONNECTION_ATTEMPTS2   6
#define  CONNECTION_ATTEMPTS3   9

Timer T;
MyFi W;
MyRTC R;
HttpPoster H;

bool rtc_available = false;
byte led = 2;

void setup() {
    pinMode (led, OUTPUT);
    init_serial();
    rtc_available = R.init();
    if (!rtc_available)
        SERIAL_PRINTLN (F("There is no RTC clock !"));  // TODO
    if (R.is_valid())
        SERIAL_PRINTLN (F("The RTC clock is upto date.")); // TODO
    R.debug_print ();
    W.init(1,3);
    H.init();
    T.every (15000, tick);  
}

void loop() {
    T.update();
}

int connection_attempts = 0;
bool sync_success = false;
void tick() {
    if (W.isConnected()) {
        sync_success = send_time_sync(); // TODO: blink LED if sync failed
        return;
    }
    connection_attempts++;  // TODO: move this block into MyFi; use reinit(), disable() etc as needed
    SERIAL_PRINT (F("connection attempts: "));
    SERIAL_PRINTLN (connection_attempts);
    if (connection_attempts > CONNECTION_ATTEMPTS3) {
        SERIAL_PRINTLN (F("\n\n****** Could not get WiFi. Rebooting !!!!!!  ****"));
        delay (2000);
        ESP.restart();
    } 
    else if (connection_attempts > CONNECTION_ATTEMPTS2) {
        SERIAL_PRINTLN (F("\n** Main: Calling W.reinit...."));
        W.reinit();  
    }
    else if (connection_attempts > CONNECTION_ATTEMPTS1) {
        SERIAL_PRINTLN (F("\n* Main: Calling W.reconnect...."));
        W.reconnect(); // switch off and turn on again
    }    
}

bool send_time_sync () {
    SERIAL_PRINTLN (F("\nsyncing time.."));
    R.print_time(); 
    int result;
    result = H.get ("http://192.168.1.100:5000/cm?cmnd=HostName");
    SERIAL_PRINT ("1.100 returned: ");
    SERIAL_PRINTLN (result);    
    result = H.get ("http://192.168.1.100:5000/cm?cmnd=Time");
    SERIAL_PRINT ("1.100 returned: ");
    SERIAL_PRINTLN (result);        
    /*
    result = H.get ("http://192.168.1.17/cm?cmnd=HostName");
    SERIAL_PRINT ("1.17 returned: ");
    SERIAL_PRINTLN (result);
    
    result = H.get ("http://192.168.1.18/cm?cmnd=Time");    
    SERIAL_PRINT ("1.18 returned: ");
    SERIAL_PRINTLN (result);   
    */ 
    return (result==CODE_OK);
}

void init_serial() {
#ifdef ENABLE_DEBUG
    Serial.begin (BAUD_RATE); 
    #ifdef VERBOSE_MODE
       Serial.setDebugOutput(true);
    #endif
    Serial.setTimeout (200); 
    SERIAL_PRINTLN (F("\n\n<--------- Intof IoT device starting.. ---------->\n"));  
#endif     
}
