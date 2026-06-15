# Architecture and Diagrams

## Design

The simulator uses a layered architecture. Domain models do not depend on the
UI. AI engines expose typed result objects, and `HybridPlanner` coordinates
them. Streamlit renders those results and stores only simulation session state.

## UML Class Diagram

```mermaid
classDiagram
    class HouseEnvironment {
      +int width
      +int height
      +dict rooms
      +set obstacles
      +dict dirt
      +Graph graph
      +neighbors(position)
      +clean(robot)
      +peas()
    }
    class Robot {
      +Position position
      +float battery
      +KnowledgeBase knowledge
      +move_to(position)
      +clean(position)
      +recharge()
    }
    class Room {
      +str name
      +set cells
      +int priority
      +set available_slots
    }
    class CleaningTask {
      +str room_name
      +int duration
      +float battery_cost
      +int assigned_slot
    }
    class HybridPlanner {
      +assess_rooms(policy)
      +create_schedule(assessments)
      +plan(algorithm, policy)
      +execute_next_step(plan)
    }
    class CSPScheduler {
      +solve()
      +min_conflicts()
      +detect_conflicts()
    }
    class DirtBayesianNetwork {
      +fuse_sensors()
      +variable_elimination()
      +predict_markov()
      +hidden_dirt_filter()
    }
    class DecisionEngine {
      +utility()
      +choose_policy()
      +minimax()
      +alpha_beta()
      +expectimax()
    }
    class SearchResult

    HouseEnvironment "1" o-- "*" Room
    Robot "1" o-- "1" KnowledgeBase
    CSPScheduler "1" o-- "*" CleaningTask
    HybridPlanner --> HouseEnvironment
    HybridPlanner --> Robot
    HybridPlanner --> CSPScheduler
    HybridPlanner --> DirtBayesianNetwork
    HybridPlanner --> DecisionEngine
    HybridPlanner --> SearchResult
```

## Hybrid Planner Flowchart

```mermaid
flowchart TD
    A[Read sensors and environment] --> B[Bayesian sensor fusion]
    B --> C[Markov dirt prediction]
    C --> D[Generate CSP cleaning tasks]
    D --> E{Schedule feasible?}
    E -- Yes --> F[Score feasible rooms]
    E -- No --> G[Min-conflicts repair]
    G --> F
    F --> H[Select highest expected utility]
    H --> I[Run selected graph search]
    I --> J{Path found?}
    J -- Yes --> K[Move or clean]
    J -- No --> L[Explain route failure]
    K --> M[Update knowledge and analytics]
    M --> N[Explain complete decision]
```

## Search State Flow

```mermaid
stateDiagram-v2
    [*] --> Frontier
    Frontier --> Closed: expand best/next node
    Closed --> Goal: goal test succeeds
    Closed --> Frontier: add unseen successors
    Goal --> ReconstructPath
    Frontier --> Failure: frontier empty
    ReconstructPath --> [*]
    Failure --> [*]
```

## SOLID Mapping

- Single responsibility: each package owns one AI capability.
- Open/closed: search selection uses an enum and shared result contract.
- Liskov substitution: every search algorithm returns `SearchResult`.
- Interface segregation: UI consumes narrow planner/result APIs.
- Dependency inversion: the hybrid layer coordinates domain-level abstractions,
  while visualization remains downstream.

