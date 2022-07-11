#pragma once

#include <iostream>
#include <sstream>

[[noreturn]] inline void performAbort() {
    throw std::exception{};
}

inline void dumpLog(std::ostream &out) {
}

template <typename Arg, typename... Args>
inline void dumpLog(std::ostream &out, Arg &&arg, Args &&...args) {
    out << arg;
    dumpLog(out, std::forward<Args>(args)...);
}

template <typename... Args>
inline void dumpLogLine(std::ostream &out, Args &&...args) {
    dumpLog(out, std::forward<Args>(args)...);
    out << std::endl;
}

#define NON_FATAL_ERROR(...) \
    dumpLogLine(std::cerr, "ERROR: ", __VA_ARGS__);

#define FATAL_ERROR(...)                                  \
    dumpLogLine(std::cerr, "FATAL ERROR: ", __VA_ARGS__); \
    performAbort();

#define FATAL_ERROR_IF(condition, ...) \
    if (condition) {                   \
        FATAL_ERROR(__VA_ARGS__);      \
    }

#define INFO(...) \
    dumpLogLine(std::cerr, "INFO: ", __VA_ARGS__);

#define WARNING(...) \
    dumpLogLine(std::cerr, "WARNING: ", __VA_ARGS__);

#define WARNING_IF(condition, ...) \
    if (condition) {               \
        WARNING(__VA_ARGS__);      \
    }

#define PERROR(...)                               \
    {                                             \
        std::ostringstream message;               \
        dumpLog(message, "ERROR: ", __VA_ARGS__); \
        perror(message.str().c_str());            \
    }
