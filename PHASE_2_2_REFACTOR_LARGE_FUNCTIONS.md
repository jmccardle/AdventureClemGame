# Phase 2.2: Refactor Large Functions - Detailed Plan

**Status:** Deferred
**Priority:** High
**Estimated Effort:** 5 days
**Dependencies:** Phase 2.1 (completed)

---

## Overview

This document outlines the detailed plan for refactoring large, complex functions in the AdventureGame codebase. The primary goal is to break down functions exceeding 100 lines into smaller, more maintainable units while preserving all functionality.

---

## Success Criteria

- ✅ No functions exceed 100 lines in main production files
- ✅ Each extracted helper function has a single, clear responsibility
- ✅ All tests pass after refactoring
- ✅ Code coverage maintained or improved
- ✅ No changes to external API/behavior

---

## Target Functions for Refactoring

### 1. `if_wrapper.py::resolve_action()` (362 lines → target: ~80 lines)

**Current Location:** `adventuregame/if_wrapper.py:2381-2743`

**Current Responsibilities:**
- Parse action dictionary structure
- Validate action exists in action types
- Check action preconditions
- Apply action effects
- Handle "new word" actions (special replacement logic)
- Generate player feedback
- Update world state
- Track action failures
- Handle edge cases (empty actions, unknown actions)

**Proposed Refactoring:**

```python
def resolve_action(self, action_dict, ...):
    """Main action resolution orchestrator (target: ~80 lines)."""

    # Step 1: Validate action structure
    if not self._validate_action_structure(action_dict):
        return self._create_error_response("Invalid action structure")

    # Step 2: Handle special action types
    if self._is_new_word_action(action_dict):
        return self._resolve_new_word_action(action_dict)

    # Step 3: Get action definition
    action_def = self._get_action_definition(action_dict)
    if action_def is None:
        return self._create_unknown_action_response(action_dict)

    # Step 4: Check preconditions
    precondition_result = self._check_action_preconditions(action_dict, action_def)
    if not precondition_result.satisfied:
        return self._create_precondition_failure_response(precondition_result)

    # Step 5: Apply effects
    effect_result = self._apply_action_effects(action_dict, action_def)

    # Step 6: Generate feedback
    feedback = self._generate_action_feedback(action_dict, effect_result)

    # Step 7: Update tracking
    self._update_action_tracking(action_dict, effect_result)

    return feedback


def _validate_action_structure(self, action_dict) -> bool:
    """
    Validate that action dictionary has required structure.

    Args:
        action_dict: Action dictionary to validate

    Returns:
        True if valid, False otherwise

    Target: ~20 lines
    """
    # Extract current validation logic from resolve_action lines 2390-2410
    pass


def _is_new_word_action(self, action_dict) -> bool:
    """
    Check if action is a "new word" action requiring special handling.

    Args:
        action_dict: Action dictionary to check

    Returns:
        True if new word action, False otherwise

    Target: ~10 lines
    """
    # Extract from lines 2420-2430
    pass


def _resolve_new_word_action(self, action_dict):
    """
    Handle new word action resolution with replacement logic.

    Args:
        action_dict: New word action dictionary

    Returns:
        Action resolution result

    Target: ~40 lines
    """
    # Extract from lines 2430-2480
    pass


def _get_action_definition(self, action_dict):
    """
    Retrieve action definition from action types.

    Args:
        action_dict: Action dictionary

    Returns:
        Action definition dict or None if not found

    Target: ~15 lines
    """
    # Extract from lines 2490-2505
    pass


def _create_unknown_action_response(self, action_dict) -> dict:
    """
    Create response for unknown/undefined actions.

    Args:
        action_dict: Action dictionary

    Returns:
        Error response dictionary

    Target: ~20 lines
    """
    # Extract from lines 2510-2530
    pass


def _check_action_preconditions(self, action_dict, action_def):
    """
    Check if all preconditions for action are satisfied.

    Args:
        action_dict: Action dictionary
        action_def: Action definition

    Returns:
        PreconditionResult namedtuple with (satisfied, failed_conditions, bindings)

    Target: ~50 lines
    """
    # Extract from lines 2540-2590
    # This is already a complex function - may need further sub-extraction
    pass


def _create_precondition_failure_response(self, precondition_result) -> dict:
    """
    Create response when preconditions fail.

    Args:
        precondition_result: PreconditionResult from check

    Returns:
        Failure response dictionary

    Target: ~25 lines
    """
    # Extract from lines 2595-2620
    pass


def _apply_action_effects(self, action_dict, action_def):
    """
    Apply action effects to world state.

    Args:
        action_dict: Action dictionary
        action_def: Action definition

    Returns:
        EffectResult namedtuple with (state_changes, added_facts, removed_facts)

    Target: ~60 lines
    """
    # Extract from lines 2625-2685
    # This is complex - may benefit from helper for forall/when constructs
    pass


def _generate_action_feedback(self, action_dict, effect_result) -> dict:
    """
    Generate player-facing feedback for action.

    Args:
        action_dict: Action dictionary
        effect_result: Result of applying effects

    Returns:
        Feedback dictionary with message and metadata

    Target: ~40 lines
    """
    # Extract from lines 2690-2730
    pass


def _update_action_tracking(self, action_dict, effect_result):
    """
    Update internal tracking for action execution.

    Args:
        action_dict: Action dictionary
        effect_result: Result of applying effects

    Target: ~20 lines
    """
    # Extract from lines 2735-2743
    pass
```

