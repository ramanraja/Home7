// main.h

#ifndef MAIN_H
#define MAIN_H

#include "common.h"
#include "config.h"
#include "ether.h"
#include "emqttlite.h"
#include <Timer.h>

#define NULL_TERM  '\0'

// ALL = all the 6 sensors are enabled
// 1=drinking water tank, 2=salt water tank
// FULL = inflow + overflow + halfway sensor of one tank
// HALF = halfway sensors of both tanks
enum {
    MODE_ALL,
    MODE_FULL1,
    MODE_FULL2,
    MODE_HALF,
    MODE_NONE
};

#endif