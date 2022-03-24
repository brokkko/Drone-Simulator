#include "Vector.h"

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

