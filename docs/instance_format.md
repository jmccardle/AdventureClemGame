# Game Instance Format

This document describes the structure of game instance files used by AdventureGame.

## Overview

Game instances are JSON files that contain all the information needed to run a single game episode. They include:
- Initial world state
- Goal state
- Action definitions (PDDL)
- Domain definitions (PDDL)
- Optional event definitions
- Prompts and metadata

## File Location

Instances are stored in `adventuregame/in/`:
- `instances.json`: Main production instances
- `instances_*.json`: Experimental or variant instances

## Top-Level Structure

```json
{
  "experiments": [
    {
      "experiment_id": "basic_easy",
      "game_instances": [
        {
          "game_id": "0",
          "variant": "basic",
          // ... instance details
        }
      ]
    }
  ]
}
```

### Experiments

Each experiment contains a collection of related game instances:

```json
{
  "experiment_id": "basic_easy",
  "game_instances": [ /* list of instances */ ]
}
```

Common experiment IDs:
- `basic_easy`: Basic variant, easy difficulty
- `basic_hard`: Basic variant, hard difficulty
- `plan_easy`: Planning variant, easy difficulty
- `basic_invlimit_easy`: With inventory limits
- `basic_preexplore_easy`: With pre-exploration

## Game Instance Structure

### Complete Example

```json
{
  "game_id": "0",
  "variant": "basic",
  "adventure_id": "home_deliver_easy_0",
  "adventure_type": "home_deliver_three",
  "difficulty": "easy",
  
  "prompt": "You are playing a text adventure game...",
  
  "initial_state": [
    ["at", "player", "kitchen"],
    ["at", "orange", "kitchen"],
    ["at", "cupboard", "kitchen"],
    ["closed", "cupboard"],
    ["exit", "kitchen", "bedroom", "north"]
  ],
  
  "goal_state": [
    ["at", "orange", "bedroom"]
  ],
  
  "optimal_turns": 3,
  "max_turns": 20,
  
  "action_definitions": [ /* PDDL actions */ ],
  "domain_definitions": [ /* PDDL domains */ ],
  "event_definitions": [ /* PDDL events (optional) */ ]
}
```

### Core Fields

#### game_id (string)
Unique identifier for the instance within its experiment.

```json
"game_id": "0"
```

#### variant (string)
Game variant type:
- `"basic"`: Single action per turn
- `"plan"`: Action + future plan
- `"basic_invlimit"`: With inventory constraints
- `"basic_preexplore"`: With pre-exploration phase

```json
"variant": "basic"
```

#### adventure_id (string)
Identifier linking to source adventure from generation.

```json
"adventure_id": "home_deliver_easy_0"
```

#### adventure_type (string)
Type of adventure:
- `"home_deliver_three"`: Delivery task
- `"potion_brewing_easy"`: Potion crafting
- `"new-words_created"`: Novel action learning

```json
"adventure_type": "home_deliver_three"
```

#### difficulty (string)
Difficulty level: `"easy"` or `"hard"`

```json
"difficulty": "easy"
```

### Prompt Field

The initial prompt shown to the player. May include placeholders.

```json
"prompt": "You are playing a text adventure game. You are in a kitchen. Your goal is to get the orange to the bedroom. You can interact with objects and move between rooms.\n\nAvailable actions: take, drop, go, examine, open, close"
```

**Placeholders** (replaced at runtime):
- `$GOAL$`: Replaced with formatted goal
- `$ACTIONS$`: Replaced with action list

### State Definitions

#### initial_state (array of arrays)
List of PDDL facts defining the starting world state.

```json
"initial_state": [
  ["at", "player", "kitchen"],
  ["at", "orange", "kitchen"],
  ["at", "cupboard", "kitchen"],
  ["closed", "cupboard"],
  ["in", "key", "cupboard"],
  ["exit", "kitchen", "bedroom", "north"],
  ["exit", "bedroom", "kitchen", "south"],
  ["itemcount", "inventory", 0]
]
```

**Fact Format**: `[predicate, param1, param2, ...]`

