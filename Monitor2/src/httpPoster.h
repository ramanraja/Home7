// httpPoster.h

#ifndef HTTP_POSTER_H
#define HTTP_POSTER_H

#include "common.h"
#include <ESP8266WiFi.h>        
#include <ESP8266HTTPClient.h>   // https://github.com/esp8266/Arduino/tree/master/libraries/ESP8266HTTPClient
 
class HttpPoster {
public:
    HttpPoster();
    void init();
    int get  (const char *url);
    int post (const char *url, const char *payload); // stringified JSON
    int getResponseCode();
    
private:
    int reponse_code = 0;    
    int do_http (int GP, const char *url, const char *payload);
};
 
#endif 
