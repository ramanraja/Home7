// water12.ino

/*------------------------------------------------------------------------------------------
Water level sensor for two tanks.  
  Each tank has 3 sensors: (1) Water flowing inlet from motor (2) Overflow (3) Half tank level  
  Directly dip 3 sensor electrodes + a common ground in water
  The sensors can be turned on/off as needed, to minimize electrode corrosion.
NOTES:
  Avoid using the digital pins used by the Ethernet shield (10 to 13) for the water sensors !
  Also avoid pin 4 which is chip select for the SD card reader
  Using analog pins for digital input with pullup was found unreliable. (Why ?)
Status message format:
  status_msg[] is 10 bytes max in length. 
  status_msg[0] is 'A','B', 'C', 'D', 'E', 'R' or 'N' indicating the payload type.
  status_msg[1] is always a space, used for frame integrity check.
  Type A: MODE_FULL1
     status_msg[2,3 and 4] are ASCII characters '1' or '0'. They indicate tank infow,overflow and half-full 
         indicator for drining water tank. 
     status_msg[5] is NULL. End of payload.
  Type B: MODE_FULL2
     status_msg[2,3 and 4] are ASCII characters '1' or '0'. They indicate tank infow,overflow and half-full 
         indicator for salt water tank. 
     status_msg[5] is NULL. End of payload.
  Type C: MODE_ALL
     status_msg[2,3 and 4] are ASCII characters '1' or '0' for drinking water tank.
     status_msg[5] is again a space. 
     status_msg[6,7 and 8] are ASCII characters '1' or '0'  for salt water tank. 
     status_msg[9] is NULL. End of payload.
  Type D: MODE_HALF; this is the default mode when no commands have been received.
     This is autonomous event notification packet. Only the two half-way sensors are enabled.
     status_msg[2] is '1' or '0' for the half way sensor of drinking water tank.
     status_msg[3] is '1' or '0' for the half way sensor of salt water tank.
     status_msg[4] is NULL. End of payload.
  Type E: Error notification
     An unexpected or malformed command was received and was ignored. The mode remains unchanged.
     status_msg[2] is NULL. End of payload.      
  Type R: MODE_ALL, after a reboot
     The water level sensor rebooted. The Monitor has to intimate the desired mode again.
     The packet structure is the same as in Type C.
  Type N: MODE_NONE
     All sensors are disabled. Only empty keep-alive signal is sent once in 5 minutes.
     status_msg[2] is NULL. End of payload. 
Command format:
  A command must have 3 bytes of ASCII characters:
  cmd[0] is 'A','B', 'C', 'D', 'O', or 'N' indicating the required mode/packet type.
  cmd[1] is always a space for sanity check.
  cmd[2] is '1' or '0' indicating start/stop of that mode. 
  cmd[3] is '\0'.
  if cmd[0] is 'O', the tank controller sends a single 'C' type packet and reverts to its previous mode.
  if cmd[0] is 'N', the tank controller stops sensing and sends empty keep-alive packets once in 5 minutes.
  In all other cases, after receiving a '0' at cmd[2], which signals the end of the current mode, it goes 
      to its default mode, ie, MODE_HALF.
TODO:
  Read half way sensor once in 5 minutes, and double-check it. Notify downward transition.
--------------------------------------
Test:
  mosquitto_sub -h 192.168.0.99 -t intof/tank/+  -v
  mosquitto_pub -h 192.168.0.99 -t intof/tank/cmnd -m  "A015"
On MQTT broker (Raspberry Pi):
  sudo systemctl stop  mosquitto.service  
  sudo systemctl start mosquitto.service
---------------------------------------------------------------------------------------------*/

#include "src/main.h"

#define ON  LOW
#define OFF HIGH

Timer T;
Config C; 
Ether E;
EmqttLite M;

int led = A0;                           // active low
byte sd_card_cs = 4;                    // disable SD card by making its CS pin HIGH
// drinking water tank
byte inflow1 = 2;                       // red wires
byte overflow1 = 3;                     // green wires
byte halfway1 = 8;                      // yellow & black
// salt water tank
byte inflow2 = 5;                       // red wires
byte overflow2 = 6;                     // green wires
byte halfway2 = 7;                      // yellow & black  

int NETWORK_CHECK_INTERVAL = 29;        // this is a count (=29 seconds)
int TANK_CHECK_INTERVAL = 3000;         // this is in mSec 
unsigned int TICK_INTERVAL = 1000;      // this is in mSec
unsigned long KEEP_ALIVE_INTERVAL = 1*60;  // for testing! // 5*60; // count; (=5 minutes)
bool connection_status = false;         // true=MQTT connected
bool monitor_enabled = true;            // enable/disable sensing current
char status_msg [10];                   // all 10 bytes are used *

