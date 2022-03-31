#include <SFML/Graphics.hpp>
#include "src/Drone.h"
#include "src/DronePhysics.h"
#include "math.h"



void addNeighbors(std::vector<Drone> drones){
    for(auto &drone1: drones){
        for(auto &drone2: drones){
            drone1.neighbors.push_back(drone2);
            drone2.neighbors.push_back(drone1);
        }
    }
}

int main()
{
    sf::RenderWindow window(sf::VideoMode(1000, 700), "Drones");

    DronePhysics physics;

    Vector init = {100, 200, 0};
    std::vector<Drone> drones;
    double radius = 100; // радиус между дронами
    std::vector<sf::CircleShape> circles;

    for(int i=0; i<5; i++){
        Drone drone = { {10,10 + i*70.0,0}, {1,0,0}, {1000, 50, 0}};
        drones.push_back(drone);
        //std::cout << drones[i].state.position.x << " " << drones[i].state.position.y << std::endl;

        sf::CircleShape circle;
        circle.setRadius(5);
        circle.setOutlineColor(sf::Color::Magenta);
        circle.setFillColor(sf::Color::Magenta);
        circle.setOutlineThickness(5);
        circle.setPosition(init.x + drones[i].state.position.x, init.y + drones[i].state.position.y);
        circles.push_back(circle);

        circle.setRadius(5 + radius);
        circle.setOutlineColor(sf::Color::White);
        circle.setFillColor(sf::Color::Transparent);
        circle.setOutlineThickness(1);
        circle.setPosition(init.x + drones[i].state.position.x, init.y + drones[i].state.position.y);

    }

    double h = 0.05;

    while (window.isOpen())
    {
        sf::Event event;
        while (window.pollEvent(event))
        {
            if (event.type == sf::Event::Closed)
                window.close();
        }

        window.clear();

        addNeighbors(drones);

        for(int i=0; i<drones.size(); i++){
            drones[i] = physics.rungeKutta(drones[i], h);
            circles[i].setPosition(init.x + drones[i].state.position.x, init.y + drones[i].state.position.y);
            window.draw(circles[i]);

        }

        window.display();
    }

    return 0;
}