**Testing Strategy:**
1. Add unit tests for each extracted function
2. Use existing integration tests to verify overall behavior
3. Test edge cases: empty actions, unknown actions, precondition failures
4. Verify new word actions still work correctly

**Acceptance Criteria:**
- Main `resolve_action()` function is ≤100 lines
- Each helper function is ≤60 lines
- All existing tests pass
- No behavior changes

---

### 2. `master.py::compute_scores()` (282 lines → target: ~60 lines)

**Current Location:** `adventuregame/master.py:459-741`

**Current Responsibilities:**
- Extract episode metadata (turns, actions, etc.)
- Compute turn-level metrics
- Compute episode-level metrics (success, goal achievement)
- Compute planning metrics (for 'plan' variant)
- Compute exploration metrics (epistemic/pragmatic actions)
- Calculate action failure statistics
- Compute efficiency metrics (turns over par, turn ratio)
- Handle edge cases (aborted episodes, loop detection)

**Proposed Refactoring:**

```python
def compute_scores(self, episode_interactions: Dict) -> None:
    """
    Compute all episode scores and metrics.

    Orchestrates metric computation and aggregation.
    Target: ~60 lines
    """
    # Extract episode metadata
    metadata = self._extract_episode_metadata(episode_interactions)

    # Compute different metric categories
    turn_metrics = self._compute_turn_metrics(episode_interactions, metadata)
    episode_metrics = self._compute_episode_metrics(episode_interactions, metadata)
    planning_metrics = self._compute_planning_metrics(episode_interactions, metadata)
    exploration_metrics = self._compute_exploration_metrics(episode_interactions, metadata)

    # Combine all metrics
    all_metrics = {
        **turn_metrics,
        **episode_metrics,
        **planning_metrics,
        **exploration_metrics,
    }

    # Log metrics to episode
    for metric_name, metric_value in all_metrics.items():
        self.log_episode_score(metric_name, metric_value)


def _extract_episode_metadata(self, episode_interactions: Dict) -> Dict:
    """
    Extract basic metadata from episode interactions.

    Args:
        episode_interactions: Episode interaction data

    Returns:
        Dict with metadata: num_turns, game_finished, loop_aborted, etc.

    Target: ~30 lines
    """
    # Extract from lines 465-495
    pass


def _compute_turn_metrics(self, episode_interactions: Dict, metadata: Dict) -> Dict:
    """
    Compute per-turn aggregated metrics.

    Args:
        episode_interactions: Episode interaction data
        metadata: Episode metadata

    Returns:
        Dict with turn metrics: turns_taken, actions_attempted, etc.

    Target: ~40 lines
    """
    # Extract from lines 500-540
    pass


def _compute_episode_metrics(self, episode_interactions: Dict, metadata: Dict) -> Dict:
    """
    Compute episode-level success/failure metrics.

    Args:
        episode_interactions: Episode interaction data
        metadata: Episode metadata

    Returns:
        Dict with episode metrics: BENCH_SCORE, achieved_goal_ratio, etc.

    Target: ~60 lines
    """
    # Extract from lines 545-605
    # Includes goal achievement calculation
    # Includes efficiency metrics (turns_over_par, turn_ratio)
    pass


def _compute_planning_metrics(self, episode_interactions: Dict, metadata: Dict) -> Dict:
    """
    Compute planning-specific metrics (for 'plan' variant).

    Args:
        episode_interactions: Episode interaction data
        metadata: Episode metadata

    Returns:
        Dict with planning metrics: plan_adherence, plan_updates, etc.
        Returns empty dict if not planning variant.

    Target: ~50 lines
    """
    # Extract from lines 610-660
    # Only applicable to 'plan' variant
    pass


def _compute_exploration_metrics(self, episode_interactions: Dict, metadata: Dict) -> Dict:
    """
    Compute exploration behavior metrics.

    Args:
        episode_interactions: Episode interaction data
        metadata: Episode metadata

    Returns:
        Dict with exploration metrics: epistemic_actions, pragmatic_actions,
        entity_knowledge, etc.

    Target: ~70 lines
    """
    # Extract from lines 665-735
    # Categorizes actions by type
    # Tracks entity knowledge gain
    pass


def _compute_action_failure_stats(self, episode_interactions: Dict) -> Dict:
    """
    Compute detailed action failure statistics.

    Args:
        episode_interactions: Episode interaction data

    Returns:
        Dict with failure stats by category and phase

    Target: ~40 lines
    """
    # Extract failure categorization logic
    # May be called from _compute_episode_metrics
    pass
```