**Common Predicates**:
- `["at", entity, location]`: Entity location
- `["in", entity, container]`: Inside container
- `["on", entity, supporter]`: On supporter
- `["open", container]`: Container state
- `["closed", container]`: Container state
- `["exit", room1, room2, direction]`: Room connections
- `["trait", entity, trait_name]`: Entity trait
- `["itemcount", "inventory", count]`: Inventory count

#### goal_state (array of arrays)
List of PDDL facts that must be true to win.

```json
"goal_state": [
  ["at", "orange", "bedroom"],
  ["at", "key", "bedroom"]
]
```

All facts must be present in world state to achieve the goal.

### Turn Limits

#### optimal_turns (number)
Minimum turns needed to complete (from Clingo solver).

```json
"optimal_turns": 3
```

Used for computing efficiency metrics.

#### max_turns (number)
Maximum turns before episode ends.

```json
"max_turns": 20
```

Typically `optimal_turns * 5` or similar.

### PDDL Definitions

#### action_definitions (array of objects)
List of available actions. See [PDDL Guide](pddl_guide.md) for details.

```json
"action_definitions": [
  {
    "action_id": "take",
    "parameters": [
      {"name": "?object", "type": "entity"}
    ],
    "preconditions": {
      "condition_type": "and",
      "conditions": [
        {
          "predicate": "at",
          "parameters": ["?object", "?room"]
        },
        {
          "predicate": "at",
          "parameters": ["player", "?room"]
        }
      ]
    },
    "effects": {
      "effect_type": "and",
      "effects": [
        {
          "effect_modifier": "not",
          "predicate": "at",
          "parameters": ["?object", "?room"]
        },
        {
          "predicate": "in",
          "parameters": ["?object", "inventory"]
        }
      ]
    },
    "feedback": {
      "success": "You take the {object}.",
      "failure": "You can't take the {object}."
    }
  }
]
```

#### domain_definitions (array of objects)
Type system and predicate definitions.

```json
"domain_definitions": [
  {
    "domain_id": "adventure_domain",
    "types": {
      "entity": ["item", "container", "supporter"],
      "room": ["kitchen", "bedroom", "garden"]
    },
    "predicates": [
      {
        "predicate_id": "at",
        "parameters": [
          {"name": "?entity", "type": "entity"},
          {"name": "?location", "type": "room"}
        ],
        "mutable": true
      },
      {
        "predicate_id": "trait",
        "parameters": [
          {"name": "?entity", "type": "entity"},
          {"name": "?trait", "type": "string"}
        ],
        "mutable": false
      }
    ],
    "mutable_states": ["open", "closed", "at", "in", "on"]
  }
]
```

#### event_definitions (array of objects, optional)
Reactive events triggered by state changes.

```json
"event_definitions": [
  {
    "event_id": "container_opened",
    "parameters": [
      {"name": "?container", "type": "container"}
    ],
    "triggers": {
      "condition_type": "and",
      "conditions": [
        {
          "predicate": "open",
          "parameters": ["?container"]
        }
      ]
    },
    "effects": {
      "effect_type": "forall",
      "variable": "?item",
      "variable_type": "entity",
      "when": {
        "predicate": "in",
        "parameters": ["?item", "?container"]
      },
      "effects": [
        {
          "predicate": "visible",
          "parameters": ["?item"]
        }
      ]
    },
    "feedback": "Opening the {container} reveals: {items}"
  }
]
```

## Variant-Specific Fields

### Plan Variant

Includes planning-specific configuration:

```json
{
  "variant": "plan",
  "plan_separator": "Next actions:",
  "plan_format": "comma-separated"
}
```

Players provide:
```
> take orange
Next actions: go north, drop orange
```

### Inventory Limit Variant

Adds inventory constraints:

```json
{
  "variant": "basic_invlimit",
  "max_inventory": 2,
  "initial_state": [
    ["itemcount", "inventory", 0],
    // ...
  ]
}
```

Uses `itemcount` predicate and numeric comparisons in actions.

### Pre-explore Variant

Includes pre-exploration actions:

```json
{
  "variant": "basic_preexplore",
  "preexplore_actions": [
    "look",
    "examine cupboard",
    "open cupboard"
  ]
}
```

These actions are executed before the main task begins.

### New-Words Variant

Includes novel action definitions:

