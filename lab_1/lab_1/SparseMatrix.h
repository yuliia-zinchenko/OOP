#ifndef SPARSEMATRIX_H
#define SPARSEMATRIX_H


#include <iostream>
#include <vector>
#include <tuple>
#include <stdexcept>
#include <string>
#include <algorithm>

template <typename A>
class SparseMatrix {
private:
    std::vector<std::tuple<std::size_t, std::size_t, A>> vectorIndexValue;
    std::size_t rows, cols;
    A defaultValue;

public:
    SparseMatrix(std::size_t r, std::size_t c, A defaultVal = A()) : rows(r), cols(c), defaultValue(defaultVal) {}

    explicit SparseMatrix(std::vector<std::tuple<std::size_t, std::size_t, A>> input) : defaultValue(A()) {
        std::size_t rowTempQuantity = 0, colTempQuantity = 0;
        for (auto& iter : input) {
            std::size_t i = std::get<0>(iter);
            std::size_t j = std::get<1>(iter);
            if (rowTempQuantity < i) rowTempQuantity = i;
            if (colTempQuantity < j) colTempQuantity = j;

            if (std::get<2>(iter) != defaultValue) {
                vectorIndexValue.push_back(iter);
            }
            else {
                throw std::logic_error("Error! DefaultValue cannot be indexed!");
            }
        }
        rows = rowTempQuantity + 1;
        cols = colTempQuantity + 1;
        std::sort(vectorIndexValue.begin(), vectorIndexValue.end());
    }

    A& at(std::size_t row, std::size_t column) {
        if (row >= rows || column >= cols) {
            throw std::out_of_range("Error! Index went out of bounds!");
        }
        for (auto& iter : vectorIndexValue) {
            if (std::get<0>(iter) == row && std::get<1>(iter) == column) {
                return std::get<2>(iter);
            }
        }
        throw std::out_of_range("Error! No value found at this index!");
    }

    const A& at(std::size_t row, std::size_t column) const {
        if (row >= rows || column >= cols) {
            throw std::out_of_range("Error! Index went out of bounds!");
        }
        for (const auto& iter : vectorIndexValue) {
            if (std::get<0>(iter) == row && std::get<1>(iter) == column) {
                return std::get<2>(iter);
            }
        }
        return defaultValue; // Якщо значення немає, повертаємо значення за замовчуванням
    }

    void set(std::size_t row, std::size_t column, const A& value) {
        if (row >= rows || column >= cols) {
            throw std::out_of_range("Error! Index went out of bounds!");
        }
        if (value == defaultValue) {
            // Дозволяємо скидання значення до значення за замовчуванням
            for (auto it = vectorIndexValue.begin(); it != vectorIndexValue.end(); ) {
                if (std::get<0>(*it) == row && std::get<1>(*it) == column) {
                    it = vectorIndexValue.erase(it);
                }
                else {
                    ++it;
                }
            }
            return;
        }

        for (auto& iter : vectorIndexValue) {
            if (std::get<0>(iter) == row && std::get<1>(iter) == column) {
                std::get<2>(iter) = value;
                return;
            }
        }

        vectorIndexValue.push_back(std::make_tuple(row, column, value));
        std::sort(vectorIndexValue.begin(), vectorIndexValue.end());
    }

    SparseMatrix<A> operator+(const SparseMatrix<A>& rhs) const {
        if (this->cols != rhs.cols || this->rows != rhs.rows) {
            throw std::invalid_argument("Error! Can't sum matrices of different size!");
        }

        SparseMatrix<A> result(this->rows, this->cols, defaultValue);

        // Додаємо ненульові елементи з лівої матриці
        for (const auto& i : this->vectorIndexValue) {
            size_t row = std::get<0>(i);
            size_t column = std::get<1>(i);
            A data = std::get<2>(i);
            try {
                data += rhs.at(row, column); // Додаємо значення з правої матриці
            }
            catch (const std::out_of_range&) {
                // Якщо елемента немає у правій матриці, просто беремо значення з лівої
            }
            if (data != defaultValue) {
                result.set(row, column, data);
            }
        }

        // Додаємо ненульові елементи з правої матриці, які не були включені
        for (const auto& i : rhs.vectorIndexValue) {
            size_t row = std::get<0>(i);
            size_t column = std::get<1>(i);
            try {
                this->at(row, column); // Перевіряємо, чи елемент з лівої матриці існує
            }
            catch (const std::out_of_range&) {
                result.set(row, column, std::get<2>(i)); // Додаємо значення з правої матриці
            }
        }

        return result;
    }

