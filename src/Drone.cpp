#include "Drone.h"

Drone::Drone(Vector position, Vector velocity, Vector target)  {
    this->state.position = position;
    this->state.velocity = velocity;
    this->target = target;
//    this->velocity = {0, 0, 0};
//    this->position = {0, 0, 0};
}




