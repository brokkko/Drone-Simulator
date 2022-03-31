#include "DronePhysics.h"
#include "cmath"

double DronePhysics::DegreesToRadians(double degrees) {
    return ( degrees * M_PI) / 180 ;;
}

Drone::State DronePhysics::Fdt(Drone &drone, double h) {

    //

    Drone::State dX;
    dX.position = pathDefinition(drone, h);

    return dX;
}

Drone DronePhysics::rungeKutta(Drone &drone, double &h) {

    Drone::State xdt = Fdt(drone, h);
    drone.state = drone.state + h * xdt;
    //std::cout << "AFTER: " << drone.state.position.x << " " << drone.state.position.y << std::endl;
    return drone;
}

Vector DronePhysics::pathDefinition(Drone &drone, double h) {
    // здесь перебираем вектора, выбираем наилучший

    double angle = this->DegreesToRadians(20);
    Vector v = drone.state.velocity.rotate(-angle);
    Vector pBest;
    double best = 0.0;
    for(int i = 0; i<3; i++){
        double current = quality(drone, v.rotate(i*angle), h);
        if(current > best){
            best = current;
            pBest = v;
        }
    }

    return pBest;
}

double DronePhysics::quality(const Drone &drone, Vector nextVelocity, double &h) {

   // Drone droneNext = droneCurrent;
    //droneNext.state.d

    // f = Ttarget + Tclose
    double Ttarget = (((drone.target - drone.state.position) //to target
                    - (drone.target - drone.state.position + nextVelocity * h))).length() / nextVelocity.length();

    double radius = 10;
    double nextClosest = drone.neighbors[0].state.position.distanceTo(drone.state.position + nextVelocity * h);
    double currentClosest = drone.neighbors[0].state.position.distanceTo(drone.state.position);
    for(auto& neighbour : drone.neighbors){
        double nextDist = neighbour.state.position.distanceTo(drone.state.position + nextVelocity * h);
        double currentDist = neighbour.state.position.distanceTo(drone.state.position + nextVelocity * h);
        if(nextDist < nextClosest){
            nextClosest = nextDist;
            currentClosest = currentDist;
        }
    }

    if(nextClosest < radius){
        return .0;
    }

    double Tclose = (currentClosest - nextClosest) / nextVelocity.length();

    std::cout << "F: " << std::endl;
    std::cout << "target = " << Ttarget << "\nclose = "<< Tclose << std::endl;

    return Ttarget + Tclose;
}

