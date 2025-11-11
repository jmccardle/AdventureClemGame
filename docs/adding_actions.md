# Adding New Actions to AdventureGame

This guide walks through the process of adding a new action to AdventureGame, from defining the PDDL action to testing it in a full adventure.

## Overview

Adding a new action involves:
1. Defining the PDDL action specification
2. (Optional) Updating the grammar if needed
3. (Optional) Updating ASP encoding for adventure generation
4. Regenerating adventures and instances
5. Testing the new action

## Step 1: Define the PDDL Action

### Choose Action Location

Action definitions live in `adventuregame/resources/definitions/`:
- `basic_actions_*.json`: Standard actions (take, drop, go, etc.)
- `special_actions_*.json`: Domain-specific actions (potion brewing, etc.)

### Action Definition Template

Create or update a JSON file with your action:

```json
{
  "action_id": "examine",
  "action_name": "examine",
  "parameters": [
    {
      "name": "?object",
      "type": "entity"
    }
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
    "effects": []
  },
  "feedback": {
    "success": "You examine the {object}. {description}",
    "failure": "You don't see any {object} here."
  }
}
```

### Design Considerations

**Preconditions:**
- What must be true for this action to succeed?
- Consider: location, state, inventory, accessibility

**Effects:**
- What changes in the world after this action?
- Consider: state changes, location changes, inventory changes

**Feedback:**
- What does the player see when the action succeeds?
- What about when it fails?

### Example: Add "Read" Action

Let's add an action to read readable objects:

```json
{
  "action_id": "read",
  "action_name": "read",
  "parameters": [
    {
      "name": "?item",
      "type": "entity"
    }
  ],
  "preconditions": {
    "condition_type": "and",
    "conditions": [
      {
        "condition_type": "or",
        "conditions": [
          {
            "predicate": "in",
            "parameters": ["?item", "inventory"]
          },
          {
            "condition_type": "and",
            "conditions": [
              {
                "predicate": "at",
                "parameters": ["?item", "?room"]
              },
              {
                "predicate": "at",
                "parameters": ["player", "?room"]
              }
            ]
          }
        ]
      },
      {
        "predicate": "trait",
        "parameters": ["?item", "readable"]
      }
    ]
  },
  "effects": {
    "effect_type": "and",
    "effects": [
      {
        "predicate": "examined",
        "parameters": ["?item"]
      }
    ]
  },
  "feedback": {
    "success": "You read the {item}. It says: {text_content}",
    "failure": "You can't read that."
  }
}
```

## Step 2: Update Grammar (If Needed)

### When Grammar Updates Are Needed

Most actions work with the default grammar. Update if:
- New parameter patterns
- Special syntax requirements
- Multiple parameter variations

### Grammar Location

`adventuregame/pddl_actions.lark`

### Adding a Grammar Rule

For a two-parameter action like "put X in Y":

```lark
?action: take_action
       | drop_action
       | put_action
       | read_action  // Add your action here
       | ...

read_action: "read" ENTITY
ENTITY: /[a-z_]+/
```

For more complex patterns:

```lark
put_action: "put" ENTITY ("in" | "into" | "inside") ENTITY
          | "place" ENTITY ("on" | "onto") ENTITY
```

### Test Grammar

Create a test file `test_pddl_actions_read.txt`:

```
action: read ?item - entity

parameters:
  ?item - entity

preconditions:
  (trait ?item readable)

effects:
  (examined ?item)
```

Test parsing:
```bash
python3 -c "
from lark import Lark
parser = Lark.open('pddl_actions.lark')
with open('test_pddl_actions_read.txt') as f:
    tree = parser.parse(f.read())
    print(tree.pretty())
"
```

## Step 3: Update Entity Definitions

If your action requires new traits or entity types:

### Add Entity Traits

In `resources/definitions/entities_*.json`:

```json
{
  "entity_id": "book",
  "entity_name": "book",
  "entity_type": "item",
  "traits": ["takeable", "readable"],
  "description": "A leather-bound book",
  "text_content": "The book contains ancient recipes."
}
```

