# Interactive AdventureGame Roadmap

**Goal**: Make AdventureGame playable by humans with real-time metadata visibility, and enable manual adventure authoring without complex academic scaffolding.

**Status**: AdventureGame currently supports human play via the clemgame framework, but lacks standalone interactive tools and simple manual authoring workflows.

---

## Current State Analysis

### What Works Now

1. **Terminal Play Support EXISTS**
   - `AdventurePlayer._terminal_response()` in `master.py:57-81` handles human input
   - Auto-adds `> ` prefix to match IF conventions
   - Integrates with clemgame framework's interactive mode

2. **IF Interpreter is Standalone-Ready**
   - `AdventureIFInterpreter` (`if_wrapper.py`) is the core engine
   - Already decoupled from model-specific code
   - Can process actions and return detailed state

3. **Instance Format is Well-Defined**
   - JSON structure in `adventuregame/in/instances.json`
   - Clear separation: initial state, goals, actions, rooms, entities
   - See `docs/instance_format.md` for complete spec

### What's Missing

1. **No Standalone Interactive Player**
   - Must run through entire clemgame framework (`scripts/cli.py run -g adventuregame`)
   - No simple `python play.py` script
   - No real-time metadata dashboard

2. **No Manual Authoring Tools**
   - Current workflow: complex Clingo ASP → JSON generation
   - Academic examples with made-up words (new-words variants)
   - No "just write an adventure in JSON" guide

3. **Metadata is Hidden**
   - Goal tracking, action resolution details buried in logs
   - No real-time visibility into interpreter state
   - Evaluation happens post-game via Jupyter notebooks

---

## Roadmap: Phase 1 - Standalone Interactive Player

**Deliverable**: A `play_adventure.py` script that lets you play any instance with live metadata.

### 1.1 Create Interactive Player Script

**File**: `adventuregame/play_adventure.py`

```python
#!/usr/bin/env python3
"""
Standalone interactive player for AdventureGame.

Usage:
    python play_adventure.py                    # Play first instance
    python play_adventure.py --instance 5       # Play specific instance
    python play_adventure.py --file my_adventure.json  # Play custom adventure
    python play_adventure.py --debug            # Show full metadata
"""

Features:
- Load instance from instances.json or custom file
- Initialize AdventureIFInterpreter standalone (no GameMaster needed)
- Terminal loop: display state → prompt action → process → show results
- Live metadata display (optional --debug mode)
```

**Key Implementation Points**:
- Import `AdventureIFInterpreter` from `if_wrapper.py`
- Parse CLI args (argparse)
- Load instance JSON
- Initialize interpreter: `AdventureIFInterpreter(game_path, game_instance)`
- Game loop:
  ```python
  while not game_over:
      # Display current state
      print(interpreter.get_full_room_desc())

      # Get action
      action = input("> ")

      # Process
      result = interpreter.process_action(action)

      # Show feedback + metadata
      print(result['feedback'])
      if debug_mode:
          print_metadata(result)

      # Check goals
      if result['goal_achieved']:
          print("GOAL ACHIEVED!")
  ```

**Challenges**:
- `AdventureIFInterpreter.__init__` expects specific clemgame paths
- May need to refactor constructor to work standalone
- Solution: Add optional `standalone_mode=True` parameter

### 1.2 Real-Time Metadata Display

**Enhancement**: Add rich metadata output in debug mode

Display after each action:
```
==================== METADATA ====================
Action Parsed: {'action': 'take', 'arg1': 'orange'}
Preconditions: ✓ at(player, kitchen) ✓ at(orange, kitchen)
Effects Applied: + in(orange, inventory) - at(orange, kitchen)
Goals Progress: [1/3] ⬜⬜⬛
Current Inventory: [orange]
==================================================
```

**Implementation**:
- Access `interpreter.current_state` (set of facts)
- Track `interpreter.goals_achieved` vs `interpreter.goals_required`
- Pretty-print action resolution details
- Optional: colorize with `colorama` or `rich` library

### 1.3 Save/Load Game State

**Feature**: Checkpoint system for human playtesting

```python
# During play
> save checkpoint1
Game saved to checkpoints/checkpoint1.json

> load checkpoint1
Game loaded from checkpoints/checkpoint1.json
```

