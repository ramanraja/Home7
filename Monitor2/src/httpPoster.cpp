// httpPoster.cpp

#include "httpPoster.h"

#define DO_GET   0 
#define DO_POST  1

HttpPoster::HttpPoster(){
}

void HttpPoster::init(){
    SERIAL_PRINTLN("HttpPoster: initializing..");
}

int HttpPoster::getResponseCode() {
    return (reponse_code);
} 

/***
    Sends a Json payload (stringified)
***/
int HttpPoster::post (const char *url, const char *payload) {
    return do_http (DO_POST, url, payload);
}

int HttpPoster::get (const char *url) {
    return do_http (DO_GET, url, NULL);
}

int HttpPoster::do_http (int GP, const char *url, const char *payload) {
   if (WiFi.status() != WL_CONNECTED) {
      SERIAL_PRINTLN ("HttpPoster: Wifi not connected");
      return NO_WIFI;
  }
  SERIAL_PRINT ("HttpPoster:  server URL= ");
  SERIAL_PRINTLN (url);
  
  HTTPClient http_client;  // TODO: make it class member? STUDY reuse problems first!
  //http_client.setReuse (true);  // enable this for class level operation - CAUTION !
  http_client.setTimeout (3000); // milliSec; (does not work ?!)
   
  bool begun = http_client.begin (url);   // this just parses the url
  if (!begun) {
    SERIAL_PRINTLN ("Invalid HTTP URL");
    http_client.end();   // releases buffers (useful for class level variable) 
    return BAD_URL;
  }
  if (GP == DO_POST) {
    http_client.addHeader ("Content-Type", "application/json; charset=utf-8");
    reponse_code = http_client.POST(payload);
  }
  else {
    reponse_code = http_client.GET();
  }
  SERIAL_PRINT ("HttpPoster: HTTP response code:");
  SERIAL_PRINTLN (reponse_code);

   if (reponse_code < 0) {
      SERIAL_PRINTLN ("HttpPoster: Could not connect to server");
      SERIAL_PRINTLN (http_client.errorToString (reponse_code));   //.c_str());
      http_client.end();
      return CONNECTION_FAILED;
   } 
   if (reponse_code < 200 || reponse_code >= 300) {
      SERIAL_PRINTLN ("HttpPoster: HTTP server returned an error !");
      http_client.end();   // close connection
      return HTTP_FAILED;
   } 
   /////safe_strncpy (reponse_string, http_client.getString().c_str());
   SERIAL_PRINTLN (http_client.getString()); // TODO: avoid this line in production
   SERIAL_PRINTLN ("HTTPPoster: closing HTTP connection..");
   
   http_client.end();   // close the connection [may crash if the server is also 8266]
   SERIAL_PRINTLN ("closed connection.");
   
   /////http_client.end();   // close the connection [may crash if the server is also 8266]
   /////SERIAL_PRINTLN ("did not close connection.");   // https://github.com/esp8266/Arduino/issues/869
   
   //// http_client.abort();  // extreme !
   ///SERIAL_PRINTLN ("Aborted the connection!");
   return  CODE_OK;
} 
/*----------------------------------------------------------------------------------
https://github.com/esp8266/Arduino/issues/869


Connected to WiFi SSID: Mithila
My IP Address: 192.168.1.3
Signal strength (RSSI):-12 dBm

HttpPoster: initializing..
syncing time..
2021-05-19  18:41:00
HttpPoster:  server URL= http://192.168.1.18/cm?cmnd=time
HttpPoster: HTTP response code:200
{"Time":"1970-01-01T01:08:01"}
HTTPPoster: closing HTTP connection..

Exception (9):
epc1=0x40209258 epc2=0x00000000 epc3=0x00000000 excvaddr=0x0000012e depc=0x00000000

>>>stack

--------------------------------------------------

Connected to WiFi SSID: Mithila
My IP Address: 192.168.1.3
Signal strength (RSSI):-12 dBm

HttpPoster: initializing..
syncing time..
2021-05-19  18:40:51
HttpPoster:  server URL= http://192.168.1.18/cm?cmnd=time
HttpPoster: HTTP response code:200
{"Time":"1970-01-01T01:07:52"}
HTTPPoster: closing HTTP connection..

Exception (9):
epc1=0x40209258 epc2=0x00000000 epc3=0x00000000 excvaddr=0x0000012e depc=0x00000000

>>>stack>>>

ctx: cont
sp: 3ffffcb0 end: 3fffffc0 offset: 01a0
3ffffe50:  00000000 00000025 3ffffe80 402042b4  
3ffffe60:  00000000 3ffee594 3ffffe80 4020511c  
*/