byte mode = MODE_ALL;                   // enum in main.h

void setup() {
    init_hardware();
    init_serial();
    C.init();
    E.init(&C);
    M.init(&C);
    blink();
    check_network();
    send_initial_status();
    T.every (TICK_INTERVAL, tick);
    T.every (TANK_CHECK_INTERVAL, check_tanks);
}

void loop () {
    T.update();
    M.update();
}

void init_hardware() {
    pinMode (sd_card_cs, OUTPUT); // active LOW 
    digitalWrite (sd_card_cs, HIGH); // disable the SD card reader
    pinMode (led, OUTPUT);
    digitalWrite (led, OFF); 
}   

// The sensors can be enabled or disabled at will
// Disabling them when not needed minimizes corrosion of electrodes
// all sensors are active LOW.  (low when sensor is triggered by water)

void enable_sensors() {
    if (mode==MODE_FULL1 || mode==MODE_ALL) {
        pinMode (inflow1, INPUT_PULLUP); 
        pinMode (overflow1, INPUT_PULLUP);
        pinMode (halfway1, INPUT_PULLUP);    
    }
    if (mode==MODE_FULL2 || mode==MODE_ALL) {
        pinMode (inflow2, INPUT_PULLUP);  
        pinMode (overflow2, INPUT_PULLUP);
        pinMode (halfway2, INPUT_PULLUP);  
    }
    else if (mode==MODE_HALF) {
        pinMode (halfway1, INPUT_PULLUP); 
        pinMode (halfway2, INPUT_PULLUP); 
    }
    delayMicroseconds(50); // enough time to stabilize before reading?
}

// prevent current flowing to the electrodes
void disable_sensors() {
    if (mode==MODE_FULL1 || mode==MODE_ALL || mode==MODE_NONE) {
        pinMode (inflow1, OUTPUT); 
        pinMode (overflow1, OUTPUT);
        pinMode (halfway1, OUTPUT);    
        digitalWrite (inflow1, LOW);  
        digitalWrite (overflow1, LOW);    
        digitalWrite (halfway1, LOW);    
    }
    if (mode==MODE_FULL2 || mode==MODE_ALL || mode==MODE_NONE) {
        pinMode (inflow2, OUTPUT);  
        pinMode (overflow2, OUTPUT);
        pinMode (halfway2, OUTPUT); 
        digitalWrite (inflow2, LOW);   
        digitalWrite (overflow2, LOW);
        digitalWrite (halfway2, LOW);           
    }
    else if (mode==MODE_HALF) {
        pinMode (halfway1, OUTPUT);    
        pinMode (halfway2, OUTPUT);    
        digitalWrite (halfway1, LOW);    
        digitalWrite (halfway2, LOW);    
    }
}

void blink() {
    for (int i=0; i<4; i++) {
      digitalWrite (led, ON);
      delay (150);
      digitalWrite (led, OFF);
      delay (150);      
    }
}

unsigned int tick_count = 0;  // max: 65,536
// at 1 second tick, this wraps around once in 18 hours
void tick () {
  indicate_network_status();
  tick_count++;
  if (tick_count % NETWORK_CHECK_INTERVAL == 0)
    check_network();
  else if (tick_count % KEEP_ALIVE_INTERVAL == 0)
    keep_alive();
}

bool flash = false;
void indicate_network_status() {
  if (!connection_status) {
    digitalWrite (led, flash);
    flash = !flash;
  }
}
  
void check_network() {  
  connection_status = M.checkConnection(); // this will reconnect if needed
  SERIAL_PRINT (F("MQTT connected="));
  SERIAL_PRINTLN (connection_status);
  if (connection_status)
      digitalWrite (led, OFF); // avoid LED stuck in the ON state
}

void init_serial() {
    Serial.begin(115200);
    SERIAL_PRINTLN (F("Water tank sensor V1.0 starts.."));
}

//----------------------------------------------------------------------------------------------------
// business logic