### Add to Domain Predicates

In domain definition or `resources/definitions/domain_*.json`:

```json
{
  "predicate_id": "examined",
  "parameters": [
    {"name": "?entity", "type": "entity"}
  ],
  "mutable": true
}
```

## Step 4: Update ASP Encoding (For Generation)

If you want the adventure generator to use your action:

### Location

`adventuregame/resources/pddl_to_asp.py`

### Add ASP Rules

Convert PDDL preconditions/effects to ASP:

```python
def action_read_asp():
    return """
    % Read action
    possible(read(I), T) :-
        holds(at(I, R), T),
        holds(at(player, R), T),
        holds(trait(I, readable), T).

    holds(examined(I), T+1) :-
        occurs(read(I), T).
    """
```

### Update Adventure Generation

In `resources/clingo_adventures2-2.py`:

```python
# Add to action list
self.available_actions.append({
    "action_id": "read",
    "asp_encoding": action_read_asp(),
    "required_traits": ["readable"]
})
```

## Step 5: Test Action Locally

### Create Test Instance

Create a minimal test instance:

```python
{
  "game_id": "test_read",
  "initial_state": [
    ["at", "player", "library"],
    ["at", "book", "library"],
    ["trait", "book", "readable"]
  ],
  "goal_state": [
    ["examined", "book"]
  ],
  "action_definitions": [
    // Your read action definition
  ],
  "domain_definitions": [
    // Domain with relevant predicates
  ]
}
```

### Test with IF Interpreter

```python
from if_wrapper import AdventureIFInterpreter

interpreter = AdventureIFInterpreter(test_instance)
result = interpreter.process_action("read book")
print(result["feedback"])
```

### Expected Output

```
You read the book. It says: The book contains ancient recipes.
```

## Step 6: Generate Adventures

### Update Adventure Definitions

If adding to existing adventure types, ensure entity definitions include necessary traits:

```json
{
  "adventure_type": "library_quest",
  "entities": [
    {
      "entity_id": "ancient_book",
      "traits": ["takeable", "readable"],
      "text_content": "Seek the golden key in the eastern tower."
    }
  ]
}
```

### Run Adventure Generator

```bash
cd adventuregame/resources
python3 clingo_adventures2-2.py
```

This generates raw adventures with:
- Initial states including readable items
- Goals that may require reading
- Optimal solutions using the read action

### Verify Generated Adventures

Check output JSON files in `resources/adventures_*.json`:

```python
import json
with open('adventures_basic_easy.json') as f:
    adventures = json.load(f)
    for adv in adventures:
        if 'read' in str(adv.get('optimal_solution', [])):
            print(f"Adventure {adv['adventure_id']} uses read action")
```

## Step 7: Generate Instances

Convert raw adventures to game instances:

```bash
cd adventuregame
python3 instancegenerator.py
```

This creates `in/instances.json` with:
- Complete game instances
- Prompt templates
- Action definitions including your new action

### Verify Instance

```python
import json
with open('in/instances.json') as f:
    instances = json.load(f)['experiments'][0]['game_instances']
    for inst in instances:
        actions = inst.get('action_definitions', [])
        if any(a['action_id'] == 'read' for a in actions):
            print(f"Instance {inst['game_id']} has read action")
```

## Step 8: Full Integration Test

### Run with clemgame Framework

From clemgame root directory:

```bash
python3 scripts/cli.py run -g adventuregame -m test_model --instances 1
```

### Check Episode Logs

```bash
cat results/adventuregame/test_model/episode_1/interactions.json
```

Look for:
- Your action being parsed correctly
- Preconditions evaluated properly
- Effects applied to world state
- Feedback displayed to player

### Common Issues

**Action not recognized:**
- Check grammar includes action pattern
- Verify action_id matches grammar rule

**Preconditions always fail:**
- Check initial state includes required predicates
- Verify variable binding works correctly
- Use debug logging to see precondition evaluation

**Effects not applied:**
- Check effect syntax is correct
- Verify predicates exist in domain
- Check for typos in predicate names

