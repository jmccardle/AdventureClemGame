"""
Generate instances for adventuregame.

Creates files in ./in
"""

import logging
import os

import clemcore
import numpy as np
from clemcore.clemgame import GameInstanceGenerator
from config_loader import get_config
from tqdm import tqdm

logger = logging.getLogger(__name__)

config = get_config()


class AdventureGameInstanceGenerator(GameInstanceGenerator):
    def __init__(self):
        super().__init__(os.path.dirname(os.path.abspath(__file__)))
        self.rng = np.random.default_rng(seed=config.random_seeds["default"])

    def on_generate(self, raw_adventures_files: list, variants: list = ["basic"]):
        """Generate both basic and planning variant instances from raw adventures.
        Args:
            raw_adventures_files: List of file names of the JSON files containing raw adventures data.
            variants: Which variants to make instances for. Currently supported variants are "basic", "planning",
                "basic_invlimit", "planning_invlimit".
        """
        for raw_adventures_file in raw_adventures_files:
            # load raw adventures:
            adventures = self.load_json(f"{config.paths['resources_dir']}{raw_adventures_file}")
            # get difficulties:
            difficulties = list(adventures.keys())
            # get adventure type from first raw adventure:
            adventure_type = adventures[difficulties[0]][0]["adventure_type"]

            for difficulty in difficulties:
                # BASIC
                if "basic" in variants:
                    # create basic experiment:
                    basic_experiment = self.add_experiment(f"{adventure_type}_basic_{difficulty}")

                    for adventure_id in tqdm(range(len(adventures[difficulty]))):
                        goal_str = adventures[difficulty][adventure_id]["goal"]

                        initial_state = adventures[difficulty][adventure_id]["initial_state"]
                        goal_state = adventures[difficulty][adventure_id]["goal_state"]

                        # load the prepared initial prompt:
                        if (
                            adventures[difficulty][adventure_id]["prompt_template_set"]
                            == config.adventure_types["home_delivery"]
                        ):
                            basic_prompt = self.load_template(
                                config.paths["prompt_templates"]["basic"]
                            )
                        elif (
                            config.adventure_types["new_words"]
                            in adventures[difficulty][adventure_id]["prompt_template_set"]
                        ):
                            basic_prompt = self.load_template(
                                config.paths["prompt_templates"]["new_words"]
                            )
                        elif (
                            config.adventure_types["potion_brewing"]
                            in adventures[difficulty][adventure_id]["prompt_template_set"]
                        ):
                            basic_prompt = self.load_template(
                                config.paths["prompt_templates"]["potion_brewing"]
                            )
                        # Replace the goal in the templated initial prompt
                        instance_prompt = basic_prompt.replace(
                            config.template_placeholders["goal"], goal_str
                        )
                        # fill in new-words explanations:
                        if (
                            adventures[difficulty][adventure_id]["prompt_template_set"]
                            == config.adventure_types["new_words_created"]
                        ):
                            # BASIC full new-words just lists the available
                            new_word_actions = list()
                            for action_def in adventures[difficulty][adventure_id][
                                "action_definitions"
                            ]:
                                if (
                                    action_def["type_name"]
                                    not in config.actions["excluded_from_shuffle"]
                                ):
                                    new_word_actions.append(action_def["type_name"])
                            # shuffle available new-word actions to mitigate first action with first new-word object
                            # matching one of the generated goals:
                            new_word_actions_remap = np.arange(len(new_word_actions))
                            self.rng.shuffle(new_word_actions_remap)
                            new_word_actions = [
                                new_word_actions[remap_idx] for remap_idx in new_word_actions_remap
                            ]
                            # fill in new-words actions template placeholder:
                            explanation_str = (
                                f"In addition to common actions, you can "
                                f"{', '.join(new_word_actions[:-1])} and {new_word_actions[-1]}."
                            )
                            instance_prompt = instance_prompt.replace(
                                config.template_placeholders["new_words_explanations"],
                                explanation_str,
                            )

                        if (
                            adventures[difficulty][adventure_id]["prompt_template_set"]
                            == config.adventure_types["new_words_replace_explanation"]
                        ):
                            # list the available new-word action and add its explanation
                            new_word_actions = adventures[difficulty][adventure_id][
                                "replacement_dict"
                            ]["actions"]
                            new_word_action = [
                                action
                                for action in adventures[difficulty][adventure_id][
                                    "action_definitions"
                                ]
                                if action["type_name"] == list(new_word_actions.keys())[0]
                            ][0]
                            # fill in new-words actions template placeholder:
                            explanation_str = (
                                f"In addition to common actions, you can {list(new_word_actions.values())[0]}. "
                                f"{new_word_action['explanation']}"
                            )

                            instance_prompt = instance_prompt.replace(
                                config.template_placeholders["new_words_explanations"],
                                explanation_str,
                            )

                        if (
                            adventures[difficulty][adventure_id]["prompt_template_set"]
                            == config.adventure_types["new_words_replace_no_explanation"]
                        ):
                            new_word_actions = list(
                                adventures[difficulty][adventure_id]["replacement_dict"][
                                    "actions"
                                ].values()
                            )
                            # shuffle available new-word actions to mitigate first action with first new-word object
                            # matching one of the generated goals:
                            new_word_actions_remap = np.arange(len(new_word_actions))
                            self.rng.shuffle(new_word_actions_remap)
                            new_word_actions = [
                                new_word_actions[remap_idx] for remap_idx in new_word_actions_remap
                            ]
                            # fill in new-words actions template placeholder:
                            explanation_str = (
                                f"In addition to common actions, you can "
                                f"{', '.join(new_word_actions[:-1])} and {new_word_actions[-1]}."
                            )
                            instance_prompt = instance_prompt.replace(
                                config.template_placeholders["new_words_explanations"],
                                explanation_str,
                            )

                        # Create a game instance
                        game_instance = self.add_game_instance(basic_experiment, adventure_id)
                        game_instance["variant"] = config.variants["basic"]  # game parameters
                        game_instance["prompt"] = instance_prompt  # game parameters
                        # game_instance["goal_str"] = goal_str  # game parameters
                        # game_instance["first_room_str"] = first_room_str  # game parameters
                        game_instance["initial_state"] = initial_state  # game parameters
                        game_instance["goal_state"] = goal_state  # game parameters
                        game_instance["max_turns"] = adventures[difficulty][adventure_id][
                            "bench_turn_limit"
                        ]  # game parameters
                        game_instance["optimal_turns"] = adventures[difficulty][adventure_id][
                            "optimal_turns"
                        ]  # game parameters
                        game_instance["optimal_solution"] = adventures[difficulty][adventure_id][
                            "optimal_solution"
                        ]  # game parameters
                        game_instance["optimal_commands"] = adventures[difficulty][adventure_id][
                            "optimal_commands"
                        ]  # game parameters
                        game_instance["action_definitions"] = adventures[difficulty][adventure_id][
                            "action_definitions"
                        ]  # game parameters
                        game_instance["room_definitions"] = adventures[difficulty][adventure_id][
                            "room_definitions"
                        ]  # game parameters
                        game_instance["entity_definitions"] = adventures[difficulty][adventure_id][
                            "entity_definitions"
                        ]  # game parameters
                        if adventure_type == config.adventure_types["home_deliver_three"]:
                            game_instance["domain_definitions"] = adventures[difficulty][
                                adventure_id
                            ][
                                "domain_definitions"
                            ]  # game parameters
                        # elif adventure_type == "new-words_created":
                        elif config.adventure_types["new_words"] in adventure_type:
                            game_instance["domain_definitions"] = adventures[difficulty][
                                adventure_id
                            ][
                                "domain_definitions"
                            ]  # game parameters
                            # TODO: de-hardcode the domain difference; just add full domain to home delivery too
                        if adventure_type == config.adventure_types["potion_brewing"]:
                            game_instance["domain_definitions"] = adventures[difficulty][
                                adventure_id
                            ][
                                "domain_definitions"
                            ]  # game parameters
                            game_instance["event_definitions"] = adventures[difficulty][
                                adventure_id
                            ]["event_definitions"]

                # BASIC with pre-exploration

                if "basic_preexplore" in variants:
                    if config.adventure_types["new_words"] in adventure_type:
                        continue
                    # create basic pre-explore experiment:
                    basic_experiment = self.add_experiment(
                        f"{adventure_type}_basic_preexplore_{difficulty}"
                    )

                    for adventure_id in tqdm(range(len(adventures[difficulty]))):
                        goal_str = adventures[difficulty][adventure_id]["goal"]

                        initial_state = adventures[difficulty][adventure_id]["initial_state"]
                        goal_state = adventures[difficulty][adventure_id]["goal_state"]

                        # load the prepared initial prompt:
                        if (
                            adventures[difficulty][adventure_id]["prompt_template_set"]
                            == config.adventure_types["home_delivery"]
                        ):
                            basic_prompt = self.load_template(
                                config.paths["prompt_templates"]["basic"]
                            )
                        # Replace the goal in the templated initial prompt
                        instance_prompt = basic_prompt.replace(
                            config.template_placeholders["goal"], goal_str
                        )
                        # Create a game instance
                        game_instance = self.add_game_instance(basic_experiment, adventure_id)
                        game_instance["variant"] = config.variants[
                            "basic_preexplore"
                        ]  # game parameters
                        game_instance["prompt"] = instance_prompt  # game parameters
                        # game_instance["goal_str"] = goal_str  # game parameters
                        # game_instance["first_room_str"] = first_room_str  # game parameters
                        game_instance["initial_state"] = initial_state  # game parameters
                        game_instance["goal_state"] = goal_state  # game parameters
                        game_instance["max_turns"] = adventures[difficulty][adventure_id][
                            "bench_turn_limit"
                        ]  # game parameters
                        game_instance["optimal_turns"] = adventures[difficulty][adventure_id][
                            "optimal_turns"
                        ]  # game parameters
                        game_instance["optimal_solution"] = adventures[difficulty][adventure_id][
                            "optimal_solution"
                        ]  # game parameters
                        game_instance["optimal_commands"] = adventures[difficulty][adventure_id][
                            "optimal_commands"
                        ]  # game parameters
                        game_instance["action_definitions"] = adventures[difficulty][adventure_id][
                            "action_definitions"
                        ]  # game parameters
                        game_instance["room_definitions"] = adventures[difficulty][adventure_id][
                            "room_definitions"
                        ]  # game parameters
                        game_instance["entity_definitions"] = adventures[difficulty][adventure_id][
                            "entity_definitions"
                        ]  # game parameters
                        if adventure_type == config.adventure_types["home_deliver_three"]:
                            game_instance["domain_definitions"] = adventures[difficulty][
                                adventure_id
                            ][
                                "domain_definitions"
                            ]  # game parameters
                        game_instance["visiting_turns"] = adventures[difficulty][adventure_id][
                            "visiting_turns"
                        ]  # game parameters
                        game_instance["visiting_solution"] = adventures[difficulty][adventure_id][
                            "visiting_solution"
                        ]  # game parameters
                        game_instance["visiting_commands"] = adventures[difficulty][adventure_id][
                            "visiting_commands"
                        ]  # game parameters

                # PLANNING

                if "planning" in variants:
                    if config.adventure_types["new_words"] in adventure_type:
                        continue
                    # create an experiment:
                    planning_experiment = self.add_experiment(
                        f"{adventure_type}_planning_{difficulty}"
                    )

                    # Load the prepared initial prompt
                    # planning_prompt = self.load_template("resources/initial_prompts/plan_prompt")
                    planning_prompt = self.load_template(config.paths["prompt_templates"]["plan"])

                    for adventure_id in tqdm(range(len(adventures[difficulty]))):
                        goal_str = adventures[difficulty][adventure_id]["goal"]
                        # first_room_str = adventures[adventure_id]['first_room']

                        initial_state = adventures[difficulty][adventure_id]["initial_state"]
                        goal_state = adventures[difficulty][adventure_id]["goal_state"]

                        # Replace the goal in the templated initial prompt
                        instance_prompt = planning_prompt.replace(
                            config.template_placeholders["goal"], goal_str
                        )
                        # instance_prompt = instance_prompt.replace("$FIRST_ROOM$", first_room_str)

                        # Create a game instance
                        game_instance = self.add_game_instance(planning_experiment, adventure_id)
                        game_instance["variant"] = config.variants["plan"]  # game parameters
                        game_instance["prompt"] = instance_prompt  # game parameters
                        # game_instance["goal_str"] = goal_str  # game parameters
                        # game_instance["first_room_str"] = first_room_str  # game parameters
                        game_instance["initial_state"] = initial_state  # game parameters
                        game_instance["goal_state"] = goal_state  # game parameters
                        game_instance["max_turns"] = adventures[difficulty][adventure_id][
                            "bench_turn_limit"
                        ]  # game parameters
                        game_instance["optimal_turns"] = adventures[difficulty][adventure_id][
                            "optimal_turns"
                        ]  # game parameters
                        game_instance["optimal_solution"] = adventures[difficulty][adventure_id][
                            "optimal_solution"
                        ]  # game parameters
                        game_instance["optimal_commands"] = adventures[difficulty][adventure_id][
                            "optimal_commands"
                        ]  # game parameters
                        game_instance["action_definitions"] = adventures[difficulty][adventure_id][
                            "action_definitions"
                        ]  # game parameters
                        game_instance["room_definitions"] = adventures[difficulty][adventure_id][
                            "room_definitions"
                        ]  # game parameters
                        game_instance["entity_definitions"] = adventures[difficulty][adventure_id][
                            "entity_definitions"
                        ]  # game parameters
                        game_instance["domain_definitions"] = adventures[difficulty][adventure_id][
                            "domain_definitions"
                        ]  # game parameters

                # PLANNING with pre-exploration

                if "planning_preexplore" in variants:
                    if config.adventure_types["new_words"] in adventure_type:
                        continue
                    # create an experiment:
                    planning_experiment = self.add_experiment(
                        f"{adventure_type}_planning_preexplore_{difficulty}"
                    )

                    # Load the prepared initial prompt
                    # planning_prompt = self.load_template("resources/initial_prompts/plan_prompt")
                    planning_prompt = self.load_template(config.paths["prompt_templates"]["plan"])

                    for adventure_id in tqdm(range(len(adventures[difficulty]))):
                        goal_str = adventures[difficulty][adventure_id]["goal"]
                        # first_room_str = adventures[adventure_id]['first_room']

                        initial_state = adventures[difficulty][adventure_id]["initial_state"]
                        goal_state = adventures[difficulty][adventure_id]["goal_state"]

                        # Replace the goal in the templated initial prompt
                        instance_prompt = planning_prompt.replace(
                            config.template_placeholders["goal"], goal_str
                        )
                        # instance_prompt = instance_prompt.replace("$FIRST_ROOM$", first_room_str)

                        # Create a game instance
                        game_instance = self.add_game_instance(planning_experiment, adventure_id)
                        game_instance["variant"] = config.variants[
                            "plan_preexplore"
                        ]  # game parameters
                        game_instance["prompt"] = instance_prompt  # game parameters
                        # game_instance["goal_str"] = goal_str  # game parameters
                        # game_instance["first_room_str"] = first_room_str  # game parameters
                        game_instance["initial_state"] = initial_state  # game parameters
                        game_instance["goal_state"] = goal_state  # game parameters
                        game_instance["max_turns"] = adventures[difficulty][adventure_id][
                            "bench_turn_limit"
                        ]  # game parameters
                        game_instance["optimal_turns"] = adventures[difficulty][adventure_id][
                            "optimal_turns"
                        ]  # game parameters
                        game_instance["optimal_solution"] = adventures[difficulty][adventure_id][
                            "optimal_solution"
                        ]  # game parameters
                        game_instance["optimal_commands"] = adventures[difficulty][adventure_id][
                            "optimal_commands"
                        ]  # game parameters
                        game_instance["action_definitions"] = adventures[difficulty][adventure_id][
                            "action_definitions"
                        ]  # game parameters
                        game_instance["room_definitions"] = adventures[difficulty][adventure_id][
                            "room_definitions"
                        ]  # game parameters
                        game_instance["entity_definitions"] = adventures[difficulty][adventure_id][
                            "entity_definitions"
                        ]  # game parameters
                        game_instance["domain_definitions"] = adventures[difficulty][adventure_id][
                            "domain_definitions"
                        ]  # game parameters
                        game_instance["visiting_turns"] = adventures[difficulty][adventure_id][
                            "visiting_turns"
                        ]  # game parameters
                        game_instance["visiting_solution"] = adventures[difficulty][adventure_id][
                            "visiting_solution"
                        ]  # game parameters
                        game_instance["visiting_commands"] = adventures[difficulty][adventure_id][
                            "visiting_commands"
                        ]  # game parameters

                # BASIC INVENTORY LIMIT

                if "basic_invlimit" in variants:
                    if config.adventure_types["new_words"] in adventure_type:
                        continue
                    # create an experiment:
                    basic_invlimit_experiment = self.add_experiment(
                        f"{adventure_type}_basic_{difficulty}_{config.output_settings['experiment_suffixes']['invlimit']}"
                    )

                    # Load the prepared initial prompt
                    basic_invlimit_prompt = self.load_template(
                        config.paths["prompt_templates"]["basic_invlimit"]
                    )

                    for adventure_id in tqdm(range(len(adventures[difficulty]))):
                        goal_str = adventures[difficulty][adventure_id]["goal"]

                        initial_state = adventures[difficulty][adventure_id]["initial_state"]
                        goal_state = adventures[difficulty][adventure_id]["goal_state"]

                        # Replace the goal in the templated initial prompt
                        instance_prompt = basic_invlimit_prompt.replace(
                            config.template_placeholders["goal"], goal_str
                        )
                        # instance_prompt = instance_prompt.replace("$FIRST_ROOM$", first_room_str)

                        # Create a game instance
                        game_instance = self.add_game_instance(
                            basic_invlimit_experiment, adventure_id
                        )
                        game_instance["variant"] = config.variants["basic"]  # game parameters
                        game_instance["prompt"] = instance_prompt  # game parameters
                        # game_instance["goal_str"] = goal_str  # game parameters
                        # game_instance["first_room_str"] = first_room_str  # game parameters
                        game_instance["initial_state"] = initial_state  # game parameters
                        game_instance["goal_state"] = goal_state  # game parameters
                        game_instance["max_turns"] = adventures[difficulty][adventure_id][
                            "bench_turn_limit"
                        ]  # game parameters
                        game_instance["optimal_turns"] = adventures[difficulty][adventure_id][
                            "optimal_turns"
                        ]  # game parameters
                        game_instance["optimal_solution"] = adventures[difficulty][adventure_id][
                            "optimal_solution"
                        ]  # game parameters
                        game_instance["optimal_commands"] = adventures[difficulty][adventure_id][
                            "optimal_commands"
                        ]  # game parameters

                        game_instance["action_definitions"] = [
                            config.paths["definition_files"]["invlimit_actions"]
                        ]  # game parameters

                        game_instance["room_definitions"] = adventures[difficulty][adventure_id][
                            "room_definitions"
                        ]  # game parameters
                        game_instance["entity_definitions"] = adventures[difficulty][adventure_id][
                            "entity_definitions"
                        ]  # game parameters

                        game_instance["domain_definitions"] = [
                            config.paths["definition_files"]["invlimit_domain"]
                        ]  # game parameters

                # PLANNING INVENTORY LIMIT
                if "planning_invlimit" in variants:
                    if config.adventure_types["new_words"] in adventure_type:
                        continue
                    # create an experiment:
                    planning_invlimit_experiment = self.add_experiment(
                        f"{adventure_type}_planning_{difficulty}_{config.output_settings['experiment_suffixes']['invlimit']}"
                    )

                    # Load the prepared initial prompt
                    planning_invlimit_prompt = self.load_template(
                        config.paths["prompt_templates"]["plan_invlimit"]
                    )

                    for adventure_id in tqdm(range(len(adventures[difficulty]))):
                        goal_str = adventures[difficulty][adventure_id]["goal"]

                        initial_state = adventures[difficulty][adventure_id]["initial_state"]
                        goal_state = adventures[difficulty][adventure_id]["goal_state"]

                        # Replace the goal in the templated initial prompt
                        instance_prompt = planning_invlimit_prompt.replace(
                            config.template_placeholders["goal"], goal_str
                        )
                        # instance_prompt = instance_prompt.replace("$FIRST_ROOM$", first_room_str)

                        # Create a game instance
                        game_instance = self.add_game_instance(
                            planning_invlimit_experiment, adventure_id
                        )
                        game_instance["variant"] = config.variants["plan"]  # game parameters
                        game_instance["prompt"] = instance_prompt  # game parameters
                        # game_instance["goal_str"] = goal_str  # game parameters
                        # game_instance["first_room_str"] = first_room_str  # game parameters
                        game_instance["initial_state"] = initial_state  # game parameters
                        game_instance["goal_state"] = goal_state  # game parameters
                        game_instance["max_turns"] = adventures[difficulty][adventure_id][
                            "bench_turn_limit"
                        ]  # game parameters
                        game_instance["optimal_turns"] = adventures[difficulty][adventure_id][
                            "optimal_turns"
                        ]  # game parameters
                        game_instance["optimal_solution"] = adventures[difficulty][adventure_id][
                            "optimal_solution"
                        ]  # game parameters
                        game_instance["optimal_commands"] = adventures[difficulty][adventure_id][
                            "optimal_commands"
                        ]  # game parameters

                        game_instance["action_definitions"] = [
                            config.paths["definition_files"]["invlimit_actions"]
                        ]  # game parameters

                        game_instance["room_definitions"] = adventures[difficulty][adventure_id][
                            "room_definitions"
                        ]  # game parameters
                        game_instance["entity_definitions"] = adventures[difficulty][adventure_id][
                            "entity_definitions"
                        ]  # game parameters

                        game_instance["domain_definitions"] = [
                            config.paths["definition_files"]["invlimit_domain"]
                        ]  # game parameters

                        game_instance["visiting_turns"] = adventures[difficulty][adventure_id][
                            "visiting_turns"
                        ]  # game parameters
                        game_instance["visiting_solution"] = adventures[difficulty][adventure_id][
                            "visiting_solution"
                        ]  # game parameters
                        game_instance["visiting_commands"] = adventures[difficulty][adventure_id][
                            "visiting_commands"
                        ]  # game parameters


if __name__ == "__main__":
    # The resulting instances.json is automatically saved to the "in" directory of the game folder
    # AdventureGameInstanceGenerator().generate(raw_adventures_files=["generated_new-words_created_adventures"])
    """
    AdventureGameInstanceGenerator().generate(raw_adventures_files=[
        "curated_home_deliver_three_adventures_v2_2_a",
        "generated_new-words_home-delivery_easy_adventures",
        "generated_new-words_home-delivery_medium_adventures",
        "generated_new-words_created_adventures"],
        variants=["basic", "basic_preexplore", "planning", "planning_preexplore", "basic_invlimit", "planning_invlimit"]
    )
    """
    AdventureGameInstanceGenerator().generate(
        raw_adventures_files=["generated_potion_brewing_adventures"], variants=["basic"]
    )
