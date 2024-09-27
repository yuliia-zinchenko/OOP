#include "SparseList.h"
#include "SparseMatrix.h"
#include "Transport.h"
#include "PathFinder.h"
#include "Graph.h"


#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <ctime>
#include <set>
#include <cstdlib>


std::vector<std::pair<std::pair<std::size_t, std::size_t>, int>> generateRandomSparseMatrix(std::size_t rows, std::size_t cols, int nonZeroCount, int maxValue) {
    std::vector<std::pair<std::pair<std::size_t, std::size_t>, int>> matrix;
    std::set<std::pair<std::size_t, std::size_t>> uniqueIndices;
    while (uniqueIndices.size() < nonZeroCount) {
        std::size_t row = rand() % rows;
        std::size_t col = rand() % cols;
        uniqueIndices.insert({ row, col });
    }
    for (const auto& index : uniqueIndices) {
        int value = rand() % maxValue + 1; 
        matrix.push_back({ index, value });
    }
    return matrix;
}

std::vector<std::pair<std::pair<std::size_t, std::size_t>, std::vector<int>>> generateRandomSparseMatrixVectors(
    const std::size_t rows, const std::size_t cols, const int nonZeroCount) {
    std::vector<std::pair<std::pair<std::size_t, std::size_t>, std::vector<int>>> matrix;

    for (int i = 0; i < nonZeroCount; ++i) {
        std::size_t row = rand() % rows;
        std::size_t col = rand() % cols;
        std::vector<int> value = { rand() % 10, rand() % 10 }; // Вектор з 2 випадкових значень
        matrix.emplace_back(std::make_pair(std::make_pair(row, col), value));
    }

    return matrix;
}

void demoSparseMatrixInt() {
    std::cout << "==== Demo: SparseLMatrix with integers ====\n";
    const std::size_t rows = 3;
    const std::size_t cols = 3;
    const int nonZeroCount = 5; 
    const int maxValue = 10; 

    auto inputMatrix1 = generateRandomSparseMatrix(rows, cols, nonZeroCount, maxValue);
    auto inputMatrix2 = generateRandomSparseMatrix(rows, cols, nonZeroCount, maxValue);

    SparseMatrix<int> matrix1(inputMatrix1);
    SparseMatrix<int> matrix2(inputMatrix2);

    std::cout << "Matrix 1:\n";
    matrix1.print();
    int valueToFind = 6;
    try {
        auto position = matrix1.find(valueToFind);
        std::cout << "Search: value " << valueToFind << " found at position (in Matrix1): (" << position.first << ", " << position.second << ")\n";
    }
    catch (const std::runtime_error& e) {
        std::cerr << e.what() << "\n";
    }

    try {
        auto position = matrix1.find_if([](const int& value) {
            return value > 5;
            });
        std::cout << "First value > 5 was found at possition: ("
            << position.first << ", " << position.second << ")\n";
    }
    catch (const std::runtime_error& e) {
        std::cout << e.what() << std::endl;
    }

    std::cout << "\nMatrix 2:\n";
    matrix2.print();

    try {
        std::cout << "\nValue at (0, 0) Matrix 1: " << matrix1.at(0, 0) << "\n";
        std::cout << "Value at (2, 1) Matrix 2: " << matrix2.at(2, 1) << "\n";
    }
    catch (const std::out_of_range& e) {
        std::cerr << e.what() << "\n";
    }

    SparseMatrix<int> resultsumMatrix = matrix1 + matrix2;
    std::cout << "\nResult of Matrix 1 + Matrix 2:\n";
    resultsumMatrix.print();

    SparseMatrix<int> resultmult = matrix1 * matrix2;
    std::cout << "\nResult of multiplication:\n";
    resultmult.print();

    matrix1.transpose();
    std::cout << "\nTransposed Matrix 1 \n";
    matrix1.print();

}

