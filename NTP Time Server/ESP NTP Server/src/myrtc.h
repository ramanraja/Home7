// myrtc.h

#ifndef MYRTC_H
#define MYRTC_H

// Real time clock DS3231 library wrapper
// Serves UTC time as a formatted date time string or a Unix integer
/*
RTC ZS-042 which is a clone of DS3231 RTC module: supply voltage 3.3V (preferred) or 5V
CAUTION: see https://forum.arduino.cc/t/zs-042-ds3231-rtc-module/268862/21
Solution for battery charging problem: https://www.youtube.com/watch?v=ND2shVqV9s4

Connections for For ESP8266:  (GPIO5) D1=SCL, (GPIO4) D2=SDA

Software:
http://www.esp8266learning.com/wemos-ds3231-rtc-example.php 
https://forum.arduino.cc/t/how-to-use-timespan-for-the-rtclib-rtc_ds3231/655614/14
*/
#include <Wire.h>
#include <RTClib.h>  // https://github.com/adafruit/RTClib
#include "common.h"

#define MAX_BUFFER      32              // it is sufficient only for a timestamp string *
#define OFFSET_1970     2208988800UL    //  No. of seconds in the 70 years 1900-1970

class MyRTC {
public:
    MyRTC();
    bool init();
    void init_time();
    bool is_valid();    
    const char *get_time_str ();
    const char *to_string (const DateTime& dt);    
    const DateTime& get_time ();
    unsigned long get_epoch_time_1900 ();   
    unsigned long get_epoch_time_1970 (); 

    // NOTE: the RTC library does not support years before 2000 ***
    bool set_time (int year, int month, int day, int hour, int minute, int second); 
    bool set_time (const DateTime& dt); 
    bool set_epoch_time (unsigned long epoch_time); 
    bool adjust_time (int ddays, int dhours, int dminutes, int dseconds); // we just increase or decrease current time
                                                                          // The library method RTC.adjust_time() works differently:
                                                                          // it is the equivalent of our set_time() 
    bool adjust_epoch_time (long epoch_delta);    // delta in seconds
    bool fine_tune (int dminutes, int dseconds);  // this is an alias for adjust_time (0,0,dminutes,dseconds)
            
    void print_time (); 
    void print_epoch_time ();
    void debug_print(); // print the system clock at compile time
private:
    DateTime now;
    RTC_DS3231 rtc;
    char buffer[MAX_BUFFER];
    //static char WEEK_DAYS[7][] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

};

#endif  // MYRTC_H  