    SparseMatrix<A> operator*(const SparseMatrix<A>& rhs) const {
        if (this->cols != rhs.rows) {
            throw std::invalid_argument("Error! Matrix1 column quantity != Matrix2 row quantity.");
        }

        SparseMatrix<A> result(this->rows, rhs.cols, defaultValue);

        // Перебираємо ненульові елементи лівої матриці
        for (const auto& i : this->vectorIndexValue) {
            size_t row = std::get<0>(i);
            size_t col = std::get<1>(i);
            A leftValue = std::get<2>(i);

            // Перебираємо ненульові елементи правої матриці
            for (const auto& j : rhs.vectorIndexValue) {
                size_t rhsRow = std::get<0>(j);
                size_t rhsCol = std::get<1>(j);
                A rightValue = std::get<2>(j);

                // Перевіряємо, чи колонки лівої матриці збігаються з рядками правої матриці
                if (col == rhsRow) {
                    A product = leftValue * rightValue;
                    if (product != defaultValue) {
                        // Додаємо до результуючої матриці
                        try {
                            result.set(row, rhsCol, result.at(row, rhsCol) + product);
                        }
                        catch (const std::out_of_range&) {
                            result.set(row, rhsCol, product); // Додаємо, якщо немає значення
                        }
                    }
                }
            }
        }

        return result;
    }

    //Пошук за значенням
    template<typename Comparator>
    const std::tuple<std::size_t, std::size_t, A>& find_if(const A& value, const Comparator& comparator) {
        if (value == defaultValue) {
            throw std::logic_error("Error! Unable to find default value!");
        }
        for (const auto& iter : vectorIndexValue) {
            if (comparator(std::get<2>(iter), value)) {
                return iter; // Повертаємо знайдений елемент
            }
        }
        throw std::runtime_error("Element not found!"); // Кидаємо виняток, якщо не знайдено
    }



    // Пошук першого елемента за заданою умовою (lambda-функція)
    std::tuple<std::size_t, std::size_t, A> find(const A& value) const {
        for (const auto& iter : vectorIndexValue) {
            if (std::get<2>(iter) == value) {
                return iter; // Повертаємо знайдений елемент
            }
        }
        throw std::runtime_error("Element not found!"); // Кидаємо виняток, якщо не знайдено
    }

    std::vector<A> multiplyVector(const std::vector<A>& vec) const {
        if (cols != vec.size()) {
            throw std::invalid_argument("Error! Matrix column count does not match vector size.");
        }

        std::vector<A> result(rows, defaultValue); // Результуючий вектор

        for (const auto& iter : vectorIndexValue) {
            std::size_t row = std::get<0>(iter);
            std::size_t col = std::get<1>(iter);
            A value = std::get<2>(iter);
            result[row] += value * vec[col];
        }

        return result;
    }

    SparseMatrix<A> transpose() const {
        SparseMatrix<A> transposed(cols, rows, defaultValue); // Створюємо транспоновану матрицю

        // Перебираємо ненульові елементи поточної матриці
        for (const auto& iter : vectorIndexValue) {
            std::size_t row = std::get<0>(iter);
            std::size_t col = std::get<1>(iter);
            A value = std::get<2>(iter);

            // Додаємо значення у транспоновану матрицю
            transposed.set(col, row, value);
        }

        return transposed; // Повертаємо транспоновану матрицю
    }


    void print(std::ostream& out = std::cout) const {
        for (std::size_t i = 0; i < rows; ++i) {
            for (std::size_t j = 0; j < cols; ++j) {
                try {
                    out << at(i, j) << " ";
                }
                catch (const std::out_of_range&) {
                    out << defaultValue << " ";
                }
            }
            out << '\n'; // Використовуємо '\n' для пришвидшення виводу
        }
    }
};

#endif // SPARSEMATRIX_H
