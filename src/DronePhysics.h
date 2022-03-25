#ifndef DRONES2D_DRONEPHYSICS_H
#define DRONES2D_DRONEPHYSICS_H


#include "Drone.h"

class DronePhysics {
public:
    Drone::State Fdt(Drone::State &drone, double &t);
    Drone rungeKutta(Drone &drone, double &h, double &dt);
};


#endif //DRONES2D_DRONEPHYSICS_H