**Implementation**:
- Serialize `interpreter.current_state` + turn count
- Store in JSON file
- Reload by reinitializing interpreter with saved state

---

## Roadmap: Phase 2 - Manual Adventure Authoring

**Deliverable**: Simple JSON template + guide for creating adventures by hand.

### 2.1 Create Minimal Adventure Template

**File**: `adventuregame/templates/simple_adventure_template.json`

```json
{
  "name": "My Custom Adventure",
  "game_instances": [
    {
      "game_id": "custom_1",
      "variant": "basic",

      "prompt": "You wake up in a mysterious room. Find the key and escape!",

      "initial_state": [
        "at(player,bedroom)",
        "at(key,kitchen)",
        "at(door,bedroom)",
        "closed(door)",
        "locked(door)",
        "exit(bedroom,kitchen,north)"
      ],

      "goal_state": [
        "at(player,kitchen)"
      ],

      "max_turns": 10,
      "optimal_turns": 3,

      "action_definitions": [/* Use from basic_actions_v2.json */],
      "room_definitions": [/* Use from home_rooms.json */],
      "entity_definitions": [/* Use from home_entities.json */],
      "domain_definitions": [/* Use from home_domain.json */]
    }
  ]
}
```

### 2.2 Create Authoring Guide

**File**: `docs/MANUAL_AUTHORING.md`

**Contents**:
1. **Quick Start**: Copy template, edit initial_state/goal_state, play
2. **State Syntax**: How to write facts
   - `at(thing, location)` - thing is at location
   - `in(thing, container)` - thing is inside container
   - `closed(container)` - container is closed
   - `locked(door)` - door is locked
3. **Using Pre-Built Actions**: Reference `resources/definitions/basic_actions_v2.json`
4. **Common Patterns**:
   - Delivery quest: Move objects to target locations
   - Locked door: Requires key in inventory
   - Container puzzle: Open container to access items
5. **Testing Your Adventure**: Run with `play_adventure.py --file my_adventure.json`

### 2.3 Action Definition Library

**File**: `docs/ACTION_LIBRARY.md`

Human-readable catalog of available actions:

```markdown
# Available Actions

## Movement
- `go <direction>`: Move to adjacent room
  - Requires: exit(current_room, target_room, direction)
  - Example: `go north`

## Object Manipulation
- `take <object>`: Pick up object
  - Requires: object at current location, not in container
  - Example: `take key`

- `drop <object>`: Drop object from inventory
  - Example: `drop orange`

## Container Actions
- `open <container>`: Open closed container
  - Requires: container is closed
  - Example: `open cupboard`

[... full catalog with examples ...]
```

### 2.4 Adventure Validator Script

**File**: `adventuregame/validate_adventure.py`

```python
"""
Validate custom adventure JSON before playing.

Usage:
    python validate_adventure.py my_adventure.json
"""

Checks:
- JSON syntax valid
- Required fields present
- State facts use valid predicates
- Referenced rooms/entities/actions exist
- Goals are achievable (optional: run Clingo solver)
```

---

## Roadmap: Phase 3 - Enhanced Authoring Tools

**Deliverable**: Higher-level authoring abstractions for non-programmers.

### 3.1 YAML Adventure Format

**Alternative**: More human-friendly syntax

```yaml
adventure:
  name: Escape the Cottage

  rooms:
    - bedroom: "A cozy bedroom with a locked door"
    - kitchen: "A small kitchen with a window"

  items:
    - key: "A rusty old key"
    - door: "A heavy wooden door"

  initial:
    player: bedroom
    key: kitchen
    door: bedroom (closed, locked)

  connections:
    - bedroom -> kitchen (north)

  goal: player in kitchen
```

**Converter**: `yaml_to_instance.py` translates to full JSON instance

### 3.2 Interactive Authoring CLI

**Tool**: `adventuregame/author.py`

```bash
$ python author.py create
Adventure Name: The Lost Treasure
How many rooms? 3
Room 1 name: cave_entrance
Room 1 description: A dark cave entrance
[... interactive prompts ...]

Adventure created: adventures/the_lost_treasure.json
Test with: python play_adventure.py --file adventures/the_lost_treasure.json
```

### 3.3 Web-Based Adventure Editor (Stretch Goal)

