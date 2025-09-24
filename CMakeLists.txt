cmake_minimum_required(VERSION 3.0.2)
project(rosneuro_tutorials)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  pluginlib
  rosneuro_filters
  rosneuro_filters_butterworth
  rosneuro_msgs
)

find_package(Eigen3 REQUIRED)

find_package(PkgConfig)


catkin_package(
  INCLUDE_DIRS 
  	include
  LIBRARIES
  CATKIN_DEPENDS 
  	roscpp std_msgs
  DEPENDS
)

###########
## Build ##
###########

include_directories(
# include
  ${catkin_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIRS}
  include
)
add_definitions(${EIGEN3_DEFINITIONS})

## Declare a python executable
catkin_install_python(PROGRAMS scripts/blink_detector.py scripts/bandpower.py scripts/bar_plot.py scripts/talker.py scripts/listener.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## Declare a C++ executable

add_executable(blink_detector src/blink_detector.cpp)
target_link_libraries(blink_detector ${catkin_LIBRARIES})
add_dependencies(blink_detector ${catkin_EXPORTED_TARGETS})
