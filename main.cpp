#include <SFML/Graphics.hpp>
#include "src/Drone.h"

int main()
{
    sf::RenderWindow window(sf::VideoMode(1000, 700), "Drones");

    Drone drone;
    double h = 0.1, t = 0;
    drone.velocity = {1, 0, 0};
    drone.position = {10, 10, 10};

    Vector init = {10, 300, 0};

    sf::CircleShape circle;
    circle.setRadius(5);
    circle.setOutlineColor(sf::Color::Magenta);
    circle.setOutlineThickness(5);
    circle.setPosition(init.x, init.y);

    while (window.isOpen())
    {
        sf::Event event;
        while (window.pollEvent(event))
        {
            if (event.type == sf::Event::Closed)
                window.close();
        }

        drone = drone.rungeKutta(drone, h, t);
        t += h;
        circle.setPosition(init.x + drone.position.x, init.y + drone.position.y);

        window.clear();
        window.draw(circle);
        window.display();
    }

    return 0;
}
