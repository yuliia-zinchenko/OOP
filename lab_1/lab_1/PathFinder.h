#ifndef PATHFINDER_H
#define PATHFINDER_H




class Path {
public:
    virtual double getDistance() const = 0;
    virtual std::string getPathType() const = 0;
    virtual ~Path() = default;
};

class Road : public Path {
private:
    double distance;
public:
    Road(double d) : distance(d) {}
    double getDistance() const override { return distance; }
    std::string getPathType() const override { return "Road"; }
};

class River : public Path {
private:
    double distance;
public:
    River(double d) : distance(d) {}
    double getDistance() const override { return distance; }
    std::string getPathType() const override { return "River"; }
};

class AirCorridor : public Path {
private:
    double distance;
public:
    AirCorridor(double d) : distance(d) {}
    double getDistance() const override { return distance; }
    std::string getPathType() const override { return "AirCorridor"; }
};

#endif // PATHFINDER_H