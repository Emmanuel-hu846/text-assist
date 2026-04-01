cmake_minimum_required(VERSION 3.10)
project(MessageAutoReply)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Fetch nlohmann/json library
include(FetchContent)
FetchContent_Declare(json
  URL https://github.com/nlohmann/json/releases/download/v3.11.2/include.zip
)
FetchContent_MakeAvailable(json)

add_executable(message_engine message_engine.cpp)

# Link the nlohmann/json library
target_include_directories(message_engine PRIVATE ${json_SOURCE_DIR})