**Testing Strategy:**
1. Create test episodes with known metrics
2. Verify each metric category independently
3. Test edge cases: empty episodes, aborted episodes, loop detection
4. Verify planning metrics only computed for 'plan' variant
5. Ensure all original metrics are still computed

**Acceptance Criteria:**
- Main `compute_scores()` function is ≤70 lines
- Each helper function is ≤70 lines
- All computed metrics match pre-refactoring values
- No regression in scoring functionality

---

### 3. `if_wrapper.py::run_events()` (262 lines → target: ~60 lines)

**Current Location:** `adventuregame/if_wrapper.py:2090-2352`

**Current Responsibilities:**
- Iterate through event types
- Check event preconditions
- Apply event effects
- Handle conditional events (when clauses)
- Handle forall constructs in events
- Track event triggering
- Generate event feedback
- Update world state based on events

**Proposed Refactoring:**

```python
def run_events(self):
    """
    Check and trigger all applicable events.

    Target: ~60 lines
    """
    triggered_events = []

    for event_type, event_def in self.event_types.items():
        # Check if event should trigger
        if self._should_trigger_event(event_type, event_def):
            # Apply event effects
            result = self._trigger_event(event_type, event_def)
            triggered_events.append((event_type, result))

            # Log event triggering
            logger.debug("Event triggered: %s", event_type)

    # Process any cascading effects
    if triggered_events:
        self._process_event_cascade(triggered_events)

    return triggered_events


def _should_trigger_event(self, event_type: str, event_def: Dict) -> bool:
    """
    Check if event preconditions are satisfied.

    Args:
        event_type: Event type identifier
        event_def: Event definition dict

    Returns:
        True if event should trigger, False otherwise

    Target: ~50 lines
    """
    # Extract precondition checking from lines 2100-2150
    # Reuse check_conditions logic where possible
    pass


def _trigger_event(self, event_type: str, event_def: Dict):
    """
    Apply event effects to world state.

    Args:
        event_type: Event type identifier
        event_def: Event definition dict

    Returns:
        Event result with state changes

    Target: ~60 lines
    """
    # Extract from lines 2155-2215
    # Handle effect application
    pass


def _handle_event_forall(self, event_def: Dict, forall_body: List):
    """
    Handle forall constructs in event effects.

    Args:
        event_def: Event definition
        forall_body: Forall body to process

    Returns:
        List of effect results

    Target: ~40 lines
    """
    # Extract from lines 2220-2260
    pass


def _handle_event_conditional(self, event_def: Dict, when_clause: Dict):
    """
    Handle conditional (when) clauses in events.

    Args:
        event_def: Event definition
        when_clause: When clause to evaluate

    Returns:
        Conditional result

    Target: ~35 lines
    """
    # Extract from lines 2265-2300
    pass


def _process_event_cascade(self, triggered_events: List):
    """
    Handle cascading effects from triggered events.

    Some events may trigger other events - process these chains.

    Args:
        triggered_events: List of (event_type, result) tuples

    Target: ~30 lines
    """
    # Extract cascading logic from lines 2305-2335
    pass
```

