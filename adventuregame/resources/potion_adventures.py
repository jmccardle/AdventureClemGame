"""Functions for creating potion brewing adventures."""

import numpy as np


def generate_potion_recipe(
        domain_def: dict, entity_defs: dict, tool_categories: tuple = ('stirrer', 'wand'),
        n_ingredients: int = 4, n_tools: int = 2, n_steps: int = 6, always_bucket: bool = True,
        rng_seed: int = 42):
    """Generate a potion recipe.
    By default, a potion has four ingredients and uses two tools, one always being a base liquid bucket.
    Args:
        domain_def: Domain definition dictionary to get ingredients and tools from.
        entity_defs: Entity definitions, including tool attributes 'applied_attribute' and 'applied_predicate'.
        tool_categories: Which domain types denote tools to be used. Default: ('stirrer', 'wand')
        n_ingredients: Number of ingredients per recipe. Default: 4
        n_tools: Number of tools per recipe. Default: 2
        n_steps: Number of steps per recipe. Default: 6
        always_bucket: If True, the first step is using a liquid bucket to add a base liquid to the cauldron.
            Default: True
        rng_seed: Numpy random generation seed.
    """
    rng = np.random.default_rng(seed=rng_seed)

    # get ingredient types from domain:
    ingredient_types = domain_def['types']['ingredient']
    ingredients: list = list()
    if always_bucket:
        # get liquids from corresponding bucket entities:
        starting_liquids: list = list()
        starting_buckets = domain_def['types']['bucket']
        for bucket in starting_buckets:
            starting_liquids.append(entity_defs[bucket]['produced_entity_type'])
        # add starting liquid:
        starting_liquid = rng.choice(starting_liquids)
        ingredients.append(starting_liquid)
    # sample ingredients:
    if ingredients:
        ingredients += list(rng.choice(ingredient_types, n_ingredients - 1, replace=False))
    else:
        ingredients += list(rng.choice(ingredient_types, n_ingredients, replace=False))

    # get tool types from domain:
    tool_types: list = list()
    for tool_category in tool_categories:
        tool_types += domain_def['types'][tool_category]
    # sample tools
    tools: list = list(rng.choice(tool_types, n_tools, replace=False))

    # STEPS
    steps: list = list()
    # always add first ingredient before tool steps:
    steps.append({'step_type': 'add_ingredient', 'entity_type': ingredients[0], 'instruction': str()})
    if always_bucket:
        steps[0]['instruction'] = f"pour {entity_defs[steps[0]['entity_type']]['repr_str']} into your cauldron"
    elif steps[0]['entity_type'] in domain_def['types']['liquid']:
        steps[0]['instruction'] = f"pour {entity_defs[steps[0]['entity_type']]['repr_str']} into your cauldron"
    else:
        steps[0]['instruction'] = (f"{rng.choice(['add', 'drop', 'put'])} the "
                                   f"{entity_defs[steps[0]['entity_type']]['repr_str']} into your cauldron")
    # combine remaining tools and ingredients to sample from:
    step_entities = ingredients[1:] + tools
    viable_entity_categories = ['ingredient'] + list(tool_categories)
    # remaining steps:
    for step in range(n_steps-1):
        # sample ingredient to add or tool to use:
        step_entity = rng.choice(step_entities)
        step_entities.remove(step_entity)
        step_dict = {'step_type': str(), 'entity_type': step_entity, 'instruction': str()}
        # determine step type by entity:
        for entity_category in domain_def['types']:
            if step_entity in domain_def['types'][entity_category] and entity_category in viable_entity_categories:
                if entity_category == 'ingredient':
                    step_type = "add_ingredient"
                    if step_entity in domain_def['types']['liquid']:
                        step_instruction = f"pour {entity_defs[steps[0]['entity_type']]['repr_str']} into your cauldron"
                    else:
                        step_instruction = (f"{rng.choice(['add', 'drop', 'put'])} the "
                                            f"{entity_defs[step_entity]['repr_str']} into your cauldron")
                elif entity_category in tool_categories:
                    step_type = "use_tool"
                step_dict['step_type'] = step_type

                if entity_category == 'stirrer':
                    step_instruction = (f"{rng.choice(['stir', 'agitate', 'mix'])} the liquid using a "
                                        f"{entity_defs[step_entity]['repr_str']}")
                elif entity_category == 'wand':
                    step_instruction = (f"{rng.choice(['wave', 'wiggle', 'swirl', 'use'])} a "
                                        f"{entity_defs[step_entity]['repr_str']} "
                                        f"{rng.choice(['at', 'over', 'on'])} your cauldron")
                step_dict['instruction'] = step_instruction

                steps.append(step_dict)
                break
    # RECIPE TEXT
    names = ["Asaboni's", "Holperdinger", "Fruitbat", "Jingle", "Hungro's", "Kawummio", "Espeldertatarum", "Shoowoogoo",
             "My favorite", "That odd", "Granny Weatherwax's", "Rincewind's", "Happy birthday", "Hamboning", "Corvidae",
             "Very tasty", "Absolutely incredulous", "Long-term", "Tax-evasive", "Satisfying", "Floorboard"]
    potion_name = f"{rng.choice(names)} potion"

    ingredients_repr_strs = [entity_defs[ingredient]['repr_str'] for ingredient in ingredients]
    ingredients_text: str = (f"Ingredients: {ingredients_repr_strs[0].capitalize()}, "
                             f"{', '.join(ingredients_repr_strs[1:])}.")

    steps_text: str = str()

    for step in range(len(steps)):
        steps_text += f"{step+1}. {steps[step]['instruction'].capitalize()}.\n"

    recipe_text = f"{potion_name}\n{ingredients_text}\n{steps_text}"

    potion_recipe = {'ingredients': ingredients, 'tools': tools, 'steps': steps, 'text': recipe_text}
    return potion_recipe



