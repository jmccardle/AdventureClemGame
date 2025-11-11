import logging
import os
from typing import Any, Dict, List, Optional, Set, Tuple

import clemcore.clemgame.metrics as metrics
import numpy as np
from clemcore.backends import Model
from clemcore.clemgame import (
    DialogueGameMaster,
    GameBenchmark,
    GameError,
    GameMaster,
    GameScorer,
    GameSpec,
    ParseError,
    Player,
)
from clemcore.clemgame.master import RuleViolationError
from clemcore.utils import file_utils
from config_loader import get_config
from if_wrapper import AdventureIFInterpreter

from adventuregame.exceptions import AdventureGameError, ConfigurationError

logger = logging.getLogger(__name__)

# Initialize config at module level
config = get_config()


class AdventurePlayer(Player):
    """Player class for AdventureGame.

    Handles player responses for both model-based and human terminal interactions.
    Extends the base Player class from clemcore with custom response handling.
    """

    def __init__(self, model: Model) -> None:
        """Initialize the AdventurePlayer.

        Args:
            model: The language model backend for generating responses.
        """
        super().__init__(model)

    def _custom_response(self, context: Dict[str, Any]) -> str:
        """Generate a custom response for the player.

        Args:
            context: The dialogue context dictionary.

        Returns:
            The default custom response message from configuration.
        """
        return str(config.messages["default_custom_response"])

    def _terminal_response(self, context: Dict[str, Any]) -> str:
        """Generate response for human interaction via terminal.

        Adds the '> ' prefix required by the GM to prevent participant fatigue leading to aborted episodes.
        Since the prefix requirement is used to check continuous instruction following *by LLMs*, it is not important
        for human players. This also makes AdventureGame play like classic IF games for human players, since the '>'
        present in gameplay logs from these games are a feature of vintage terminal UIs and did not need to be typed in
        for each command input.

        Args:
            context: The dialogue context dictionary containing the message to display to the player.

        Returns:
            The human player's action input with the command prefix prepended.
        """
        latest_response: str = config.messages["initial_response"]
        if context is not None:
            latest_response = context[config.keys["message_content"]]
        logger.info(latest_response)
        user_input: str = input(
            f"Type in your action, {config.game_constants['command_prefix']} will be automatically added if missing:\n"
        )
        if not user_input.startswith(config.game_constants["command_prefix"]):
            user_input = config.game_constants["command_prefix_with_space"] + user_input.strip()
        return user_input


