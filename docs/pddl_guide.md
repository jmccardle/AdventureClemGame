# PDDL Guide for AdventureGame

## Overview

AdventureGame uses PDDL (Planning Domain Definition Language) to define game mechanics, actions, and world state. This guide explains how PDDL is used in the system and how to write PDDL definitions.

## What is PDDL?

PDDL is a standardized language for defining planning problems. In AdventureGame, we use a subset of PDDL to define:

- **Domains**: Types and predicates that describe the world
- **Actions**: What the player can do and what effects actions have
- **Events**: Reactive behaviors triggered by state changes
- **States**: Facts about the current world configuration

## Domain Definitions

### Structure

```
domain: adventure_domain

types:
  entity: [item, container, supporter]
  room: [kitchen, bedroom, garden]

predicates:
  (at ?e - entity ?r - room)
  (in ?e1 - entity ?e2 - entity)
  (open ?c - container)
  (closed ?c - container)
```

### Types

Types define categories of objects in the game world:

```python
"types": {
  "entity": ["item", "container", "supporter", "ingredient"],
  "room": ["kitchen", "bedroom", "garden"],
  "trait": ["openable", "edible", "takeable"]
}
```

**Type Hierarchy:**
- Entity types can have subtypes (e.g., "container" is a type of "entity")
- Traits are special types that entities can have
- Rooms are separate from entities

### Predicates

Predicates describe properties and relationships:

```python
{
  "predicate_id": "at",
  "parameters": [
    {"name": "?entity", "type": "entity"},
    {"name": "?location", "type": "room"}
  ],
  "mutable": true
}
```

**Common Predicates:**

| Predicate | Meaning | Example |
|-----------|---------|---------|
| `(at ?e ?r)` | Entity is in room | `(at orange kitchen)` |
| `(in ?e1 ?e2)` | Entity is inside container | `(in key cupboard)` |
| `(on ?e1 ?e2)` | Entity is on supporter | `(on book table)` |
| `(open ?c)` | Container is open | `(open cupboard)` |
| `(closed ?c)` | Container is closed | `(closed cupboard)` |
| `(itemcount ?i ?n)` | Inventory count | `(itemcount inventory 2)` |

**Mutable vs Immutable:**
- **Mutable** predicates can change during the game (e.g., `open`, `closed`, `at`)
- **Immutable** predicates are fixed (e.g., entity types, traits)

## Action Definitions

### Structure

```
action: take ?object - entity
parameters:
  ?object - entity

preconditions:
  (and
    (at ?object ?room)
    (at player ?room)
    (not (in ?object ?container))
  )

effects:
  (and
    (not (at ?object ?room))
    (in ?object inventory)
  )
```

### Complete Example: Take Action

```json
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
      },
      {
        "condition_type": "not",
        "conditions": [
          {
            "predicate": "in",
            "parameters": ["?object", "?container"]
          }
        ]
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
  }
}
```

### Preconditions

Preconditions define when an action can be executed.

**Logical Operators:**

1. **and**: All conditions must be true
   ```
   (and
     (at player kitchen)
     (at orange kitchen)
   )
   ```

2. **or**: At least one condition must be true
   ```
   (or
     (open cupboard)
     (not (exists ?lock - entity (locked cupboard)))
   )
   ```

3. **not**: Condition must be false
   ```
   (not (in orange inventory))
   ```

**Numeric Comparisons:**
```
(< (itemcount inventory) 3)  # Less than
(> (itemcount inventory) 0)  # Greater than
(<= (itemcount inventory) 5) # Less than or equal
(>= (itemcount inventory) 1) # Greater than or equal
```

**Existential Quantification:**
```
(exists ?container - container
  (and
    (in ?object ?container)
    (closed ?container)
  )
)
```

### Effects

Effects define how the world state changes after an action.

**Basic Effects:**
```
effects:
  (and
    (at player bedroom)         # Add fact
    (not (at player kitchen))   # Remove fact
  )
```

**Conditional Effects (when):**
```
(when
  (closed ?container)
  (open ?container)
)
```

Applies the effect only if the condition is true.

**Universal Effects (forall):**
```
(forall ?item - entity
  (when
    (in ?item ?container)
    (visible ?item)
  )
)
```

Applies effect to all entities matching the condition.

**Numeric Effects:**
```
(increase (itemcount inventory) 1)  # Increment
(decrease (itemcount inventory) 1)  # Decrement
(assign (itemcount inventory) 0)    # Set value
```

### Feedback Templates

Actions can include feedback templates:

```json
"feedback": {
  "success": "You take the {object}.",
  "failure_precondition": "You can't take the {object} right now.",
  "failure_not_found": "There's no {object} here."
}
```

Variables in curly braces are substituted with actual values.

## Event Definitions

Events are reactive behaviors triggered by world state changes.

### Structure

```
event: container_opened
parameters:
  ?container - container

triggers:
  (open ?container)

preconditions:
  (exists ?item - entity
    (in ?item ?container)
  )

effects:
  (forall ?item - entity
    (when
      (in ?item ?container)
      (visible ?item)
    )
  )

feedback:
  "Opening the {container} reveals: {items}."
```

### Event Processing

Events are checked after every action:
1. Check if event trigger condition matches new state
2. Evaluate preconditions with variable bindings
3. Apply effects if preconditions satisfied
4. Generate feedback

### Example: Potion Brewing Event

