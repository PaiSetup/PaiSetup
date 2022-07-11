#pragma once

#include "error.h"

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <sys/socket.h>

constexpr static inline int maxClientsCount = 10;
constexpr static inline int serverPort = 10000;
constexpr static inline int maxMessageSize = 256;

enum class RecvSizeResult {
    Success,
    Fail,
    ConnectionStopped,
};

RecvSizeResult recvSize(int fd, void *buf, size_t size) {
    size_t sizeLeft = size;
    while (sizeLeft > 0) {
        ssize_t messageSize = recv(fd, buf, sizeLeft, 0);

        if (messageSize < 0) {
            return RecvSizeResult::Fail;
        }
        if (messageSize == 0) {
            return RecvSizeResult::ConnectionStopped;
        }

        FATAL_ERROR_IF(messageSize > sizeLeft, "Too big message size");
        sizeLeft -= messageSize;
    }

    return RecvSizeResult::Success;
}

#pragma pack(push, 1)
enum class ClientCommandType : unsigned char {
    SetStatus,
    ReadWarnings
};

struct ClientCommandSetStatus {
    uint8_t type; // must be SetStatus
    uint16_t length;
    char data[maxMessageSize];

    constexpr inline static int headerSize = sizeof(type) + sizeof(length);
    int getLength() const {
        return headerSize + length;
    }
};

struct ServerResponseGetWarnings {
    uint8_t warningsCount;
    uint16_t length;
    char data[maxMessageSize];

    constexpr inline static int headerSize = sizeof(warningsCount) + sizeof(length);
    int getLength() const {
        return headerSize + length;
    }
};

#pragma pack(pop)