class AdventureGameMaster(DialogueGameMaster):
    """DialogueGameMaster subclass for AdventureGame.

    Orchestrates game episodes by prompting the model, parsing responses, and interacting
    with the IF (Interactive Fiction) interpreter. Handles format adherence checks,
    goal tracking, and creates detailed episode records for scoring.

    Attributes:
        game_path: Path to the game directory.
        turns: List of turn success indicators.
        success: Flag indicating if current turn was successful.
        invalid_format: Error message for invalid format responses.
        finished: Flag indicating if all goals were achieved.
        model_done: Flag indicating if model used DONE action.
        turn_goal_score: Number of goals achieved in current turn.
        game_instance: Game instance configuration dictionary.
        if_variant: Game variant ('basic', 'plan', 'invlimit', etc.).
        if_interpreter: The Interactive Fiction interpreter instance.
        player: The AdventurePlayer instance.
        plan_history: History of planned action sequences (plan variant only).
        plan_success_ratio_history: History of plan success ratios (plan variant only).
        pre_explore_inputs: Pre-exploration action sequence (preexplore variants only).
        goals_required: Set of goal states that must be achieved.
        goals_required_cnt: Total number of required goals.
        goals_achieved: Set of goals achieved so far.
        if_input_history: History of IF inputs for loop detection.
        loop_detected: Flag indicating if input loop was detected.
    """

    def __init__(
        self, game_name: str, game_path: str, experiment: Dict[str, Any], player_models: List[Model]
    ) -> None:
        """Initialize the AdventureGameMaster.

        Args:
            game_name: Name of the game.
            game_path: Path to the game directory.
            experiment: Experiment configuration dictionary.
            player_models: List of model instances for the players.
        """
        super().__init__(game_name, game_path, experiment, player_models)
        self.game_path: str = game_path
        self.turns: List[bool] = []
        self.success: bool = True
        self.invalid_format: str = ""  # to track responses with invalid format
        self.finished: bool = False  # game finished successfully
        self.model_done: bool = False  # model used DONE action to end game
        self.turn_goal_score: int = 0

    def _on_setup(self, **game_instance: Any) -> None:
        """Set up the game instance before the episode begins.

        Initializes the IF interpreter, creates the player, sets up variant-specific
        features (planning, pre-exploration), and initializes goal tracking.

        Args:
            **game_instance: Game instance configuration containing variant, goals,
                max_turns, optimal_turns, and other game-specific parameters.
        """
        self.game_instance: Dict[str, Any] = game_instance  # fetch game parameters here
        # check game variant; 'basic' or 'planning':
        self.if_variant: str = self.game_instance["variant"]
        # initialize IF interpreter:
        self.if_interpreter: AdventureIFInterpreter = AdventureIFInterpreter(
            self.game_path, self.game_instance
        )
        # create clem player:
        self.player: AdventurePlayer = AdventurePlayer(self.player_models[0])
        # Add the players: these will be logged to the records interactions.json
        # Note: During game play the players will be called in the order added here
        self.add_player(self.player)
        # keep history of plans:
        if self.if_variant == config.variants["plan"]:
            self.plan_history: List[List[str]] = list()
            self.plan_success_ratio_history: List[float] = list()  # for 'bad' plan scoring
        if "preexplore" in self.if_variant:
            # get pre-exploration sequence for pre-explore adventures:
            self.pre_explore_inputs: List[str] = self.game_instance["visiting_commands"]
        # get goal data set from game instance:
        self.goals_required: Set[str] = set(self.game_instance["goal_state"])
        self.goals_required_cnt: int = len(self.goals_required)
        # initially empty set of achieved goals:
        self.goals_achieved: Set[str] = set()
        # get and record adventure information:
        adventure_info: Dict[str, Any] = {
            "variant": self.game_instance["variant"],
            "max_turns": self.game_instance["max_turns"],
            "optimal_turns": self.game_instance["optimal_turns"],
            "goal_count": self.goals_required_cnt,
        }
        self.log_key("adventure_info", adventure_info)
        # if input history to detect loops:
        self.if_input_history: List[str] = list()
        self.loop_detected: bool = False

    def _on_before_game(self) -> None:
        """Execute pre-game setup before the first turn.

        For pre-explore variants, executes the pre-exploration sequence by visiting
        specified rooms and adding the interaction history to the player's messages.
        For regular variants, sets up the initial context with the room description.
        """
        # pre-explore rooms for pre-explore variants:
        if "preexplore" in self.if_variant:
            # get initial room description from IF interpreter:
            initial_room_desc: str = self.if_interpreter.get_full_room_desc()
            # combine prompt with initial room description as first message:
            first_message_content: str = self.game_instance["prompt"] + initial_room_desc
            first_message: Dict[str, str] = {
                config.keys["message_role"]: config.keys["message_role_user"],
                config.keys["message_content"]: first_message_content,
            }
            # add initial prompt message to player message history:
            self.player._messages.append(first_message)
            # execute pre-explore visiting sequence:
            for pre_exp_idx, pre_exp_action in enumerate(self.pre_explore_inputs):
                if (
                    pre_exp_idx < len(self.pre_explore_inputs) - 1
                ):  # only do this by simple history appending before last
                    # add IF input message to player message history:
                    if config.variants["plan"] in self.if_variant:
                        input_message = {
                            config.keys["message_role"]: config.keys["message_role_assistant"],
                            config.keys[
                                "message_content"
                            ]: f"{config.game_constants['command_prefix_with_space']}{pre_exp_action}\n"
                            f"Next actions: "
                            f"{config.delimiters['plan_separator'].join(self.pre_explore_inputs[pre_exp_idx+1:])}",
                        }
                    else:
                        input_message = {
                            config.keys["message_role"]: config.keys["message_role_assistant"],
                            config.keys[
                                "message_content"
                            ]: f"{config.game_constants['command_prefix_with_space']}{pre_exp_action}",
                        }
                    self.player._messages.append(input_message)
                    # execute pre-explore action:
                    goals_achieved, if_response, action_info = self.if_interpreter.process_action(
                        pre_exp_action
                    )
                    # add IF response to player message history:
                    response_message: Dict[str, str] = {
                        config.keys["message_role"]: config.keys["message_role_user"],
                        config.keys["message_content"]: if_response,
                    }
                    self.player._messages.append(response_message)
                else:  # handle last pair by using set_context_for
                    # add IF input message to player message history:
                    if config.variants["plan"] in self.if_variant:
                        input_message = {
                            config.keys["message_role"]: config.keys["message_role_assistant"],
                            config.keys[
                                "message_content"
                            ]: f"{config.game_constants['command_prefix_with_space']}{pre_exp_action}\n"
                            f"Next actions: {self.pre_explore_inputs[-1]}",
                        }
                    else:
                        input_message = {
                            config.keys["message_role"]: config.keys["message_role_assistant"],
                            config.keys[
                                "message_content"
                            ]: f"{config.game_constants['command_prefix_with_space']}{pre_exp_action}",
                        }
                    self.player._messages.append(input_message)
                    # execute pre-explore action:
                    goals_achieved, if_response, action_info = self.if_interpreter.process_action(
                        pre_exp_action
                    )
                    self.set_context_for(self.player, if_response)
        else:
            # get initial room description from IF interpreter:
            initial_room_desc = self.if_interpreter.get_full_room_desc()
            # combine prompt with initial room description as first message:
            first_message = self.game_instance["prompt"] + initial_room_desc
            # add the initial prompts to the message history:
            self.set_context_for(self.player, first_message)

    def _parse_response(self, player: Player, utterance: str) -> Tuple[str, bool]:
        """Parse and validate a player's response utterance.

        Checks that the response follows the required format (starts with command prefix,
        contains 'Next actions:' for plan variant). For planning variants, extracts the
        planned action sequence and adds it to plan history.

        Args:
            player: The player instance that produced the response.
            utterance: The raw response string from the player.

        Returns:
            A tuple of (parsed_utterance, should_log) where parsed_utterance is the
            potentially modified response and should_log indicates whether to log a
            parse event (default: True).

        Raises:
            ParseError: If the command prefix is missing or 'Next actions:' is missing
                in plan variant (except for DONE action).
        """
        # logger.info(f"Player response:\n{utterance}")
        # check player response:
        if player == self.player:
            # check rule: response must start with IF >
            if not utterance.startswith(config.game_constants["command_prefix"]):
                self.success = False
                # hallucinated finish heuristic:
                hallucinated_finish_strs = config.hallucination_keywords
                for hallucinated_finish_str in hallucinated_finish_strs:
                    if hallucinated_finish_str in utterance:
                        self.log_to_self(config.event_types["hallucinated_finish"], utterance)
                        break
                self.invalid_format = config.parse_errors["command_tag_missing"]
                raise ParseError(config.parse_errors["command_tag_missing"], utterance)
            if self.if_variant == config.variants["plan"]:
                # check rule: response must contain 'Next actions:' on its own line
                # if utterance is DONE action, don't fail
                if (
                    config.delimiters["plan_delimiter"] not in utterance
                    and config.actions["done"] not in utterance
                ):
                    self.success = False
                    self.invalid_format = config.parse_errors["next_actions_missing"]
                    raise ParseError(config.parse_errors["next_actions_missing"], utterance)

        # logger.info(f"AdventureGameMaster._on_parse_response() input utterance: {utterance}")
        if self.if_variant == config.variants["plan"]:
            # do not split for next actions plan if action is 'done'
            if utterance == config.actions["done_command"]:
                return utterance, True
            # split the response to extract only the planned actions:
            split_response = utterance.split(config.delimiters["plan_delimiter"])
            if len(split_response) >= config.thresholds["min_split_parts_for_plan"]:
                new_plan = utterance.split(config.delimiters["plan_delimiter"])[1]
                # split by comma and strip to get assumed individual action commands:
                plan_sequence = [
                    command.strip()
                    for command in new_plan.split(config.delimiters["plan_separator"])
                ]
                # add new plan sequence to plan history:
                self.plan_history.append(plan_sequence)
                # record the new plan for processing:
                self.log_to_self(config.event_types["turn_plan"], plan_sequence)
                return utterance, True
            else:
                raise ParseError(config.parse_errors["next_actions_missing"], utterance)

        return utterance, True

    def _on_before_round(self) -> None:
        """Execute actions before each round.

        Called after turn increment but before prompting the player.
        Logs the current turn index for convenient comparison of runtime logs and transcripts.
        """
        self.log_to_self("metadata", f"Turn {self.current_round}")

    def _does_game_proceed(self) -> bool:
        """Check if the game should continue to the next turn.

        The game stops if any of the following conditions are met:
        - Invalid output format detected
        - Turn limit reached
        - Model performed DONE action
        - Input loop detected (same action repeated multiple times)

        Note: Achieving all goal states is recorded but does NOT stop the episode.

        Returns:
            True if the game should continue, False otherwise.
        """
        # record invalid format failures:
        if self.invalid_format:
            self.log_to_self(config.event_types["invalid_format"], self.invalid_format)
            return False
        # check if all goal states have been achieved:
        if self.goals_achieved == self.goals_required:
            self.finished = True
            self.log_to_self(
                config.event_types["adventure_finished"], list(self.goals_achieved)
            )  # can be JSON'd; for easier eval
            # return False  # do not stop game when all goal states have been achieved
        # stop game when turn limit is reached:
        if self.current_round >= self.game_instance["max_turns"]:
            self.log_to_self(
                config.event_types["turn_limit_reached"],
                f"Turn limit {self.game_instance['max_turns']} reached, end episode.",
            )
            return False
        # stop game when model used DONE action:
        if self.model_done:
            self.log_to_self(
                config.event_types["model_done"],
                f"Model produced DONE action at turn {self.current_round}, end episode.",
            )
            return False
        # stop game when last three IF inputs were the same:
        if self.loop_detected:
            self.log_to_self(
                config.event_types["loop_detected"],
                f"Model produced IF input '{self.if_input_history[-1]}' {config.thresholds['loop_detection']} "
                f"times consecutively, abort episode.",
            )
            return False
        # otherwise keep playing:
        return True

    def _advance_game(self, player: Player, parsed_response: Tuple[str, bool]) -> None:
        """Advance the game state after a player's action.

        Main game loop hook called after all players have been prompted and their
        responses have been parsed and validated. Processes the player's action through
        the IF interpreter, updates goal tracking, handles plan evaluation (for plan
        variant), and sets up context for the next turn.

        Args:
            player: The player instance that performed the action.
            parsed_response: Tuple of (parsed_utterance, should_log) from _parse_response.
        """
        if self._does_game_proceed():  # only pass last message to IF if the game is still going
            # IF INTERACTION

            # get the last player action from message history:
            # last_action: str = self.messages_by_names[self.player.descriptor][-1]['content']
            # logger.info(f"Raw last message:\n{last_action}")

            last_action: str = parsed_response[0]

            # strip player action to IF input; only first line action command is used:
            if_input: str = last_action[1:].split("\n")[0].strip()
            logger.info(f"Stripped IF input: {if_input}")

            # loop checking:
            self.if_input_history.append(if_input)
            # check if last four IF inputs are the same:
            if len(self.if_input_history) >= config.thresholds["loop_detection"]:
                if (
                    self.if_input_history[-config.thresholds["loop_detection"]]
                    == self.if_input_history[-3]
                    == self.if_input_history[-2]
                    == self.if_input_history[-1]
                ):
                    self.loop_detected = True
                    logger.info(
                        f"Aborting - IF input loop detected: Last {config.thresholds['loop_detection']} inputs are '{self.if_input_history[-1]}'"
                    )

            # count achieved goals:
            prior_goal_count = len(self.goals_achieved)

            # send to IF interpreter to process action:
            goals_achieved, if_response, action_info = self.if_interpreter.process_action(if_input)
            # IF interpreter returns: set of achieved goal states in string form,
            # textual feedback response, failure/action info dict
            logger.info(f"IF response: {if_response}")

            if config.keys["fail_type"] in action_info:
                # record failure dict for scoring:
                self.log_to_self(
                    config.event_types["action_fail"], action_info
                )  # can be JSON'd; for easier eval
            else:
                self.log_to_self(config.event_types["action_info"], action_info)

            # catch DONE action to end game after this turn:
            if config.keys["done_action"] in action_info:
                logger.info(f"model_done: {action_info[config.keys['done_action']]}")
                # self.log_to_self("model_done", if_input)
                self.model_done = True

            # if 'exploration_info' in action_info:
            #    self.log_to_self("exploration_info", action_info['exploration_info'])

            # handle goals:
            self.goals_achieved = goals_achieved
            # count goals achieved this turn:
            post_goal_count = len(self.goals_achieved)
            # calculate turn goal score; can be negative if a goal is 'unachieved':
            turn_score = post_goal_count - prior_goal_count
            # set turn_goal_score attribute for playpen turn score:
            self.turn_goal_score = turn_score
            # combine goal info into dict:
            goal_status = {
                config.keys["goal_states_achieved"]: list(self.goals_achieved),
                config.keys["turn_goal_score"]: turn_score,
            }
            # record goal status dict for scoring:
            self.log_to_self(
                config.event_types["goal_status"], goal_status
            )  # can be JSON'd; for easier eval

            if self.if_variant == config.variants["plan"]:
                # current plan viability:
                # get latest/current plan from plan history:
                cur_plan: list = self.plan_history[-1]
                self.log_to_self(config.event_types["current_plan"], f"{str(cur_plan)}")
                # get length of plan:
                cur_plan_command_count: int = len(cur_plan)
                self.log_to_self(config.log_keys["plan_length"], cur_plan_command_count)
                # pass plan to IF interpreter for execution:
                cur_plan_results: list = self.if_interpreter.execute_plan_sequence(cur_plan)
                self.log_to_self(config.log_keys["plan_results"], cur_plan_results)
                # plan result sequences cut off after the first failed plan action
                # so the sequence at this point only contains one failed action
                # or successful actions followed by a single failed action
                # get successful planned actions:
                cur_plan_successes: list = list()
                for plan_result in cur_plan_results:
                    # plan_result[2] is action_info dict, if it does not contain fail_type key, the action succeeded
                    if (
                        config.keys["fail_type"]
                        not in plan_result[config.array_indices["plan_result_action_info"]]
                    ):
                        cur_plan_successes.append(plan_result)
                # calculate the ratio of successful planned actions:
                cur_plan_success_ratio: float = len(cur_plan_successes) / cur_plan_command_count
                self.log_to_self(
                    config.log_keys["plan_command_success_ratio"], cur_plan_success_ratio
                )
                # append success ratio to history for 'bad' plan scoring:
                self.plan_success_ratio_history.append(cur_plan_success_ratio)
                # plan following:
                if len(self.plan_history) >= config.thresholds["min_plan_history_for_comparison"]:
                    prior_plan: list = self.plan_history[-2]
                    first_prior_plan_command: str = prior_plan[0]
                    plan_followed: int = 0
                    # check if this turn's action matches the next action planned in the turn before:
                    if first_prior_plan_command == if_input:
                        plan_followed = 1
                    else:
                        plan_followed = 0
                    # since plan scoring is intended to check for plan adaptation, only two-turn plan execution is
                    # covered; longer planned sequences and their execution would require this to be a lot more
                    # elaborate and recursive than this
                    self.log_to_self(
                        config.event_types["plan_followed"], plan_followed
                    )  # can be JSON'd; for easier eval
            # add IF response to dialog:
            # self.add_user_message(self.player, if_response)
            self.set_context_for(self.player, if_response)
            # record successful turn:
            self.turns.append(self.success)

    def _on_after_game(self) -> None:
        """Execute cleanup and logging after the game episode ends.

        Records the final game results including which goals were achieved and
        whether the episode finished successfully.
        """
        # record final results once game episode has ended:
        game_result: Dict[str, Any] = {
            config.keys["goal_states_achieved"]: list(self.goals_achieved),
            config.keys["game_successfully_finished"]: self.finished,
        }
        self.log_to_self(config.event_types["game_result"], game_result)

    def compute_turn_score(self) -> int:
        """Compute the score for the current turn.

        Returns:
            The number of goal states achieved during this turn (can be negative
            if goals were unachieved).
        """
        return self.turn_goal_score

    def compute_episode_score(self) -> int:
        """Compute the total score for the entire episode.

        Returns:
            The total number of goal states achieved during this episode.
        """
        return len(self.goals_achieved)