**Tech**: Simple Flask/FastAPI app

Features:
- Visual room layout (drag-and-drop connections)
- Item placement via UI
- Live validation
- Export to JSON
- Test play in browser

---

## Roadmap: Phase 4 - Metadata Dashboard

**Deliverable**: Rich terminal UI for gameplay with live stats.

### 4.1 TUI Player with Stats Panel

**Tech**: Use `rich` library for terminal UI

```
┌─────────────────── GAME ───────────────────┐
│ A cozy bedroom with a bed and a door.     │
│ You can see:                               │
│   - door (closed, locked)                  │
│ Exits: north                               │
└────────────────────────────────────────────┘

┌─────────────── METADATA ──────────────────┐
│ Goals: [1/3] ⬜⬜⬛                         │
│ Inventory: [key]                           │
│ Turn: 5/10                                 │
│ Last Action: ✓ take key                   │
└────────────────────────────────────────────┘

> unlock door with key
```

### 4.2 Action Log Viewer

Show full action resolution trace:
```
Turn 5: unlock door with key
  ✓ Precondition: at(player, bedroom)
  ✓ Precondition: at(door, bedroom)
  ✓ Precondition: locked(door)
  ✓ Precondition: in(key, inventory)
  → Effect: -locked(door)
  Status: SUCCESS
```

---

## Roadmap: Phase 5 - LLM Comparison Mode

**Deliverable**: Watch an LLM play your custom adventure.

### 5.1 AI Player Mode

```bash
# Watch GPT-4 play your adventure
python play_adventure.py --ai gpt-4 --file my_adventure.json

# Compare multiple models
python play_adventure.py --compare gpt-4,claude-3,llama-3
```

**Shows**:
- Model's action choices in real-time
- Reasoning (if available via chain-of-thought)
- Success rate on your custom puzzle

### 5.2 Difficulty Tuning

Based on LLM performance:
```bash
# Test difficulty
python test_difficulty.py my_adventure.json

Results:
  GPT-4:       Success in 5 turns (optimal: 3)
  Claude-3:    Success in 4 turns
  Llama-3:     Failed (turn limit)

Difficulty Rating: HARD (33% success rate)
Suggestions:
  - Increase max_turns from 10 to 15
  - Add hint about key location
```

---

## Implementation Priority

### High Priority (Do First)
1. ✅ **Phase 1.1**: Standalone player script
2. ✅ **Phase 2.1-2.2**: Manual authoring template + guide
3. ✅ **Phase 2.4**: Adventure validator

### Medium Priority
4. **Phase 1.2**: Real-time metadata display
5. **Phase 2.3**: Action library documentation
6. **Phase 3.1**: YAML format support

### Low Priority (Nice to Have)
7. **Phase 1.3**: Save/load
8. **Phase 3.2**: Interactive authoring CLI
9. **Phase 4**: TUI dashboard
10. **Phase 5**: AI player comparison

---

## Quick Start Implementation Guide

### Step 1: Create Standalone Player (2-3 hours)

**File**: `adventuregame/play_adventure.py`

Minimal working version:
```python
import json
import sys
from if_wrapper import AdventureIFInterpreter

# Load instance
with open('adventuregame/in/instances.json') as f:
    data = json.load(f)
    instance = data['experiments'][0]['game_instances'][0]

# Initialize interpreter (CHALLENGE: fix path dependencies)
game_path = "adventuregame"  # May need adjustment
interpreter = AdventureIFInterpreter(game_path, instance)

# Game loop
print(instance['prompt'])
print("\n" + interpreter.get_full_room_desc())

while True:
    action = input("\n> ")
    if action.lower() in ['quit', 'exit']:
        break

    result = interpreter.process_action(action)
    print(result['feedback'])

    if result.get('goal_achieved'):
        print("\n🎉 GOAL ACHIEVED!")
        break
```

### Step 2: Create Simple Template (30 minutes)

Copy existing instance, simplify, add comments:
```json
{
  "name": "Simple Escape Room",
  "game_instances": [
    {
      "game_id": "simple_1",
      "variant": "basic",
      "prompt": "Find the key and escape!",
      "initial_state": [
        "at(player,room1)",  // Player starts in room1
        "at(key,room2)",     // Key is in room2
        // ... etc
      ],
      // ... rest of structure
    }
  ]
}
```

