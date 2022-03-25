#include "DronePhysics.h"

Drone::State DronePhysics::Fdt(Drone::State &drone, double &t) {

    Drone::State dbody;
    dbody.position = drone.velocity * t;
    drone.velocity = drone.velocity;

    return dbody;
}

Drone DronePhysics::rungeKutta(Drone &drone, double &h, double &dt) {
    std::cout << "INPUT: " << dt << std::endl;
    drone.state = Fdt(drone.state, dt);
    std::cout << "AFTER: " << drone.state.velocity.x << " " << drone.state.velocity.y << std::endl;
    return drone;
}