void demoSparseMatrixString() {
    std::cout << "==== Demo: SparseMatrix with strings ====\n";
    std::vector<std::pair<std::pair<std::size_t, std::size_t>, std::string>> input1 = {
        {{0, 0}, "A"},
        {{0, 1}, "BB"},
        {{2, 2}, "C"}
    };

    std::vector<std::pair<std::pair<std::size_t, std::size_t>, std::string>> input2 = {
    {{0, 0}, "A"},
    {{1, 2}, "B"},
    {{2, 1}, "C"}
    };

    SparseMatrix<std::string> matrix1(input1);
    std::cout << "\nMatrix 1:\n";
    matrix1.print();

    std::string valueToFind = "B";
    try {
        auto position = matrix1.find(valueToFind);
        std::cout << "Search: value " << valueToFind << " found at position: (" << position.first << ", " << position.second << ")\n";
    }
    catch (const std::runtime_error& e) {
        std::cerr << e.what() << "\n";
    }

    try {
        auto position = matrix1.find_if([](const std::string& value) {
            return value.length() > 1; 
            });
        std::cout << "First value lenght > 1 was found at possition: ("
            << position.first << ", " << position.second << ")\n";
    }
    catch (const std::runtime_error& e) {
        std::cout << e.what() << std::endl;
    }

    SparseMatrix<std::string> matrix2(input2);
    std::cout << "\nMatrix 2:\n";
    matrix2.print();

    try {
        std::cout << "\nValue at (0, 0) Matrix 1: " << matrix1.at(0, 0) << "\n";
        std::cout << "Value at (2, 1) Matrix 2: " << matrix2.at(2, 1) << "\n";
    }
    catch (const std::out_of_range& e) {
        std::cerr << e.what() << "\n";
    }

    SparseMatrix<std::string> resultMatrix = matrix1 + matrix2;
    std::cout << "\nResult of Matrix 1 + Matrix 2:\n";
    resultMatrix.print();

    matrix1.transpose();
    std::cout << "\nTransposed Matrix1 \n";
    matrix1.print();

}

void demoSparseMatrixVector() {
    std::cout << "==== Demo: SparseMatrix with int vector ====\n";
    const std::size_t rows = 3;
    const std::size_t cols = 3;
    const int nonZeroCount = 5;
    const int maxValue = 10;
    auto generateRandomSparseMatrix = [](std::size_t rows, std::size_t cols, int nonZeroCount, int maxValue) {
        std::vector<std::pair<std::pair<std::size_t, std::size_t>, std::vector<int>>> inputMatrix;
        std::set<std::pair<std::size_t, std::size_t>> positions;

        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(1, maxValue);

        while (inputMatrix.size() < nonZeroCount) {
            std::size_t row = std::rand() % rows;
            std::size_t col = std::rand() % cols;
            auto pos = std::make_pair(row, col);
            if (positions.find(pos) == positions.end()) {
                positions.insert(pos);
                inputMatrix.emplace_back(pos, std::vector<int>{dis(gen), dis(gen), dis(gen)});
            }
        }
        return inputMatrix;
        };

    auto inputMatrix1 = generateRandomSparseMatrix(rows, cols, nonZeroCount, maxValue);
    auto inputMatrix2 = generateRandomSparseMatrix(rows, cols, nonZeroCount, maxValue);

    SparseMatrix<std::vector<int>> matrix1(inputMatrix1);
    SparseMatrix<std::vector<int>> matrix2(inputMatrix2);

    std::cout << "\nMatrix 1:\n";
    matrix1.print();
    std::cout << "\nMatrix 2:\n";
    matrix2.print();

    try {
        std::cout << "\nValue at (0, 0) Matrix 1: ";
        auto val1 = matrix1.at(0, 0);
        std::cout << "{ ";
        for (const auto& elem : val1) {
            std::cout << elem << " ";
        }
        std::cout << "}\n";

        std::cout << "Value at (2, 1) Matrix 2: ";
        auto val2 = matrix2.at(2, 1);
        std::cout << "{ ";
        for (const auto& elem : val2) {
            std::cout << elem << " ";
        }
        std::cout << "}\n";
    }
    catch (const std::out_of_range& e) {
        std::cerr << e.what() << "\n";
    }

    matrix1.transpose();
    std::cout << "\nTransposed Matrix 1 \n";
    matrix1.print();
}