**Testing Strategy:**
1. Create test scenarios with various event types
2. Test conditional events (when clauses)
3. Test forall constructs in events
4. Verify event cascading works correctly
5. Test event/action interaction

**Acceptance Criteria:**
- Main `run_events()` function is ≤70 lines
- Each helper function is ≤60 lines
- All event triggering behavior preserved
- No regression in event handling

---

### 4. `if_wrapper.py::check_conditions()` (260 lines → target: ~50 lines)

**Current Location:** `adventuregame/if_wrapper.py:1580-1840`

**Current Responsibilities:**
- Validate condition structure
- Check different condition types: and, or, not, forall, when
- Evaluate numeric comparisons (=, >, >=, <, <=)
- Check predicate satisfaction
- Handle variable bindings
- Handle nested conditions
- Return satisfaction results

**Proposed Refactoring:**

```python
def check_conditions(self, conditions: List, bindings: Dict = None):
    """
    Check if conditions are satisfied in current state.

    Args:
        conditions: List of condition dicts/tuples
        bindings: Variable bindings (if any)

    Returns:
        ConditionResult with (satisfied, failed_conditions, variable_bindings)

    Target: ~50 lines
    """
    if bindings is None:
        bindings = {}

    satisfied = True
    failed_conditions = []

    for condition in conditions:
        # Dispatch to appropriate handler based on condition type
        if isinstance(condition, dict):
            result = self._check_complex_condition(condition, bindings)
        elif isinstance(condition, tuple):
            result = self._check_predicate_condition(condition, bindings)
        else:
            logger.warning("Unknown condition type: %s", type(condition))
            result = ConditionResult(False, [condition], bindings)

        if not result.satisfied:
            satisfied = False
            failed_conditions.extend(result.failed_conditions)

        # Update bindings from result
        bindings.update(result.bindings)

    return ConditionResult(satisfied, failed_conditions, bindings)


def _check_complex_condition(self, condition: Dict, bindings: Dict):
    """
    Check complex condition (and, or, not, forall, when, comparisons).

    Args:
        condition: Condition dictionary
        bindings: Variable bindings

    Returns:
        ConditionResult

    Target: ~40 lines
    """
    # Dispatch based on keys in condition dict
    if "and" in condition:
        return self._check_and_condition(condition["and"], bindings)
    elif "or" in condition:
        return self._check_or_condition(condition["or"], bindings)
    elif "not" in condition:
        return self._check_not_condition(condition["not"], bindings)
    elif "forall" in condition:
        return self._check_forall_condition(condition, bindings)
    elif "when" in condition:
        return self._check_when_condition(condition, bindings)
    elif "num_comp" in condition:
        return self._check_numeric_comparison(condition, bindings)
    else:
        logger.warning("Unknown complex condition: %s", condition)
        return ConditionResult(False, [condition], bindings)


def _check_and_condition(self, conditions: List, bindings: Dict):
    """Check AND condition - all must be satisfied."""
    # Extract from lines 1620-1650
    # Target: ~25 lines
    pass


def _check_or_condition(self, conditions: List, bindings: Dict):
    """Check OR condition - at least one must be satisfied."""
    # Extract from lines 1655-1685
    # Target: ~25 lines
    pass


def _check_not_condition(self, condition, bindings: Dict):
    """Check NOT condition - must not be satisfied."""
    # Extract from lines 1690-1710
    # Target: ~20 lines
    pass


def _check_forall_condition(self, condition: Dict, bindings: Dict):
    """Check FORALL condition - must hold for all instances."""
    # Extract from lines 1715-1760
    # Target: ~45 lines
    pass


def _check_when_condition(self, condition: Dict, bindings: Dict):
    """Check WHEN (conditional) condition."""
    # Extract from lines 1765-1790
    # Target: ~25 lines
    pass


def _check_numeric_comparison(self, condition: Dict, bindings: Dict):
    """
    Check numeric comparison condition (=, >, >=, <, <=).

    Args:
        condition: Condition dict with num_comp key
        bindings: Variable bindings

    Returns:
        ConditionResult

    Target: ~40 lines
    """
    # Extract from lines 1795-1835
    pass


def _check_predicate_condition(self, predicate: Tuple, bindings: Dict):
    """
    Check simple predicate condition against world state.

    Args:
        predicate: Predicate tuple (pred_name, arg1, arg2, ...)
        bindings: Variable bindings

    Returns:
        ConditionResult

    Target: ~30 lines
    """
    # Extract basic predicate checking
    # Apply variable bindings
    # Check against current state
    pass
```

