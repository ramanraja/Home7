/*
  ESP32 mDNS responder sample

  This is an example of an HTTP server that is accessible
  via http://esp32.local URL thanks to mDNS responder.

  Instructions:
  - Update WiFi SSID and password as necessary.
  - Flash the sketch to the ESP32 board
  - Install host software:
    - For Linux, install Avahi (http://avahi.org/).
    - For Windows, install Bonjour (http://www.apple.com/support/bonjour/).
    - For Mac OSX and iOS support is built in through Bonjour already.
  - Point your browser to http://esp32.local, you should see a response.

 */

#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiClient.h>
#include "keys.h"

const char* ssid = SSID1; 
const char* password = PASSWORD1;

// TCP server at port 80 will respond to HTTP requests
WiFiServer server(80);

void setup(void)
{  
    Serial.begin(115200);

    // Connect to WiFi network
    WiFi.begin(ssid, password);
    Serial.println("");

    // Wait for connection
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.print("Connected to ");
    Serial.println(ssid);
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

    // Set up mDNS responder:
    // - first argument is the domain name, in this example
    //   the fully-qualified domain name is "esp32.local"
    // - second argument is the IP address to advertise
    //   we send our IP address on the WiFi network
    if (!MDNS.begin("esp32")) {
        Serial.println("Error setting up MDNS responder!");
        while(1) {
            delay(1000);
        }
    }
    Serial.println("mDNS responder started !..");

    // Start TCP (HTTP) server
    server.begin();
    Serial.println("TCP server started");

    // Add service to MDNS-SD
    MDNS.addService("http", "tcp", 80);
}

void loop(void)
{
    // Check if a client has connected
    WiFiClient client = server.available();
    if (!client) {
        return;
    }
    Serial.println("");
    Serial.println("New client connected.");

    // Wait for data from client to become available
    while(client.connected() && !client.available()){
        delay(1);
    }

    // Read the first line of HTTP request
    String req = client.readStringUntil('\r');

    // First line of HTTP request looks like "GET /path HTTP/1.1"
    // Retrieve the "/path" part by finding the spaces
    int addr_start = req.indexOf(' ');
    int addr_end = req.indexOf(' ', addr_start + 1);
    if (addr_start == -1 || addr_end == -1) {
        Serial.print("Invalid request: ");
        Serial.println(req);
        return;
    }
    req = req.substring(addr_start + 1, addr_end);
    Serial.print("Request: ");
    Serial.println(req);
    
    // NOTE: Double \r\n is required after the header if any, before the content begins ***
    // Without them, the response text is not sent to the browser
    
    String s;
    int rnd = random(1,10000);
    if (req == "/")
    {
        IPAddress ip = WiFi.localIP();
        String ipStr = String(ip[0]) + '.' + String(ip[1]) + '.' + String(ip[2]) + '.' + String(ip[3]);
        s = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE HTML>\r\n<html>Hello from ESP32 at ";
        s += ipStr +"<br/>(Rand: ";
        s += String(rnd);
        s += ")</html>\r\n\r\n";
        Serial.print("OK. Sending 200..Rand= ");
        Serial.println(rnd);
    }
    else  
    if (req == "/rand") {
        s = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html>Random number: ";
        s += String(rnd);
        s += "</html>\r\n\r\n";
        Serial.print("Dice: Sending a lucky random= ");      
        Serial.println(rnd);
    }
    else
    {
        s = "HTTP/1.1 404\r\n\r\nThat URL is not Found :( try again, man!\r\n\r\n";
        Serial.println("Not found - Sending 404 !");
    }
    client.print(s);

    client.stop();
    Serial.println("Client exits");
}
