"""Functions to create AdventureGame definitions (actions, domains, entities, rooms) with generated new-words."""
import json
from copy import deepcopy
import numpy as np

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
        replacement_dict[old_repr_str] = cur_def['repr_str']
        new_word_idx += 1

    return new_room_definitions, replacement_dict, new_word_idx


def new_word_rooms_create(num_rooms_created: int = 4,
                          min_connections: int = 1, max_connections: int = 4, max_exit_targets: int = 4,
                          last_new_words_idx: int = 0, seed: int = 42):
        """Replace room representation strings of an existing rooms definition with new words.
        This leaves other values intact, only changing the surface form the rooms are referred to as in the IF feedback.
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
            new_room_type_dict['type_name'] = new_room_type_name
            new_room_type_dict['repr_str'] = new_room_type_name
            new_room_type_dict['exit_targets'] = []  # left empty here due to incomplete info about all room types
            new_room_type_dict['max_connections'] = int(rng.integers(min_connections, max_connections))
            new_room_definitions.append(new_room_type_dict)
            new_room_type_names.append(new_room_type_name)
            new_word_idx += 1
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

# ACTIONS
"""
New-word action types:
- replace existing action surface form
- change applicable entity's new-word mutable state
- ???
"""

# DOMAINS
# best after other def types, as it relies on their contents existing in adventure/domain

if __name__ == "__main__":
    """
    new_word_rooms, replacement_dict = new_word_rooms_replace("../definitions/home_rooms.json", 2)
    print(new_word_rooms)
    print(replacement_dict)
    """
    created_room_defs, last_new_word_idx = new_word_rooms_create()
    print(created_room_defs)