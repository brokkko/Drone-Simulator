#ifndef DRONES2D_DRONE_H
#define DRONES2D_DRONE_H


#include "Vector.h"

class Drone {
public:
    Vector velocity;
    Vector position;
    double mass;
public:
    Drone();
    Drone F(Drone drone, double t);
    Drone rungeKutta(Drone drone, double h, double dt);

    friend Drone operator +(Drone a, Drone b);
    friend Drone operator *(double a, Drone b);
};


#endif //DRONES2D_DRONE_H
