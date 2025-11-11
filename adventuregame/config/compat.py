"""
Compatibility layer for the old config_loader interface.

This module provides backward compatibility with the old monolithic config system
while using the new focused configuration modules under the hood. This allows
code to gradually migrate from the old interface to the new type-safe interface.

Usage:
    Old way (still works):
        from config_loader import get_config
        config = get_config()
        value = config.messages["unknown_command"]

    New way (recommended):
        from adventuregame.config import get_message_templates
        from adventuregame import constants
        templates = get_message_templates()
        value = templates.errors.unknown_command
"""

from typing import Any, Dict, List, Optional

from adventuregame import constants
from adventuregame.config.experiments import ExperimentConfig, get_experiment_config
from adventuregame.config.messages import MessageTemplates, get_message_templates
from adventuregame.config.runtime import RuntimeConfig, get_runtime_config


class CompatConfigLoader:
    """
    Compatibility class that mimics the old ConfigLoader interface.

    This class provides the same property-based access as the old monolithic
    config system, but delegates to the new focused configuration modules.
    """

    def __init__(self) -> None:
        """Initialize the compatibility config loader."""
        # Lazy-load the new configs
        self._runtime: Optional[RuntimeConfig] = None
        self._experiments: Optional[ExperimentConfig] = None
        self._messages: Optional[MessageTemplates] = None

    @property
    def runtime(self) -> RuntimeConfig:
        """Get runtime config (lazy loaded)."""
        if self._runtime is None:
            self._runtime = get_runtime_config()
        return self._runtime

    @property
    def experiments(self) -> ExperimentConfig:
        """Get experiment config (lazy loaded)."""
        if self._experiments is None:
            self._experiments = get_experiment_config()
        return self._experiments

    @property
    def message_templates(self) -> MessageTemplates:
        """Get message templates (lazy loaded)."""
        if self._messages is None:
            self._messages = get_message_templates()
        return self._messages

    # Old property accessors that delegate to new system

    @property
    def paths(self) -> Dict[str, Any]:
        """Get path configurations (compatibility)."""
        rt = self.runtime
        return {
            "resources_dir": str(rt.paths.resources_dir),
            "definitions_dir": str(rt.paths.definitions_dir),
            "instances_dir": str(rt.paths.instances_dir),
            "grammar_files": {
                "pddl_actions": rt.paths.grammar_files.pddl_actions,
                "pddl_domain": rt.paths.grammar_files.pddl_domain,
                "pddl_events": rt.paths.grammar_files.pddl_events,
                "grammar_core": rt.paths.grammar_files.grammar_core,
            },
            "prompt_templates": {
                "basic": constants.PROMPT_TEMPLATE_BASIC,
                "new_words": constants.PROMPT_TEMPLATE_NEW_WORDS,
                "potion_brewing": constants.PROMPT_TEMPLATE_POTION_BREWING,
                "plan": constants.PROMPT_TEMPLATE_PLAN,
                "basic_invlimit": constants.PROMPT_TEMPLATE_BASIC_INVLIMIT,
                "plan_invlimit": constants.PROMPT_TEMPLATE_PLAN_INVLIMIT,
            },
            "definition_files": {
                "adventure_types": constants.DEFINITION_FILE_ADVENTURE_TYPES,
                "clingo_templates": constants.DEFINITION_FILE_CLINGO_TEMPLATES,
                "invlimit_actions": constants.DEFINITION_FILE_INVLIMIT_ACTIONS,
                "invlimit_domain": constants.DEFINITION_FILE_INVLIMIT_DOMAIN,
            },
        }

    @property
    def game_constants(self) -> Dict[str, Any]:
        """Get game constants (compatibility)."""
        rt = self.runtime
        return {
            "game_name": rt.game.name,
            "game_description": rt.game.description,
            "command_prefix": rt.game.command_prefix,
            "command_prefix_with_space": rt.game.command_prefix_with_space,
        }

    @property
    def variants(self) -> Dict[str, Any]:
        """Get variant configurations (compatibility)."""
        return {
            "basic": constants.VARIANT_BASIC,
            "plan": constants.VARIANT_PLAN,
            "basic_preexplore": constants.VARIANT_BASIC_PREEXPLORE,
            "plan_preexplore": constants.VARIANT_PLAN_PREEXPLORE,
            "basic_invlimit": constants.VARIANT_BASIC_INVLIMIT,
            "planning": constants.VARIANT_PLANNING,
            "planning_invlimit": constants.VARIANT_PLANNING_INVLIMIT,
            "default_variants": [constants.VARIANT_BASIC],
        }

    @property
    def adventure_types(self) -> Dict[str, str]:
        """Get adventure type identifiers (compatibility)."""
        return {
            "home_delivery": constants.ADVENTURE_HOME_DELIVERY,
            "home_deliver_three": constants.ADVENTURE_HOME_DELIVER_THREE,
            "home_deliver_two": constants.ADVENTURE_HOME_DELIVER_TWO,
            "new_words": constants.ADVENTURE_NEW_WORDS,
            "new_words_created": constants.ADVENTURE_NEW_WORDS_CREATED,
            "new_words_replace_explanation": (constants.ADVENTURE_NEW_WORDS_REPLACE_EXPLANATION),
            "new_words_replace_no_explanation": (
                constants.ADVENTURE_NEW_WORDS_REPLACE_NO_EXPLANATION
            ),
            "new_words_deliver": constants.ADVENTURE_NEW_WORDS_DELIVER,
            "new_word_states": constants.ADVENTURE_NEW_WORD_STATES,
            "potion": constants.ADVENTURE_POTION,
            "potion_brewing": constants.ADVENTURE_POTION_BREWING,
        }

    @property
    def actions(self) -> Dict[str, Any]:
        """Get action configurations (compatibility)."""
        return {
            "done": constants.ACTION_DONE,
            "done_command": constants.ACTION_DONE_COMMAND,
            "unknown": constants.ACTION_UNKNOWN,
            "excluded_from_shuffle": constants.ACTIONS_EXCLUDED_FROM_SHUFFLE,
            "object_manipulation_types": constants.OBJECT_MANIPULATION_ACTIONS,
        }

    @property
    def entities(self) -> Dict[str, Any]:
        """Get entity configurations (compatibility)."""
        return {
            "player_id": constants.PLAYER_ID,
            "inventory_id": constants.INVENTORY_ID,
            "floor_id_suffix": constants.FLOOR_ID_SUFFIX,
            "ceiling_id_suffix": constants.CEILING_ID_SUFFIX,
            "default_instance_suffix": constants.DEFAULT_INSTANCE_SUFFIX,
            "exempt_from_support": constants.ENTITIES_EXEMPT_FROM_SUPPORT,
            "floor_type": constants.FLOOR_TYPE,
        }

    @property
    def predicates(self) -> Dict[str, Any]:
        """Get predicate definitions (compatibility)."""
        return {
            "mutable_states": constants.MUTABLE_STATE_PREDICATES,
            "inventory_predicates": constants.INVENTORY_PREDICATES,
            "text": constants.PREDICATE_TEXT,
            "openable": constants.PREDICATE_OPENABLE,
            "takeable": constants.PREDICATE_TAKEABLE,
            "needs_support": constants.PREDICATE_NEEDS_SUPPORT,
            "container": constants.PREDICATE_CONTAINER,
            "support": constants.PREDICATE_SUPPORT,
            "predicate_in": constants.PREDICATE_IN,
            "predicate_on": constants.PREDICATE_ON,
        }

    @property
    def keys(self) -> Dict[str, str]:
        """Get dictionary key constants (compatibility)."""
        return {
            "message_role": constants.KEY_MESSAGE_ROLE,
            "message_content": constants.KEY_MESSAGE_CONTENT,
            "message_role_user": constants.KEY_MESSAGE_ROLE_USER,
            "message_role_assistant": constants.KEY_MESSAGE_ROLE_ASSISTANT,
            "type_name": constants.KEY_TYPE_NAME,
            "repr_str": constants.KEY_REPR_STR,
            "pddl": constants.KEY_PDDL,
            "pddl_param_mapping": constants.KEY_PDDL_PARAM_MAPPING,
            "event_definitions": constants.KEY_EVENT_DEFINITIONS,
            "entity_definitions": constants.KEY_ENTITY_DEFINITIONS,
            "room_definitions": constants.KEY_ROOM_DEFINITIONS,
            "action_definitions": constants.KEY_ACTION_DEFINITIONS,
            "domain_definitions": constants.KEY_DOMAIN_DEFINITIONS,
            "goal_state": constants.KEY_GOAL_STATE,
            "optimal_commands": constants.KEY_OPTIMAL_COMMANDS,
            "fail_type": constants.KEY_FAIL_TYPE,
            "done_action": constants.KEY_DONE_ACTION,
            "metadata": constants.KEY_METADATA,
            "goal_states_achieved": constants.KEY_GOAL_STATES_ACHIEVED,
            "turn_goal_score": constants.KEY_TURN_GOAL_SCORE,
            "game_successfully_finished": constants.KEY_GAME_SUCCESSFULLY_FINISHED,
        }

    @property
    def delimiters(self) -> Dict[str, str]:
        """Get delimiter strings (compatibility)."""
        msg = self.message_templates
        return {
            "plan_delimiter": msg.delimiters.plan_delimiter,
            "plan_separator": msg.delimiters.plan_separator,
            "list_separator": msg.delimiters.list_separator,
            "list_last_conjunction": msg.delimiters.list_last_conjunction,
        }

    @property
    def template_placeholders(self) -> Dict[str, str]:
        """Get template placeholder strings (compatibility)."""
        return {
            "goal": constants.TEMPLATE_PLACEHOLDER_GOAL,
            "new_words_explanations": constants.TEMPLATE_PLACEHOLDER_NEW_WORDS,
        }

    @property
    def event_types(self) -> Dict[str, str]:
        """Get event type identifiers (compatibility)."""
        return {
            "action_fail": constants.EVENT_ACTION_FAIL,
            "action_info": constants.EVENT_ACTION_INFO,
            "goal_status": constants.EVENT_GOAL_STATUS,
            "hallucinated_finish": constants.EVENT_HALLUCINATED_FINISH,
            "invalid_format": constants.EVENT_INVALID_FORMAT,
            "adventure_finished": constants.EVENT_ADVENTURE_FINISHED,
            "loop_detected": constants.EVENT_LOOP_DETECTED,
            "turn_plan": constants.EVENT_TURN_PLAN,
            "current_plan": constants.EVENT_CURRENT_PLAN,
            "turn_limit_reached": constants.EVENT_TURN_LIMIT_REACHED,
            "model_done": constants.EVENT_MODEL_DONE,
            "game_result": constants.EVENT_GAME_RESULT,
            "plan_followed": constants.EVENT_PLAN_FOLLOWED,
        }

    @property
    def log_keys(self) -> Dict[str, str]:
        """Get log key constants (compatibility)."""
        return {
            "plan_length": constants.LOG_PLAN_LENGTH,
            "plan_results": constants.LOG_PLAN_RESULTS,
            "plan_command_success_ratio": constants.LOG_PLAN_COMMAND_SUCCESS_RATIO,
            "turn_limit_loss": constants.LOG_TURN_LIMIT_LOSS,
            "adventure_info": constants.LOG_ADVENTURE_INFO,
        }

    @property
    def parse_errors(self) -> Dict[str, str]:
        """Get parse error type identifiers (compatibility)."""
        return {
            "command_tag_missing": constants.PARSE_ERROR_COMMAND_TAG_MISSING,
            "next_actions_missing": constants.PARSE_ERROR_NEXT_ACTIONS_MISSING,
        }

    @property
    def fail_types(self) -> List[str]:
        """Get list of all action failure types (compatibility)."""
        return constants.FAIL_TYPES

    @property
    def plan_metrics(self) -> List[str]:
        """Get list of plan metrics to track (compatibility)."""
        return constants.PLAN_METRICS

    @property
    def hallucination_keywords(self) -> List[str]:
        """Get list of hallucination indicator keywords (compatibility)."""
        return constants.HALLUCINATION_KEYWORDS

    @property
    def thresholds(self) -> Dict[str, Any]:
        """Get threshold values (compatibility)."""
        exp = self.experiments
        return {
            "loop_detection": exp.thresholds.loop_detection,
            "min_plan_history": exp.thresholds.min_plan_history,
            "bad_plan_viability": exp.thresholds.bad_plan_viability,
            "exploration_history": exp.thresholds.exploration_history,
            "goal_count_min": exp.thresholds.goal_count_min,
            "predicate_arg_length": constants.PREDICATE_ARG_LENGTHS,
            "room_exit_counts": constants.ROOM_EXIT_COUNTS,
            "inventory_counts": constants.INVENTORY_COUNTS,
            "container_content_counts": constants.CONTAINER_CONTENT_COUNTS,
            "supported_entity_counts": constants.SUPPORTED_ENTITY_COUNTS,
            "fact_tuple_length": constants.FACT_TUPLE_LENGTH,
            "entity_replacement_threshold": constants.ENTITY_REPLACEMENT_THRESHOLD,
        }

    @property
    def array_indices(self) -> Dict[str, int]:
        """Get array index constants (compatibility)."""
        return {
            "primary_model": constants.INDEX_PRIMARY_MODEL,
            "split_result_check": constants.INDEX_SPLIT_RESULT_CHECK,
            "plan_result_action_info": constants.INDEX_PLAN_RESULT_ACTION_INFO,
            "plan_analysis_start_turn": constants.INDEX_PLAN_ANALYSIS_START_TURN,
            "zero_index": constants.INDEX_ZERO,
            "action_string_prefix_len": constants.INDEX_ACTION_STRING_PREFIX_LEN,
            "action_string_suffix_len": constants.INDEX_ACTION_STRING_SUFFIX_LEN,
        }

    @property
    def scores(self) -> Dict[str, int]:
        """Get scoring values (compatibility)."""
        exp = self.experiments
        return {
            "success": exp.scoring.success,
            "failure": exp.scoring.failure,
        }

    @property
    def messages(self) -> Dict[str, str]:
        """Get user-facing message templates (compatibility)."""
        msg = self.message_templates
        return {
            "default_custom_response": msg.initial.default_custom_response,
            "initial_response": msg.initial.initial_response,
            "room_description_template": msg.descriptions.room_template,
            "multi_item_description": msg.descriptions.multi_item,
            "two_item_description": msg.descriptions.two_items,
            "single_item_description": msg.descriptions.single_item,
            "empty_inventory": msg.inventory.empty,
            "inventory_description": msg.inventory.description,
            "exit_description_template": msg.descriptions.exit_template,
            "unknown_command": msg.errors.unknown_command,
            "undefined_action": msg.errors.undefined_action,
            "unknown_entity": msg.errors.unknown_entity,
            "cannot_take": msg.errors.cannot_take,
            "cannot_put": msg.errors.cannot_put,
            "no_need_open": msg.errors.no_need_open,
            "cannot_close": msg.errors.cannot_close,
            "unknown_item_type": msg.errors.unknown_item_type,
            "already_in_inventory": msg.errors.already_in_inventory,
            "cannot_take_from_inventory": msg.errors.cannot_take_from_inventory,
            "not_in_room": msg.errors.not_in_room,
            "cannot_do_that": msg.errors.cannot_do_that,
        }

    @property
    def parser_settings(self) -> Dict[str, str]:
        """Get parser configuration (compatibility)."""
        rt = self.runtime
        return {
            "action_grammar_start_rule": rt.parser.action_start_rule,
            "domain_grammar_start_rule": rt.parser.domain_start_rule,
            "event_grammar_start_rule": rt.parser.event_start_rule,
        }

    @property
    def clingo_settings(self) -> Dict[str, Any]:
        """Get Clingo solver settings (compatibility)."""
        exp = self.experiments
        return {
            "control_all_models": exp.clingo.control_all_models,
            "status_sat": exp.clingo.status_sat,
            "status_unsat": exp.clingo.status_unsat,
            "picking_strategies": exp.clingo.picking_strategies,
            "default_layout_generation_limit": exp.clingo.default_layout_generation_limit,
            "default_initial_states_per_layout": exp.clingo.default_initial_states_per_layout,
            "default_initial_state_limit": exp.clingo.default_initial_state_limit,
            "default_adventures_per_initial_state": exp.clingo.default_adventures_per_initial_state,
            "default_target_adventure_count": exp.clingo.default_target_adventure_count,
            "add_floors_default": exp.clingo.add_floors_default,
            "pair_exits_default": exp.clingo.pair_exits_default,
        }

    @property
    def generation_settings(self) -> Dict[str, Any]:
        """Get instance generation settings (compatibility)."""
        exp = self.experiments
        return {
            "definition_methods": exp.generation.definition_methods,
            "adjective_configs": exp.generation.adjective_configs,
            "difficulty_levels": exp.generation.difficulty_levels,
            "task_types": {"deliver": "deliver"},
            "default_raw_adventures_files": ["generated_potion_brewing_adventures"],
        }

    @property
    def goal_settings(self) -> Dict[str, str]:
        """Get goal-related settings (compatibility)."""
        return {
            "potion_goal": constants.GOAL_POTION,
            "potion_goal_description": constants.GOAL_POTION_DESCRIPTION,
            "goal_delivery_prefix": constants.GOAL_DELIVERY_PREFIX,
            "goal_state_prefix": constants.GOAL_STATE_PREFIX,
            "goal_article": constants.GOAL_ARTICLE,
        }

    @property
    def output_settings(self) -> Dict[str, Any]:
        """Get output formatting settings (compatibility)."""
        return {
            "timestamp_format": constants.TIMESTAMP_FORMAT,
            "output_filename_template": constants.OUTPUT_FILENAME_TEMPLATE,
            "experiment_suffixes": {
                "invlimit": constants.EXPERIMENT_SUFFIX_INVLIMIT,
            },
        }

    @property
    def random_seeds(self) -> Dict[str, int]:
        """Get random seed configurations (compatibility)."""
        exp = self.experiments
        return {
            "default": exp.random_seed,
            "max_seed": exp.max_random_seed,
        }

    @property
    def initial_counts(self) -> Dict[str, int]:
        """Get initial count values (compatibility)."""
        return {
            "inventory_items": constants.COUNT_INITIAL_INVENTORY_ITEMS,
            "iterator_value": constants.COUNT_INITIAL_ITERATOR_VALUE,
        }

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value by path (compatibility method).

        This provides the old get() interface for backward compatibility.

        Args:
            *keys: Nested keys to traverse
            default: Default value if key not found

        Returns:
            The configuration value or default
        """
        # Navigate through properties
        current: Any = self
        for key in keys:
            if hasattr(current, key):
                current = getattr(current, key)
            elif isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current


# Global singleton instance
_compat_config_instance: Optional[CompatConfigLoader] = None


def get_config() -> CompatConfigLoader:
    """
    Get the compatibility configuration instance.

    This function provides backward compatibility with the old config_loader
    interface while using the new focused configuration modules.

    Returns:
        The global CompatConfigLoader instance

    Example:
        >>> config = get_config()
        >>> print(config.game_constants["command_prefix"])
        >
    """
    global _compat_config_instance
    if _compat_config_instance is None:
        _compat_config_instance = CompatConfigLoader()
    return _compat_config_instance
