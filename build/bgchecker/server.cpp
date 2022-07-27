#include "common.h"

#include <array>
#include <atomic>
#include <cstring>
#include <mutex>
#include <netinet/in.h>
#include <sys/socket.h>
#include <thread>
#include <unistd.h>
#include <unordered_map>
#include <vector>

struct Threads {
    struct ThreadSlot {
        std::unique_ptr<std::thread> thread{nullptr};
        std::atomic_bool completion{false};
    };

    bool hasFreeSlot() const {
        for (const ThreadSlot &slot : threads) {
            if (slot.thread == nullptr) {
                return true;
            }
        }
        return false;
    }

    template <typename... Args>
    void run(Args &&...args) {
        ThreadSlot &slot = getFreeSlot();
        slot.thread = std::make_unique<std::thread>(std::forward<Args>(args)..., &slot.completion);
    }

    void retire() {
        for (ThreadSlot &slot : threads) {
            if (slot.thread != nullptr && slot.completion) {
                slot.thread->join();
                slot.thread.reset();

                slot.completion = false;
            }
        }
    }

    ~Threads() {
        retire();
    }

private:
    ThreadSlot &getFreeSlot() {
        for (ThreadSlot &slot : threads) {
            if (slot.thread == nullptr) {
                return slot;
            }
        }
        FATAL_ERROR("No free thread slots");
    }

    std::array<ThreadSlot, maxClientsCount> threads;
};

struct Warnings {
    void clientWarning(const std::string &warning) {
        std::lock_guard lock{mutex};
        clientWarnings[std::this_thread::get_id()] = warning;
    }

    void serverWarning(const std::string &warning) {
        std::lock_guard lock{mutex};
        serverWarnings.push_back(std::string("BgCheckerServer: ") + warning);
    }

    void clearClient() {
        std::lock_guard lock{mutex};
        clientWarnings.erase(std::this_thread::get_id());
    }

    void getAllWarnings(char *outBuffer, size_t bufferSize, size_t &outSize, size_t &outWarningsCount) {
        std::lock_guard lock{mutex};
        std::ostringstream resultStream;
        outWarningsCount = 0;

        for (const auto &warning : clientWarnings) {
            if (!warning.second.empty()) {
                resultStream << warning.second << "\n";
                outWarningsCount++;
            }
        }
        for (const auto &warning : serverWarnings) {
            if (!warning.empty()) {
                resultStream << warning << "\n";
                outWarningsCount++;
            }
        }

        std::string result = resultStream.str();
        outSize = std::min(result.size(), bufferSize - 1);
        std::memcpy(outBuffer, result.c_str(), outSize);
        outBuffer[outSize] = '\0';
    }

private:
    std::unordered_map<std::thread::id, std::string> clientWarnings;
    std::vector<std::string> serverWarnings;
    std::mutex mutex;
} warnings;

bool serverRecvSize(int fd, void *buf, size_t size) {
    auto result = recvSize(fd, buf, size);
    if (result == RecvSizeResult::Success) {
        return false;
    }

    if (result == RecvSizeResult::Fail) {
        PERROR("recv() failed");
        warnings.serverWarning("recv() failed");
    }

    return true;
}

void clientThread(int clientSocket, std::atomic_bool *completion) {
    union {
        ClientCommandType type;
        ClientCommandSetStatus setStatus;
        ServerResponseGetWarnings response;
        char raw[maxMessageSize];
    } buffer;

    while (1) {
        // Get message type
        if (serverRecvSize(clientSocket, buffer.raw, 1)) {
            break;
        }

        switch (buffer.type) {
        case ClientCommandType::ReadWarnings: {
            size_t size{};
            size_t warningsCount{};
            warnings.getAllWarnings(buffer.response.data, maxMessageSize, size, warningsCount);
            buffer.response.length = size;
            buffer.response.warningsCount = warningsCount;
            INFO("ReadWarnings (count=", warningsCount, ")");
            send(clientSocket, buffer.raw, buffer.response.getLength(), 0);
            break;
        }
        case ClientCommandType::SetStatus:
            serverRecvSize(clientSocket, buffer.raw + 1, 2);
            serverRecvSize(clientSocket, buffer.raw + 3, buffer.setStatus.length);
            warnings.clientWarning(buffer.setStatus.data);
            INFO("SetStatus ", buffer.setStatus.data);
            break;
        default:
            warnings.serverWarning("Unknown command type");
        }
    }

    warnings.clearClient();
    close(clientSocket);
    *completion = true;
}

int main(int argc, char const *argv[]) {
    // Create socket
    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    FATAL_ERROR_IF(serverSocket == 0, "Could not create server socket");

    // Set options
    int opt = 1;
    FATAL_ERROR_IF(setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0, "Could not setsockopt for server socket");

    // Bind to address
    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(serverPort);
    FATAL_ERROR_IF(bind(serverSocket, (sockaddr *)&address, sizeof(address)) < 0, "Could not bind server socket");

    // Make it a server socket
    FATAL_ERROR_IF(listen(serverSocket, maxClientsCount) < 0, "listen() failed");

    // Main connection loop
    INFO("Server running");
    Threads threads = {};
    while (true) {
        // Get next connection
        sockaddr_in clientAddress;
        socklen_t clientAddressLen;
        int clientSocket = accept(serverSocket, (sockaddr *)&clientAddress, &clientAddressLen);

        // Handle connection failure
        if (clientSocket < 0) {
            PERROR("accept() failed");
            warnings.serverWarning("accept() failed");
            sleep(1);
            continue;
        }

        // If there are too many connections, drop this one
        threads.retire();
        if (!threads.hasFreeSlot()) {
            WARNING("Too many connections, ignoring a client");
            close(clientSocket);
            continue;
        }

        // Process out client
        threads.run(clientThread, clientSocket);
    }

    // Cleanup server socket
    shutdown(serverSocket, SHUT_RDWR);
}
