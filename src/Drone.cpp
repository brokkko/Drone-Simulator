#include "Drone.h"

Drone::Drone() : position({0, 0, 0}), velocity({0,0,0}) {
    this->velocity = {0, 0, 0};
    this->position = {0, 0, 0};
    this->mass = 2;
}

Drone Drone::F(Drone body, double t){
    Drone dbody;
    dbody.position = body.velocity * t;
    dbody.velocity = body.velocity;

    return dbody;
}

Drone Drone::rungeKutta(Drone drone, double h, double dt)
{
//    Drone k1, k2, k3, k4;
//    k1 = F(drone, dt);
//    k2 = F(drone + 0.5 * h * k1, dt + 0.5 * h);
//    k3 = F(drone + 0.5 * h * k2, dt + 0.5 * h);
//    k4 = F(drone + h * k3, dt + h);
//    drone = drone + (h / 6) * k1;
//    drone = drone + (h / 3) * k2;
//    drone = drone + (h / 3) * k3;
//    drone = drone + (h / 6) * k4;
    drone = F(drone, dt);
    //std::cout << "AFTER: " << drone.position.x << " " << drone.position.y << std::endl;
    return drone;
}

Drone operator+(Drone a, Drone b) {
    a.position = a.position + b.position;
    a.velocity = a.velocity + b.velocity;
    return a;
}

Drone operator*(double a, Drone b) {
    b.position = b.position * a;
    b.velocity = b.velocity * a;
    return b;
}
