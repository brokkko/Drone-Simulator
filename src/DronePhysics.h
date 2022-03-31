#ifndef DRONES2D_DRONEPHYSICS_H
#define DRONES2D_DRONEPHYSICS_H

#include "Drone.h"

class DronePhysics {
public:
    double DegreesToRadians(double degrees);
    Drone::State Fdt(Drone &drone, double h);
    Drone rungeKutta(Drone &drone, double &h);
    Vector pathDefinition(Drone &drone, double h);
    double quality(const Drone &drone, Vector velocity, double &h);
};


#endif //DRONES2D_DRONEPHYSICS_H