def create_potion_recipe_events(potion_recipe: dict,
                                domain_def: dict, entity_defs: dict, tool_categories: tuple = ('stirrer', 'wand'),
                                always_bucket: bool = True):
    """Create events for stages of a potion recipe.
    Args:
        potion_recipe: A dict holding all ingredients and steps of a potion recipe.
        domain_def: Domain definition dictionary to get ingredients and tools from.
        entity_defs: Entity definitions, including tool attributes 'applied_attribute' and 'applied_predicate'.
        always_bucket: If True, the first step is using a liquid bucket to add a base liquid to the cauldron.
            Default: True
    """
    # TODO: implement recipe event creation
    step_events: list = list()

    if always_bucket:
        step_start: int = 1
    else:
        step_start: int = 0

    for step in potion_recipe['steps']:
        print(step)
    print()

    for step_idx, step in enumerate(potion_recipe['steps'][step_start:]):
        print(step)
        step_event_dict: dict = {"type_name": f"potion_step_{step_idx+1}",
                                 "pddl": "",
                                 "event_feedback": "",
                                 "asp": ""}
        prior_ingredient: str = ""
        prior_tool: str = ""
        if step_idx == 0:
            prior_ingredient = f"{potion_recipe['steps'][0]['entity_type']}1"
            print(f"prior_ingredient is {prior_ingredient}")
        else:
            if potion_recipe['steps'][step_idx]['step_type'] == 'use_tool':
                prior_tool = f"{potion_recipe['steps'][step_idx]['entity_type']}1"
                print(f"prior_tool is {prior_tool}")
            elif potion_recipe['steps'][step_idx]['step_type'] == 'add_ingredient':
                prior_ingredient = f"{potion_recipe['steps'][step_idx]['entity_type']}1"
                print(f"prior_ingredient is {prior_ingredient}")

        current_entity = step['entity_type']

        current_entity_id = f"{step['entity_type']}1"
        print(f"current entity ID is {current_entity_id}")

        # check precondition
        precon_facts: list = list()
        if step['step_type'] == 'add_ingredient':
            # absorb into liquid event
            if step_idx == 0:
                # create liquid1
                pass
            else:
                # iterate liquid
                pass
            pass
            # after first step event:
            event_pddl = (f"(:event POTIONSTEP{step_idx + 1}\n"
                          f"\t:parameters (?l - liquid ?i - ingredient ?c - container ?r - room)\n"
                          f"\t:precondition (and\n"
                          f"\t\t(at liquid1 ?r)\n"
                          f"\t\t(at ?c ?r)\n"
                          f"\t\t(at ?i ?r)\n"
                          f"\t\t(type ?c cauldron)\n"
                          f"\t\t(type ?i {current_entity})\n"
                          f"\t\t(in ?i ?c)\n"
                          f"\t\t(in liquid1 ?c)\n"
                          f"\t\t)\n"
                          )
        elif step['step_type'] == 'use_tool':
            # swirl/puff/etc event
            if step_idx == 0:
                # create liquid1
                pass
            else:
                # iterate liquid
                pass
            pass
            event_pddl = (f"(:event POTIONSTEP{step_idx + 1}\n"
                          f"\t:parameters (l - liquid ?c - container ?r - room)\n"
                          f"\t:precondition (and\n"
                          f"\t\t(at ?l ?r)\n"
                          f"\t\t(at ?c ?r)\n"
                          f"\t\t(in ?l ?c)\n"
                          f"\t\t(type ?c cauldron)\n"
                          f"\t\t(type ?l {prior_ingredient})\n"
                          f"\t\t({cauldron_tool_predicate} ?c)"
                          f")")




