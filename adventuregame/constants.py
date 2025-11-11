"""
Constants for AdventureGame.

This module contains true constants - values that never change during runtime
or across experiments. These are domain knowledge about the game mechanics,
not configuration that researchers modify.

For values that DO change (paths, thresholds, messages), see the config/ module.
"""

from typing import List

# Action constants
ACTION_DONE = "done"
ACTION_DONE_COMMAND = "> done"
ACTION_UNKNOWN = "unknown"
ACTIONS_EXCLUDED_FROM_SHUFFLE = ["go", "done", "examine", "look"]
OBJECT_MANIPULATION_ACTIONS = ["take", "put", "open", "close"]

# Entity constants
PLAYER_ID = "player1"
INVENTORY_ID = "inventory"
FLOOR_ID_SUFFIX = "floor1"
CEILING_ID_SUFFIX = "ceiling1"
DEFAULT_INSTANCE_SUFFIX = "1"
ENTITIES_EXEMPT_FROM_SUPPORT = ["floor", "player"]
FLOOR_TYPE = "floor"

# Predicate constants
MUTABLE_STATE_PREDICATES = ["open", "closed", "at", "in", "on"]
INVENTORY_PREDICATES = ["at", "in"]
PREDICATE_TEXT = "text"
PREDICATE_OPENABLE = "openable"
PREDICATE_TAKEABLE = "takeable"
PREDICATE_NEEDS_SUPPORT = "needs_support"
PREDICATE_CONTAINER = "container"
PREDICATE_SUPPORT = "support"
PREDICATE_IN = "in"
PREDICATE_ON = "on"

# Dictionary key constants (for interaction records)
KEY_MESSAGE_ROLE = "role"
KEY_MESSAGE_CONTENT = "content"
KEY_MESSAGE_ROLE_USER = "user"
KEY_MESSAGE_ROLE_ASSISTANT = "assistant"
KEY_TYPE_NAME = "type_name"
KEY_REPR_STR = "repr_str"
KEY_PDDL = "pddl"
KEY_PDDL_PARAM_MAPPING = "pddl_parameter_mapping"
KEY_EVENT_DEFINITIONS = "event_definitions"
KEY_ENTITY_DEFINITIONS = "entity_definitions"
KEY_ROOM_DEFINITIONS = "room_definitions"
KEY_ACTION_DEFINITIONS = "action_definitions"
KEY_DOMAIN_DEFINITIONS = "domain_definitions"
KEY_GOAL_STATE = "goal_state"
KEY_OPTIMAL_COMMANDS = "optimal_commands"
KEY_FAIL_TYPE = "fail_type"
KEY_DONE_ACTION = "done_action"
KEY_METADATA = "metadata"
KEY_GOAL_STATES_ACHIEVED = "goal_states_achieved"
KEY_TURN_GOAL_SCORE = "turn_goal_score"
KEY_GAME_SUCCESSFULLY_FINISHED = "game_successfully_finished"

# Event type constants
EVENT_ACTION_FAIL = "action_fail"
EVENT_ACTION_INFO = "action_info"
EVENT_GOAL_STATUS = "goal_status"
EVENT_HALLUCINATED_FINISH = "hallucinated_finish"
EVENT_INVALID_FORMAT = "invalid_format"
EVENT_ADVENTURE_FINISHED = "adventure_finished"
EVENT_LOOP_DETECTED = "loop_detected"
EVENT_TURN_PLAN = "turn_plan"
EVENT_CURRENT_PLAN = "current_plan"
EVENT_TURN_LIMIT_REACHED = "turn_limit_reached"
EVENT_MODEL_DONE = "model_done"
EVENT_GAME_RESULT = "game_result"
EVENT_PLAN_FOLLOWED = "plan_followed"

# Log key constants
LOG_PLAN_LENGTH = "plan_length"
LOG_PLAN_RESULTS = "plan_results"
LOG_PLAN_COMMAND_SUCCESS_RATIO = "plan_command_success_ratio"
LOG_TURN_LIMIT_LOSS = "turn_limit_loss"
LOG_ADVENTURE_INFO = "adventure_info"

# Parse error constants
PARSE_ERROR_COMMAND_TAG_MISSING = "command_tag_missing"
PARSE_ERROR_NEXT_ACTIONS_MISSING = "next_actions_missing"

# Fail type constants
FAIL_TYPES: List[str] = [
    "parsing",
    "resolution",
    "lark_exception",
    "malformed_command",
    "undefined_action_verb",
    "undefined_action",
    "undefined_repr_str",
    "manipulating_room",
    "undefined_argument_type",
    "taking_from_inventory",
    "other_room_argument",
    "domain_trait_type_mismatch",
    "domain_type_discrepancy",
    "world_state_discrepancy",
    "entity_not_accessible",
    "entity_state_mismatch",
    "entity_trait_mismatch",
    "entity_already_inventory",
    "going_to_current_room",
    "no_exit_to",
    "inventory_limit_exceeded",
]

