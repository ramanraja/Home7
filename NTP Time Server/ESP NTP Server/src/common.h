//common.h
#ifndef COMMON_H
#define COMMON_H

#include <Arduino.h>
extern "C" {
  #include "user_interface.h"
}

// keep MQTT Rx messages short (~100 bytes); PubSubClient silently drops longer messages !
#define  MAX_MSG_LENGTH              128        // MQTT message body -usully a json.dumps() string, excluding parser overhead

// comment out this line to disable all serial messages
#define ENABLE_DEBUG
#define BAUD_RATE   115200 
#ifdef ENABLE_DEBUG
  #define  SERIAL_PRINT(x)       Serial.print(x)
  #define  SERIAL_PRINTLN(x)     Serial.println(x)
  #define  SERIAL_PRINTLNF(x,y)  Serial.println(x,y)   
  #define  SERIAL_PRINTF(x,y)    Serial.printf(x,y) 
#else
  #define  SERIAL_PRINT(x)
  #define  SERIAL_PRINTLN(x)
  #define  SERIAL_PRINTLNF(x,y)
  #define  SERIAL_PRINTF(x,y)
#endif


enum connection_result {
    CODE_OK = 0,
    NO_WIFI,
    BAD_URL,
    CONNECTION_FAILED,
    HTTP_FAILED,
    URI_NOT_FOUND,
    NO_ACCESS
} ;

#endif
