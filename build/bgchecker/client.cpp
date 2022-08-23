#include "common.h"

#include <arpa/inet.h>
#include <cstring>
#include <signal.h>

bool setStatus(int clientSocket, const std::string &status) {
    ClientCommandSetStatus command;
    command.type = static_cast<uint8_t>(ClientCommandType::SetStatus);
    strcpy(command.data, status.c_str());
    command.length = strlen(command.data) + 1;

    if (send(clientSocket, &command, command.getLength(), 0) < 0) {
        PERROR("Failed to send SetStatus request");
        return false;
    }

    INFO("Setting status \"", status, "\"");
    return true;
}

bool readWarnings(int clientSocket) {
    ClientCommandType readWarningsCommand = ClientCommandType::ReadWarnings;
    if (send(clientSocket, &readWarningsCommand, sizeof(readWarningsCommand), 0) < 0) {
        PERROR("Failed to send ReadWarnings request");
        return false;
    }

    union {
        ServerResponseGetWarnings response;
        char raw[maxMessageSize];
    } buffer;

    switch (recvSize(clientSocket, buffer.raw, ServerResponseGetWarnings::headerSize)) {
    case RecvSizeResult::Fail:
        PERROR("Failed to receive header from ReadWarning response");
        return false;
    case RecvSizeResult::ConnectionStopped:
        PERROR("Failed to receive header from ReadWarning response (connection stopped)");
        return false;
    }

    if (recvSize(clientSocket, buffer.raw + ServerResponseGetWarnings::headerSize, buffer.response.length) != RecvSizeResult::Success) {
        PERROR("Failed to receive data from ReadWarning response");
        return false;
    }

    if (buffer.response.length != 0) {
        buffer.response.data[buffer.response.length] = '\0';
        printf(buffer.response.data);
    }
    return true;
}

void connectToServer(int &clientSocket, bool &connected, sockaddr_in serverAddress) {
    if (clientSocket == 0) {
        FATAL_ERROR_IF(connected, "It is impossible to be connected through an invalid socket");
        clientSocket = socket(AF_INET, SOCK_STREAM, 0);
        FATAL_ERROR_IF(clientSocket == 0, "Could not create a socket");
    }

    if (!connected) {
        if (connect(clientSocket, reinterpret_cast<sockaddr *>(&serverAddress), sizeof(serverAddress)) < 0) {
            INFO("Waiting for server...");
        } else {
            INFO("Connected to server");
            connected = true;
        }
    }
}

void disconnectFromServer(int &clientSocket, bool &connected) {
    if (connected) {
        close(clientSocket);
        clientSocket = 0;
        connected = false;
        INFO("Disconnected from server");
    }
}

bool executeStatusCommand(const char *command, std::string &outOutput) {
    FILE *outStream = popen(command, "r");
    if (outStream == nullptr) {
        NON_FATAL_ERROR("Could not execute command \"", command, "\"");
        return false;
    }

    constexpr static size_t commandOutputBufferSize = 1024;
    static char commandOutputBuffer[commandOutputBufferSize];

    size_t usedBufferSize = 0;
    while (true) {
        const size_t bytesRead = fread(commandOutputBuffer + usedBufferSize, sizeof(char), commandOutputBufferSize - usedBufferSize, outStream);
        if (bytesRead != 0) {
            usedBufferSize += bytesRead;
        } else {
            WARNING_IF(ferror(outStream), "Reading the subprocess's stdout failed")
            break;
        }
    }
    if (usedBufferSize == 0) {
        INFO("Empty output");
    }
    commandOutputBuffer[usedBufferSize++] = '\0';

    const int exitCode = WEXITSTATUS(pclose(outStream));
    if (exitCode != 0) {
        NON_FATAL_ERROR("Command failed");
        return false;
    }

    outOutput = commandOutputBuffer;

    if (outOutput.back() == ' ') {
        outOutput.pop_back();
    }

    return true;
}

int main(int argc, char const *argv[]) {
    // Parse cmdline
    enum class Operation {
        ReadWarnings,
        SetStatus,
    } operation{};
    std::string scriptPath{};
    int interval{};
    if (argc < 2) {
        NON_FATAL_ERROR("Specify operation to perform");
        return 1;
    }
    if (strcmp(argv[1], "ReadWarnings") == 0) {
        operation = Operation::ReadWarnings;
    } else if (strcmp(argv[1], "SetStatus") == 0) {
        if (argc < 4) {
            NON_FATAL_ERROR("Specify time interval and a command to run");
            return 1;
        }
        operation = Operation::SetStatus;
        interval = std::atoi(argv[2]);
        scriptPath = argv[3];
        if (interval < 0) {
            NON_FATAL_ERROR("Interval should be a positive number");
            return 1;
        }
    } else {
        NON_FATAL_ERROR("Unknown operation specified: \"", argv[1], "\"");
        return 1;
    }

    // If server terminates, SIGPIPE will be sent, which by default terminates our client.
    // We want to handle it and keep the process running, so we ignore SIGPIPE.
    struct sigaction ignoreSigAction {
        SIG_IGN
    };
    sigaction(SIGPIPE, &ignoreSigAction, NULL);

    // Prepare status variables
    std::string status = "";
    const std::string faulyClientStatus = std::string("Faulty client at pid=") + std::to_string(getpid());

    // Prepare connection variables
    int clientSocket = 0;
    bool connected = false;
    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(serverPort);
    FATAL_ERROR_IF(inet_pton(AF_INET, "127.0.0.1", &serverAddress.sin_addr) != 1, "Converting address failed");

    // Main loop
    bool keepRunning = true;
    int retVal = 0;
    while (keepRunning) {
        // Try to connect or do nothing if we're already connected
        connectToServer(clientSocket, connected, serverAddress);

        switch (operation) {
        case Operation::SetStatus:
            if (!connected) {
                sleep(1);
                break;
            }
            if (!executeStatusCommand(scriptPath.c_str(), status)) {
                status = faulyClientStatus;
            }
            if (!setStatus(clientSocket, status)) {
                disconnectFromServer(clientSocket, connected);
            }
            sleep(interval);
            break;
        case Operation::ReadWarnings:
            if (!connected) {
                NON_FATAL_ERROR("Could not connect to server");
                retVal = 1;
            } else if (!readWarnings(clientSocket)) {
                disconnectFromServer(clientSocket, connected);
                retVal = 1;
            }
            keepRunning = false;
            break;
        default:
            FATAL_ERROR("Invalid operation");
            break;
        }
    }

    disconnectFromServer(clientSocket, connected);

    return retVal;
}