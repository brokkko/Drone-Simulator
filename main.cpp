#include <SFML/Graphics.hpp>
#include "src/Drone.h"
#include "src/DronePhysics.h"

int main()
{
    sf::RenderWindow window(sf::VideoMode(1000, 700), "Drones");

    DronePhysics physics;

    Vector init = {10, 300, 0};
    std::vector<Drone> drones;

    std::vector<sf::CircleShape> circles;

    for(int i=0; i<2; i++){
        Drone drone = { {10,10 + i*50.0,0}, {1,0,0}};
        drones.push_back(drone);

        sf::CircleShape circle;
        circle.setRadius(5);
        circle.setOutlineColor(sf::Color::Magenta);
        circle.setOutlineThickness(5);
        circle.setPosition(init.x + drones[i].state.position.x, init.y + drones[i].state.position.y);
        circles.push_back(circle);
    }

    double h = 0.05, t = 0;

    while (window.isOpen())
    {
        sf::Event event;
        while (window.pollEvent(event))
        {
            if (event.type == sf::Event::Closed)
                window.close();
        }

        window.clear();

        for(int i=0; i<drones.size(); i++){
            drones[i] = physics.rungeKutta(drones[i], h, t);
            //std::cout << "here" << std::endl;
            //std::cout << drones[i].state.position.x << " " << drones[i].state.position.y << std::endl;
            circles[i].setPosition(init.x + drones[i].state.position.x, init.y + drones[i].state.position.y);
            window.draw(circles[i]);
        }
        std::cout << std::endl;
        t += h;

        //window.draw(circles);
        window.display();
    }

    return 0;
}