**Helper Data Structures:**

```python
from collections import namedtuple

ConditionResult = namedtuple('ConditionResult',
                             ['satisfied', 'failed_conditions', 'bindings'])
```

**Testing Strategy:**
1. Test each condition type independently
2. Test nested conditions (and of ors, etc.)
3. Test variable binding propagation
4. Test numeric comparisons
5. Test forall with various quantifications

**Acceptance Criteria:**
- Main `check_conditions()` function is ≤60 lines
- Each condition type handler is ≤50 lines
- All condition evaluation behavior preserved
- Variable bindings work correctly

---

### 5. `if_wrapper.py::get_entity_desc()` (163 lines → target: ~40 lines)

**Current Location:** `adventuregame/if_wrapper.py:1245-1408`

**Current Responsibilities:**
- Get base entity description
- Check entity properties (open/closed, on/off, etc.)
- List entity contents
- List entities with relation "on" the target
- Format descriptions with proper grammar
- Handle special cases (containers, supporters, etc.)
- Track entity visibility

**Proposed Refactoring:**

```python
def get_entity_desc(self, entity_id: str, include_contents: bool = True) -> str:
    """
    Get formatted description of entity.

    Args:
        entity_id: Entity identifier
        include_contents: Whether to include contents/on-items

    Returns:
        Formatted description string

    Target: ~40 lines
    """
    if entity_id not in self.entity_types:
        return f"Unknown entity: {entity_id}"

    # Build description parts
    base_desc = self._get_base_entity_desc(entity_id)
    properties_desc = self._get_entity_properties_desc(entity_id)

    # Combine base + properties
    full_desc = f"{base_desc}{properties_desc}"

    # Add contents/on-items if requested
    if include_contents:
        contents_desc = self._get_entity_contents_desc(entity_id)
        if contents_desc:
            full_desc += f" {contents_desc}"

    return full_desc


def _get_base_entity_desc(self, entity_id: str) -> str:
    """
    Get base description from entity definition.

    Args:
        entity_id: Entity identifier

    Returns:
        Base description string

    Target: ~20 lines
    """
    # Extract from lines 1250-1270
    # Get entity name/description from definition
    pass


def _get_entity_properties_desc(self, entity_id: str) -> str:
    """
    Get description of entity properties (open/closed, on/off, etc.).

    Args:
        entity_id: Entity identifier

    Returns:
        Properties description string (may be empty)

    Target: ~40 lines
    """
    # Extract from lines 1275-1315
    # Check for 'open', 'closed', 'on', 'off' predicates
    # Format property descriptions
    pass


def _get_entity_contents_desc(self, entity_id: str) -> str:
    """
    Get description of entity contents and items "on" entity.

    Args:
        entity_id: Entity identifier

    Returns:
        Contents description string (may be empty)

    Target: ~60 lines
    """
    # Extract from lines 1320-1380
    # Find items "in" or "on" this entity
    # Format with proper grammar (commas, "and")
    pass


def _format_entity_list(self, entity_ids: List[str]) -> str:
    """
    Format list of entity IDs as natural language.

    Args:
        entity_ids: List of entity identifiers

    Returns:
        Formatted string like "apple, orange and banana"

    Target: ~20 lines
    """
    # Extract list formatting logic
    # Could use utils.string_utils.format_list_with_and()
    pass
```

**Testing Strategy:**
1. Test basic entity descriptions
2. Test entities with properties (open/closed, etc.)
3. Test containers with contents
4. Test supporters with items on them
5. Test empty containers/supporters
6. Test nested containment

