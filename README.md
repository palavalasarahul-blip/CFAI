# CFAI
# Autonomous Cleaning Strategy Planner

## Project Overview

The Autonomous Cleaning Strategy Planner is an AI-based cleaning robot simulation developed in Python. The robot operates in a grid-based environment containing dirt and obstacles. Using the Breadth-First Search (BFS) algorithm, the robot intelligently finds the shortest path to the nearest dirty cell, navigates around obstacles, and cleans the environment efficiently.

This project demonstrates fundamental Artificial Intelligence concepts such as intelligent agents, path planning, search algorithms, environment perception, and autonomous decision-making.

---

## Features

* Grid-based room simulation
* Random generation of dirt and obstacles
* Intelligent cleaning agent
* Shortest-path navigation using BFS
* Automatic obstacle avoidance
* Real-time room visualization
* Performance tracking

  * Total cleaned cells
  * Total movement steps
* Detection of unreachable dirty cells

---

## Technologies Used

* Python 3.x
* Collections Module (Deque)
* Random Module
* Breadth-First Search (BFS)

---

## Project Structure

```
Autonomous-Cleaning-Strategy-Planner/
│
├── cleaning_robot.py
├── README.md
└── requirements.txt
```

---

## Working Principle

### Environment Setup

The room is represented as a 2D grid where:

| Symbol | Meaning        |
| ------ | -------------- |
| R      | Robot Position |
| D      | Dirty Cell     |
| X      | Obstacle       |
| .      | Clean Cell     |

Example:

```
R . D . .
. X . D .
. . X . .
D . . X .
. D . . D
```

---

### Cleaning Strategy

1. Scan the room for dirty cells.
2. Find the nearest dirty cell.
3. Use BFS to determine the shortest path.
4. Move step-by-step toward the target.
5. Clean the dirty cell.
6. Repeat until all reachable dirty cells are cleaned.

---

## Algorithm Used

### Breadth-First Search (BFS)

BFS is used to:

* Explore neighboring cells level by level.
* Find the shortest path in an unweighted grid.
* Avoid obstacles.
* Reach dirty cells efficiently.

### BFS Steps

1. Start from the robot's current position.
2. Add the position to a queue.
3. Visit neighboring cells.
4. Mark visited cells.
5. Continue until the target dirty cell is found.
6. Return the shortest path.

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/autonomous-cleaning-strategy-planner.git
```

### Navigate to Project Folder

```bash
cd autonomous-cleaning-strategy-planner
```

### Run the Program

```bash
python cleaning_robot.py
```

---

## Input Parameters

```python
rows = 5
cols = 5
dirt_count = 6
obstacle_count = 5
```

### Description

* rows → Number of grid rows
* cols → Number of grid columns
* dirt_count → Number of dirty cells
* obstacle_count → Number of obstacles

---

## Sample Output

```
Initial Room Layout

R . D . .
. X . D .
. . X . .
D . . X .
. D . . D

Moving to dirty cell: (0,2)

Cleaned dirt at: (0,2)

Cleaning Completed

Total cleaned cells: 6
Total steps taken: 14
```

---

## AI Concepts Used

### Intelligent Agent

The cleaning robot acts as an intelligent agent that perceives the environment and takes actions to achieve the goal of cleaning all dirt.

### Search-Based Problem Solving

The robot uses BFS search to determine optimal movement paths.

### Environment Representation

* Observable Environment
* Deterministic Environment
* Static Environment
* Single-Agent System
* Discrete Environment

---

## PEAS Description

### Performance Measure

* Maximum cleaned cells
* Minimum movement cost
* Shortest cleaning time
* Efficient obstacle avoidance

### Environment

* Grid-based room
* Dirt cells
* Obstacles
* Robot position

### Actuators

* Move Up
* Move Down
* Move Left
* Move Right
* Cleaning action

### Sensors

* Current position sensor
* Dirt detection sensor
* Obstacle detection sensor
* Environment scanner

---

## Future Enhancements

* A* Search Algorithm
* Dynamic obstacle handling
* Battery management system
* Multi-robot coordination
* Graphical User Interface (GUI)
* Real-time sensor integration
* Machine Learning-based cleaning optimization

---

## Applications

* Home cleaning robots
* Office maintenance systems
* Hospital sanitation robots
* Warehouse cleaning automation
* Smart building management

---

## Conclusion

The Autonomous Cleaning Strategy Planner demonstrates how Artificial Intelligence can be applied to autonomous cleaning tasks. By integrating BFS-based path planning and intelligent decision-making, the robot efficiently navigates the environment, avoids obstacles, and cleans all reachable dirty cells. This project provides a practical understanding of AI agents, search algorithms, and autonomous systems.
