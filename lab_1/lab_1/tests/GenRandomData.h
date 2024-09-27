#include <algorithm>
#include <concepts>
#include <iostream>
#include <random>
#include <ranges>
#include <string>
#include <vector>

template<typename T>
void generateRandomData(T &data);

namespace randomGen {
    template<std::integral T>
    T gen_random(T &&t) {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<T> distrib(std::numeric_limits<T>::min(), std::numeric_limits<T>::max());
        t = distrib(gen);
        return std::forward<T>(t);
    }

    template<std::floating_point F>
    F gen_random(F &&f) {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> distrib(std::numeric_limits<F>::min(), std::numeric_limits<F>::max());
        f = distrib(gen);
        return std::forward<F>(f);
    }

    template<std::ranges::range R>
    R gen_random(R &&r) {
        std::ranges::generate(r, []() {
            using rvt = std::ranges::range_value_t<R>;
            rvt value{};
            return gen_random<rvt>(std::forward<rvt>(value));
        });
        return std::forward<R>(r);
    }
}

template<typename T>
void generateRandomData(T &data) {
    data = randomGen::gen_random(std::decay_t<T>(data));
}