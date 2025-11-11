"""
String utility functions for AdventureGame.

This module contains common string manipulation functions used throughout
the codebase, particularly for entity name normalization and formatting.
"""

from typing import List, Tuple, Any


def strip_trailing_digits(text: str) -> str:
    """
    Remove trailing digits from a string.

    Args:
        text: Input string that may have trailing digits

    Returns:
        String with trailing digits removed

    Example:
        >>> strip_trailing_digits("orange1")
        'orange'
        >>> strip_trailing_digits("table23")
        'table'
        >>> strip_trailing_digits("sword")
        'sword'
    """
    return text.rstrip("0123456789")


def normalize_entity_name(name: str) -> str:
    """
    Normalize entity name by removing trailing digits.

    This is commonly used to get the base name of entities that
    have numeric suffixes (e.g., "orange1" -> "orange").

    Args:
        name: Entity name that may have trailing digit suffix

    Returns:
        Normalized entity name without trailing digits

    Example:
        >>> normalize_entity_name("cupboard1")
        'cupboard'
        >>> normalize_entity_name("player")
        'player'
    """
    return strip_trailing_digits(name)


def format_predicate_list(predicates: List[Tuple[str, ...]], delimiter: str = ", ") -> str:
    """
    Format a list of predicates (tuples) into a readable string.

    Args:
        predicates: List of predicate tuples
        delimiter: String to use between predicates (default: ", ")

    Returns:
        Formatted string representation of predicates

    Example:
        >>> predicates = [('at', 'player', 'kitchen'), ('holding', 'player', 'orange')]
        >>> format_predicate_list(predicates)
        'at(player,kitchen), holding(player,orange)'
    """
    formatted = []
    for pred in predicates:
        if len(pred) == 0:
            continue
        pred_name = pred[0]
        pred_args = pred[1:]
        formatted.append(f"{pred_name}({','.join(pred_args)})")
    return delimiter.join(formatted)


def format_fact_tuple(fact: Tuple[str, ...]) -> str:
    """
    Format a single fact tuple into a string representation.

    Args:
        fact: Tuple representing a fact (predicate_name, arg1, arg2, ...)

    Returns:
        String representation of the fact

    Example:
        >>> format_fact_tuple(('at', 'player', 'kitchen'))
        'at(player,kitchen)'
        >>> format_fact_tuple(('open', 'door1'))
        'open(door1)'
    """
    if len(fact) == 0:
        return ""
    if len(fact) == 1:
        return f"{fact[0]}()"
    pred_name = fact[0]
    pred_args = fact[1:]
    return f"{pred_name}({','.join(pred_args)})"


def capitalize_first(text: str) -> str:
    """
    Capitalize the first letter of a string.

    Args:
        text: Input string

    Returns:
        String with first letter capitalized

    Example:
        >>> capitalize_first("hello world")
        'Hello world'
    """
    if not text:
        return text
    return text[0].upper() + text[1:]


def format_list_with_and(items: List[str]) -> str:
    """
    Format a list of strings with commas and 'and' before the last item.

    Args:
        items: List of strings to format

    Returns:
        Formatted string

    Example:
        >>> format_list_with_and(['apple', 'orange', 'banana'])
        'apple, orange and banana'
        >>> format_list_with_and(['apple', 'orange'])
        'apple and orange'
        >>> format_list_with_and(['apple'])
        'apple'
    """
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])} and {items[-1]}"


def sanitize_string(text: str) -> str:
    """
    Remove extra whitespace and normalize a string.

    Args:
        text: Input string

    Returns:
        Sanitized string with normalized whitespace

    Example:
        >>> sanitize_string("  hello   world  ")
        'hello world'
    """
    return " ".join(text.split())
