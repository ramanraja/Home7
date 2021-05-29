// TODO :set up Mithila's SSID;    
// NTP server sending 32 bit integers converted to 4 byte arrays (Big endian)
// Use it with any NTP time receiver, including Tasmota devices.
// This serves actual UTC time data using a hardware RTC module.
// New in this version: integrated with the new  MyFiMulti (formerly, QD-WiFi) class
// https://stackoverflow.com/questions/3784263/converting-an-int-into-a-4-byte-char-array-c
// https://thearduinoandme.wordpress.com/tutorials/esp8266-send-receive-binary-data/
// https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/udp-examples.html
// http://www.esp8266learning.com/wemos-ds3231-rtc-example.php 

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "src/main.h"

#define TX_BUFFER_SIZE    48        // NTP packets are 48 bytes long
#define RX_BUFFER_SIZE    64        // NTP clients can follow some strange protocols         
#define FIRST_BYTE        0x1C      // magic constant, see NTP protocol header
#define TS_STARTING_BYTE  40        // bytes 40,41,42,43 are the time stamp 44 to 47 can be filled with zeros
 
#define MOCK_TS    3830932228UL
unsigned long ts_counter = MOCK_TS;

MyRTC R;
MyfiMulti W;
WiFiUDP udp_socket;
unsigned long listening_port =  123;  // local NTP port to listen on  // 9000
unsigned char rx_buffer [RX_BUFFER_SIZE];   // incoming data buffer  
unsigned char tx_buffer [TX_BUFFER_SIZE];   // out going data buffer; NOTE: this MUST be unsigned char only ***  

void setup()
{
    init_serial();
    SERIAL_PRINTLN (F("\nQ&DIY NTP server starting.."));  
    W.init(0, 95);  // for testing
    //W.init(1, 95);  // for Mithila AP
    R.init();  // RTC
    
    // we send a quick and dirty non-standard payload: it is all zeros except
    // the first byte (flags) and the 4 byte Unix time stamp in bytes 40-43
    tx_buffer [0] = FIRST_BYTE;
    for (int i=1; i<TX_BUFFER_SIZE; i++)
        tx_buffer[i] = 0x0; 
        
    udp_socket.begin (listening_port);
    SERIAL_PRINT (F("Listening at IP "));
    SERIAL_PRINT (WiFi.localIP());
    SERIAL_PRINT (F(", UDP port "));        
    SERIAL_PRINT (listening_port);
    SERIAL_PRINTLN (F(" ..."));
}

void loop()
{
    W.update();  // this is necessary to rejoin wifi after a connection loss
    check_serial(); // RTC time can be adjusted through serial commands
    check_udp();  // serve unsuspecting NTP time clients :)
}

void check_udp() {    
    int packetSize = udp_socket.parsePacket();
    if (packetSize <= 0) // no client requests
        return;  
    SERIAL_PRINT (F("\nRx "));
    SERIAL_PRINT (packetSize);
    SERIAL_PRINT (F(" bytes from "));        
    SERIAL_PRINT (udp_socket.remoteIP());
    SERIAL_PRINT (F(":"));
    SERIAL_PRINTLN (udp_socket.remotePort());
      
    int len = udp_socket.read (rx_buffer, RX_BUFFER_SIZE);
    if (len > TX_BUFFER_SIZE) { // RX_BUFFER_SIZE is kept larger than TX_BUFFER_SIZE for this check
        SERIAL_PRINTLN ("\n** RX buffer overflow !!**\n");
        return;
    }
    SERIAL_PRINT ("UTC: ");
    R.print_time(); 
    ts_counter = R.get_epoch_time_1970();  // Tasmota expects 1970-baselined UTC time
    convert_and_embed (ts_counter);  // the result is written directly into the global tx_buffer
    // reply back to the IP address and port of the sender
    udp_socket.beginPacket (udp_socket.remoteIP(), udp_socket.remotePort());
    udp_socket.write (tx_buffer, TX_BUFFER_SIZE);  //  ((char *)tx_buffer);
    udp_socket.endPacket();
}

// Convert the 32 bit mock time stamp into 4 bytes and write directly into the tx_buffer at bytes 40-43 *
void convert_and_embed (unsigned long n) {
    tx_buffer[TS_STARTING_BYTE]   = (n >> 24) & 0xFF; // this conforms to Big Endian network byte order
    tx_buffer[TS_STARTING_BYTE+1] = (n >> 16) & 0xFF;
    tx_buffer[TS_STARTING_BYTE+2] = (n >> 8) & 0xFF;
    tx_buffer[TS_STARTING_BYTE+3] = n & 0xFF;
}

void init_serial() {
#ifdef ENABLE_DEBUG
    Serial.begin (BAUD_RATE); 
    #ifdef VERBOSE_MODE
       Serial.setDebugOutput(true);
    #endif
    Serial.setTimeout (200); 
#endif     
}

// You can adjust the time by sending 4 integers, separated by space, through the serial port:
// they are the delta increase/decrease in day,hour,min,sec. (can be negative also).
void check_serial () {
    if (!Serial.available()) 
        return;
    int days = Serial.parseInt();  // can be negative also
    int hours = Serial.parseInt();
    int minutes = Serial.parseInt();
    int seconds = Serial.parseInt();
    delay(250); // without this delay, it still reads a couple of zeros
    while (Serial.available())
        Serial.read();   // discard newline and other junk
    SERIAL_PRINTLN (F("\n----------------------------------------------------"));
    SERIAL_PRINTLN (F("Adjusting the clock.."));    
    R.print_time();
    SERIAL_PRINT (F("Adjusting by ")); 
    SERIAL_PRINT (days);
    SERIAL_PRINT (F(" days, "));     
    SERIAL_PRINT (hours);
    SERIAL_PRINT (F(" hours, "));    
    SERIAL_PRINT (minutes);
    SERIAL_PRINT (F(" mins, ")); 
    SERIAL_PRINT (seconds);
    SERIAL_PRINTLN (F(" secs."));
    // Aliter:
    //R.fine_tune (minutes, seconds);
    R.adjust_time (days, hours, minutes, seconds);
    R.print_time();
    SERIAL_PRINTLN (F("-----------------------------------------------------\n"));
} 
 