### Step 3: Write Authoring Guide (2 hours)

See **Phase 2.2** outline above.

---

## Challenges & Solutions

### Challenge 1: IF Interpreter Coupling

**Problem**: `AdventureIFInterpreter` expects clemgame directory structure.

**Solution**: Refactor constructor to accept optional paths:
```python
def __init__(self, game_path=None, game_instance=None, standalone=False):
    if standalone:
        # Use relative paths, skip clemgame resource loading
        self.resources_path = "./resources"
    else:
        # Use clemgame GameResourceLocator
        self.resources_path = GameResourceLocator(game_path).get_resources()
```

### Challenge 2: Action Definitions Complexity

**Problem**: PDDL action definitions are verbose and technical.

**Solution**:
- Provide pre-built action libraries (already exists in `resources/definitions/`)
- Reference by filename in manual adventures
- Create "action pack" bundles: `basic_home.json`, `fantasy_dungeon.json`

### Challenge 3: Goal Solvability

**Problem**: Manually authored adventures might be unsolvable.

**Solution**:
- Validator checks basic constraints
- Optional: Run Clingo solver to verify solvability
- Provide "test mode" that shows optimal solution

---

## Example: End-to-End Custom Adventure

### 1. Create `my_escape_room.json`

```json
{
  "name": "Escape Room",
  "game_instances": [{
    "game_id": "escape_1",
    "variant": "basic",
    "prompt": "You're locked in a room. Find the key in the drawer and escape!",

    "initial_state": [
      "at(player,bedroom)",
      "at(drawer,bedroom)",
      "at(key,bedroom)",
      "at(door,bedroom)",
      "in(key,drawer)",
      "closed(drawer)",
      "closed(door)",
      "locked(door)",
      "exit(bedroom,hallway,north)"
    ],

    "goal_state": ["at(player,hallway)"],

    "max_turns": 10,
    "optimal_turns": 4,

    "action_definitions": "@import:resources/definitions/basic_actions_v2.json",
    "room_definitions": "@import:resources/definitions/home_rooms.json",
    "entity_definitions": "@import:resources/definitions/home_entities.json",
    "domain_definitions": "@import:resources/definitions/home_domain.json"
  }]
}
```

### 2. Validate

```bash
$ python adventuregame/validate_adventure.py my_escape_room.json
✓ JSON syntax valid
✓ All required fields present
✓ State facts valid
✓ Actions/rooms/entities resolved
✓ Goal is achievable (Clingo solver: 4 turns)

Adventure is ready to play!
```

### 3. Play

```bash
$ python adventuregame/play_adventure.py --file my_escape_room.json

You're locked in a room. Find the key in the drawer and escape!

A bedroom. You can see:
  - drawer (closed)
  - door (closed, locked)
Exits: north

> open drawer
You open the drawer. Inside you see:
  - key

> take key
You take the key.

> unlock door with key
You unlock the door.

> open door
You open the door.

> go north
You move north to the hallway.

🎉 GOAL ACHIEVED!
Turns: 5 (Optimal: 4)
```

### 4. Test with LLM

```bash
$ python adventuregame/play_adventure.py --ai gpt-4 --file my_escape_room.json

[Turn 1] GPT-4: examine room
...
[Turn 4] GPT-4: go north

🎉 GOAL ACHIEVED!
Model performance: 4 turns (optimal!)
```

---

## Next Steps

1. **Review this roadmap** with project stakeholders
2. **Prioritize phases** based on immediate needs
3. **Start with Phase 1.1**: Get standalone player working
4. **Iterate**: Build minimal versions, gather feedback
5. **Document as you go**: Keep authoring guide updated

---

## Questions to Answer

Before implementation:

1. **Target Audience**: Who will author adventures? (Researchers? Educators? Hobbyists?)
2. **Scope**: Do we need full Clingo solver integration for manual adventures, or just validation?
3. **UI**: Terminal-only, or also web interface?
4. **Distribution**: Standalone tool, or keep integrated with clemgame framework?

---

**Document Version**: 1.0
**Last Updated**: 2025-11-12
**Author**: Claude (via AdventureClemGame investigation)
