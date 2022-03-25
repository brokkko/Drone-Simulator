#ifndef DRONES2D_DRONE_H
#define DRONES2D_DRONE_H

#include <iostream>
#include "list"
#include "Vector.h"



class Drone {
public:
    struct State{
        Vector velocity;
        Vector position;

        friend State operator +(State &a, State &b);
        friend State operator *(double &a, State &b);
    };

    State state;
    std::list<Drone> neighbors;

public:
    Drone(Vector position, Vector velocity);

};


#endif //DRONES2D_DRONE_H
