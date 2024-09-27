#define CATCH_CONFIG_MAIN
#include "catch2/catch.hpp"
#include "sparseMatrix.h"
#include "GenRandomData.h" 
#include <random>
#include <vector>

TEST_CASE("SparseMatrix tests", "[SparseMatrix]") {

    SparseMatrix<int> matrix;

    SECTION("Add non-default values") {
        for (size_t i = 0; i < 10; ++i) {
            std::size_t row = rand() % 10; 
            std::size_t col = rand() % 10; 
            int value;
            generateRandomData(value); 
            REQUIRE_NOTHROW(matrix.add(row, col, value));
            REQUIRE(matrix.at(row, col) == value);
        }
    }

    SECTION("Add default values throws error") {
        REQUIRE_THROWS_AS(matrix.add(0, 0, 0), std::logic_error);
    }

    SECTION("Add existing index throws error") {
        std::size_t row = 1;
        std::size_t col = 1;
        int value = 5;
        matrix.add(row, col, value);
        REQUIRE_THROWS_AS(matrix.add(row, col, 10), std::invalid_argument);
    }

    SECTION("Find existing element") {
        std::size_t row = 2;
        std::size_t col = 2;
        int value;
        generateRandomData(value);
        matrix.add(row, col, value);
        auto found = matrix.find(value);
        REQUIRE(found.first == row);
        REQUIRE(found.second == col);
    }

    SECTION("Find non-existing element throws error") {
        REQUIRE_THROWS_AS(matrix.find(999), std::runtime_error);
    }

    SECTION("Transpose matrix") {
        matrix.add(0, 1, 1);
        matrix.add(1, 0, 2);
        matrix.transpose();

        REQUIRE(matrix.at(1, 0) == 1);
        REQUIRE(matrix.at(0, 1) == 2);
    }

    SECTION("Matrix addition") {
        SparseMatrix<int> matrixA;
        SparseMatrix<int> matrixB;

        for (size_t i = 0; i < 5; ++i) {
            std::size_t row = rand() % 5;
            std::size_t col = rand() % 5;
            int valueA, valueB;
            generateRandomData(valueA);
            generateRandomData(valueB);
            matrixA.add(row, col, valueA);
            matrixB.add(row, col, valueB);
        }

        SparseMatrix<int> result = matrixA + matrixB;

        for (size_t i = 0; i < 5; ++i) {
            for (size_t j = 0; j < 5; ++j) {
                int expected = matrixA.at(i, j) + matrixB.at(i, j);
                if (expected != 0) { 
                    REQUIRE(result.at(i, j) == expected);
                }
            }
        }
    }
}
