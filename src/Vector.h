#ifndef DRONES2D_VECTOR_H
#define DRONES2D_VECTOR_H

class Vector {
public:
    double x;
    double y;
    double z;

    Vector(double x, double y, double z){
        this->x = x;
        this->y = y;
        this->z = z;
    }

    Vector operator+(Vector r) const;
    Vector operator-(Vector r) const;
    Vector operator*(Vector r) const;
    Vector operator/(Vector r) const;
    Vector operator*(double r) const;
    Vector operator/(double r) const;
    // friend Vector operator*(double l, Vector r);
};


#endif //DRONES2D_VECTOR_H
