// ESP 8266 based native time server (not NTP)
// Serves time string using RTC module 2321
// HTTP server loosely based on:
// https://www.electronicshub.org/esp8266-web-server/

#include "src/main.h"

#define  MAX_CONNECTION_ATTEMPTS   3
//Timer T;
MyFi W;
MyRTC R;
WiFiServer espServer(80);  // This is just a wifi server; so for HTTP server you need to go into DIY mode

bool rtc_available = false;
byte led = 2;

void setup() 
{
    pinMode (led, OUTPUT);
    init_serial();
    rtc_available = R.init();
    if (!rtc_available)
        SERIAL_PRINTLN (F("There is no RTC clock !"));  // TODO
    if (R.is_valid())
        SERIAL_PRINTLN (F("The RTC clock is upto date.")); // TODO
    R.debug_print ();
    W.init(1,3);
    start_web_server();
    //T.every (1000, tick);  
}

void loop()
{
    //T.update();
    handle_client();
}

void start_web_server () {
  SERIAL_PRINTLN("Starting Web Server...");
  espServer.begin(); /* Start the HTTP web Server */
  SERIAL_PRINTLN("ESP8266 Web Server Started.");
  SERIAL_PRINT("Point your browser to: ");
  SERIAL_PRINT("http://");
  SERIAL_PRINT(WiFi.localIP());
  SERIAL_PRINTLN("/time\n");
}
/***
// we are responding only to client requests, so for now we assume that WiFi is working fine
// TODO: later, enable reconnect logic
int connection_attempts = 0;
bool sync_success = false;
void tick() {
    if (W.isConnected()) {
        sync_success = send_time_sync();
        return;
    }
    connection_attempts++;
    if (connection_attempts > MAX_CONNECTION_ATTEMPTS) {
        connection_attempts = 0; // TODO: set up exponential retry interval
        W.reconnect();  // TODO: enable this
    }
}

// TODO: implement push notification for time broadcasts
bool send_time_sync () {
    SERIAL_PRINTLN (F("syncing time STUB."));
    R.print_time(); 
}
***/

#define BUF_SIZE  64
char buf[BUF_SIZE]; // NOTE: for longer messages increase the size of the buffer
const char* url_error = "Invalid URL; please try  /time";
//const char* rtc_error = "Error: RTC module not available";
//const char* invalid_time_error = "Error: RTC time not initialized";
bool valid_request = false;

void handle_client ()
{
  WiFiClient client = espServer.available(); // 'client' is a local variable inside the loop. Study: is it safe to be made global?
  if(!client)
      return;
  SERIAL_PRINTLN("New Client connected.");

  String request = client.readStringUntil('\r'); /* Read the first line of the request from client */
  SERIAL_PRINTLN(request); /* Print the request on the Serial monitor */
  /* The request is in the form of HTTP GET Method */ 
  client.flush();

  // Extract the URL of the request 
  // expected: http://192.168.1.3/time
  if (request.indexOf("/time") != -1 || request.indexOf("/favicon") != -1 ) {
      sprintf (buf, "Unix Time: %d", R.get_epoch_time()); // enable this if unix time is needed
      valid_request = true;
  }
  else 
      valid_request = false;
  
  client.println("HTTP/1.1 200 OK"); // This is DIY HTTP server code
  client.println("Content-Type: text/plain);  // html");
  client.println(); //  this blank line after the headers is IMPORTANT
  //client.println ("<html>");
  if (valid_request) {
      //client.println (R.get_time_str());
      client.println (buf); // enable this if unix time is needed
  }
  else
      client.println (url_error);
  //client.println ("</html>");
  client.print("\n");
  client.flush();
  
  delay(1);
  client.stop();  //Close the connection 
  SERIAL_PRINTLN("Client disconnected.\n");
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
