"""
Message templates for AdventureGame.

This module provides type-safe access to user-facing message templates.
These can be modified for localization or to change the game's tone.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class InitialMessages:
    """Initial/default messages."""

    default_custom_response: str
    initial_response: str


@dataclass(frozen=True)
class Descriptions:
    """Description message templates."""

    room_template: str
    multi_item: str
    two_items: str
    single_item: str
    exit_template: str


@dataclass(frozen=True)
class InventoryMessages:
    """Inventory-related messages."""

    empty: str
    description: str


@dataclass(frozen=True)
class ErrorMessages:
    """Error and failure messages."""

    unknown_command: str
    undefined_action: str
    unknown_entity: str
    cannot_take: str
    cannot_put: str
    no_need_open: str
    cannot_close: str
    unknown_item_type: str
    already_in_inventory: str
    cannot_take_from_inventory: str
    not_in_room: str
    cannot_do_that: str


@dataclass(frozen=True)
class Delimiters:
    """Delimiters for parsing and formatting."""

    plan_delimiter: str
    plan_separator: str
    list_separator: str
    list_last_conjunction: str


@dataclass(frozen=True)
class MessageTemplates:
    """
    Type-safe message templates.

    This configuration contains all user-facing message templates that can be
    modified for localization or to change the game's tone.
    """

    initial: InitialMessages
    descriptions: Descriptions
    inventory: InventoryMessages
    errors: ErrorMessages
    delimiters: Delimiters

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "MessageTemplates":
        """
        Load message templates from JSON file.

        Args:
            config_path: Path to messages.json. If None, uses default location.

        Returns:
            MessageTemplates instance with type-safe access to all messages.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if config_path is None:
            config_path = Path(__file__).parent / "messages.json"

        try:
            with open(config_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Messages config not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {config_path}: {e}")

        # Parse initial messages
        initial_data = data["initial"]
        initial = InitialMessages(
            default_custom_response=initial_data["default_custom_response"],
            initial_response=initial_data["initial_response"],
        )

        # Parse descriptions
        descriptions_data = data["descriptions"]
        descriptions = Descriptions(
            room_template=descriptions_data["room_template"],
            multi_item=descriptions_data["multi_item"],
            two_items=descriptions_data["two_items"],
            single_item=descriptions_data["single_item"],
            exit_template=descriptions_data["exit_template"],
        )

        # Parse inventory messages
        inventory_data = data["inventory"]
        inventory = InventoryMessages(
            empty=inventory_data["empty"],
            description=inventory_data["description"],
        )

        # Parse error messages
        errors_data = data["errors"]
        errors = ErrorMessages(
            unknown_command=errors_data["unknown_command"],
            undefined_action=errors_data["undefined_action"],
            unknown_entity=errors_data["unknown_entity"],
            cannot_take=errors_data["cannot_take"],
            cannot_put=errors_data["cannot_put"],
            no_need_open=errors_data["no_need_open"],
            cannot_close=errors_data["cannot_close"],
            unknown_item_type=errors_data["unknown_item_type"],
            already_in_inventory=errors_data["already_in_inventory"],
            cannot_take_from_inventory=errors_data["cannot_take_from_inventory"],
            not_in_room=errors_data["not_in_room"],
            cannot_do_that=errors_data["cannot_do_that"],
        )

        # Parse delimiters
        delimiters_data = data["delimiters"]
        delimiters = Delimiters(
            plan_delimiter=delimiters_data["plan_delimiter"],
            plan_separator=delimiters_data["plan_separator"],
            list_separator=delimiters_data["list_separator"],
            list_last_conjunction=delimiters_data["list_last_conjunction"],
        )

        return cls(
            initial=initial,
            descriptions=descriptions,
            inventory=inventory,
            errors=errors,
            delimiters=delimiters,
        )

    def get_error_message(self, error_type: str) -> Optional[str]:
        """
        Get an error message by type.

        Args:
            error_type: The error type (e.g., 'unknown_command')

        Returns:
            The error message template, or None if not found

        Example:
            >>> templates = get_message_templates()
            >>> msg = templates.get_error_message('unknown_command')
            >>> print(msg)
            I don't know what you mean.
        """
        return getattr(self.errors, error_type, None)


# Module-level singleton
_message_templates: Optional[MessageTemplates] = None


def get_message_templates(config_path: Optional[Path] = None) -> MessageTemplates:
    """
    Get the global message templates instance.

    Args:
        config_path: Optional path to config file. Only used on first call.

    Returns:
        The global MessageTemplates instance with type-safe access.

    Example:
        >>> templates = get_message_templates()
        >>> print(templates.errors.unknown_command)
        I don't know what you mean.
        >>> print(templates.delimiters.plan_delimiter)
        \\nNext actions:
    """
    global _message_templates
    if _message_templates is None:
        _message_templates = MessageTemplates.load(config_path)
    return _message_templates
