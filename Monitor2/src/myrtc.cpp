// myrtc.cpp

#include  "myrtc.h"
#define   LAST_COMPILE_TIME               (DateTime(F(__DATE__), F(__TIME__)))
#define   AN_HOUR_AFTER_LAST_COMPILE_TIME   (DateTime(F(__DATE__), F(__TIME__))+TimeSpan(0,1,0,0)) 
////#define   A_DAY_AFTER_LAST_COMPILE_TIME   (DateTime(F(__DATE__), F(__TIME__))+TimeSpan(1,0,0,0))

MyRTC::MyRTC () {
    strcpy (buffer, "1970-01-01 00:00:01");
}

bool MyRTC::init () {
    if (rtc.begin()) {  
        init_time();
        return true;
    }
    SERIAL_PRINTLN (F("\n***** ERROR: Failed to initialize RTC ! *****\n"));
    return false;
}

void MyRTC::init_time() {
    if (rtc.lostPower()) {
        SERIAL_PRINTLN(F("\n *** RTC had lost power, setting the time manually!"));
        /***
          Set the RTC to the date & time this sketch was compiled.
          NOTE: this will work only for the initial deployment. If battery fails afterwards,
          the RTC will be initialized to the date this code was compiled !
          Always validate time with is_valid()
        ***/
        rtc.adjust (LAST_COMPILE_TIME);       
        // add 3 minutes (empirically found) for 8266 compiling and loading delay:  
        fine_tune (3,0);
    }
    else
        SERIAL_PRINTLN (F("\n[INFO] RTC backup battery is working fine!"));
}

bool MyRTC::is_valid() {
    bool valid = (rtc.now() > AN_HOUR_AFTER_LAST_COMPILE_TIME);  // A_DAY_AFTER_LAST_COMPILE_TIME
    if (!valid)
        SERIAL_PRINTLN(F("\n *** RTC time is invalid. Please call set_time() first!"));
    return (valid);
}

const DateTime& MyRTC::get_time () {
    now = rtc.now();
    return ((const DateTime) now);
}

const char *MyRTC::to_string (const DateTime& dt) {
    sprintf (buffer, "%d-%02d-%02d  %2d:%02d:%02d", dt.year(),dt.month(),dt.day(), dt.hour(),dt.minute(),dt.second());
    return ((const char*)buffer);
}

const char *MyRTC::get_time_str () {
    now = rtc.now();
    sprintf (buffer, "%d-%02d-%02d  %2d:%02d:%02d", now.year(),now.month(),now.day(), now.hour(),now.minute(),now.second());
    return ((const char*)buffer);
}

unsigned long MyRTC::get_epoch_time () {
    now = rtc.now();
    return now.unixtime();
}

bool MyRTC::fine_tune (int dminutes, int dseconds) {
    return adjust_time (0,0, dminutes, dseconds);
}

// NOTE: TimeSpan class does not allow negative values, but some of the
//       parameters passed to this function can be negative; this is taken care of.
bool MyRTC::adjust_time (int ddays, int dhours, int dminutes, int dseconds) {
     long delta =  ddays * 86400L + dhours * 3600 + dminutes * 60 + dseconds;
     if (delta > 0)
            rtc.adjust (rtc.now() + TimeSpan (delta));
     else
            rtc.adjust (rtc.now() - TimeSpan (-delta));
     return true;
}

bool MyRTC::adjust_epoch_time (long epoch_delta) {
    if (epoch_delta > 0)
        rtc.adjust (rtc.now() + TimeSpan (epoch_delta));
    else
        rtc.adjust (rtc.now() - TimeSpan (-epoch_delta));    
    return true;
}

bool MyRTC::set_time (int year, int month, int day, int hour, int minute, int second) {
    if (year > 99 && year < 2000) {
        SERIAL_PRINTLN (F("The RTC library does not support years before 2000 !"));
        return false;
    }
    DateTime dt = DateTime (year,month,day, hour,minute,second);
    return set_time (dt);
}

bool MyRTC::set_time (const DateTime& dt) {
    if (!dt.isValid())  {
        SERIAL_PRINTLN (F("\n* Invalid date. *"));
        return false;
    }
    rtc.adjust (dt);
    return true;
}

bool MyRTC::set_epoch_time (unsigned long epoch_time) {
    DateTime dt = DateTime (epoch_time);
    if (!dt.isValid())  {
        SERIAL_PRINTLN (F("\n* Invalid date. *"));
        return false;
    }
    rtc.adjust (dt);
    return true;
}

void MyRTC::print_time () {
    SERIAL_PRINTLN (get_time_str());
}

void MyRTC::print_epoch_time () {
    SERIAL_PRINTLN (get_epoch_time());
}

void MyRTC::debug_print() {
    SERIAL_PRINT ("LAST_COMPILE_TIME: ");
    SERIAL_PRINTLN (to_string(LAST_COMPILE_TIME));
    SERIAL_PRINT ("AN_HOUR_AFTER_LAST_COMPILE_TIME: ");
    SERIAL_PRINTLN (to_string(AN_HOUR_AFTER_LAST_COMPILE_TIME));    
    //SERIAL_PRINT ("A_DAY_AFTER_LAST_COMPILE_TIME: ");
    //SERIAL_PRINTLN (to_string(A_DAY_AFTER_LAST_COMPILE_TIME));
}
