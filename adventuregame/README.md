# AdventureGame
AdventureGame is a Interactive Fiction/Text Adventure clemgame.  
![AdventureGame Simplified](adv_graphic_2_lower.png)
The model is given descriptions of rooms and their contents, along with a task, and interacts with the game world by 
giving action commands. The IF interpreter changes the game world state based on the given action or returns a textual 
failure response if that is not possible.
## Overview
![AdventureGame Flowchart](adv_flowchart_cut.png)
This flowchart shows the core process of AdventureGame. Some connections are omitted for visual clarity, as it's mainly 
showing how the [benchmark](master.py) and [the IF interpreter code](if_wrapper.py) interact. Read files are located in 
the [instances](in) and [resources](resources) directories.
## Instantiation
### Adventure Generation
The Clingo Answer Set solver is used to generate viable initial world state sets based on room and entity definitions. 
These initial world states are used to create goal sets via script. Initial world states and task goal sets are combined 
into adventures. As a last step, Clingo is used to generate the optimal solution for each adventure, using action 
definitions.  
Each step above can output intermediate adventures for manual editing, which was used to create the v1 set of adventures 
with two difficulty levels. Difficulty is based on the accessibility of task objects and the complexity of tasks, which 
are easy to manipulate at an intermediate stage that has generated initial world states and goal sets, but no optimal 
solution yet. An example JSON file of that stage is `adventuregame/resources/adv_source.json`.
### Instances
Different prompts are used for the two game variants, 'basic' and 'planning', to generate two instance sets from the 
same pool of adventures. This means that the initial world state and goal sets are identical between the 'basic' and 
'planning' variants for each difficulty - 'basic-easy' instance 0 has the same adventure as 'planning-easy' instance 0.
## Evaluation
### Metrics
Standard clembench metrics are implemented, metrics listed here are AdventureGame-specific metrics.
#### Turn-level
goal_score: How many goal states have been achieved at this turn. Records **change** of the number of achieved goal 
states, meaning that if less goal states are achieved at this turn compared to the turn before, the number is negative.
#### Episode-level
turns_over_par: Number of turns taken over the optimal number of turns. If adventure is finished as fast as possible, 
this score is 0. Recorded as `NaN` if adventure was not successfully finished.  
turn_ratio: Ratio of turns taken within the possible range of turns. Possible range of turns `turn_range` is the number 
of turns between the optimal number of turns and the turn limit. Calculated as `1 - turns_over_par / turn_range`, so 
that this score is 1.0 if the number of turns taken is the optimal number of turns. Recorded as `NaN` if adventure was 
not successfully finished.  
achieved_goal_ratio: Ratio of achieved goal states by total adventure goal states. 1.0 if all goal states are achieved, 
0.0 if none are achieved. Recorded regardless of successful finish and aborting.  
BENCH_SCORE: `achieved_goal_ratio * 100` to fit expected scale of clemgame quality scores as used in the overall 
clemscore.  
#### Interaction Failures
IF Interaction failures are recorded at each turn. They are divided by two phases, parsing and resolution.  
Parsing phase failures are `lark_exception`, `malformed_command`, `undefined_action_verb`, `undefined_action`, 
`undefined_repr_str`, `manipulating_room` (due to action type not allowing room as argument), `undefined_argument_type`, 
`taking_from_inventory` (due to 'inventory' argument) and `other_room_argument` (due to other room than current location as 
second argument; ie '> take plate from kitchen' while not in kitchen).  
Resolution phase failures are `not_room_type` ('go' action with undefined/non-existing room argument),
`going_to_current_room`, `no_exit_to` (no passage to argument room present), `entity_already_inventory` ('take'-ing
entity that is already in inventory), `thing_arg1_room` (ie '> take kitchen'), `entity_not_accessible`,
`thing_arg2_room` (ie '> put plate in kitchen') and `pre_state_mismatch` (fallback; unfulfilled conditions and edge
cases).

## Development

### Running Tests

The project uses pytest for testing. To run tests:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=adventuregame --cov-report=html

# Run specific test file
pytest tests/test_config_loader.py

# Run with verbose output
pytest -v
```

Coverage reports are generated in HTML format in the `htmlcov/` directory.

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks for automated checks

To run code quality checks:

```bash
# Format code
black adventuregame/
isort adventuregame/

# Run linter
flake8 adventuregame/

# Run type checker
mypy adventuregame/

# Run all pre-commit hooks
pre-commit run --all-files
```

Pre-commit hooks are automatically run before each commit to ensure code quality.

### Logging

The project uses Python's logging module for all output. Logging is configured in `config.json`:

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": null,
    "console": true
  }
}
```

**Logging Levels:**
- `DEBUG`: Detailed diagnostic information (variable dumps, intermediate states)
- `INFO`: General progress and status messages
- `WARNING`: Unexpected but recoverable situations
- `ERROR`: Error conditions that impact functionality
- `CRITICAL`: Critical errors requiring immediate attention

**Usage Example:**
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Processing state: %s", state_dict)
logger.info("Generated %d adventures", count)
logger.warning("Using default config")
logger.error("Failed to parse file: %s", filename)
```

For detailed logging guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md).

### Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on code style, logging best practices, and the contribution process.