class AdventureGameScorer(GameScorer):
    """GameScorer subclass for AdventureGame.

    Processes episode records to extract turn-level and episode-level metrics.
    Computes action success/failure counts, goal achievement rates, planning metrics,
    exploration metrics, and overall benchmark scores. Writes results to score files
    for downstream analysis.
    """

    def __init__(
        self, game_name: str, experiment: Dict[str, Any], game_instance: Dict[str, Any]
    ) -> None:
        """Initialize the AdventureGameScorer.

        Args:
            game_name: Name of the game.
            experiment: Experiment configuration dictionary.
            game_instance: Game instance configuration dictionary.
        """
        super().__init__(game_name, experiment, game_instance)

    def _extract_turn_metrics(
        self, episode_interactions: Dict[str, Any]
    ) -> Tuple[
        List[Dict[str, Any]],
        List[Dict[str, int]],
        List[int],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
        bool,
        List[str],
        bool,
        str,
    ]:
        """Extract and aggregate turn-level metrics from episode interactions.

        Processes each turn's events to extract action failures, goal scores,
        hallucinations, exploration info, and planning metrics.

        Args:
            episode_interactions: Episode interaction data containing turns and events.

        Returns:
            A tuple containing:
                - turn_scores: List of turn score dictionaries
                - turn_fails: List of turn failure dictionaries
                - turn_hallucinations: List of hallucination counts per turn
                - turn_explorations: List of exploration info dictionaries
                - plan_records: List of plan record dictionaries
                - successfully_finished: Whether the episode finished successfully
                - final_goals_achieved: List of achieved goal states
                - loop_abort: Whether episode was aborted due to loop detection
                - invalid_format: Invalid format error string if any
        """
        fail_types: List[str] = config.fail_types
        plan_types: List[str] = config.plan_metrics

        turn_scores: List[Dict[str, Any]] = []
        turn_fails: List[Dict[str, int]] = []
        turn_hallucinations: List[int] = []
        turn_explorations: List[Dict[str, Any]] = []
        plan_records: List[Dict[str, Any]] = []

        invalid_format: str = ""
        turn_limit_loss: bool = False
        successfully_finished: bool = False
        final_goals_achieved: List[str] = []
        loop_abort: bool = False

        for turn_idx, turn in enumerate(episode_interactions["turns"]):
            turn_score: Dict[str, Any] = {"request_count": 1, "goal_score": 0}
            turn_fail: Dict[str, int] = {fail_type: 0 for fail_type in fail_types}
            plan_record: Dict[str, Any] = {plan_type: 0 for plan_type in plan_types}
            hallucination: int = 0
            turn_exploration: Dict[str, Any] = dict()

            for event in turn:
                action = event["action"]

                if action["type"] == config.event_types["invalid_format"]:
                    invalid_format = action["content"]
                if action["type"] == config.event_types["adventure_finished"]:
                    successfully_finished = True
                if action["type"] == config.event_types["hallucinated_finish"]:
                    hallucination = 1
                if action["type"] == config.event_types["loop_detected"]:
                    loop_abort = True
                if (
                    action["type"] == config.event_types["action_info"]
                    and action["content"]["action_type"] == config.actions["done"]
                ):
                    if not successfully_finished:
                        hallucination = 1
                if action["type"] == config.event_types["action_fail"]:
                    if action["content"][config.keys["fail_type"]] not in fail_types:
                        logger.info(
                            f"Unlisted fail type: {action['content'][config.keys['fail_type']]}"
                        )
                    turn_fail[action["content"]["phase"]] = 1
                    turn_fail[action["content"][config.keys["fail_type"]]] = 1

                if (
                    action["type"] == config.event_types["action_info"]
                    or action["type"] == config.event_types["action_fail"]
                ):
                    exploration_info = action["content"]["exploration_info"]
                    logger.info(f"exploration_info: {exploration_info}")
                    turn_exploration["epistemic_action"] = (
                        1 if exploration_info["action_epistemic"] else 0
                    )
                    turn_exploration["pragmatic_action"] = (
                        1 if exploration_info["action_pragmatic"] else 0
                    )
                    turn_exploration["effective_epistemic_gain_amount"] = exploration_info[
                        "effective_epistemic_gain_amount"
                    ]
                    turn_exploration["known_entities_ratio"] = exploration_info[
                        "known_entities_ratio"
                    ]
                    turn_exploration["visited_rooms_ratio"] = exploration_info[
                        "visited_rooms_ratio"
                    ]
                    turn_exploration["known_goal_entities_ratio"] = exploration_info[
                        "known_goal_entities_ratio"
                    ]

                if action["type"] in plan_types:
                    plan_record[action["type"]] = action["content"]
                if action["type"] == config.event_types["turn_limit_reached"]:
                    turn_limit_loss = True
                    successfully_finished = False
                if action["type"] == config.event_types["goal_status"]:
                    turn_score["goal_score"] = action["content"][config.keys["turn_goal_score"]]
                if action["type"] == config.event_types["game_result"]:
                    successfully_finished = action["content"][
                        config.keys["game_successfully_finished"]
                    ]
                    final_goals_achieved = action["content"][config.keys["goal_states_achieved"]]

            if invalid_format:
                turn_score["violated_request_count"] = 1
                turn_score["parsed_request_count"] = 0
            else:
                turn_score["violated_request_count"] = 0
                turn_score["parsed_request_count"] = 1

            turn_scores.append(turn_score)
            turn_fails.append(turn_fail)
            turn_hallucinations.append(hallucination)
            turn_explorations.append(turn_exploration)

            if turn_idx >= config.array_indices["plan_analysis_start_turn"]:
                followed_bad_plan = 0
                if (
                    plan_records[-1][config.log_keys["plan_command_success_ratio"]]
                    == config.thresholds["bad_plan_viability"]
                    and plan_record[config.event_types["plan_followed"]]
                ):
                    followed_bad_plan = 1
                plan_record["bad_plan_followed"] = followed_bad_plan

            plan_records.append(plan_record)

        return (
            turn_scores,
            turn_fails,
            turn_hallucinations,
            turn_explorations,
            plan_records,
            successfully_finished,
            final_goals_achieved,
            loop_abort,
            invalid_format,
        )

    def _log_turn_level_scores(
        self,
        episode_interactions: Dict[str, Any],
        turn_scores: List[Dict[str, Any]],
        turn_fails: List[Dict[str, int]],
        turn_hallucinations: List[int],
        turn_explorations: List[Dict[str, Any]],
        plan_records: List[Dict[str, Any]],
        invalid_format: str,
        loop_abort: bool,
    ) -> None:
        """Log all turn-level metrics to score files.

        Writes metrics for each turn including request counts, parsing errors,
        action failures, hallucinations, exploration info, and planning metrics.

        Args:
            episode_interactions: Episode interaction data containing all turns.
            turn_scores: List of turn score dictionaries (request/goal counts).
            turn_fails: List of turn failure dictionaries (by type).
            turn_hallucinations: List of hallucination counts per turn.
            turn_explorations: List of exploration info dictionaries.
            plan_records: List of plan record dictionaries.
            invalid_format: Invalid format error string if any.
            loop_abort: Whether episode was aborted due to loop detection.
        """
        fail_types: List[str] = config.fail_types
        plan_types: List[str] = config.plan_metrics

        for turn_idx in range(len(episode_interactions["turns"])):
            turn_score: Dict[str, Any] = turn_scores[turn_idx]
            turn_fail: Dict[str, int] = turn_fails[turn_idx]
            hallucination: int = turn_hallucinations[turn_idx]
            turn_exploration: Dict[str, Any] = turn_explorations[turn_idx]
            plan_record: Dict[str, Any] = plan_records[turn_idx]

            self.log_round_score(
                turn_idx, metrics.METRIC_REQUEST_COUNT, turn_score["request_count"]
            )
            self.log_round_score(
                turn_idx, metrics.METRIC_REQUEST_COUNT_PARSED, turn_score["parsed_request_count"]
            )
            self.log_round_score(
                turn_idx,
                metrics.METRIC_REQUEST_COUNT_VIOLATED,
                turn_score["violated_request_count"],
            )

            if invalid_format == config.parse_errors["command_tag_missing"]:
                self.log_round_score(turn_idx, config.parse_errors["command_tag_missing"], 1)
                self.log_round_score(turn_idx, config.parse_errors["next_actions_missing"], 0)
            elif invalid_format == config.parse_errors["next_actions_missing"]:
                self.log_round_score(turn_idx, config.parse_errors["command_tag_missing"], 0)
                self.log_round_score(turn_idx, config.parse_errors["next_actions_missing"], 1)
            else:
                self.log_round_score(turn_idx, config.parse_errors["command_tag_missing"], 0)
                self.log_round_score(turn_idx, config.parse_errors["next_actions_missing"], 0)

            self.log_round_score(turn_idx, "hallucination", hallucination)
            if loop_abort:
                self.log_round_score(turn_idx, "loop_detected", 1)

            self.log_round_score(turn_idx, "action_parsing_fail", turn_fail["parsing"])
            self.log_round_score(turn_idx, "action_resolution_fail", turn_fail["resolution"])

            for fail_type in fail_types[2:]:
                self.log_round_score(turn_idx, fail_type, turn_fail[fail_type])

            self.log_round_score(turn_idx, "goal_score", turn_score["goal_score"])

            if turn_exploration:
                self.log_round_score(
                    turn_idx, "epistemic_action", turn_exploration["epistemic_action"]
                )
                self.log_round_score(
                    turn_idx, "pragmatic_action", turn_exploration["pragmatic_action"]
                )
                self.log_round_score(
                    turn_idx,
                    "effective_epistemic_gain_amount",
                    turn_exploration["effective_epistemic_gain_amount"],
                )
                self.log_round_score(
                    turn_idx, "known_entities_ratio", turn_exploration["known_entities_ratio"]
                )
                self.log_round_score(
                    turn_idx, "visited_rooms_ratio", turn_exploration["visited_rooms_ratio"]
                )
                self.log_round_score(
                    turn_idx,
                    "known_goal_entities_ratio",
                    turn_exploration["known_goal_entities_ratio"],
                )

            for plan_type in plan_types:
                self.log_round_score(turn_idx, plan_type, plan_record[plan_type])

    def _compute_and_log_episode_metrics(
        self,
        turn_scores: List[Dict[str, Any]],
        turn_fails: List[Dict[str, int]],
        turn_hallucinations: List[int],
        successfully_finished: bool,
        final_goals_achieved: List[str],
        adventure_info: Dict[str, Any],
        plan_records: List[Dict[str, Any]],
        invalid_format: str,
        turn_limit_loss: bool,
        loop_abort: bool,
    ) -> None:
        """Compute and log episode-level metrics.

        Aggregates turn-level metrics to compute episode-level statistics including
        success rates, action failure counts, goal achievement ratios, speed metrics
        (turns over par, turn ratio), and planning metrics (plan following, viability).

        Args:
            turn_scores: List of turn score dictionaries.
            turn_fails: List of turn failure dictionaries.
            turn_hallucinations: List of hallucination counts per turn.
            successfully_finished: Whether the episode finished successfully.
            final_goals_achieved: List of goal states achieved.
            adventure_info: Adventure metadata (variant, max_turns, optimal_turns, etc.).
            plan_records: List of plan record dictionaries.
            invalid_format: Invalid format error string if any.
            turn_limit_loss: Whether the turn limit was reached.
            loop_abort: Whether episode was aborted due to loop detection.
        """
        fail_types: List[str] = config.fail_types

        # Request scores
        violated_request_count: int = sum([turn["violated_request_count"] for turn in turn_scores])
        self.log_episode_score(metrics.METRIC_REQUEST_COUNT_VIOLATED, violated_request_count)
        parsed_request_count: int = sum([turn["parsed_request_count"] for turn in turn_scores])
        self.log_episode_score(metrics.METRIC_REQUEST_COUNT_PARSED, parsed_request_count)
        request_count: int = sum([turn["request_count"] for turn in turn_scores])
        self.log_episode_score(metrics.METRIC_REQUEST_COUNT, request_count)
        self.log_episode_score(
            metrics.METRIC_REQUEST_SUCCESS_RATIO, parsed_request_count / request_count
        )

        # Hallucination scores
        hallucination_count: int = sum(turn_hallucinations)
        self.log_episode_score("hallucination_count", hallucination_count)

        # Action fail scores
        action_parsing_fail_count: int = sum([turn["parsing"] for turn in turn_fails])
        self.log_episode_score("action_parsing_fail", action_parsing_fail_count)
        action_resolution_fail_count: int = sum([turn["resolution"] for turn in turn_fails])
        self.log_episode_score("action_resolution_fail", action_resolution_fail_count)
        for fail_type in fail_types[2:]:
            type_fail_count: int = sum([turn[fail_type] for turn in turn_fails])
            self.log_episode_score(fail_type, type_fail_count)
        fail_sum: int = action_parsing_fail_count + action_resolution_fail_count
        sucessful_actions: int = parsed_request_count - fail_sum
        self.log_episode_score("successful_actions", sucessful_actions)

        # Turn limit loss
        self.log_episode_score(config.log_keys["turn_limit_loss"], 1 if turn_limit_loss else 0)

        # Speed metrics
        turn_count: int = len(turn_scores)
        optimal_turns: int = adventure_info["optimal_turns"]
        turns_over_par: int = turn_count - optimal_turns
        if successfully_finished:
            self.log_episode_score("turns_over_par", turns_over_par)
        else:
            self.log_episode_score("turns_over_par", np.nan)

        turn_range: int = adventure_info["max_turns"] - adventure_info["optimal_turns"]
        turn_ratio: float = 1 - (turns_over_par / turn_range)
        if successfully_finished:
            self.log_episode_score("turn_ratio", turn_ratio)
        else:
            self.log_episode_score("turn_ratio", np.nan)

        finish_speed_rating: float = 1 - turn_ratio
        if successfully_finished:
            self.log_episode_score("finish_speed", finish_speed_rating)
        else:
            self.log_episode_score("finish_speed", np.nan)

        # Goal achievement
        final_goal_score: int = len(final_goals_achieved)
        goal_count: int = adventure_info["goal_count"]
        achieved_ratio: float = final_goal_score / goal_count
        self.log_episode_score("achieved_goal_ratio", achieved_ratio)
        partial_success_rating: float = achieved_ratio * 100
        self.log_episode_score("achieved_goal_rating", partial_success_rating)

        # Main score
        total_success_rating: int
        if successfully_finished:
            total_success_rating = config.scores["success"]
        else:
            total_success_rating = config.scores["failure"]
        self.log_episode_score(metrics.BENCH_SCORE, total_success_rating)

        # Aborted/Success/Lose metrics
        if invalid_format or turn_limit_loss or loop_abort:
            self.log_episode_score(metrics.METRIC_ABORTED, 1)
            self.log_episode_score(metrics.METRIC_SUCCESS, 0)
            self.log_episode_score(metrics.METRIC_LOSE, 0)
        else:
            self.log_episode_score(metrics.METRIC_ABORTED, 0)
            if successfully_finished:
                self.log_episode_score(metrics.METRIC_SUCCESS, 1)
                self.log_episode_score(metrics.METRIC_LOSE, 0)
            else:
                self.log_episode_score(metrics.METRIC_SUCCESS, 0)
                self.log_episode_score(metrics.METRIC_LOSE, 1)

        # Planning metrics
        plan_followed_count: int = sum([turn["plan_followed"] for turn in plan_records[1:]])
        plan_followed_ratio: float = plan_followed_count / turn_count
        self.log_episode_score("plan_followed_ratio", plan_followed_ratio)

        plan_viability_sum: float = sum(
            [turn["plan_command_success_ratio"] for turn in plan_records]
        )
        plan_average_viability_ratio: float = plan_viability_sum / turn_count
        self.log_episode_score("plan_average_viability_ratio", plan_average_viability_ratio)

        bad_plan_followed_sum: int = sum([turn["bad_plan_followed"] for turn in plan_records])
        bad_plan_followed_ratio: float = bad_plan_followed_sum / turn_count
        self.log_episode_score("bad_plan_follow_ratio", bad_plan_followed_ratio)
        bad_plan_dismiss_ratio: float = 1 - bad_plan_followed_ratio
        self.log_episode_score("bad_plan_dismiss_ratio", bad_plan_dismiss_ratio)

    def compute_scores(self, episode_interactions: Dict[str, Any]) -> None:
        """Compute episode-level scores from interaction records.

        Main entry point for scoring. Extracts turn-level metrics, computes aggregated
        episode-level metrics, and writes all scores to the episode's score file.

        Args:
            episode_interactions: Dictionary containing episode records for the entire
                episode including all turns and events.
        """

        # NOTE: Scoring updated for clemcore 3.1.0 compatibility

        # Get adventure metadata
        adventure_info: Dict[str, Any] = episode_interactions[config.log_keys["adventure_info"]]

        # Step 1: Extract turn-level metrics from episode interactions
        (
            turn_scores,
            turn_fails,
            turn_hallucinations,
            turn_explorations,
            plan_records,
            successfully_finished,
            final_goals_achieved,
            loop_abort,
            invalid_format,
        ) = self._extract_turn_metrics(episode_interactions)

        # Compute turn_limit_loss from extracted data
        turn_limit_loss = any(
            event["action"]["type"] == config.event_types["turn_limit_reached"]
            for turn in episode_interactions["turns"]
            for event in turn
        )

        # Step 2: Log all turn-level scores
        self._log_turn_level_scores(
            episode_interactions,
            turn_scores,
            turn_fails,
            turn_hallucinations,
            turn_explorations,
            plan_records,
            invalid_format,
            loop_abort,
        )

        # Step 3: Compute and log episode-level metrics
        self._compute_and_log_episode_metrics(
            turn_scores,
            turn_fails,
            turn_hallucinations,
            successfully_finished,
            final_goals_achieved,
            adventure_info,
            plan_records,
            invalid_format,
            turn_limit_loss,
            loop_abort,
        )


