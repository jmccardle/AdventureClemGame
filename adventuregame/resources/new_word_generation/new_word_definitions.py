"""Functions to create AdventureGame definitions (actions, domains, entities, rooms) with generated new-words."""
import json
from copy import deepcopy
import numpy as np
import re

from new_word_util import read_new_words_file

# ROOMS
"""
New-word room types:
- replace existing room surface form
- new, arbitrary types

Possible entities in room is part of entity def.
"""

def new_word_rooms_replace(source_definition_file_path: str, num_replace: int = 0, last_new_words_idx: int = 0,
                           seed: int = 42):
    """Replace room representation strings of an existing rooms definition with new words.
    This leaves other values intact, only changing the surface form the rooms are referred to as in the IF feedback.
    Args:
        source_definition_file_path: Path to the source definition file.
        num_replace: How many of the room definitions in the source definition file will have their representation
            replaced by new words. If this value is 0 (default), all room types will have their surface string replaced.
        last_new_words_idx: New word source index of next new word to use when iterating.
        seed: Seed number for the RNG.
    """
    # init RNG:
    rng = np.random.default_rng(seed)

    # load new words from file:
    new_words_source = read_new_words_file("new_words.tsv")
    new_word_idx = last_new_words_idx

    # load source room definitions:
    with open(source_definition_file_path, 'r', encoding='utf-8') as source_definition_file:
        source_definitions = json.load(source_definition_file)

    if num_replace > 0:
        # get random list of room def indices to replace:
        def_idx_to_replace = rng.choice(range(len(source_definitions)), size=num_replace).tolist()
    else:
        def_idx_to_replace = list(range(len(source_definitions)))

    replacement_dict = dict()
    new_room_definitions = deepcopy(source_definitions)
    for def_idx in def_idx_to_replace:
        cur_def = new_room_definitions[def_idx]
        old_repr_str = cur_def['repr_str']
        cur_def['repr_str'] = new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['NN']
        new_word_idx += 1
        replacement_dict[old_repr_str] = cur_def['repr_str']

    return new_room_definitions, new_word_idx, replacement_dict


def new_word_rooms_create(num_rooms_created: int = 4,
                          min_connections: int = 1, max_connections: int = 4, max_exit_targets: int = 4,
                          last_new_words_idx: int = 0, seed: int = 42):
        """Create rooms definition with new words.
        Args:
            num_rooms_created: Number of new-word room definitions to create.
            min_connections: Minimum number of room connections. Default: 1
            max_connections: Maximum number of room connections. Default: 4 (Beware of non-euclidian passages!)
            max_exit_targets: Maximum number of exit target room types.
            last_new_words_idx: New-word source index of next new word to use when iterating.
            seed: Seed number for the RNG.
        """
        # init RNG:
        rng = np.random.default_rng(seed)
        # load new words from file:
        new_words_source = read_new_words_file("new_words.tsv")
        new_word_idx = last_new_words_idx

        new_room_definitions = list()
        new_room_type_names = list()
        # create specified number of new word room definitions:
        for def_idx in range(num_rooms_created):
            new_room_type_dict = dict()
            new_room_type_name = new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['NN']
            new_word_idx += 1
            new_room_type_dict['type_name'] = new_room_type_name
            new_room_type_dict['repr_str'] = new_room_type_name
            new_room_type_dict['exit_targets'] = []  # left empty here due to incomplete info about all room types
            new_room_type_dict['max_connections'] = int(rng.integers(min_connections, max_connections))
            new_room_definitions.append(new_room_type_dict)
            new_room_type_names.append(new_room_type_name)
        # add exit targets after all new room types are defined:
        for new_room_type_def in new_room_definitions:
            # new room type name list without current new room type name:
            new_room_type_names_culled = deepcopy(new_room_type_names)
            new_room_type_names_culled.remove(new_room_type_def['type_name'])
            # random other-room-type exit targets:
            new_exit_targets = rng.choice(new_room_type_names_culled,
                                          size=rng.integers(1, max_exit_targets),
                                          replace=False)
            new_room_type_def['exit_targets'] = new_exit_targets.tolist()

        return new_room_definitions, new_word_idx


