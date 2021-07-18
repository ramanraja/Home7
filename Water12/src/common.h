//common.h
#ifndef COMMON_H
#define COMMON_H

//////////#include <Arduino.h>

// keep MQTT Rx messages short (~100 bytes); PubSubClient silently drops longer messages !
#define  MAX_MSG_LENGTH              128        // MQTT message body -usully a json.dumps() string, excluding parser overhead
#define  TINY_STRING_LENGTH          16         // to store client ID etc
#define  SHORT_STRING_LENGTH         32 

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
    NO_NETWORK,
    BAD_URL,
    URI_NOT_FOUND,
    NO_ACCESS,
    HTTP_FAILED
} ;

#endif
