/*
  user_config_override.h - user configuration overrides my_user_config.h for Tasmota

  Copyright (C) 2021  Theo Arends

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef _USER_CONFIG_OVERRIDE_H_
#define _USER_CONFIG_OVERRIDE_H_

// force the compiler to show a warning to confirm that this file is included
#warning **** user_config_override.h: Using Settings from this File ****

/*****************************************************************************************************\
 * USAGE:
 *   To modify the stock configuration without changing the my_user_config.h file:
 *   (1) copy this file to "user_config_override.h" (It will be ignored by Git)
 *   (2) define your own settings below
 *
 ******************************************************************************************************
 * ATTENTION:
 *   - Changes to SECTION1 PARAMETER defines will only override flash settings if you change define CFG_HOLDER.
 *   - Expect compiler warnings when no ifdef/undef/endif sequence is used.
 *   - You still need to update my_user_config.h for major define USE_MQTT_TLS.
 *   - All parameters can be persistent changed online using commands via MQTT, WebConsole or Serial.
\*****************************************************************************************************/

// -- Master parameter control --------------------
/***
#undef  CFG_HOLDER
// original value
#define CFG_HOLDER               4617     // [Reset 1] Change this value to load SECTION1 configuration parameters to flash
// changed by Rajaraman, in order to load the config: 
// https://tasmota.github.io/docs/FAQ/#why-is-my-changed-configuration-not-loaded
//#define CFG_HOLDER                 4616     // Enough to change it by + or- 1
// but if you are doing this OTA, you have to change it back to 4617 and burn again a second time!
***/

/***
// Undocumented feature:
// https://github.com/arendst/Tasmota/issues/3128
// the following is redundant, since the retry intervals now automatically increase with every attempt
#undef  MQTT_RETRY_SECS
#define MQTT_RETRY_SECS        20
***/

// --  Wifi settings  ---------------
#undef  STA_SSID1
#undef  STA_PASS1
#undef  STA_SSID2
#undef  STA_PASS2
// --  MQTT settings  ---------------
#undef  MQTT_HOST
#undef  MQTT_PORT
#undef MQTT_USER
#undef MQTT_PASS

// Raja
#define STA_SSID1      "xxxx"             // [Ssid1] Wifi SSID
#define STA_PASS1      "yyyy"             // [Password1] Wifi password
#define STA_SSID2      "zzzzzz"           // [Ssid1] Wifi SSID
#define STA_PASS2      "wwwww"            // [Password1] Wifi password

#define MQTT_HOST       "192.168.0.100"         // [MqttHost]
#define MQTT_PORT       1883                    // [MqttPort] MQTT port (10123 on CloudMQTT)
#define MQTT_USER       ""
#define MQTT_PASS       ""

/***
// Vaidy
#define STA_SSID1        ""                  // [Ssid1] Wifi SSID
#define STA_PASS1        ""                  // [Password1] Wifi password
#define STA_SSID2        ""                  // [Ssid1] Wifi SSID
#define STA_PASS2        ""                  // [Password1] Wifi password

#define MQTT_HOST       "" // [MqttHost]
#define MQTT_PORT       1883                   // [MqttPort] MQTT port (10123 on CloudMQTT)
#define MQTT_USER       ""
#define MQTT_PASS       ""
****/

// -- OTA -----------------------------------------
// gzip all your binaries using 7-zip; rename the file to tasmota.bin.gz; upload through OTA
#ifdef ESP8266
  #undef OTA_URL 
  //#define OTA_URL  "http://192.168.0.100/ota/tasmota.bin.gz"                 // run a phthon web server locally
  #define OTA_URL    "http://ota.tasmota.com/tasmota/release/tasmota.bin.gz"  // [OtaUrl]
#endif  // ESP8266

// ---- Alexa -------------------------------------

#undef FRIENDLY_NAME                 
#undef EMULATION               

#define FRIENDLY_NAME          "tasmota"         // [FriendlyName] Friendlyname up to 32 characters used by web pages and Alexa
#define EMULATION              EMUL_NONE         // [Emulation]  (select EMUL_NONE, EMUL_WEMO or EMUL_HUE)
// tasmota ,  portico  ,   fan  ,   coffee   ,  drinking water  ,  salt water 