# ENTITIES
"""
New-word entity types:
- replace existing entity surface form
- new, arbitrary types

Mutable states:
Binary: Get two new-words, use first to make entity trait (suffixing with -able), link to action to switch between new-words states.
Trinary?
"""

def new_word_entities_replace(source_definition_file_path: str, num_replace: int = 0, last_new_words_idx: int = 0,
                              seed: int = 42):
    """Replace entities representation strings of an existing entities definition with new words.
    This leaves other values intact, only changing the surface form the entities are referred to as in the IF feedback.
    Args:
        source_definition_file_path: Path to the source definition file.
        num_replace: How many of the entity definitions in the source definition file will have their representation
            replaced by new words. If this value is 0 (default), all entity types will have their surface string
            replaced.
        last_new_words_idx: New word source index of next new word to use when iterating.
        seed: Seed number for the RNG.
    """
    # init RNG:
    rng = np.random.default_rng(seed)

    # load new words from file:
    new_words_source = read_new_words_file("new_words.tsv")
    new_word_idx = last_new_words_idx

    # load source room definitions:
    with open(source_definition_file_path, 'r', encoding='utf-8') as source_definition_file:
        source_definitions = json.load(source_definition_file)

    if num_replace > 0:
        # get random list of room def indices to replace:
        def_idx_to_replace = rng.choice(range(len(source_definitions)), size=num_replace).tolist()
    else:
        def_idx_to_replace = list(range(len(source_definitions)))

    replacement_dict = dict()
    new_entity_definitions = deepcopy(source_definitions)
    for def_idx in def_idx_to_replace:
        cur_def = new_entity_definitions[def_idx]
        old_repr_str = cur_def['repr_str']
        cur_def['repr_str'] = new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['NN']
        new_word_idx += 1
        replacement_dict[old_repr_str] = cur_def['repr_str']

    return new_entity_definitions, new_word_idx, replacement_dict


