"""Custom exception hierarchy for AdventureGame.

This module defines all custom exceptions used throughout the AdventureGame
codebase. Using specific exceptions improves error handling, debugging, and
makes the code's error conditions explicit.
"""


class AdventureGameError(Exception):
    """Base exception for all AdventureGame errors.

    All custom exceptions in the AdventureGame module should inherit from this
    base class. This allows catching all AdventureGame-specific errors with a
    single except clause if needed.
    """

    pass


class PDDLParseError(AdventureGameError):
    """Raised when PDDL parsing fails.

    This includes failures in parsing:
    - PDDL domain definitions
    - PDDL action definitions
    - PDDL event definitions
    - Action input commands
    """

    pass


class ActionResolutionError(AdventureGameError):
    """Raised when an action cannot be resolved.

    This includes failures such as:
    - Action not found in available actions
    - Invalid action parameters
    - Preconditions not met
    - Effect application failures
    """

    pass


class InvalidStateError(AdventureGameError):
    """Raised when game state is invalid or inconsistent.

    This includes situations where:
    - Required state predicates are missing
    - State contains contradictory predicates
    - Entity references are invalid
    - Room connections are malformed
    """

    pass


class ConfigurationError(AdventureGameError):
    """Raised when configuration is invalid or cannot be loaded.

    This includes:
    - Missing required configuration files
    - Invalid JSON in configuration
    - Required configuration keys missing
    - Configuration values out of valid range
    """

    pass


class InstanceGenerationError(AdventureGameError):
    """Raised when instance generation fails.

    This includes:
    - Invalid adventure definitions
    - Template substitution failures
    - Missing required instance components
    - Goal generation failures
    """

    pass


class ClingoSolverError(AdventureGameError):
    """Raised when Clingo ASP solver encounters an error.

    This includes:
    - Unsatisfiable problem (no valid solution)
    - ASP syntax errors in encodings
    - Solver timeout
    - Memory exhaustion
    """

    pass


class EventProcessingError(AdventureGameError):
    """Raised when event processing fails.

    This includes:
    - Event condition checking failures
    - Event effect application failures
    - Event randomization errors
    - Recursive event triggering issues
    """

    pass


class ValidationError(AdventureGameError):
    """Raised when validation checks fail.

    This includes:
    - Predicate validation failures
    - Type checking failures
    - Constraint violations
    - Invariant violations
    """

    pass
