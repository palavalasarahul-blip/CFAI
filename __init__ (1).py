# Project Report: Autonomous Cleaning Strategy Planner

## Abstract

This project implements an intelligent cleaning robot simulator for a dynamic
indoor grid. It integrates classical search, constraint satisfaction,
decision theory, Bayesian inference, temporal prediction, and explainable AI.
The result is a reproducible teaching and demonstration platform where every
route, schedule, and target choice can be inspected.

## 1. Problem Statement

A cleaning robot must choose what to clean, when to clean it, and how to reach
it while handling obstacles, finite battery, uncertain dirt observations,
occupancy, room priorities, availability, and maintenance periods. A shortest
path alone cannot solve this multi-stage problem.

## 2. Objectives

- Model a partially observable indoor cleaning environment.
- Compare uninformed, cost-based, and heuristic graph search.
- Generate valid cleaning timetables with CSP methods.
- Adapt cleaning behavior through expected utility.
- Infer hidden cleaning need from noisy sensors.
- Combine all modules in one explainable hybrid workflow.

## 3. PEAS and Environment

Performance measures include cleaned area, energy, time, collision avoidance,
and schedule adherence. The environment contains rooms, floor cells,
obstacles, chargers, dirt, and occupancy evidence. The robot acts through
movement, cleaning, and charging, and observes the world through dirt, camera,
occupancy, position, and battery sensors.

The environment is represented both as a grid for human interpretation and an
undirected weighted NetworkX graph for search. A state contains robot position,
battery, and remaining dirty locations.

## 4. Search Algorithms

BFS and DFS use a deque frontier. UCS, Greedy Best-First, and A* use a priority
queue. UCS ranks by path cost, Greedy ranks by Manhattan distance, and A* ranks
by `g(n) + h(n)`. Every implementation records open-list snapshots, closed-list
expansion order, parent links, path cost, runtime, expanded nodes, peak traced
memory, and path length.

## 5. Constraint Satisfaction

Each room is a variable and available start hours form its domain. Constraints
cover availability, task duration overlap, battery budget, room priority, and
maintenance. The systematic solver uses MRV, degree tie-breaking, LCV,
forward checking, backtracking, and an AC-3-style support pass. Min-conflicts
provides local repair. Failed checks are retained as explanations.

## 6. Decision Making

The base utility model is:

`Utility = weighted cleaning benefit - time cost - battery cost - occupancy risk`

Four policy weight sets create Fast, Energy Saving, Deep Cleaning, and Balanced
behavior. The module also includes reusable minimax, alpha-beta pruning,
depth-limited evaluation, iterative deepening, and expectimax implementations.
In this domain, occupancy and future dirt can be interpreted as uncertain
environment responses rather than an adversarial player.

## 7. Probabilistic Reasoning

The Bayesian network uses room type and occupancy as causes of dirt, with dirt
causing cleaning need. Conditional probabilities are explicit and interpretable.
Dirt and camera sensors are fused sequentially with Bayes rule. Variable
elimination sums out occupancy and dirt. A two-state Markov model predicts dirt
accumulation, while HMM filtering estimates hidden dirt over a sensor sequence.
Rejection sampling and likelihood weighting demonstrate approximate inference.

## 8. Hybrid Planner

The planner executes this pipeline:

1. Detect evidence for every room.
2. Fuse sensors and predict dirt probability.
3. Convert probable cleaning needs into CSP tasks.
4. Produce or repair a feasible schedule.
5. Calculate utility for feasible rooms.
6. Select the best target and policy.
7. Search for a route.
8. Execute one transparent action.
9. Update knowledge, analytics, and explanations.

## 9. Explainability

The system logs prior and posterior probabilities, sensor contributions,
predicted dirt, selected utility, schedule feasibility, route cost, expanded
nodes, movement energy, and cleaning energy. Explanations are displayed in the
dashboard and persisted to `cleaning_planner.log`.

## 10. Testing

Unit tests cover all search algorithms, shortest-path behavior, blocked goals,
CSP feasibility and battery failure, min-conflicts, Bayesian normalization,
sensor updates, Markov bounds, utility monotonicity, and alpha-beta equivalence.
An integration test verifies that the hybrid planner creates an explainable
scheduled route.

## 11. Results and Evaluation

Expected evaluation compares search runtime, memory, expanded nodes, path
length, and cost. Operational evaluation reports cleaned cells per battery
percentage, total consumption, elapsed runtime, schedule quality, and
classification accuracy of dirt beliefs. The deterministic demo seed allows
repeatable classroom comparisons.

## 12. Limitations and Future Work

The simulator uses discrete cells and hourly schedules rather than continuous
robot dynamics. Future extensions can add SLAM, multi-robot coordination,
reinforcement learning, learned CPTs, continuous battery discharge, live IoT
sensors, and ROS integration.

## 13. Conclusion

The project demonstrates that autonomous cleaning is naturally a hybrid AI
problem. Search provides navigation, CSP supplies temporal feasibility,
probabilistic models handle uncertainty, utility selects behavior, and XAI
makes the resulting autonomy auditable.