def new_word_entities_create(room_definitions: list, num_entities_created: int = 10,
                             min_std_locations: int = 1, max_std_locations: int = 3,
                             add_traits: bool = False, premade_traits: list = [], limited_trait_pool: int = 0,
                             min_traits: int = 0, max_traits: int = 3,
                             add_adjectives: bool = False, premade_adjectives: list = [], limited_adjective_pool: int = 0,
                             min_adjectives: int = 0, max_adjectives: int = 3,
                             last_new_words_idx: int = 0, seed: int = 42):
    """Create entity definitions with new words.
    Args:
        room_definitions: Room definitions list to use for entity standard locations.
        num_entities_created: Number of new-word entity definitions to create.
        min_std_locations: Minimum number of standard locations sampled from room definitions.
        max_std_locations: Maximum number of standard locations sampled from room definitions.
        add_traits: If True, new-word traits are assigned to created entities.
        limited_trait_pool: Use a pool of new-word traits of the given size for all created entity definitions. 0 will
            assign different new-word traits to each created entity definition.
        min_traits: Minimum number of traits for all created entities.
        max_traits: Maximum number of traits for all created entities.
        add_adjectives: If True, possible new-word adjectives are assigned to created entities.
        limited_adjective_pool: Use a pool of possible new-word adjectives of the given size for all created entity
            definitions. 0 will assign different new-word traits to each created entity definition.
        min_adjectives: Minimum number of possible adjectives for all created entities.
        max_adjectives: Maximum number of possible adjectives for all created entities.
        last_new_words_idx: New-word source index of next new word to use when iterating.
        seed: Seed number for the RNG.
    Returns:
        Tuple of:
        new_entity_definitions: List of new-word entity definitions.
        new_word_idx: Next unused new-word index.
        trait_pool: List of trait words used (new-words or passed premade traits).
        adjective_pool: List of adjective words used (new-words or passed premade adjectives).
    """
    # init RNG:
    rng = np.random.default_rng(seed)
    # load new words from file:
    new_words_source = read_new_words_file("new_words.tsv")
    new_word_idx = last_new_words_idx

    # traits pool:
    trait_pool = list()
    if add_traits and not premade_traits and limited_trait_pool:
        for new_word in range(limited_trait_pool):
            # trait_pool.append(new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ'])
            trait_pool.append(f"{new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ']}-able")
            new_word_idx += 1

    # adjectives pool:
    adjective_pool = list()
    if add_adjectives and not premade_adjectives and limited_adjective_pool:
        for new_word in range(limited_adjective_pool):
            adjective_pool.append(new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ'])
            new_word_idx += 1

    new_entity_definitions = list()
    new_entity_type_names = list()
    # create specified number of new word room definitions:
    for def_idx in range(num_entities_created):
        new_entity_type_dict = dict()
        new_entity_type_name = new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['NN']
        new_word_idx += 1
        new_entity_type_dict['type_name'] = new_entity_type_name
        new_entity_type_dict['repr_str'] = new_entity_type_name
        # traits:
        if add_traits:
            new_entity_type_dict['traits'] = list()
            if limited_trait_pool == 0 and not premade_traits:
                for add_trait_idx in range(min_traits, rng.integers(min_traits, max_traits)):
                    taken_new_word = f"{new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ']}-able"
                    new_word_idx += 1
                    new_entity_type_dict['traits'].append(taken_new_word)
                    trait_pool.append(taken_new_word)
            else:
                if premade_traits:
                    trait_pool = premade_traits
                new_entity_type_dict['traits']+= rng.choice(trait_pool,
                                                                 size=rng.integers(min_traits, max_traits),
                                                                 replace=False).tolist()
        # adjectives:
        if add_adjectives:
            new_entity_type_dict['possible_adjs'] = list()
            if limited_adjective_pool == 0 and not premade_adjectives:
                for add_adj_idx in range(min_adjectives, rng.integers(min_adjectives, max_adjectives)):
                    taken_new_word = new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ']
                    new_word_idx += 1
                    new_entity_type_dict['possible_adjs'].append(taken_new_word)
                    adjective_pool.append(taken_new_word)
            else:
                if premade_adjectives:
                    adjective_pool = premade_adjectives
                new_entity_type_dict['possible_adjs'] += rng.choice(adjective_pool,
                                                                 size=rng.integers(min_adjectives, max_adjectives),
                                                                 replace=False).tolist()
        # standard locations:
        new_entity_type_dict['standard_locations'] = rng.choice([room_def['type_name'] for room_def in room_definitions],
                                                                 size=rng.integers(min_std_locations, max_std_locations),
                                                                 replace=False).tolist()

        new_entity_definitions.append(new_entity_type_dict)
        new_entity_type_names.append(new_entity_type_name)

    return new_entity_definitions, new_word_idx, trait_pool, adjective_pool


# ACTIONS
"""
New-word action types:
- replace existing action surface form
- change applicable entity's new-word mutable state
    - requires connected mutability trait and transition trajectories
- ???

Explanations (to be put into initial prompts)
- "X is like Y existing action"
- circumscription: Handwritten for the small amount of existing default actions
"""

def new_word_actions_replace(source_definition_file_path: str, num_replace: int = 0, last_new_words_idx: int = 0,
                            seed: int = 42):
    """Replace action definition strings of an existing actions definition with new words.
    This leaves other values intact, only changing the surface form of the actions. The key/id of the action will not
    change, only surface grammar is adapted.
    Args:
        source_definition_file_path: Path to the source definition file.
        num_replace: How many of the action definitions in the source definition file will have their representation
            replaced by new words. If this value is 0 (default), all action types will have surface strings replaced.
        last_new_words_idx: New word source index of next new word to use when iterating.
        seed: Seed number for the RNG.
    """
    # init RNG:
    rng = np.random.default_rng(seed)

    # load new words from file:
    new_words_source = read_new_words_file("new_words.tsv")
    new_word_idx = last_new_words_idx

    # load source action definitions:
    with open(source_definition_file_path, 'r', encoding='utf-8') as source_definition_file:
        source_definitions = json.load(source_definition_file)

    if num_replace > 0:
        # get random list of action def indices to replace:
        def_idx_to_replace = rng.choice(range(len(source_definitions)), size=num_replace).tolist()
    else:
        def_idx_to_replace = list(range(len(source_definitions)))

    replacement_dict = dict()
    new_action_definitions = deepcopy(source_definitions)
    for def_idx in def_idx_to_replace:
        cur_def = new_action_definitions[def_idx]
        # get new verb:
        new_action_verb = new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['VB']
        new_word_idx += 1
        # replace surface verb portion of lark grammar snippet:
        old_lark = cur_def['lark']
        lark_verb_regex = r"\.1: (.+) WS"  # this assumes action lark grammar snippets with separated verb surface forms
        verb_forms = re.search(lark_verb_regex, old_lark)
        new_lark = old_lark.replace(verb_forms.group(1), f'"{new_action_verb}"')
        cur_def['lark'] = new_lark
        # store new word surface verb form for explanation filling:
        cur_def['new_word'] = new_action_verb

        replacement_dict[cur_def['type_name']] = new_action_verb

    return new_action_definitions, new_word_idx, replacement_dict


def new_word_actions_create(entity_definitions: list, num_actions_created: int = 6, trait_pool: list = [],
                            allowed_mutable_state_interactions: tuple = ("irreversible", "binary", "trinary"),
                            last_new_words_idx: int = 0, seed: int = 42):
    """Create action definitions with new words.
    Args:
        entity_definitions: Entity definitions list to use for entity mutable states and traits.
        num_actions_created: Number of new-word action definitions to create.
        trait_pool: List of mutable state applicability traits strings. To limit mutable state applicability traits
            used for new-word actions to a specific list, if not given, mutable state applicability traits will be taken
            from entity definitions.
        allowed_mutable_state_interactions: Tuple of string keywords determining which types of mutable state
            interactions created new word actions can result in. Actions fitting the interaction sets are created in
            order of the list. The types are:
                - irreversible: This allows an action to be created that changes the mutable state tied to a mutable
                    state applicability trait only once. Mutable state space can be singular (single mutable state is
                    not applied to entity until action is performed with it) or paired (one of two applicable mutable
                    states is initially applied to entity and when action is performed with it, the other mutable state
                    is applied).
                - binary: This allows action pairs to be created that switch between two mutable states tied to a mutable
                    state applicability trait. Mutable state space is paired (one of two applicable mutable states
                    initially applies to entity and when actions are performed with it, the other mutable state is
                    applied). Example: OPEN and CLOSE actions, with mutable state applicability trait 'openable'
                    switching entities between 'opened' and 'closed' respectively.
                - trinary: This allows action triplets to be created that switch between three mutable states tied to a
                    mutable state applicability trait. Mutable state space is chained (one of three applicable mutable
                    states initially applies to entity and when actions are performed with it, the next mutable state is
                    applied if allowed by chain order). Example: mutable state applicability trait = 'reheatable',
                    'frozen' + THAW -> 'unfrozen' + COOK -> 'edible' + FREEZE -> 'frozen'.
        last_new_words_idx: New-word source index of next new word to use when iterating.
        seed: Seed number for the RNG.
    Returns:
        Tuple of:
        new_action_definitions: List of new-word action definitions.
        new_word_idx: Next unused new-word index.
        trait_pool: List of trait words used (new-words or passed premade traits).
    """
    # init RNG:
    rng = np.random.default_rng(seed)
    # load new words from file:
    new_words_source = read_new_words_file("new_words.tsv")
    new_word_idx = last_new_words_idx

    # print("entities:", entity_definitions)

    # get mutable state applicability traits and create mutable state sets:
    mutable_state_sets = dict()
    if not trait_pool:
        traits = list()
        for entity_def in entity_definitions:
            for trait in entity_def['traits']:
                if trait not in traits:
                    traits.append(trait)
    else:
        traits = trait_pool
    # print(traits)
    trait_dict = dict()
    mutable_state_interaction_idx = 0
    for trait in traits:
        cur_trait_list = list()
        cur_trait_dict = dict()
        if allowed_mutable_state_interactions[mutable_state_interaction_idx] == "irreversible":
            mutable_set_type = rng.choice(["singular", "paired"])
            # always use mutability trait word as mutable state:
            cur_trait_list.append(trait.replace("-able", ""))
            if mutable_set_type == "paired":
                cur_trait_list.append(new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ'])
                new_word_idx += 1
                # reverse list to have other new word as initial mutable state:
                cur_trait_list.reverse()
            cur_trait_dict['interaction'] = "irreversible"
            cur_trait_dict['mutable_states'] = cur_trait_list
            cur_trait_dict['mutable_set_type'] = str(mutable_set_type)
        elif allowed_mutable_state_interactions[mutable_state_interaction_idx] == "binary":
            cur_trait_list.append(trait.replace("-able", ""))
            cur_trait_list.append(new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ'])
            new_word_idx += 1
            cur_trait_dict['interaction'] = "binary"
            cur_trait_dict['mutable_states'] = cur_trait_list
            cur_trait_dict['mutable_set_type'] = "paired"
        elif allowed_mutable_state_interactions[mutable_state_interaction_idx] == "trinary":
            cur_trait_list.append(trait.replace("-able", ""))
            cur_trait_list.append(new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ'])
            new_word_idx += 1
            cur_trait_list.append(new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['JJ'])
            new_word_idx += 1
            cur_trait_dict['interaction'] = "trinary"
            cur_trait_dict['mutable_states'] = cur_trait_list
            cur_trait_dict['mutable_set_type'] = "chained"
            # TODO?: arbitrary switching in addition to chaining?

        # loop through mutable state interaction type tuple:
        if mutable_state_interaction_idx < len(allowed_mutable_state_interactions)-1:
            mutable_state_interaction_idx += 1
        else:
            mutable_state_interaction_idx = 0

        trait_dict[trait] = cur_trait_dict

    print(trait_dict)

    # TODO?: single-action pair/chain progression?

    new_word_actions_definitions = list()
    created_actions_count = 0
    # iterate through trait dict and create actions resulting in transitions between mutable states:
    for trait, trait_features in trait_dict.items():
        if trait_features['interaction'] == "irreversible":
            # single action
            new_action = dict()

            new_word = new_words_source[list(new_words_source.keys())[new_word_idx]]['pos']['VB']
            new_word_idx += 1

            new_action['type_name'] = new_word
            # lark grammar snippet:
            # "open: OPEN thing\nOPEN.1: \"open\" WS"
            lark_string = f"{new_word}: {new_word.upper()} thing\n{new_word.upper()}.1: \"{new_word}\" WS"
            print(lark_string)

            # PDDL
            # expose values to allow feedback creation

        break

    return new_word_actions_definitions, new_word_idx

# DOMAINS
# best after other def types, as it relies on their contents existing in adventure/domain



def create_new_words_definitions_set():
    new_room_definitions, last_new_word_idx = new_word_rooms_create()
    new_entity_definitions, last_new_word_idx, trait_pool, adjective_pool = new_word_entities_create(new_room_definitions,
                                                                                                     add_traits=True, limited_trait_pool=3, min_traits=1,
                                                                                   last_new_words_idx=last_new_word_idx)
    new_action_definitions, last_new_word_idx = new_word_actions_create(new_entity_definitions,
                                                                        last_new_words_idx=last_new_word_idx)

    return new_action_definitions

if __name__ == "__main__":
    """
    new_word_rooms, replacement_dict = new_word_rooms_replace("../definitions/home_rooms.json", 2)
    print(new_word_rooms)
    print(replacement_dict)
    """
    """
    created_room_defs, last_new_word_idx = new_word_rooms_create()
    print(created_room_defs)
    """
    # new_word_actions, new_word_idx, replacement_dict = new_word_actions_replace("../definitions/basic_actions_v2-2.json")
    create_new_words_definitions_set()