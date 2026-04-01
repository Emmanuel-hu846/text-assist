cmake_minimum_required(VERSION 3.10)
project(MessageAutoReply)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(message_engine message_engine.cpp)

target_include_directories(message_engine PRIVATE /usr/include)