if __name__ == "__main__":
    domain_def = {'domain_id': 'witchhouse',
                  'types': {
                      'room': ['kitchen', 'pantry', 'hallway', 'broomcloset', 'bedroom', 'storage', 'readingroom',
                               'workshop',
                               'cellar', 'conservatory', 'garden', 'outhouse'],
                      'entity': ['player', 'inventory', 'floor', 'table', 'sidetable', 'counter', 'icebox', 'cupboard',
                                 'wardrobe',
                                 'shelf', 'chair', 'bed', 'couch', 'broom', 'mop', 'sandwich', 'apple', 'banana',
                                 'orange', 'peach',
                                 'plate', 'book', 'pillow', 'toad', 'greenbeetle', 'redbeetle', 'eyeofnewt',
                                 'plinklecrystal',
                                 'plonklecrystal', 'plunklecrystal', 'spider', 'spiderweb', 'spideregg',
                                 'lilyofthevalley',
                                 'nightshade', 'pricklypear', 'waterbucket', 'water', 'plasmbucket', 'ectoplasm',
                                 'cauldron', 'ladle',
                                 'whisk', 'spoon', 'borpulus', 'firewand', 'icewand', 'fairywand', 'zulpowand',
                                 'liquid', 'potion',
                                 'potionrecipe'],
                      'receptacle': ['inventory', 'floor', 'table', 'sidetable', 'counter', 'icebox', 'cupboard',
                                     'wardrobe', 'shelf',
                                     'chair', 'bed', 'couch', 'cauldron'],
                      'container': ['inventory', 'icebox', 'cauldron', 'wardrobe'],
                      'beetle': ['greenbeetle', 'redbeetle'],
                      'toad': ['toad'],
                      'ingredient': ['sandwich', 'apple', 'banana', 'orange', 'peach', 'greenbeetle', 'redbeetle',
                                     'eyeofnewt',
                                     'plinklecrystal', 'plonklecrystal', 'plunklecrystal', 'spider', 'spiderweb',
                                     'spideregg',
                                     'lilyofthevalley', 'nightshade', 'pricklypear'],
                      'liquid': ['liquid', 'water', 'ectoplasm'],
                      'stirrer': ['ladle', 'whisk', 'spoon', 'borpulus'],
                      'wand': ['firewand', 'icewand', 'fairywand', 'zulpowand'],
                      'bucket': ['waterbucket', 'plasmbucket'],
                      'readable': ['potionrecipe', 'book']},
                  'functions': [
                      {'function_def_predicate': 'itemcount', 'function_def_variable': {'variable': 'i'},
                       'function_def_type': 'inventory'}]}

    entity_defs = {'player': {'repr_str': 'you', 'hidden': True, 'traits': []},
                   'inventory': {'repr_str': 'inventory', 'hidden': True, 'container': True,
                                 'traits': ['container', 'receptacle']},
                   'floor': {'repr_str': 'floor', 'hidden': True, 'support': True, 'traits': ['support', 'receptacle']},
                   'table': {'repr_str': 'table', 'support': True, 'traits': ['support', 'receptacle'],
                             'possible_adjs': ['wooden', 'metal', 'low', 'high'],
                             'standard_locations': ['kitchen', 'livingroom']},
                   'sidetable': {'repr_str': 'side table', 'support': True, 'traits': ['support', 'receptacle'],
                                 'possible_adjs': ['wooden', 'metal', 'small'],
                                 'standard_locations': ['livingroom', 'bedroom']},
                   'counter': {'repr_str': 'counter', 'support': True, 'traits': ['support', 'receptacle'],
                               'possible_adjs': ['wooden', 'metal', 'low', 'high'], 'standard_locations': ['kitchen']},
                   'icebox': {'repr_str': 'ice box', 'container': True, 'openable': True,
                              'traits': ['container', 'openable', 'receptacle'], 'possible_adjs': ['large', 'fancy'],
                              'standard_locations': ['kitchen', 'pantry']},
                   'cupboard': {'repr_str': 'cupboard', 'container': True, 'openable': True,
                                'traits': ['container', 'openable', 'receptacle'],
                                'possible_adjs': ['wooden', 'metal', 'large', 'fancy'],
                                'standard_locations': ['kitchen']},
                   'wardrobe': {'repr_str': 'wardrobe', 'container': True, 'openable': True,
                                'traits': ['container', 'openable', 'receptacle'],
                                'possible_adjs': ['wooden', 'large', 'fancy'], 'standard_locations': ['bedroom']},
                   'shelf': {'repr_str': 'shelf', 'support': True, 'traits': ['support', 'receptacle'],
                             'possible_adjs': ['wooden', 'metal', 'low', 'high'],
                             'standard_locations': ['kitchen', 'pantry', 'livingroom']},
                   'chair': {'repr_str': 'chair', 'support': True, 'traits': ['support', 'receptacle'],
                             'possible_adjs': ['comfy', 'wooden', 'padded'], 'standard_locations': ['readingroom']},
                   'bed': {'repr_str': 'bed', 'support': True, 'traits': ['support', 'receptacle'],
                           'possible_adjs': ['comfy', 'wooden'], 'standard_locations': ['bedroom']},
                   'couch': {'repr_str': 'couch', 'support': True, 'traits': ['support', 'receptacle'],
                             'possible_adjs': ['comfy', 'wooden', 'padded'], 'standard_locations': ['readingroom']},
                   'broom': {'repr_str': 'broom', 'takeable': True, 'movable': True, 'supported': True,
                             'traits': ['takeable', 'movable', 'needs_support'], 'standard_locations': ['broomcloset']},
                   'mop': {'repr_str': 'mop', 'takeable': True, 'movable': True, 'supported': True,
                           'traits': ['takeable', 'movable', 'needs_support'], 'standard_locations': ['broomcloset']},
                   'sandwich': {'repr_str': 'sandwich', 'takeable': True, 'movable': True, 'supported': True,
                                'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                'standard_locations': ['kitchen', 'pantry']},
                   'apple': {'repr_str': 'apple', 'takeable': True, 'movable': True, 'supported': True,
                             'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                             'standard_locations': ['kitchen', 'pantry']},
                   'banana': {'repr_str': 'banana', 'takeable': True, 'movable': True, 'supported': True,
                              'possible_adjs': ['ripe', 'jelly'],
                              'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                              'standard_locations': ['kitchen', 'pantry']},
                   'orange': {'repr_str': 'orange', 'takeable': True, 'movable': True, 'supported': True,
                              'possible_adjs': ['ripe', 'fresh'],
                              'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                              'standard_locations': ['kitchen', 'pantry']},
                   'peach': {'repr_str': 'peach', 'takeable': True, 'movable': True, 'supported': True,
                             'possible_adjs': ['ripe', 'fresh'],
                             'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                             'standard_locations': ['kitchen', 'pantry']},
                   'plate': {'repr_str': 'plate', 'takeable': True, 'movable': True, 'supported': True,
                             'possible_adjs': ['ceramic', 'glass'], 'traits': ['takeable', 'movable', 'needs_support'],
                             'standard_locations': ['kitchen']},
                   'book': {'repr_str': 'book', 'takeable': True, 'movable': True, 'supported': True,
                            'possible_adjs': ['old', 'thin'], 'traits': ['takeable', 'movable', 'needs_support'],
                            'standard_locations': ['readingroom', 'bedroom']},
                   'pillow': {'repr_str': 'pillow', 'takeable': True, 'movable': True, 'supported': True,
                              'possible_adjs': ['down', 'small'], 'traits': ['takeable', 'movable', 'needs_support'],
                              'standard_locations': ['bedroom']},
                   'toad': {'repr_str': 'toad', 'takeable': True, 'movable': True, 'supported': True,
                            'possible_adjs': ['warty', 'hypnotic'], 'traits': ['takeable', 'movable', 'needs_support'],
                            'standard_locations': ['bedroom', 'kitchen', 'pantry']},
                   'greenbeetle': {'repr_str': 'green beetle', 'takeable': True, 'movable': True, 'supported': True,
                                   'possible_adjs': ['shiny', 'spiny'],
                                   'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                   'standard_locations': ['garden', 'cellar']},
                   'redbeetle': {'repr_str': 'red beetle', 'takeable': True, 'movable': True, 'supported': True,
                                 'possible_adjs': ['shiny', 'spiny'],
                                 'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                 'standard_locations': ['garden', 'cellar']},
                   'eyeofnewt': {'repr_str': 'eye of newt', 'takeable': True, 'movable': True, 'supported': True,
                                 'possible_adjs': ['smelly', 'fresh'],
                                 'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                 'standard_locations': ['pantry']},
                   'plinklecrystal': {'repr_str': 'plinkle crystal', 'takeable': True, 'movable': True,
                                      'supported': True, 'possible_adjs': ['smelly', 'fresh'],
                                      'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                      'standard_locations': ['storage']},
                   'plonklecrystal': {'repr_str': 'plonkle crystal', 'takeable': True, 'movable': True,
                                      'supported': True, 'possible_adjs': ['smelly', 'fresh'],
                                      'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                      'standard_locations': ['storage']},
                   'plunklecrystal': {'repr_str': 'plunkle crystal', 'takeable': True, 'movable': True,
                                      'supported': True, 'possible_adjs': ['smelly', 'fresh'],
                                      'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                      'standard_locations': ['storage']},
                   'spider': {'repr_str': 'spider', 'takeable': True, 'movable': True, 'supported': True,
                              'possible_adjs': ['smelly', 'fresh'],
                              'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                              'standard_locations': ['storage', 'cellar']},
                   'spiderweb': {'repr_str': 'spiderweb', 'takeable': True, 'movable': True, 'supported': True,
                                 'possible_adjs': ['smelly', 'fresh'],
                                 'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                 'standard_locations': ['storage', 'cellar']},
                   'spideregg': {'repr_str': 'spider egg', 'takeable': True, 'movable': True, 'supported': True,
                                 'possible_adjs': ['smelly', 'fresh'],
                                 'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                 'standard_locations': ['storage', 'cellar']},
                   'lilyofthevalley': {'repr_str': 'lily of the valley', 'takeable': True, 'movable': True,
                                       'supported': True,
                                       'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                       'possible_adjs': ['large', 'small'],
                                       'standard_locations': ['herbarium', 'garden']},
                   'nightshade': {'repr_str': 'nightshade', 'takeable': True, 'movable': True, 'supported': True,
                                  'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                  'possible_adjs': ['large', 'small'], 'standard_locations': ['herbarium', 'garden']},
                   'pricklypear': {'repr_str': 'prickly pear', 'takeable': True, 'movable': True, 'supported': True,
                                   'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                   'possible_adjs': ['large', 'small'], 'standard_locations': ['herbarium']},
                   'waterbucket': {'repr_str': 'bucket of water', 'takeable': True, 'movable': True, 'supported': True,
                                   'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                   'possible_adjs': ['large', 'small'], 'standard_locations': ['herbarium', 'garden'],
                                   'produced_entity_type': 'water'},
                   'water': {'repr_str': 'water', 'takeable': True, 'movable': True, 'supported': True,
                             'traits': ['needs_support', 'ingredient'], 'possible_adjs': ['clear', 'fresh'],
                             'standard_locations': []},
                   'plasmbucket': {'repr_str': 'bucket of ectoplasm', 'takeable': True, 'movable': True,
                                   'supported': True, 'traits': ['takeable', 'movable', 'needs_support', 'ingredient'],
                                   'possible_adjs': ['large', 'small'], 'standard_locations': ['storage', 'garden'],
                                   'produced_entity_type': 'ectoplasm'},
                   'ectoplasm': {'repr_str': 'ectoplasm', 'takeable': True, 'movable': True, 'supported': True,
                                 'traits': ['needs_support', 'ingredient'], 'possible_adjs': ['gooey', 'fresh'],
                                 'standard_locations': []},
                   'cauldron': {'repr_str': 'cauldron', 'container': True, 'traits': ['container', 'receptacle'],
                                'possible_adjs': ['copper', 'iron', 'earthen'], 'standard_locations': ['kitchen']},
                   'ladle': {'repr_str': 'ladle', 'takeable': True, 'movable': True, 'supported': True,
                             'possible_adjs': ['rusty', 'copper'],
                             'traits': ['takeable', 'movable', 'needs_support', 'tool'],
                             'standard_locations': ['pantry', 'kitchen', 'storage'],
                             'applied_predicate': 'ladlestirred'},
                   'whisk': {'repr_str': 'whisk', 'takeable': True, 'movable': True, 'supported': True,
                             'possible_adjs': ['rusty', 'copper'],
                             'traits': ['takeable', 'movable', 'needs_support', 'tool'],
                             'standard_locations': ['pantry', 'kitchen', 'storage'], 'applied_predicate': 'whisked'},
                   'spoon': {'repr_str': 'spoon', 'takeable': True, 'movable': True, 'supported': True,
                             'possible_adjs': ['rusty', 'copper'],
                             'traits': ['takeable', 'movable', 'needs_support', 'tool'],
                             'standard_locations': ['pantry', 'kitchen', 'storage'],
                             'applied_predicate': 'spoonstirred'},
                   'borpulus': {'repr_str': 'borpulus', 'takeable': True, 'movable': True, 'supported': True,
                                'possible_adjs': ['rusty', 'copper'],
                                'traits': ['takeable', 'movable', 'needs_support', 'tool'],
                                'standard_locations': ['pantry', 'kitchen', 'storage'],
                                'applied_predicate': 'borpulusstirred'},
                   'firewand': {'repr_str': 'fire wand', 'takeable': True, 'movable': True, 'supported': True,
                                'possible_adjs': ['rusty', 'copper'],
                                'traits': ['takeable', 'movable', 'needs_support', 'tool'],
                                'standard_locations': ['workshop'], 'applied_predicate': 'hot'},
                   'icewand': {'repr_str': 'ice wand', 'takeable': True, 'movable': True, 'supported': True,
                               'possible_adjs': ['rusty', 'copper'],
                               'traits': ['takeable', 'movable', 'needs_support', 'tool'],
                               'standard_locations': ['workshop'], 'applied_predicate': 'cold'},
                   'fairywand': {'repr_str': 'fairy wand', 'takeable': True, 'movable': True, 'supported': True,
                                 'possible_adjs': ['rusty', 'copper'],
                                 'traits': ['takeable', 'movable', 'needs_support', 'tool'],
                                 'standard_locations': ['workshop'], 'applied_predicate': 'glittery'},
                   'zulpowand': {'repr_str': "zulpo's wand", 'takeable': True, 'movable': True, 'supported': True,
                                 'possible_adjs': ['rusty', 'copper'],
                                 'traits': ['takeable', 'movable', 'needs_support', 'tool'],
                                 'standard_locations': ['workshop'], 'applied_predicate': 'zulponated'},
                   'liquid': {'repr_str': 'liquid', 'takeable': True, 'movable': True, 'supported': True,
                              'possible_adjs': [], 'traits': [], 'standard_locations': []},
                   'potion': {'repr_str': 'finished potion', 'takeable': True, 'movable': True, 'supported': True,
                              'possible_adjs': [], 'traits': [], 'standard_locations': []},
                   'potionrecipe': {'repr_str': 'potion recipe', 'takeable': True, 'movable': True, 'supported': True,
                                    'possible_adjs': [], 'traits': ['readable'], 'standard_locations': ['bedroom']}}

    potion_recipe = generate_potion_recipe(domain_def, entity_defs, rng_seed=342523)

    create_potion_recipe_events(potion_recipe, domain_def, entity_defs)