class AdventureGameBenchmark(GameBenchmark):
    """GameBenchmark subclass for AdventureGame.

    Factory class that creates game masters and scorers for benchmark runs.
    Provides the game description and handles benchmark initialization.
    """

    def __init__(self, game_spec: GameSpec) -> None:
        """Initialize the AdventureGameBenchmark.

        Args:
            game_spec: Game specification containing name, path, and configuration.
        """
        super().__init__(game_spec)

    def get_description(self) -> str:
        """Get the game description.

        Returns:
            A string describing this game.
        """
        return "Interactive Fiction clemgame"

    def create_game_master(
        self, experiment: Dict[str, Any], player_models: List[Model]
    ) -> GameMaster:
        """Create a game master for running an episode.

        Args:
            experiment: Experiment configuration dictionary.
            player_models: List of model instances for the players.

        Returns:
            An AdventureGameMaster instance configured for the experiment.
        """
        return AdventureGameMaster(self.game_name, self.game_path, experiment, player_models)

    def create_game_scorer(
        self, experiment: Dict[str, Any], game_instance: Dict[str, Any]
    ) -> GameScorer:
        """Create a game scorer for computing episode scores.

        Args:
            experiment: Experiment configuration dictionary.
            game_instance: Game instance configuration dictionary.

        Returns:
            An AdventureGameScorer instance configured for the experiment.
        """
        return AdventureGameScorer(self.game_name, experiment, game_instance)


def main() -> None:
    """Main entry point for the AdventureGame module.

    Loads game instances from the configured instances file. This function is typically
    not called directly; the game is run through the clemgame framework CLI.
    """
    game_path: str = os.path.dirname(os.path.abspath(__file__))
    experiments: Dict[str, Any] = file_utils.load_json(config.paths["instances_file"], game_path)
