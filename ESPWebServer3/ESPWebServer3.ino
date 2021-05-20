// ESP 8266 based web server
// Serves a random number to clients
// Based on:
// https://www.electronicshub.org/esp8266-web-server/

#include <ESP8266WiFi.h>
#include "keys.h"

const char* ssid = SSID1;   // SSID is a key word, so use SSID1
const char* password = PASSWORD1;  

WiFiServer espServer(80); 
 
void setup() 
{
  Serial.begin(115200);  
  Serial.print("\nESPWebServer3.ino begins...");
  Serial.print("Connecting to: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA); /* Configure ESP8266 in STA Mode */
  WiFi.begin(ssid, password); /* Connect to Wi-Fi based on above SSID and Password */
  while(WiFi.status() != WL_CONNECTED)
  {
    Serial.print("*");
    delay(500);
  }
  Serial.print("\n");
  Serial.print("Connected to Wi-Fi: ");
  Serial.println(WiFi.SSID());
  delay(100);
  
  // Assign a Static IP to ESP8266
  /*
  IPAddress ip(192,168,1,9);   
  IPAddress gateway(192,168,1,1);   
  IPAddress subnet(255,255,255,0);   
  WiFi.config(ip, gateway, subnet);
  delay(2000);
  */
    
  Serial.print("\n");
  Serial.println("Starting ESP8266 Web Server...");
  espServer.begin(); /* Start the HTTP web Server */
  Serial.println("ESP8266 Web Server Started.");
  Serial.print("Point your browser to: ");
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.print("\n");
}

char buf[32]; // NOTE: for longer messages increase the size of the buffer
void loop()
{
  WiFiClient client = espServer.available(); // 'client' is a local variable inside the loop. Study: is it safe to be made global?
  if(!client)
      return;
  Serial.println("New Client connected.");

  String request = client.readStringUntil('\r'); /* Read the first line of the request from client */
  Serial.println(request); /* Print the request on the Serial monitor */
  /* The request is in the form of HTTP GET Method */ 
  client.flush();

  // Extract the URL of the request 
  // expected: http://192.168.1.6/random
  if (request.indexOf("/random") != -1) 
  {
      int r = random (1,10000);    
      sprintf (buf, "%d", r);
  }
  else
      sprintf (buf, "use /random");
  Serial.println (buf);
  
  /* HTTP Response in the form of HTML Web Page */
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/plain);  // html");
  client.println(); //  this blank line after the headers is IMPORTANT
  //client.println ("<html>");
  client.print("random: ");
  client.println(buf);
  //client.println ("</html>");
  client.print("\n");
  client.flush();
  
  delay(1);
  /* Close the connection */
  client.stop();
  Serial.println("Client disconnected.\n");
}