# Plan metric constants
PLAN_METRICS: List[str] = [
    "plan_followed",
    "plan_command_success_ratio",
    "bad_plan_followed",
]

# Hallucination keyword constants
HALLUCINATION_KEYWORDS: List[str] = [
    "complete",
    "finish",
    "done",
    "successfully",
]

# Template placeholder constants
TEMPLATE_PLACEHOLDER_GOAL = "$GOAL$"
TEMPLATE_PLACEHOLDER_NEW_WORDS = "$NEW_WORDS_EXPLANATIONS$"

# Variant name constants
VARIANT_BASIC = "basic"
VARIANT_PLAN = "plan"
VARIANT_BASIC_PREEXPLORE = "basic_preexplore"
VARIANT_PLAN_PREEXPLORE = "plan_preexplore"
VARIANT_BASIC_INVLIMIT = "basic_invlimit"
VARIANT_PLANNING = "planning"
VARIANT_PLANNING_INVLIMIT = "planning_invlimit"

# Adventure type name constants
ADVENTURE_HOME_DELIVERY = "home_delivery"
ADVENTURE_HOME_DELIVER_THREE = "home_deliver_three"
ADVENTURE_HOME_DELIVER_TWO = "home_deliver_two"
ADVENTURE_NEW_WORDS = "new-words"
ADVENTURE_NEW_WORDS_CREATED = "new-words_created"
ADVENTURE_NEW_WORDS_REPLACE_EXPLANATION = "new-words_replace_explanation"
ADVENTURE_NEW_WORDS_REPLACE_NO_EXPLANATION = "new-words_replace_no_explanation"
ADVENTURE_NEW_WORDS_DELIVER = "new-words_deliver"
ADVENTURE_NEW_WORD_STATES = "new-word_states"
ADVENTURE_POTION = "potion"
ADVENTURE_POTION_BREWING = "potion_brewing"

# Goal description constants
GOAL_POTION = "at(potion1,kitchen1)"
GOAL_POTION_DESCRIPTION = "Brew the potion."
GOAL_DELIVERY_PREFIX = "Put "
GOAL_STATE_PREFIX = "Make "
GOAL_ARTICLE = "the "

# Array index constants (for consistency in indexing)
INDEX_PRIMARY_MODEL = 0
INDEX_SPLIT_RESULT_CHECK = 1
INDEX_PLAN_RESULT_ACTION_INFO = 2
INDEX_PLAN_ANALYSIS_START_TURN = 1
INDEX_ZERO = 0
INDEX_ACTION_STRING_PREFIX_LEN = 9
INDEX_ACTION_STRING_SUFFIX_LEN = -1

# Count constants
COUNT_INITIAL_INVENTORY_ITEMS = 0
COUNT_INITIAL_ITERATOR_VALUE = 0

# Tuple length constants
FACT_TUPLE_LENGTH = 3
PREDICATE_ARG_LENGTHS = [3, 5, 7]

# Generation constants
ROOM_EXIT_COUNTS = [0, 1, 2, 3]
INVENTORY_COUNTS = [0, 1]
CONTAINER_CONTENT_COUNTS = [0, 1, 2, 3]
SUPPORTED_ENTITY_COUNTS = [0, 1, 2, 3]
ENTITY_REPLACEMENT_THRESHOLD = 4

# Output formatting constants
TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"
OUTPUT_FILENAME_TEMPLATE = "generated_{adv_type}_adventures.json"
EXPERIMENT_SUFFIX_INVLIMIT = "invlimittwo"

# Definition file constants (relative to resources/definitions/)
DEFINITION_FILE_ADVENTURE_TYPES = "adventure_types.json"
DEFINITION_FILE_CLINGO_TEMPLATES = "clingo_templates.json"
DEFINITION_FILE_INVLIMIT_ACTIONS = "basic_actions_v2_invlimit.json"
DEFINITION_FILE_INVLIMIT_DOMAIN = "home_domain_invlimit.json"

# Prompt template paths (relative to adventuregame/)
PROMPT_TEMPLATE_BASIC = "resources/initial_prompts/basic_prompt_done"
PROMPT_TEMPLATE_NEW_WORDS = "resources/initial_prompts/new-words_prompt_done"
PROMPT_TEMPLATE_POTION_BREWING = "resources/initial_prompts/potion_brewing"
PROMPT_TEMPLATE_PLAN = "resources/initial_prompts/plan_prompt_done"
PROMPT_TEMPLATE_BASIC_INVLIMIT = "resources/initial_prompts/basic_prompt_done_invlimittwo"
PROMPT_TEMPLATE_PLAN_INVLIMIT = "resources/initial_prompts/plan_prompt_done_invlimittwo"
