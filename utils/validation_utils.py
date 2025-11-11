"""
Validation utility functions for AdventureGame.

This module contains validation functions for conditions, effects, and game state
used throughout the IF interpreter and game logic.
"""

from typing import Any, Dict, List, Set, Tuple, Union
import logging

logger = logging.getLogger(__name__)


def validate_condition(condition: Any) -> bool:
    """
    Validate that a condition is well-formed.

    Args:
        condition: Condition to validate (can be dict, tuple, or other types)

    Returns:
        True if condition is valid, False otherwise
    """
    if condition is None:
        return False

    if isinstance(condition, dict):
        # For dict conditions, check for required keys
        if "forall" in condition:
            return "body" in condition
        if "when" in condition:
            return len(condition.get("when", [])) > 0
        return True

    if isinstance(condition, (tuple, list)):
        # Tuple/list conditions should have at least a predicate name
        return len(condition) > 0

    return True


def validate_effect(effect: Any) -> bool:
    """
    Validate that an effect is well-formed.

    Args:
        effect: Effect to validate (can be dict, tuple, or other types)

    Returns:
        True if effect is valid, False otherwise
    """
    if effect is None:
        return False

    if isinstance(effect, dict):
        # For dict effects, check for required keys
        if "forall" in effect:
            return "body" in effect
        if "when" in effect:
            return len(effect.get("when", [])) > 0
        return True

    if isinstance(effect, (tuple, list)):
        # Tuple/list effects should have at least a predicate name
        return len(effect) > 0

    return True


def validate_state(state: Set[Tuple], allow_empty: bool = False) -> bool:
    """
    Validate that a game state is well-formed.

    Args:
        state: Set of tuples representing the game state
        allow_empty: Whether to allow empty state (default: False)

    Returns:
        True if state is valid, False otherwise
    """
    if not isinstance(state, set):
        logger.warning("State is not a set: %s", type(state))
        return False

    if not allow_empty and len(state) == 0:
        logger.warning("State is empty")
        return False

    # Validate each fact in the state
    for fact in state:
        if not isinstance(fact, tuple):
            logger.warning("State contains non-tuple fact: %s", fact)
            return False
        if len(fact) == 0:
            logger.warning("State contains empty tuple")
            return False
        # First element should be a string (predicate name)
        if not isinstance(fact[0], str):
            logger.warning("Fact predicate name is not a string: %s", fact[0])
            return False

    return True


def validate_action_dict(action_dict: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that an action dictionary is well-formed.

    Args:
        action_dict: Action dictionary to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(action_dict, dict):
        return False, "Action is not a dictionary"

    if "type" not in action_dict:
        return False, "Action missing 'type' field"

    # Check that type is a string
    if not isinstance(action_dict["type"], str):
        return False, "Action 'type' field is not a string"

    return True, ""


def validate_entity_id(entity_id: str, valid_entities: Set[str]) -> bool:
    """
    Validate that an entity ID exists in the set of valid entities.

    Args:
        entity_id: Entity identifier to validate
        valid_entities: Set of valid entity identifiers

    Returns:
        True if entity ID is valid, False otherwise
    """
    if not isinstance(entity_id, str):
        logger.warning("Entity ID is not a string: %s", entity_id)
        return False

    if entity_id not in valid_entities:
        logger.debug("Entity ID not found in valid entities: %s", entity_id)
        return False

    return True


def validate_predicate_arity(
    predicate: Tuple, expected_arity: Union[int, List[int]]
) -> bool:
    """
    Validate that a predicate has the expected arity (number of arguments).

    Args:
        predicate: Tuple representing a predicate (predicate_name, arg1, arg2, ...)
        expected_arity: Expected number of arguments (can be a list of valid arities)

    Returns:
        True if arity matches, False otherwise
    """
    if not isinstance(predicate, tuple):
        logger.warning("Predicate is not a tuple: %s", predicate)
        return False

    if len(predicate) == 0:
        logger.warning("Predicate is empty tuple")
        return False

    # Actual arity is length - 1 (excluding predicate name)
    actual_arity = len(predicate) - 1

    if isinstance(expected_arity, int):
        return actual_arity == expected_arity
    elif isinstance(expected_arity, list):
        return actual_arity in expected_arity
    else:
        logger.warning("Invalid expected_arity type: %s", type(expected_arity))
        return False


def validate_goal_state(
    current_state: Set[Tuple], goal_state: Set[Tuple]
) -> Tuple[bool, List[Tuple]]:
    """
    Validate whether the current state satisfies the goal state.

    Args:
        current_state: Current game state
        goal_state: Goal state to achieve

    Returns:
        Tuple of (is_satisfied, missing_goals)
    """
    if not validate_state(current_state, allow_empty=False):
        return False, list(goal_state)

    if not validate_state(goal_state, allow_empty=False):
        return False, []

    missing_goals = [goal for goal in goal_state if goal not in current_state]

    return len(missing_goals) == 0, missing_goals


def validate_pddl_definition(definition: str) -> Tuple[bool, str]:
    """
    Validate that a PDDL definition string is non-empty and well-formed.

    Args:
        definition: PDDL definition string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(definition, str):
        return False, "Definition is not a string"

    if not definition.strip():
        return False, "Definition is empty"

    # Basic PDDL syntax check - should have balanced parentheses
    open_count = definition.count("(")
    close_count = definition.count(")")

    if open_count != close_count:
        return False, f"Unbalanced parentheses: {open_count} open, {close_count} close"

    return True, ""