void integrateVehiclesAndPaths() {
    SparseMatrix<double> distanceMatrix({
    {{0, 1}, 100},  // Road
    {{1, 2}, 50},   // river
    {{2, 3}, 200}   // Повітряний коридор
        });

    LandVehicle car(80);   // Наземний транспорт зі швидкістю 80 км/год
    WaterVehicle boat(40); // Водний транспорт зі швидкістю 40 км/год
    AirVehicle plane(600); // Повітряний транспорт зі швидкістю 600 км/год

    // Відстані для кожного транспорту
    std::map<std::pair<int, int>, double> weights;
    weights[{0, 1}] = distanceMatrix.at(0, 1) / car.getSpeed();   // Дорога для наземного
    weights[{1, 2}] = distanceMatrix.at(1, 2) / (boat.getSpeed() * 0.8); // Річка для водного
    weights[{2, 3}] = distanceMatrix.at(2, 3) / (plane.getSpeed() * 0.9); // Повітря для повітряного

    Graph g;
    g.addEdge(0, 1, weights[{0, 1}]); // Дорога
    g.addEdge(1, 2, weights[{1, 2}]); // Річка
    g.addEdge(2, 3, weights[{2, 3}]); // Повітряний коридор

    // Викликаємо алгоритм Дейкстри
    std::vector<double> distances;
    std::vector<std::size_t> previous;

    // Отримуємо відстані та попередні вузли
    std::tie(distances, previous) = g.dijkstra(0, 4);

    // Виводимо інформацію
    std::cout << "Calculating the shortest paths from point 0:\n";

    for (int i = 1; i < distances.size(); i++) {
        if (previous[i] != -1) {
            std::cout << i << ". Node " << previous[i] << " -> Node " << i << ":\n";
            if (i == 1) {
                std::cout << "   - Transport type: Land vehicle\n";
                std::cout << "   - Path type: Road\n";
                std::cout << "   - Distance: " << distanceMatrix.at(0, 1) << " km\n";
                std::cout << "   - Land vehicle speed: " << car.getSpeed() << " km/h\n";
                std::cout << "   - Travel time: " << weights[{0, 1}] << " hours\n";
            }
            else if (i == 2) {
                std::cout << "   - Transport type: Water vehicle\n";
                std::cout << "   - Path type: River\n";
                std::cout << "   - Distance: " << distanceMatrix.at(1, 2) << " km\n";
                std::cout << "   - Water vehicle speed: " << boat.getSpeed() << " km/h (0.8 factor for the river)\n";
                std::cout << "   - Travel time: " << weights[{1, 2}] << " hours\n";
            }
            else if (i == 3) {
                std::cout << "   - Transport type: Air vehicle\n";
                std::cout << "   - Path type: Air corridor\n";
                std::cout << "   - Distance: " << distanceMatrix.at(2, 3) << " km\n";
                std::cout << "   - Air vehicle speed: " << plane.getSpeed() << " km/h (0.9 factor for the corridor)\n";
                std::cout << "   - Travel time: " << weights[{2, 3}] << " hours\n";
            }
            std::cout << "   => The most efficient transport has been chosen.\n\n";
        }
    }

    std::cout << "Total travel time: " << distances[3] << " hours\n";
}

void demoSparseListInt() {
    std::cout << "==== Demo: SparseList with integers ====\n";

    SparseList<int> intSparseList(0); 

    intSparseList.add(10, 2);
    intSparseList.add(20, 5);
    intSparseList.add(30, 7);

    std::cout << "SparseList (int): \n";
    std::cout << intSparseList << std::endl;
    std::cout << "Element at index 5: " << intSparseList.at(5) << std::endl;
    std::cout << "Element at index 3 (default): " << intSparseList.at(3) << std::endl;

    const std::pair<int, size_t>* foundInt = intSparseList.find(20);
    if (foundInt) {
        std::cout << "Found value 20 at index " << foundInt->second << std::endl;
    }
    else {
        std::cout << "Value 20 not found.\n";
    }
}

void demoSparselistStr() {
    std::cout << "\n==== Demo: SparseList with strings ====\n";

    SparseList<std::string> stringSparseList("empty"); 

    stringSparseList.add("Hello", 1);
    stringSparseList.add("World", 4);
    stringSparseList.add("Sparse", 6);

    std::cout << "SparseList (string): \n";
    std::cout << stringSparseList << std::endl;

    std::cout << "Element at index 4: " << stringSparseList.at(4) << std::endl;
    std::cout << "Element at index 3 (default): " << stringSparseList.at(3) << std::endl;

    const std::pair<std::string, size_t>* foundString = stringSparseList.find("World");
    if (foundString) {
        std::cout << "Found string 'World' at index " << foundString->second << std::endl;
    }
    else {
        std::cout << "'World' not found.\n";
    }
    const std::pair<std::string, size_t>* foundCondition = stringSparseList.find_if([](const std::pair<std::string, size_t>& pair) {
        return pair.first.length() > 5;
        });
    if (foundCondition) {
        std::cout << "Found string with more than 5 characters: " << foundCondition->first << " at index " << foundCondition->second << std::endl;
    }
    else {
        std::cout << "No string with more than 5 characters found.\n";
    }
}

int main() {
    integrateVehiclesAndPaths();
    //demoSparseMatrixInt();
    //demoSparseMatrixString();
    //demoSparseMatrixVector();
    //demoSparseListInt();
    //demoSparselistStr();
    return 0;
}