```json
{
  "event_id": "potion_step_1",
  "parameters": [
    {"name": "?cauldron", "type": "cauldron"},
    {"name": "?ingredient", "type": "ingredient"}
  ],
  "triggers": {
    "condition_type": "and",
    "conditions": [
      {"predicate": "in", "parameters": ["?ingredient", "?cauldron"]},
      {"predicate": "potion_stage", "parameters": ["?cauldron", "0"]}
    ]
  },
  "effects": {
    "effect_type": "and",
    "effects": [
      {
        "effect_modifier": "not",
        "predicate": "potion_stage",
        "parameters": ["?cauldron", "0"]
      },
      {
        "predicate": "potion_stage",
        "parameters": ["?cauldron", "1"]
      }
    ]
  },
  "feedback": "The potion begins to bubble as you add the {ingredient}."
}
```

## State Representation

### World State

World state is a set of ground facts (no variables):

```python
world_state = {
    ("at", "player", "kitchen"),
    ("at", "orange", "kitchen"),
    ("at", "cupboard", "kitchen"),
    ("closed", "cupboard"),
    ("in", "key", "cupboard"),
    ("itemcount", "inventory", "0")
}
```

### Goal State

Goal state is similar but represents desired facts:

```python
goal_state = {
    ("at", "orange", "bedroom"),
    ("at", "key", "bedroom")
}
```

Goals are achieved when all goal facts are present in world state.

## Variable Binding

### Parameter Matching

When resolving actions, parameters are bound to actual entities:

```
Action: take ?object
Input: "take orange"
Binding: {?object: "orange"}
```

### Type Checking

Variables must match their declared types:

```
?object - entity
```

The system checks that "orange" is of type "entity" before allowing the binding.

### Room Inference

Some variables are inferred from context:

```
Precondition: (at ?object ?room)
Given: player is in kitchen
Inferred: ?room = "kitchen"
```

## Writing New PDDL Definitions

### Action Design Checklist

- [ ] Clear action name (verb)
- [ ] Required parameters with types
- [ ] Complete preconditions (what must be true)
- [ ] Correct effects (add/remove facts)
- [ ] Feedback messages for success/failure
- [ ] Handle edge cases (containers, inventory limits)

### Testing PDDL Definitions

1. **Parse Test**: Verify grammar is valid
   ```bash
   python3 -m adventuregame.pddl_util test_action.json
   ```

2. **Logic Test**: Create test scenario
   - Define initial state
   - Execute action
   - Verify expected effects

3. **Integration Test**: Include in adventure
   - Generate adventure with action
   - Run full episode
   - Verify behavior

### Common Patterns

**Container Interaction:**
```
action: open ?container
preconditions:
  - (closed ?container)
  - (at ?container ?room)
  - (at player ?room)
effects:
  - (not (closed ?container))
  - (open ?container)
  - forall items in container: (visible ?item)
```

**Inventory Management:**
```
action: take ?object
preconditions:
  - (< (itemcount inventory) MAX_ITEMS)
  - (at ?object ?room)
  - (at player ?room)
effects:
  - (in ?object inventory)
  - (increase (itemcount inventory) 1)
```

**State Transitions:**
```
action: use ?tool ?target
preconditions:
  - (in ?tool inventory)
  - (state ?target "locked")
effects:
  - (not (state ?target "locked"))
  - (state ?target "unlocked")
```

## PDDL Parsing

### Grammar Files

- `pddl_domain.lark`: Domain definitions
- `pddl_actions.lark`: Action definitions
- `pddl_events.lark`: Event definitions

### Parser Usage

```python
from lark import Lark
from if_wrapper import PDDLDomainTransformer

parser = Lark.open("pddl_domain.lark")
tree = parser.parse(domain_text)
transformer = PDDLDomainTransformer()
processed = transformer.transform(tree)
```

## Debugging PDDL

### Common Issues

1. **Missing Preconditions**: Action succeeds when it shouldn't
   - Solution: Add more specific preconditions

2. **Incomplete Effects**: State doesn't change as expected
   - Solution: Add all necessary effects (including negations)

3. **Type Mismatches**: Variables don't bind correctly
   - Solution: Check type definitions and entity types

4. **Variable Scoping**: Variables not bound correctly
   - Solution: Ensure parameters are declared before use

### Debug Logging

Enable debug logging to see action resolution details:

```python
import logging
logging.getLogger("adventuregame").setLevel(logging.DEBUG)
```

This shows:
- Precondition checks
- Variable bindings
- Effect applications
- State changes

## Best Practices

1. **Keep actions focused**: One clear purpose per action
2. **Use descriptive names**: `take`, `open`, `examine` not `action1`
3. **Document complex logic**: Add comments for tricky preconditions
4. **Test thoroughly**: Cover success, failure, and edge cases
5. **Reuse predicates**: Use standard predicates when possible
6. **Consistent naming**: Follow existing naming conventions
7. **Type everything**: Declare types for all parameters

## Advanced Features

### Dynamic Variables

Variables can be bound dynamically during resolution:
```
(forall ?item - entity
  (when (in ?item ?container) ...)
)
```

### Nested Conditions

Conditions can be arbitrarily nested:
```
(and
  (at player ?room)
  (or
    (open ?container)
    (not (exists ?lock (locked ?container)))
  )
)
```

### Multi-step Effects

Effects can trigger events which have further effects:
```
Action effect → World state change → Event triggered → Event effects applied
```

## Resources

- **Example Definitions**: See `resources/definitions/`
- **Test Cases**: See `test_pddl_*.txt` files
- **Grammar Files**: `pddl_*.lark` files
- **Parser Code**: `if_wrapper.py`, `pddl_util.py`

## Next Steps

- Read [Adding Actions Guide](adding_actions.md) for step-by-step instructions
- See [Architecture](architecture.md) for how PDDL fits into the system
- Check [Instance Format](instance_format.md) for how PDDL is used in game instances
