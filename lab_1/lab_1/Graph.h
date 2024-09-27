#ifndef GRAPH_H
#define GRAPH_H

#include <vector>
#include <queue>
#include <limits>
#include <tuple>
#include <unordered_map>
#include <iostream>

class Graph {
private:
    struct Edge {
        std::size_t destination;
        double weight;
    };

    std::unordered_map<std::size_t, std::vector<Edge>> adjList;

public:

    void addEdge(std::size_t source, std::size_t destination, double weight) {
        adjList[source].push_back({ destination, weight });
    }

    std::tuple<std::vector<double>, std::vector<std::size_t>> dijkstra(std::size_t start, std::size_t nodes) {
        std::vector<double> distances(nodes, std::numeric_limits<double>::infinity());
        std::vector<std::size_t> previous(nodes, -1);  
        distances[start] = 0.0;

        using Pair = std::pair<double, std::size_t>;  // {distance, node}
        std::priority_queue<Pair, std::vector<Pair>, std::greater<>> pq;
        pq.push({ 0.0, start });

        while (!pq.empty()) {
            auto [currentDistance, currentNode] = pq.top();
            pq.pop();

            if (currentDistance > distances[currentNode]) continue;

            for (const auto& edge : adjList[currentNode]) {
                double newDist = currentDistance + edge.weight;
                if (newDist < distances[edge.destination]) {
                    distances[edge.destination] = newDist;
                    previous[edge.destination] = currentNode;
                    pq.push({ newDist, edge.destination });
                }
            }
        }

        return { distances, previous };
    }

    void printShortestPath(std::size_t start, std::size_t end, const std::vector<std::size_t>& previous) {
        if (previous[end] == -1) {
            std::cout << "There is no path from the node " << start << " to the node " << end << std::endl;
            return;
        }

        std::vector<std::size_t> path;
        for (std::size_t at = end; at != -1; at = previous[at]) {
            path.push_back(at);
        }
        std::reverse(path.begin(), path.end());

        std::cout << "The shortest distance from the node " << start << " to the node " << end << ": ";
        for (std::size_t node : path) {
            std::cout << node << " ";
        }
        std::cout << std::endl;
    }
};

#endif // GRAPH_H