void app_callback (const char* cmd) {
    SERIAL_PRINT  (F("cmnd: "));
    SERIAL_PRINTLN (cmd);
    if (cmd[1] != ' ' || strlen(cmd) !=3) {
      send_error_status(); // malformed command payload
      return;
    }
    switch (cmd[0]) {   
      case 'A':
        if (cmd[2]=='1')
            mode = MODE_FULL1;
        else if (cmd[2]=='0')
            mode = MODE_HALF;
        break;
      case 'B':
        if (cmd[2]=='1')
            mode = MODE_FULL2;
        else if (cmd[2]=='0')
            mode = MODE_HALF;
        break;
      case 'C':
        if (cmd[2]=='1')
            mode = MODE_ALL;
        else if (cmd[2]=='0')
            mode = MODE_HALF;
        break;    
      case 'D':  // cmd shoud still have '1' or '0', but it is ignored
        mode = MODE_HALF;
        break;
      case 'O':  // cmd shoud still have '1' or '0', but it is ignored
        send_oneoff_status();
        return;
      case 'N':  // cmd shoud still have '1' or '0', but it is ignored
        mode = MODE_NONE;
        break;
      default:
        send_error_status(); // unknown command
        return;              
    }
    M.publish (C.pub_topic, cmd); // acknowledge, by echoing the command on the pub topic
} 

// The sensors are active low: if water touches them, the pin goes LOW
void check_tanks() {   
    if (mode==MODE_HALF || mode==MODE_NONE)  // all sensing has been disabled, or only lazy default scanning is enabled
        return; 
    enable_sensors();
    read_sensors();   // read sensors and compose the payload
    disable_sensors();
    send_status();
}

void send_initial_status () {
    mode = MODE_ALL;     // temporarily set the mode
    enable_sensors();
    read_sensors();      // read sensors and compose the payload
    disable_sensors();
    status_msg[0]= 'R';  // overwrite the first byte, indicating reboot
    send_status();
    mode = MODE_HALF;    // this is the default mode
}

void send_oneoff_status () {
    int previous_mode = mode;    // save a copy
    mode = MODE_ALL;
    enable_sensors();      // temporarily change the mode
    read_sensors();        // read sensors and compose the payload
    disable_sensors();
    send_status();
    mode = previous_mode;    // restore the earlier one
}

void send_half_status () { // this should be called only in MODE_HALF
    enable_sensors();       
    read_sensors();        // read sensors and compose the payload
    disable_sensors();
    send_status();
}

void send_null_status() {
    status_msg[0]= 'N';
    status_msg[1]= ' ';
    status_msg[2] = NULL_TERM; 
    send_status(); 
}

void send_error_status() {
    status_msg[0]= 'E';
    status_msg[1]= ' ';
    status_msg[2] = NULL_TERM; 
    send_status(); 
}

void read_sensors() {
    switch (mode) {
        case MODE_FULL1:
            status_msg[0]= 'A';
            status_msg[1]= ' ';
            status_msg[2] = digitalRead (inflow1) ? '0' : '1';   
            status_msg[3] = digitalRead (overflow1) ? '0' : '1';   
            status_msg[4] = digitalRead (halfway1) ? '0' : '1'; 
            status_msg[5] = NULL_TERM;                
            break;
        case MODE_FULL2:
            status_msg[0]= 'B';
            status_msg[1]= ' ';
            status_msg[2] = digitalRead (inflow2) ? '0' : '1';   
            status_msg[3] = digitalRead (overflow2) ? '0' : '1'; 
            status_msg[4] = digitalRead (halfway2) ? '0' : '1'; 
            status_msg[5] = NULL_TERM;               
            break;
        case MODE_ALL:
            status_msg[0]= 'C';
            status_msg[1]= ' ';
            status_msg[2] = digitalRead (inflow1) ? '0' : '1';   
            status_msg[3] = digitalRead (overflow1) ? '0' : '1';   
            status_msg[4] = digitalRead (halfway1) ? '0' : '1'; 
            status_msg[5] = ' ';
            status_msg[6] = digitalRead (inflow2) ? '0' : '1';   
            status_msg[7] = digitalRead (overflow2) ? '0' : '1'; 
            status_msg[8] = digitalRead (halfway2) ? '0' : '1'; 
            status_msg[9] = NULL_TERM;  
            break;
        case MODE_HALF:
            status_msg[0]= 'D';
            status_msg[1]= ' ';
            status_msg[2] = digitalRead (halfway1) ? '0' : '1'; 
            status_msg[3] = digitalRead (halfway2) ? '0' : '1'; 
            status_msg[4] = NULL_TERM;           
            break;
        default:
            SERIAL_PRINTLN (F("\n\n***** PANIC ! INVALID MODE !! ******\n\n"));
            break;                        
    }
}

void keep_alive() {
    if (mode == MODE_HALF) 
        send_half_status();
    else if (mode == MODE_NONE) 
        send_null_status();    
}

void send_status() {
  //SERIAL_PRINTLN (status_msg);   
  M.publish (C.pub_topic, status_msg);
}
