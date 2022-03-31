#include "Vector.h"
#include "cmath"

Vector Vector::operator+(Vector r) const {
    return {this->x+r.x, this->y+r.y, this->z+r.z};
}

Vector Vector::operator-(Vector r) const {
    return {this->x - r.x, this->y - r.y, this->z - r.z};
}

Vector Vector::operator*(Vector r) const {
    return {this->x * r.x, this->y * r.y, this->z * r.z};
}

Vector Vector::operator/(Vector r) const {
    return {this->x /  r.x, this->y / r.y, this->z / r.z};
}

Vector Vector::operator*(double r) const {
    return {this->x * r, this->y * r, this->z * r};
}

Vector Vector::operator/(double r) const {
    return {this->x /  r, this->y / r, this->z / r};
}

double Vector::length() {  //TODO: add Z
    return sqrt(x*x + y*y);
}

double Vector::distanceTo(Vector d2) const {
    return sqrt((x - d2.x)*(x - d2.x)
                + (y - d2.y)* (y - d2.y));
}

Vector Vector::rotate(double angle) {
    double tx = x;
    double ty = y;
    x = tx * cos(angle) - ty * sin(angle);
    y = tx * sin(angle) + ty * cos(angle);
    return *this;
}