**Acceptance Criteria:**
- Main `get_entity_desc()` function is ≤50 lines
- Each helper function is ≤60 lines
- All description formats preserved
- Grammar remains natural

---

### 6. `resources/clingo_adventures2-2.py::generate_adventures()` (485 lines → target: ~80 lines)

**Current Location:** `adventuregame/resources/clingo_adventures2-2.py:1500-1985`

**Current Responsibilities:**
- Load adventure type configurations
- Load PDDL definitions (rooms, entities, actions, domains)
- Generate initial world states with Clingo
- Generate goal sets
- Solve for optimal solutions with Clingo
- Validate solutions
- Combine states + goals + solutions
- Write adventure JSON files
- Handle multiple adventure types
- Handle special cases (potion brewing, new words, etc.)

**Proposed Refactoring:**

```python
def generate_adventures(adventure_types: List[str], num_adventures: int):
    """
    Generate adventure instances using Clingo ASP solver.

    Args:
        adventure_types: List of adventure type names to generate
        num_adventures: Number of adventures to generate per type

    Target: ~80 lines
    """
    for adventure_type in adventure_types:
        logger.info("Generating %d adventures for type: %s",
                   num_adventures, adventure_type)

        # Load configuration for this adventure type
        config = _load_adventure_type_config(adventure_type)

        # Load PDDL definitions
        definitions = _load_pddl_definitions(config)

        # Generate adventures
        for i in range(num_adventures):
            logger.info("Generating adventure %d/%d", i+1, num_adventures)

            # Generate initial state
            initial_state = _generate_initial_state(config, definitions)

            # Generate goals
            goals = _generate_goals(config, definitions, initial_state)

            # Solve for optimal solution
            solution = _solve_adventure(config, definitions, initial_state, goals)

            if solution is not None:
                # Combine and save
                adventure = _create_adventure_dict(initial_state, goals, solution)
                _save_adventure(adventure, adventure_type, i)
            else:
                logger.warning("No solution found for adventure %d", i)


def _load_adventure_type_config(adventure_type: str) -> Dict:
    """Load configuration for adventure type."""
    # Extract from lines 1510-1540
    # Target: ~30 lines
    pass


def _load_pddl_definitions(config: Dict) -> Dict:
    """Load all PDDL definitions (rooms, entities, actions, domains)."""
    # Extract from lines 1545-1610
    # Target: ~60 lines
    pass


def _generate_initial_state(config: Dict, definitions: Dict) -> Set:
    """Generate initial world state using Clingo."""
    # Extract from lines 1615-1720
    # Target: ~100 lines (complex - may need sub-extraction)
    pass


def _generate_goals(config: Dict, definitions: Dict, initial_state: Set) -> Set:
    """Generate goal set for adventure."""
    # Extract from lines 1725-1800
    # Target: ~70 lines
    pass


def _solve_adventure(config: Dict, definitions: Dict,
                    initial_state: Set, goals: Set):
    """
    Solve adventure using Clingo to find optimal action sequence.

    Returns optimal solution or None if unsolvable.
    """
    # Extract from lines 1805-1920
    # Target: ~110 lines (complex - may need sub-extraction)
    pass


def _create_adventure_dict(initial_state: Set, goals: Set,
                          solution: List) -> Dict:
    """Combine components into adventure dictionary."""
    # Extract from lines 1925-1955
    # Target: ~30 lines
    pass


def _save_adventure(adventure: Dict, adventure_type: str, index: int):
    """Save adventure to JSON file."""
    # Extract from lines 1960-1985
    # Target: ~25 lines
    pass
```

**Testing Strategy:**
1. Generate small test adventures
2. Verify all adventure types generate successfully
3. Verify solutions are optimal
4. Test special cases (potion brewing, new words)
5. Performance test with larger batches

**Acceptance Criteria:**
- Main `generate_adventures()` function is ≤100 lines
- Most helper functions are ≤70 lines
- All adventure types generate correctly
- Generated adventures are solvable
- No regression in adventure quality

---

## Implementation Guidelines

### General Principles

1. **Single Responsibility:** Each extracted function should do one thing well
2. **Clear Naming:** Function names should clearly describe what they do
3. **Minimal Parameters:** Prefer 3-4 parameters or fewer; use data classes/namedtuples if more needed
4. **Consistent Abstraction Level:** Functions should operate at consistent abstraction levels
5. **Document Intent:** Add docstrings explaining *why*, not just *what*