```json
{
  "variant": "basic",
  "adventure_type": "new-words_created",
  "new_action": "gleeb",
  "new_action_replaces": "take",
  "action_definitions": [
    {
      "action_id": "gleeb",
      "action_name": "gleeb",
      // Same definition as "take" but different name
    }
  ]
}
```

## Entity Metadata

While not directly in instances, entities have metadata used during generation:

```json
{
  "entity_id": "orange",
  "entity_name": "orange",
  "entity_type": "item",
  "traits": ["takeable", "edible"],
  "description": "A ripe orange",
  "container_capacity": null,
  "supporter_capacity": null
}
```

This metadata is compiled into PDDL facts in `initial_state`.

## Room Metadata

```json
{
  "room_id": "kitchen",
  "room_name": "kitchen",
  "room_type": "room",
  "description": "A cozy kitchen with wooden cabinets",
  "exits": {
    "north": "bedroom",
    "east": "garden"
  }
}
```

Compiled into `exit` facts in initial state.

## Loading Instances

### Python

```python
import json

with open('adventuregame/in/instances.json') as f:
    data = json.load(f)
    
experiments = data['experiments']
for exp in experiments:
    print(f"Experiment: {exp['experiment_id']}")
    for instance in exp['game_instances']:
        print(f"  Game: {instance['game_id']}")
```

### In clemgame Framework

```python
from clemcore.clemgame import GameSpec

spec = GameSpec("adventuregame")
instances = spec.load_instances()
```

## Validation

### Required Fields

All instances must have:
- `game_id`
- `variant`
- `initial_state`
- `goal_state`
- `action_definitions`
- `domain_definitions`

### State Consistency

- All entities in `goal_state` should exist in `initial_state` entity definitions
- All predicates used must be defined in `domain_definitions`
- Room connections should be bidirectional (unless intentional)

### Type Consistency

- Entity types in facts must match `domain_definitions`
- Action parameters must reference defined types
- Predicate parameters must match definitions

## Best Practices

1. **Keep initial states minimal**: Only include necessary facts
2. **Document unusual setups**: Add comments in source files
3. **Test goal achievability**: Ensure goals can be reached
4. **Validate PDDL**: Check actions parse correctly
5. **Set reasonable turn limits**: `optimal * 4-6` is typical
6. **Include diverse instances**: Mix easy and hard in each experiment
7. **Use clear game_ids**: Sequential numbers or descriptive names

## Generating Instances

Instances are generated from raw adventures:

```bash
cd adventuregame
python3 instancegenerator.py
```

This reads `resources/adventures_*.json` and creates `in/instances.json`.

### Customizing Generation

Edit `instancegenerator.py` to:
- Change prompt templates
- Add new variants
- Modify turn limits
- Filter adventure types

## Debugging Instances

### Check Parsing

```python
from if_wrapper import AdventureIFInterpreter

interpreter = AdventureIFInterpreter(instance)
# If this succeeds, instance is valid
```

### Verify Goal Achievability

```python
# Check goal facts exist as predicates
for goal_fact in instance['goal_state']:
    predicate = goal_fact[0]
    # Check if predicate is defined in domain
```

### Test Optimal Solution

If instance includes `optimal_solution`:

```python
interpreter = AdventureIFInterpreter(instance)
for action in instance['optimal_solution']:
    result = interpreter.process_action(action)
    assert result['success'], f"Optimal action failed: {action}"
```

## Common Issues

### Missing Predicates

```
Error: Predicate 'visible' not defined
```

**Solution**: Add predicate to `domain_definitions`.

### Type Mismatches

```
Error: 'orange' is not of type 'container'
```

**Solution**: Check entity type in initial state matches action requirements.

### Unreachable Goals

```
Episode ended without achieving goals
```

**Solution**: Verify all goal facts can be produced by available actions.

### State Inconsistencies

```
Error: Multiple values for state predicate
```

**Solution**: Ensure mutually exclusive states (open/closed) aren't both present.

## References

- [Architecture](architecture.md) - How instances are used
- [PDDL Guide](pddl_guide.md) - PDDL syntax details
- [Adding Actions](adding_actions.md) - Creating action definitions
- [Development Guide](development.md) - Generation workflow
