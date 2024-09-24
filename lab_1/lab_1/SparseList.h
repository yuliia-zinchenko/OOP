#ifndef SPARSELIST_H
#define SPARSELIST_H

#include <iostream>
#include <list>
#include <utility>
#include <stdexcept>

template<typename T>
class SparseList {
private:
    std::list<std::pair<T, size_t>> listValueIndex; // Список значень і їх індексів
    size_t capacity; // Максимальний розмір списку
    T defaultValue; // Значення за замовчуванням

public:
    // Конструктор з значенням за замовчуванням
    explicit SparseList(T defaultValue) : defaultValue(defaultValue), capacity(0) {}

    // Метод для додавання значення за індексом
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
            capacity = index + 1; // Оновлюємо ємність, якщо індекс перевищує поточний
        }
    }

    // Метод для отримання значення за індексом
    T at(size_t index) const {
        if (index >= capacity) {
            throw std::out_of_range("Error! Index went out of bounds!");
        }
        for (const auto& pair : listValueIndex) {
            if (pair.second == index) {
                return pair.first;
            }
        }
        return defaultValue; // Якщо значення немає, повертаємо значення за замовчуванням
    }

    // Метод для пошуку значення
    const std::pair<T, size_t>* find(const T& value) const {
        if (value == defaultValue) {
            throw std::invalid_argument("Error! Searching default value in SparseList.");
        }
        for (const auto& pair : listValueIndex) {
            if (pair.first == value) {
                return &pair; // Повертаємо адресу знайденого елемента
            }
        }
        return nullptr; // Якщо не знайдено, повертаємо nullptr
    }

    // Метод для пошуку першого елемента за умовою
    template<typename Predicate>
    const std::pair<T, size_t>* find_if(Predicate predicate) const {
        for (const auto& pair : listValueIndex) {
            if (predicate(pair)) {
                return &pair; // Повертаємо адресу знайденого елемента
            }
        }
        return nullptr; // Якщо не знайдено, повертаємо nullptr
    }

    // Метод для виводу списку
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
                out << "[" << "index: " << i << " " << "data: " << defaultValue << "]\n";
            }
        }
    }
};

// Перевантаження оператора виводу для зручності
template<typename T>
std::ostream& operator<<(std::ostream& out, const SparseList<T>& sparseList) {
    sparseList.print(out);
    return out;
}

#endif // SPARSELIST_H
