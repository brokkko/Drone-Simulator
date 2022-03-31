#ifndef DRONES2D_DRONE_H
#define DRONES2D_DRONE_H

#include <iostream>
#include <vector>
#include "list"
#include "Vector.h"



class Drone {

public:

    struct State{
        Vector velocity;
        Vector position;

        friend State operator +(State a, State b);
        friend State operator *(double a, State b);
    };

    Vector target;

    State state;
    std::vector<Drone> neighbors;

    Drone(Vector position, Vector velocity, Vector target);

};


#endif //DRONES2D_DRONE_H