## Step 9: Add Unit Tests

### Create Test File

`tests/test_action_read.py`:

```python
import pytest
from if_wrapper import AdventureIFInterpreter

def test_read_action_success(test_game_instance):
    """Test reading a book successfully."""
    interpreter = AdventureIFInterpreter(test_game_instance)

    # Setup: book is in room with player
    interpreter.world_state.add(("at", "player", "library"))
    interpreter.world_state.add(("at", "book", "library"))
    interpreter.world_state.add(("trait", "book", "readable"))

    # Execute action
    result = interpreter.process_action("read book")

    # Verify
    assert result["success"] is True
    assert ("examined", "book") in interpreter.world_state
    assert "read the book" in result["feedback"].lower()

def test_read_action_not_readable(test_game_instance):
    """Test reading non-readable item fails."""
    interpreter = AdventureIFInterpreter(test_game_instance)

    # Setup: orange is not readable
    interpreter.world_state.add(("at", "player", "kitchen"))
    interpreter.world_state.add(("at", "orange", "kitchen"))

    # Execute action
    result = interpreter.process_action("read orange")

    # Verify
    assert result["success"] is False
    assert ("examined", "orange") not in interpreter.world_state
```

### Run Tests

```bash
pytest tests/test_action_read.py -v
```

## Advanced: Multi-Parameter Actions

For actions with multiple parameters:

```json
{
  "action_id": "give",
  "parameters": [
    {"name": "?item", "type": "entity"},
    {"name": "?recipient", "type": "entity"}
  ],
  "preconditions": {
    "condition_type": "and",
    "conditions": [
      {
        "predicate": "in",
        "parameters": ["?item", "inventory"]
      },
      {
        "predicate": "at",
        "parameters": ["?recipient", "?room"]
      },
      {
        "predicate": "at",
        "parameters": ["player", "?room"]
      },
      {
        "predicate": "trait",
        "parameters": ["?recipient", "npc"]
      }
    ]
  },
  "effects": {
    "effect_type": "and",
    "effects": [
      {
        "effect_modifier": "not",
        "predicate": "in",
        "parameters": ["?item", "inventory"]
      },
      {
        "predicate": "has",
        "parameters": ["?recipient", "?item"]
      }
    ]
  }
}
```

Grammar:
```lark
give_action: "give" ENTITY "to" ENTITY
```

## Checklist

Before merging your new action:

- [ ] Action definition complete and valid
- [ ] Grammar updated (if needed)
- [ ] Entity definitions include necessary traits
- [ ] Domain predicates defined
- [ ] ASP encoding added (if generating adventures)
- [ ] Local testing passed
- [ ] Adventures generated successfully
- [ ] Instances created correctly
- [ ] Integration test passed
- [ ] Unit tests added and passing
- [ ] Documentation updated

## Examples

See these files for complete examples:

- **Simple action**: `basic_actions_go.json` (movement)
- **Container interaction**: `basic_actions_open.json` (state change)
- **Inventory management**: `basic_actions_take.json` (inventory)
- **Special action**: `special_actions_potion.json` (brewing)
- **Complex conditions**: `basic_actions_put.json` (multi-parameter)

## Troubleshooting

### Parse Errors

```
LarkError: Unexpected token
```

**Solution**: Check grammar matches your action syntax exactly.

### Precondition Failures

```
Action failed: precondition not satisfied
```

**Solution**: Enable debug logging to see which precondition failed:
```python
import logging
logging.getLogger("adventuregame.if_wrapper").setLevel(logging.DEBUG)
```

### Variable Binding Issues

```
Cannot bind variable ?object to orange
```

**Solution**: Check that "orange" is defined as the correct type in entity definitions.

### Effect Not Applied

```
World state unchanged after action
```

**Solution**: Verify effect syntax and predicate names match domain definition.

## Next Steps

- Read [PDDL Guide](pddl_guide.md) for more on PDDL syntax
- See [Architecture](architecture.md) for how actions fit into the system
- Check [Development Guide](development.md) for workflow details
