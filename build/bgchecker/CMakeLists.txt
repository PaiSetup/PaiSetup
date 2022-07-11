cmake_minimum_required(VERSION 3.20.0)
project(BgChecker)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

add_executable(BgCheckerServer server.cpp)
set_property(TARGET BgCheckerServer PROPERTY CXX_STANDARD 17)
target_link_libraries(BgCheckerServer PRIVATE Threads::Threads)
install(TARGETS BgCheckerServer)

add_executable(BgCheckerClient client.cpp)
set_property(TARGET BgCheckerClient PROPERTY CXX_STANDARD 17)
target_link_libraries(BgCheckerClient PRIVATE Threads::Threads)
install(TARGETS BgCheckerClient)
