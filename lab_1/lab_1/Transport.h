#ifndef TRANSPORT_H
#define TRANSPORT_H

#include <iostream>
#include <vector>
#include <string>

class TransportVehicle {
protected:
    double speed;  
public:
    TransportVehicle(double speed) : speed(speed) {}  
    virtual double getSpeed() const = 0;
    virtual std::string getType() const = 0;
    virtual double calculateWeight(double distance) const = 0;
    virtual ~TransportVehicle() = default;
};

class LandVehicle : public TransportVehicle {
public:
    LandVehicle(double speed) : TransportVehicle(speed) {}  
    double getSpeed() const override { return speed; }
    std::string getType() const override { return "Land"; }
    double calculateWeight(double distance) const override {
        return distance / getSpeed();
    }
};

class WaterVehicle : public TransportVehicle {
public:
    WaterVehicle(double speed) : TransportVehicle(speed) {}
    double getSpeed() const override { return speed; }
    std::string getType() const override { return "Water"; }
    double calculateWeight(double distance) const override {
        return distance / (getSpeed() * 0.8);
    }
};

class AirVehicle : public TransportVehicle {
public:
    AirVehicle(double speed) : TransportVehicle(speed) {}
    double getSpeed() const override { return speed; }
    std::string getType() const override { return "Air"; }
    double calculateWeight(double distance) const override {
        return distance / (getSpeed() * 0.9);
    }
};
#endif //TRANSPORT_H
