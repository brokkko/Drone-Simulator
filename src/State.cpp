#include "Drone.h"

Drone::State operator+ (Drone::State &a, Drone::State &b){
    Drone::State c;
    c.position = a.position + b.position;
    c.velocity = a.velocity + b.velocity;
    return c;
}

Drone::State operator*(double &a, Drone::State &b) {
    Drone::State c;
    c.position = b.position * a;
    c.velocity = b.velocity * a;
    return c;
}
