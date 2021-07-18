// ether.h

#ifndef ETHER_H
#define ETHER_H

/*
 Ethernet shield is attached to pins 10, 11, 12, 13.
 Pin 10 is the Ethernet CS pin for most Arduino shields.
 Pin 4 is the CS pin for the SD card reader.
*/
#include <SPI.h>
#include <Ethernet.h>
#include "common.h"
#include "config.h" 

class Ether {
  public:
    bool init (Config *pC);
    int CS_PIN =10;
};

#endif