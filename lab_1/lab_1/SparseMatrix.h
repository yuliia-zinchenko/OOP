#ifndef SPARSEMATRIX_H
#define SPARSEMATRIX_H

#include <tuple>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <string>
#include <iostream>
#include <sstream>
#include <map> 
#include <functional>

template<typename, typename = void>
struct is_output_streamable : std::false_type {};

template<typename T>
struct is_output_streamable<T, std::void_t<decltype(std::declval<std::ostream&>() << std::declval<T>())>> : std::true_type {};

class MyType {
public:
    int value;
    MyType() : value(0) {}
    MyType(int v) : value(v) {}
    bool operator==(const MyType& other) const {
        return value == other.value;
    }
    bool operator!=(const MyType& other) const {
        return value != other.value;
    }
    friend std::ostream& operator<<(std::ostream& out, const MyType& obj) {
        out << obj.value;
        return out;
    }
};

std::ostream& operator<<(std::ostream& out, const std::vector<int>& vec) {
    out << "{ ";
    for (const auto& elem : vec) {
        out << elem << " ";
    }
    out << "}";
    return out;
}

template<typename A>
class SparseMatrix {
private:
    std::vector<std::tuple<std::size_t, std::size_t, A>> vectorIndexValue;
    std::vector<A> values;        
    std::vector<std::size_t> rowPtr; 
    std::vector<std::size_t> colInd;

    A defaultValue{};
    std::size_t rowQuantity{};
    std::size_t columnQuantity{};

    static bool indexSortComparator(const std::tuple<std::size_t, std::size_t, A>& a,
        const std::tuple<std::size_t, std::size_t, A>& b) {
        return std::tie(std::get<0>(a), std::get<1>(a)) < std::tie(std::get<0>(b), std::get<1>(b));
    }

public:
    SparseMatrix() : defaultValue{}, rowQuantity(0), columnQuantity(0) {}
    SparseMatrix(const std::vector<std::pair<std::pair<std::size_t, std::size_t>, A>>& input) {
        for (const auto& iter : input) {
            if (iter.second != defaultValue) {
                vectorIndexValue.push_back(std::make_tuple(std::get<0>(iter.first), std::get<1>(iter.first), iter.second));
                rowQuantity = std::max(rowQuantity, std::get<0>(iter.first) + 1);
                columnQuantity = std::max(columnQuantity, std::get<1>(iter.first) + 1);
            }
        }
        std::sort(vectorIndexValue.begin(), vectorIndexValue.end(), indexSortComparator);
        constructCSR(); 
    }

    void constructCSR() {
        values.clear();
        colInd.clear();
        rowPtr.resize(rowQuantity + 1, 0);

        for (const auto& elem : vectorIndexValue) {
            std::size_t row = std::get<0>(elem);
            std::size_t col = std::get<1>(elem);
            A value = std::get<2>(elem);

            values.push_back(value);
            colInd.push_back(col);
            rowPtr[row + 1]++;
        }

        // Cumulative sum for row pointers
        for (std::size_t i = 0; i < rowPtr.size() - 1; i++) {
            rowPtr[i + 1] += rowPtr[i];
        }
    }

    void add(std::size_t row, std::size_t column, A data) {
        if (data == defaultValue) {
            throw std::logic_error("Error! Cannot add default value to sparse matrix!");
        }
        if (isAlreadyIndexed(row, column)) {
            throw std::invalid_argument("Error! Element with this index already exists!");
        }
        vectorIndexValue.push_back(std::make_tuple(row, column, data));
        rowQuantity = std::max(rowQuantity, row + 1);
        columnQuantity = std::max(columnQuantity, column + 1);
        std::sort(vectorIndexValue.begin(), vectorIndexValue.end(), indexSortComparator);

        constructCSR();
    }

    const A& at(std::size_t row, std::size_t column) const {
        if (row >= rowQuantity || column >= columnQuantity) {
            throw std::out_of_range("Error! Index out of bounds!");
        }
        for (const auto& iter : vectorIndexValue) {
            if (std::get<0>(iter) == row && std::get<1>(iter) == column) {
                return std::get<2>(iter);
            }
        }
        return defaultValue;
    }

    std::pair<std::size_t, std::size_t> find_if(const std::function<bool(const A&)>& condition) const {
        for (const auto& iter : vectorIndexValue) {
            if (condition(std::get<2>(iter))) {
                return { std::get<0>(iter), std::get<1>(iter) };
            }
        }
        throw std::runtime_error("No element satisfying the condition found in the matrix.");
    }

    std::pair<std::size_t, std::size_t> find(const A& value) const {
        for (const auto& iter : vectorIndexValue) {
            if (std::get<2>(iter) == value) {
                return { std::get<0>(iter), std::get<1>(iter) };
            }
        }
        std::ostringstream oss;
        oss << value; 
        throw std::runtime_error("Value " + oss.str() + " not found in the matrix.");
    }

