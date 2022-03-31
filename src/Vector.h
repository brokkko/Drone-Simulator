#ifndef DRONES2D_VECTOR_H
#define DRONES2D_VECTOR_H

class Vector {
public:
    double x;
    double y;
    double z;

    Vector(double x, double y, double z): x{x}, y{y}, z{z} {};

    Vector() : x{0}, y{0}, z{0} {};

    Vector operator+(Vector r) const;
    Vector operator-(Vector r) const;
    Vector operator*(Vector r) const;
    Vector operator/(Vector r) const;
    Vector operator*(double r) const;
    Vector operator/(double r) const;

    double length();
    [[nodiscard]] double distanceTo(Vector d2) const;
    Vector rotate(double angle);
    // friend Vector operator*(double l, Vector r);
};


#endif //DRONES2D_VECTOR_H
