# AdventureGame Architecture

## Overview

AdventureGame is an Interactive Fiction (IF) text adventure game implementation designed for the clemgame benchmarking framework. It evaluates language models' ability to understand and navigate text-based adventure games by completing goals through action commands.

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    clemgame Framework                        │
│                  (Orchestration & Metrics)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼──────────┐            ┌────────▼─────────┐
│  GameBenchmark   │            │   GameScorer     │
│   (Benchmark     │            │   (Metrics &     │
│   Coordinator)   │            │   Evaluation)    │
└───────┬──────────┘            └──────────────────┘
        │
┌───────▼──────────┐
│   GameMaster     │
│  (Game Control   │
│   & Episodes)    │
└───────┬──────────┘
        │
        │  ┌─────────────────────────────────────┐
        │  │    Game Instance (JSON)              │
        │  │  - Initial state                     │
        │  │  - Goal state                        │
        │  │  - Action definitions (PDDL)         │
        └─▶│  - Domain definitions (PDDL)         │
           │  - Event definitions (PDDL)          │
           └─────────────┬───────────────────────┘
                         │
           ┌─────────────▼───────────────────────┐
           │   AdventureIFInterpreter             │
           │  (Core Game Engine)                  │
           │                                      │
           │  ┌────────────────────────────────┐ │
           │  │  PDDL Parsers (Lark)           │ │
           │  │  - Domain parser               │ │
           │  │  - Action parser               │ │
           │  │  - Event parser                │ │
           │  └────────────────────────────────┘ │
           │                                      │
           │  ┌────────────────────────────────┐ │
           │  │  State Management              │ │
           │  │  - World state (facts)         │ │
           │  │  - Entity tracking             │ │
           │  │  - Room tracking               │ │
           │  │  - Inventory management        │ │
           │  └────────────────────────────────┘ │
           │                                      │
           │  ┌────────────────────────────────┐ │
           │  │  Action Resolution              │ │
           │  │  - Precondition checking       │ │
           │  │  - Effect application          │ │
           │  │  - Feedback generation         │ │
           │  └────────────────────────────────┘ │
           │                                      │
           │  ┌────────────────────────────────┐ │
           │  │  Event Processing              │ │
           │  │  - Event triggering            │ │
           │  │  - Reactive world state        │ │
           │  └────────────────────────────────┘ │
           └──────────────────────────────────────┘
```

## Core Components

### 1. Game Master (`master.py`)

**AdventureGameMaster**
- Orchestrates game episodes and turns
- Manages prompts and player interactions
- Handles game loop and turn limits
- Processes model responses
- Tracks episode progress

**AdventureGameScorer**
- Computes episode-level metrics
- Tracks action success/failure rates
- Measures goal achievement
- Evaluates plan adherence (for 'plan' variant)
- Generates exploration metrics

**AdventureGameBenchmark**
- Creates game masters for benchmark runs
- Loads game instances
- Manages experiment configuration

### 2. IF Interpreter (`if_wrapper.py`)

The core game engine that processes actions and maintains world state.

**Key Responsibilities:**
- Parse PDDL definitions (domains, actions, events)
- Initialize world state from PDDL facts
- Parse player action inputs
- Resolve actions (check preconditions, apply effects)
- Generate textual feedback for players
- Track state changes and goal progress
- Handle reactive events

**Major Methods:**
- `initialize_*()`: Setup parsers and load definitions
- `parse_action_input()`: Convert text to action dict
- `resolve_action()`: Execute action and return feedback
- `check_conditions()`: Validate PDDL conditions
- `resolve_effect()`: Apply PDDL effects to world state
- `run_events()`: Process reactive events
- `get_full_room_desc()`: Generate room descriptions
- `process_action()`: Main action processing pipeline

### 3. Instance Generator (`instancegenerator.py`)

**AdventureGameInstanceGenerator**
- Reads raw adventures from JSON files
- Creates game instance files for benchmarking
- Substitutes prompts with goal information
- Handles adventure type variants (basic, plan, invlimit, etc.)
- Shuffles new-word actions for variety

### 4. Adventure Generator (`resources/clingo_adventures2-2.py`)

**ClingoAdventureGenerator**
- Uses Clingo ASP solver to generate adventures
- Creates viable initial world states
- Generates solvable goal sets
- Computes optimal solutions
- Validates action sequences
- Outputs raw adventure JSON files

## Data Flow

### Episode Execution Flow

```
1. GameBenchmark loads game instance
   ↓
2. GameMaster creates AdventureIFInterpreter
   ↓
3. GameMaster sends initial prompt with goal
   ↓
4. Model generates response (action command)
   ↓
5. GameMaster parses response
   ↓
6. IF Interpreter parses and resolves action
   ├─→ Check preconditions
   ├─→ Apply effects to world state
   ├─→ Run events (if any)
   ├─→ Generate feedback text
   └─→ Check goal completion
   ↓
7. GameMaster sends feedback to model
   ↓
8. Repeat steps 4-7 until:
   - Goals achieved (success)
   - Turn limit reached (failure)
   - Invalid format detected (abort)
   ↓
9. GameScorer computes metrics
   ↓
10. Results written to files
```

### Adventure Generation Flow

```
1. Load PDDL definitions
   ├─→ Rooms (locations)
   ├─→ Entities (objects)
   ├─→ Actions (player commands)
   ├─→ Domains (types & predicates)
   └─→ Events (reactive behaviors)
   ↓
2. Generate adventure configurations
   ├─→ Select rooms and entities
   ├─→ Define interaction traits
   └─→ Set difficulty parameters
   ↓
