#ifndef SPARSELIST_H
#define SPARSELIST_H

#include <iostream>
#include <list>
#include <utility>
#include <stdexcept>
#include <vector>


template<typename T>
class SparseList {
private:
    std::list<std::pair<T, size_t>> listValueIndex; 
    size_t capacity; 
    T defaultValue; 

public:
    explicit SparseList(T defaultValue) : defaultValue(defaultValue), capacity(0) {}

    void add(T data, size_t index) {
        if (data == defaultValue) {
            throw std::invalid_argument("Error! Adding default value type to SparseList!");
        }
        for (const auto& pair : listValueIndex) {
            if (pair.second == index) {
                throw std::invalid_argument("Error! Element with this index already exists in listValueIndex!");
            }
        }
        listValueIndex.push_back(std::make_pair(data, index));
        if (index >= capacity) {
            capacity = index + 1; 
        }
    }

    T at(size_t index) const {
        if (index >= capacity) {
            throw std::out_of_range("Error! Index went out of bounds!");
        }
        for (const auto& pair : listValueIndex) {
            if (pair.second == index) {
                return pair.first;
            }
        }
        return defaultValue;
    }

    const std::pair<T, size_t>* find(const T& value) const {
        if (value == defaultValue) {
            throw std::invalid_argument("Error! Searching default value in SparseList.");
        }
        for (const auto& pair : listValueIndex) {
            if (pair.first == value) {
                return &pair;
            }
        }
        return nullptr;
    }

    template<typename Predicate>
    const std::pair<T, size_t>* find_if(Predicate predicate) const {
        for (const auto& pair : listValueIndex) {
            if (predicate(pair)) { 
                return &pair;
            }
        }
        return nullptr;
    }


    void print(std::ostream& out = std::cout) const {
        for (size_t i = 0; i < capacity; ++i) {
            bool found = false;
            for (const auto& pair : listValueIndex) {
                if (pair.second == i) {
                    out << "[" << "index: " << pair.second << " " << "data: " << pair.first << "]\n";
                    found = true;
                    break;
                }
            }
            if (!found) {
                out << "[" << "index: " << i << " " << ": " << defaultValue << "]\n";
            }
        }
    }
};

template<typename T>
std::ostream& operator<<(std::ostream& out, const SparseList<T>& sparseList) {
    sparseList.print(out);
    return out;
}

#endif // SPARSELIST_H