    template<typename T>
    void printValue(std::ostream& out, const T& value) const {
        if constexpr (std::is_same<T, std::vector<int>>::value) { 
            if (value.empty()) {
                out << "{0} ";
            }
            else {
                out << "{ ";
                for (const auto& elem : value) {
                    out << elem << " ";
                }
                out << "} ";
            }
        }
        else if constexpr (std::is_same<T, MyType>::value) { 
            out << value << " ";
        }
        else if constexpr (is_output_streamable<T>::value) { 
            out << value << " ";
        }
        else {
            throw std::logic_error("Unsupported type for output!");
        }
    }

    void print(std::ostream& out = std::cout) {
        for (std::size_t i = 0; i < rowQuantity; i++) {
            for (std::size_t j = 0; j < columnQuantity; j++) {
                const auto& value = at(i, j);
                if (value == defaultValue) {
                    out << "0 "; 
                }
                else {
                    printValue(out, value); 
                }
            }
            out << "\n"; 
        }
    }

    void transpose() {
        std::vector<std::tuple<std::size_t, std::size_t, A>> transposed;
        for (const auto& iter : vectorIndexValue) {
            std::size_t row = std::get<0>(iter);
            std::size_t column = std::get<1>(iter);
            transposed.emplace_back(column, row, std::get<2>(iter));
        }
        vectorIndexValue = std::move(transposed);
        std::swap(rowQuantity, columnQuantity);
        std::sort(vectorIndexValue.begin(), vectorIndexValue.end(), indexSortComparator);
    }

    static std::vector<int> addVectors(const std::vector<int>& lhs, const std::vector<int>& rhs) {
        if (lhs.size() != rhs.size()) {
            throw std::invalid_argument("Vectors must be of the same length for addition!");
        }
        std::vector<int> result(lhs.size());
        for (std::size_t i = 0; i < lhs.size(); ++i) {
            result[i] = lhs[i] + rhs[i];
        }
        return result;
    }

    SparseMatrix<A> operator+(const SparseMatrix<A>& rhs) const {
        if (this->rowQuantity != rhs.rowQuantity || this->columnQuantity != rhs.columnQuantity) {
            throw std::invalid_argument("Error! Matrices must have the same dimensions for addition!");
        }

        SparseMatrix<A> result;
        result.rowQuantity = this->rowQuantity;
        result.columnQuantity = this->columnQuantity;

        for (const auto& elem : this->vectorIndexValue) {
            std::size_t row = std::get<0>(elem);
            std::size_t column = std::get<1>(elem);
            A sumValue = std::get<2>(elem) + rhs.at(row, column);
            if (sumValue != result.defaultValue) {
                result.add(row, column, sumValue);
            }
        }
        return result;
    }

    void printCOO(std::ostream& out = std::cout) {
        out << "COO Representation:\n";
        for (const auto& elem : vectorIndexValue) {
            out << "(" << std::get<0>(elem) << ", " << std::get<1>(elem) << ") -> " << std::get<2>(elem) << "\n";
        }
    }

    void printCSR(std::ostream& out = std::cout) {
        out << "CSR Representation:\n";
        out << "Values: ";
        for (const auto& val : values) {
            out << val << " ";
        }
        out << "\nColumn Indices: ";
        for (const auto& col : colInd) {
            out << col << " ";
        }
        out << "\nRow Pointers: ";
        for (const auto& ptr : rowPtr) {
            out << ptr << " ";
        }
        out << "\n";
    }

    SparseMatrix<A> operator*(const SparseMatrix<A>& rhs) const {
        if (this->columnQuantity != rhs.rowQuantity) {
            throw std::invalid_argument("Error! The number of columns in the first matrix must equal the number of rows in the second matrix for multiplication!");
        }

        SparseMatrix<A> result;
        result.rowQuantity = this->rowQuantity;
        result.columnQuantity = rhs.columnQuantity;

        std::map<std::pair<std::size_t, std::size_t>, A> tempResult;

        for (const auto& elemA : this->vectorIndexValue) {
            std::size_t rowA = std::get<0>(elemA);
            std::size_t columnA = std::get<1>(elemA);
            A valueA = std::get<2>(elemA);
            for (const auto& elemB : rhs.vectorIndexValue) {
                std::size_t rowB = std::get<0>(elemB);
                std::size_t columnB = std::get<1>(elemB);
                A valueB = std::get<2>(elemB);
                if (columnA == rowB) {
                    A product = valueA * valueB;
                    if (product != result.defaultValue) {
                        tempResult[{rowA, columnB}] += product;  
                    }
                }
            }
        }

        for (const auto& entry : tempResult) {
            const auto& key = entry.first;
            const auto& value = entry.second;
            result.add(key.first, key.second, value);
        }

        return result;
    }

    bool isAlreadyIndexed(std::size_t row, std::size_t column) const {
        for (const auto& iter : vectorIndexValue) {
            if (std::get<0>(iter) == row && std::get<1>(iter) == column) {
                return true;
            }
        }
        return false;
    }
};

#endif // SPARSEMATRIX_H