3. Clingo ASP solver
   ├─→ Generate valid initial state
   ├─→ Generate solvable goals
   └─→ Compute optimal solution
   ↓
4. Output raw adventure JSON
   ├─→ Initial state facts
   ├─→ Goal state facts
   ├─→ Optimal action sequence
   ├─→ Metadata (turns, difficulty)
   └─→ PDDL definitions
   ↓
5. Instance Generator processes
   ├─→ Add prompts
   ├─→ Create variants
   └─→ Output instance JSON
```

## Key Design Patterns

### 1. PDDL-Based Action System

Actions are defined in PDDL format and parsed using Lark:

```
action: "take" object
preconditions:
  - (at ?object ?room)
  - (at player ?room)
  - (not (in ?object ?container))
effects:
  - (not (at ?object ?room))
  - (in ?object inventory)
```

This allows:
- Declarative action definitions
- Automatic precondition checking
- Systematic effect application
- Easy addition of new actions

### 2. State as PDDL Facts

World state is represented as a set of tuples:
```python
{
  ("at", "player", "kitchen"),
  ("at", "orange", "kitchen"),
  ("closed", "cupboard"),
  ("in", "key", "cupboard")
}
```

This enables:
- Efficient state queries
- Easy state comparison
- Clean goal checking
- Natural PDDL integration

### 3. Parser-Based Input Processing

Uses Lark parser with custom grammar for:
- PDDL domain parsing
- PDDL action parsing
- Player command parsing
- PDDL event parsing

Benefits:
- Robust input handling
- Clear error messages
- Grammar evolution
- Syntax validation

### 4. Modular Initialization

The IF interpreter uses separate initialization methods:
- `initialize_entity_types()`
- `initialize_room_types()`
- `initialize_domain()`
- `initialize_action_types()`
- `initialize_event_types()`
- `initialize_action_parsing()`

This provides:
- Clear setup phases
- Easy debugging
- Flexible configuration
- Testable components

## Game Variants

### Basic Variant
- Player provides single action per turn
- Standard feedback loop
- Example: `> take orange`

### Plan Variant
- Player provides action + future plans
- Plans tracked and evaluated
- Example:
  ```
  > take orange
  Next actions: go north, open door
  ```

### Inventory Limit Variants
- Adds inventory capacity constraints
- Tests resource management
- Uses `itemcount` predicate

### Pre-explore Variants
- Provides initial exploration sequence
- Gives players context before goals
- Tests goal-directed behavior

### New-Words Variants
- Introduces novel action verbs
- Tests generalization ability
- Two modes: created (new action) vs replace (rename existing)

## Configuration System

### config.json Structure

```json
{
  "entities": {
    "player_id": "player",
    "inventory_id": "inventory"
  },
  "predicates": {
    "mutable_states": ["open", "closed", "at", "in", "on"]
  },
  "messages": {
    "goal_template": "Your goal is to {goal}",
    "success": "Congratulations! You achieved your goal.",
    ...
  },
  "adventure_types": {
    "home_deliver": "home_deliver_three",
    "potion_brewing": "potion_brewing_easy",
    ...
  },
  "logging": {
    "level": "INFO",
    ...
  }
}
```

### ConfigLoader Pattern

Uses singleton pattern for global configuration access:
```python
from config_loader import get_config
config = get_config()
```

## Error Handling

### Custom Exceptions

Defined in `adventuregame/exceptions.py`:
- `AdventureGameError`: Base exception
- `PDDLParseError`: PDDL parsing failures
- `ActionResolutionError`: Action execution failures
- `ConfigurationError`: Configuration issues
- `InvalidStateError`: Invalid game state

### Graceful Degradation

- Fallback type inference for unknown entities
- Default values for missing configuration
- Informative error messages with context
- Logging at appropriate levels

## Performance Considerations

### State Management
- Sets for O(1) fact lookup
- Dictionaries for entity/room mappings
- Lazy evaluation where possible

### Parsing
- Pre-compiled Lark grammars
- Cached parser instances
- Efficient transformers

### Event Processing
- Conditional event evaluation
- Early termination for impossible events
- Optimized variable binding

## Testing Strategy

### Unit Tests
- Individual component testing
- PDDL parsing validation
- Action resolution verification
- State transition checks

### Integration Tests
- Full episode simulation
- Adventure generation validation
- Instance creation verification

### Test Fixtures
- Sample game instances
- PDDL definition examples
- Expected state transitions

See `tests/conftest.py` for shared fixtures.

## Extension Points

### Adding New Actions
1. Define PDDL action in `resources/definitions/`
2. Update grammar if needed (`pddl_actions.lark`)
3. No code changes required (declarative!)

### Adding New Adventure Types
1. Define in `adventure_types.json`
2. Create entity/room definitions
3. Update `clingo_adventures2-2.py`
4. Generate and test

### Adding New Metrics
1. Extend `AdventureGameScorer.compute_scores()`
2. Add metric extraction logic
3. Update score file writing
4. Document in evaluation notebooks

## Future Enhancements

### Potential Improvements
- Split `if_wrapper.py` into smaller modules
- Add localization support for messages
- Implement caching for expensive operations
- Add visualization tools for state transitions
- Enhance event system with priorities
- Support for multi-agent scenarios

### Known Limitations
- Single-player only
- English text only
- Limited event expressiveness
- No save/load mechanism (episodes are atomic)

## References

- PDDL: Planning Domain Definition Language
- Clingo: Answer Set Programming solver
- Lark: Parsing library
- clemgame: Benchmarking framework

For more details, see:
- [PDDL Guide](pddl_guide.md)
- [Adding Actions Guide](adding_actions.md)
- [Development Guide](development.md)
