// ether.cpp

#include "ether.h"

bool Ether::init (Config *pC) {
    // optional: if you want to change the default CS pin:
    //Ethernet.init (CS_PIN);  
    SERIAL_PRINTLN (F("Registering with DHCP server.."));
    
    // Under ideal circumstances, the one line begin(mac) alone is sufficient
    if (Ethernet.begin (pC->mac) != 0) {   // return value will be zero on DHCP failure
      SERIAL_PRINT (F("DHCP assigned IP: "));
      SERIAL_PRINTLN (Ethernet.localIP());
      delay(1500);    // give the shield time initialize
      return (true);
    }
    // DHCP failed:
    SERIAL_PRINTLN (F("Ethernet could not get an IP using DHCP."));
    if (Ethernet.hardwareStatus() == EthernetNoHardware) {
        SERIAL_PRINTLN (F("Ethernet shield was not found."));
        return (false);
    }
    if (Ethernet.linkStatus() == LinkOFF) {
        SERIAL_PRINTLN (F("Ethernet cable is not connected."));
        ////return (false); // you may still be able to assign a static IP to the board
    }
    // try to congifure again, using IP address instead of DHCP:
    SERIAL_PRINTLN (F("Trying to setup a static IP.."));
    Ethernet.begin (pC->mac, pC->device_ip, pC->router_ip);  // this version of begin() returns void
    delay(1500);    // give the shield time initialize
    return (true); // how can you be sure it was a success?
}