### Refactoring Process

For each target function:

1. **Analyze:** Read and understand the entire function
2. **Identify Sections:** Mark logical sections/responsibilities
3. **Extract:** Start with easiest extractions (pure functions, no side effects)
4. **Test:** Write/run tests after each extraction
5. **Iterate:** Refine naming and interfaces
6. **Review:** Ensure main function is readable as a high-level algorithm

### Testing Requirements

- ✅ Unit tests for each extracted helper function
- ✅ Integration tests for main function behavior
- ✅ Edge case tests
- ✅ Performance tests (ensure no regression)
- ✅ Coverage maintained or improved

### Code Review Checklist

Before considering refactoring complete:

- [ ] Main function ≤100 lines
- [ ] Helper functions have clear, single responsibilities
- [ ] All functions have docstrings
- [ ] All tests pass
- [ ] No behavior changes (external API unchanged)
- [ ] Code is more readable than before
- [ ] Function names are self-documenting

---

## Priority Ordering

Based on impact and complexity:

1. **High Priority:**
   - `resolve_action()` - Core action processing, touched frequently
   - `compute_scores()` - Critical for evaluation

2. **Medium Priority:**
   - `check_conditions()` - Core logic, reusable
   - `run_events()` - Important but less frequently modified

3. **Lower Priority:**
   - `get_entity_desc()` - Simpler, less critical
   - `generate_adventures()` - Development tool, less critical for runtime

---

## Estimated Effort Breakdown

| Function | Complexity | Est. Hours | Risk |
|----------|-----------|-----------|------|
| resolve_action() | High | 12-16 | Medium |
| compute_scores() | Medium | 8-12 | Low |
| run_events() | Medium | 10-14 | Medium |
| check_conditions() | High | 10-14 | Medium |
| get_entity_desc() | Low | 4-6 | Low |
| generate_adventures() | High | 12-16 | High |
| **Total** | | **56-78 hours** | |

**Total Estimated: 7-10 working days**

---

## Risks and Mitigation

### Risk 1: Breaking Existing Functionality
**Likelihood:** Medium
**Impact:** High
**Mitigation:**
- Comprehensive test coverage before refactoring
- Small, incremental changes
- Continuous testing after each extraction
- Keep git history clean for easy rollback

### Risk 2: Introducing Performance Regressions
**Likelihood:** Low
**Impact:** Medium
**Mitigation:**
- Profile before and after refactoring
- Inline hot paths if necessary
- Use benchmarks for critical functions

### Risk 3: Scope Creep
**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- Stick to the plan
- Don't refactor beyond listed functions
- Defer "nice to have" improvements to future phases

### Risk 4: Time Overruns
**Likelihood:** Medium
**Impact:** Low
**Mitigation:**
- Start with highest priority functions
- Stop when time budget exhausted
- Document remaining work for future

---

## Success Metrics

### Before Phase 2.2:
- Functions >100 lines: **15+**
- Largest function: **485 lines** (generate_adventures)
- Average function length: **~120 lines** (for large functions)
- Code complexity: **High** (deep nesting, many responsibilities)

### After Phase 2.2 (Target):
- Functions >100 lines: **0**
- Largest function: **≤100 lines**
- Average function length: **~50 lines** (for refactored functions)
- Code complexity: **Medium** (clear hierarchy, single responsibilities)

### Quality Improvements:
- ✅ Improved readability
- ✅ Easier testing
- ✅ Easier maintenance
- ✅ Better code organization
- ✅ Reduced cognitive load

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Prioritize functions** based on immediate needs
3. **Set up test coverage** for target functions
4. **Begin with highest priority** (resolve_action or compute_scores)
5. **Iterate through list** one function at a time
6. **Document lessons learned** as you go

---

## References

- Original Roadmap: `CODE_QUALITY_ROADMAP.md`
- Code Quality Report: `CODE_QUALITY_REPORT.md`
- Phase 1 Completion: Commits aec7b3a, 8cd4080
- Related Issues: (to be created)

---

**Document Version:** 1.0
**Created:** 2025-11-11
**Author:** Claude Code
**Status:** Deferred - Awaiting Implementation