// Fix to avoid issuing ""timers 1" command after configuring
#undef TIMERS_ENABLED
#define TIMERS_ENABLED       true              // [Timers] Enable Timers  - this was false by default

// Mithila pump motor has a buzzer (active low, so Buzzeri)
#undef USE_BUZZER   
#define USE_BUZZER 
#undef BUZZER_ENABLE
#define BUZZER_ENABLE    true 
  
// fix to avoid issuing "module 0" to activate the template, after configuring it
  #undef MODULE
  #define MODULE      255 

// ---- Templates ----------------------------------
#ifdef ESP8266
//  format for USER_TEMPLATE:  "{\"NAME\":\"xxx\",\"GPIO\":[],\"FLAG\":0,\"BASE\":18}"  
#undef USER_TEMPLATE
  // Robo India Blynk board, 2 relays+DHT11  (module : nodemcu)
  // #define USER_TEMPLATE "{\"NAME\":\"Blynk2TH\",\"GPIO\":[32,1,576,1,225,224,0,0,288,1,1184,1,1,1],\"FLAG\":0,\"BASE\":18}"
  
  // Rhydolabz 4-SSR board (module : esp01_1m)
  // #define USER_TEMPLATE   "{\"NAME\":\"Rlabs4A\",\"GPIO\":[32,1,576,1,33,34,0,0,225,224,226,1,227,0],\"FLAG\":0,\"BASE\":18}"
  
  // Rhydolabz 2-EM or SSR Relay board (module : esp01_1m)
  // #define USER_TEMPLATE  "{\"NAME\":\"Rlabs2A\",\"GPIO\":[32,1,576,1,33,34,0,0,225,224,1,1,1,0],\"FLAG\":0,\"BASE\":18}"   
   
  // Rhydolabz 1-EM Relay board (module : esp01_1m)
  // #define USER_TEMPLATE  "{\"NAME\":\"Rlabs1A\",\"GPIO\":[32,1,576,1,33,34,0,0,1,224,1,1,1,0],\"FLAG\":0,\"BASE\":18}"  
    
  // ------ mostly DIY modules at Maithri: -----------
  // DIY Vaidy's circular PCB: portico lamps, active low relays  (module : nodemcu)
  // #define USER_TEMPLATE  "{\"NAME\":\"DIY2iTHLPR\",\"GPIO\":[32,1,576,1,256,257,1,1,1,1248,1,1,1,4704],\"FLAG\":0,\"BASE\":18}"  

  // DIY Vaidy's circular PCB: Maithri ground floor bathroom active high (module : nodemcu)
   #define USER_TEMPLATE  "{\"NAME\":\"DIY1THLPR\",\"GPIO\":[32,1,576,1,1,224,1,1,1,1248,1,1,1,4704],\"FLAG\":0,\"BASE\":18}"  

  // DIY coffee maker   (module : nodemcu)
  // #define USER_TEMPLATE  "{\"NAME\":\"DIY2TH\",\"GPIO\":[32,1,1,1,225,224,0,0,544,1,1184,1,1,1],\"FLAG\":0,\"BASE\":18}"  

  // Sonoff-Basic fan controller (module : esp01_1m)
  // #define USER_TEMPLATE  "{\"NAME\":\"MySonoff\",\"GPIO\":[32,1,1,1,1,0,0,0,224,320,1,0,0,0],\"FLAG\":0,\"BASE\":18}"  

  // DIY 2-pump motor at Maithri  (module : nodemcu)
  // #define USER_TEMPLATE  "{\"NAME\":\"DIY2B\",\"GPIO\":[1,1,576,1,225,224,0,0,320,321,1,1,1,1],\"FLAG\":0,\"BASE\":18}"  

  // DIY 3-pump motor at Mithila  (module : nodemcu)
  //#define USER_TEMPLATE  "{\"NAME\":\"DIYMCU3B\",\"GPIO\":[32,1,576,1,226,225,0,0,224,1,512,1,1,0],\"FLAG\":15,\"BASE\":18}"

#endif  // ESP8266
#endif  // _USER_CONFIG_OVERRIDE_H_
