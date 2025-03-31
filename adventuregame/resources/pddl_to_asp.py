"""
Functions to convert PDDL definitions to ASP for instance generation.
"""

import lark
from lark import Lark

from pddl_util import PDDLActionTransformer, PDDLDomainTransformer

# TODO: properly save mutable states and mutability state in definitions; attach to entity definitions or add to domain as in proper PDDL?

# TODO?: expand PDDL domain usage to incorporate mutable states better; ie types tied to mutable states centrally?

# load lark grammars and init lark transformers:
with open("pddl_actions.lark", 'r', encoding='utf-8') as actions_grammar_file:
    action_def_grammar = actions_grammar_file.read()
action_def_parser = Lark(action_def_grammar, start="action")

action_def_transformer = PDDLActionTransformer()

with open("pddl_domain.lark", 'r', encoding='utf-8') as domain_grammar_file:
    domain_def_grammar = domain_grammar_file.read()
domain_def_parser = Lark(domain_def_grammar, start="define")

domain_def_transformer = PDDLDomainTransformer()


example_pddl_action = {
    "pddl": "(:action OPEN\n    :parameters (?e - openable ?r - room ?p - player)\n    :precondition (and\n        (at ?p ?r)\n        (at ?e ?r)\n        (closed ?e)\n        )\n    :effect (and\n        (open ?e)\n        (not (closed ?e))\n        (forall (?c - takeable)\n            (when\n                (in ?c ?e)\n                (and\n                    (accessible ?c)\n                )\n            )\n        )\n    )\n)",
    "pddl_parameter_mapping": {
      "?e": ["arg1"],
      "?r": ["current_player_room"],
      "?p": ["player"]
    },
    "asp": "{ action_t(TURN,open,THING):at_t(TURN,THING,ROOM),closed_t(TURN,THING) } 1 :- turn(TURN), at_t(TURN,player1,ROOM), not turn_limit(TURN).\nopen_t(TURN+1,THING) :- action_t(TURN,open,THING).\nopen_t(TURN+1,THING) :- turn(TURN), open_t(TURN,THING), not action_t(TURN,close,THING)."
}

example_pddl_action2 = {
    "type_name": "mator",
    "lark": "mator: MATOR thing\nMATOR.1: \"mator\" WS",
    "pddl": "(:action MATOR\n    :parameters (?e - dented-able ?r - room ?p - player)\n    :precondition (and\n        (at ?p ?r)\n        (at ?e ?r)\n)\n    :effect (and\n        (dented ?e)\n    )\n)"}

sample_pddl = "(:action OPEN\n    :parameters (?e - openable ?r - room ?p - player)\n    :precondition (and\n        (at ?p ?r)\n        (at ?e ?r)\n        (closed ?e)\n        )\n    :effect (and\n        (open ?e)\n        (not (closed ?e))\n        (forall (?c - takeable)\n            (when\n                (in ?c ?e)\n                (and\n                    (accessible ?c)\n                )\n            )\n        )\n    )\n)"

"""
(:action OPEN\n
    :parameters (?e - openable ?r - room ?p - player)\n
    :precondition (and\n
            (at ?p ?r)\n
            (at ?e ?r)\n
            (closed ?e)\n
            )\n
    :effect (and\n
        (open ?e)\n
        (not (closed ?e))\n
        (forall (?c - takeable)\n
            (when\n
                (in ?c ?e)\n
                (and\n
                    (accessible ?c)\n
                )\n
            )\n
        )\n
    )\n
)


(:action MATOR\n
    :parameters (?e - dented-able ?r - room ?p - player)\n
    :precondition (and\n
        (at ?p ?r)\n
        (at ?e ?r)\n
    )\n
    :effect (and\n
        (dented ?e))\n
    )\n
)
"""
# TODO: fix spurious ) in generated new-words action pddl:
"""
lark.exceptions.UnexpectedCharacters: No terminal matches '
' in the current parser context, at line 9 col 6

    )
     ^
"""


# TODO: incorporate parameter portion and match types to make singular irreversible new-word action work

"""
{ action_t(TURN,open,THING):at_t(TURN,THING,ROOM),closed_t(TURN,THING) } 1 :- turn(TURN), at_t(TURN,player1,ROOM), not turn_limit(TURN).\n
open_t(TURN+1,THING) :- action_t(TURN,open,THING).\n  # if the last turn action was OPEN, thing is open next turn
open_t(TURN+1,THING) :- turn(TURN), open_t(TURN,THING), not action_t(TURN,close,THING).  # if a thing is open and the current-turn action is not CLOSE, it is still open next turn
"""

"""
Potential action at turn:
{ action_t(TURN,ACTION_TYPE,THING):at_t(TURN,THING,ROOM),closed_t(TURN,THING) } 1 :- turn(TURN), at_t(TURN,player1,ROOM), not turn_limit(TURN).\n
-> precondition
"""

# PARAMETERS AND PRECONDITION

# parsed_action_pddl = action_def_parser.parse(sample_pddl)
# parsed_action_pddl = action_def_parser.parse(example_pddl_action['pddl'])
parsed_action_pddl = action_def_parser.parse(example_pddl_action2['pddl'])
processed_action_pddl = action_def_transformer.transform(parsed_action_pddl)

# print(processed_action_pddl)
# print(processed_action_pddl['precondition'])

params = processed_action_pddl['parameters']
# print(params)
important_params = list()
for param in params['type_list']:
    if param['type_list_element'] not in ['player', 'room']:
        important_params.append(param)
# print(important_params)

param_asp_template = "MUTABILITY(THING)"
mutability_asp_strings = [f"{mutability['type_list_element']}(THING)" for mutability in important_params]
# print(mutability_asp_strings)


# TODO: make mutability type facts in base ASP solver script

# catch at condition to put on ASP RHS:
# check for default at facts (player at same as argument)
precon = processed_action_pddl['precondition']
# print(precon[0])
precon_and = precon[0]['and']
# print(precon_and)
important_precon_facts = list()
for precon_fact in precon_and:
    if precon_fact['predicate'] == "at":
        # assume that there are no interactions with other locations and the at conditions are always the same
        continue
    else:
        important_precon_facts.append(precon_fact)
# print(important_precon_facts)
important_precon_mutables = [precon['predicate'] for precon in important_precon_facts]
# print(important_precon_mutables)


asp_potential_action = "{ action_t(TURN,ACTION_TYPE,THING):at_t(TURN,THING,ROOM),PRECON_FACTS } 1 :- turn(TURN), at_t(TURN,player1,ROOM), not turn_limit(TURN)."
asp_potential_action = asp_potential_action.replace("ACTION_TYPE", processed_action_pddl['action_name'])


"_t(TURN,THING)"

mutable_asp_strings = [f"{mutable}_t(TURN,THING)" for mutable in important_precon_mutables]

asp_potential_action = asp_potential_action.replace("PRECON_FACTS", ",".join(mutability_asp_strings+mutable_asp_strings))

# print(asp_potential_action)

# EFFECT

effect = processed_action_pddl['effect'][0]['and']

print(effect)

effect_predicates = list()
for effect_pred in effect:
    effect_predicates.append(effect_pred['predicate'])


asp_next_turn_effect = "MUTABLE_FACTS :- action_t(TURN,ACTION_TYPE,THING)."
asp_next_turn_effect = asp_next_turn_effect.replace("ACTION_TYPE", processed_action_pddl['action_name'])

"open_t(TURN+1,THING)"

# effect_fact_asp_strings = [f"{pred}_t(TURN,THING)" for pred in effect_predicates]
effect_fact_asp_strings = [f"{pred}_t(TURN+1,THING)" for pred in [effect_pred['predicate'] for effect_pred in effect]]
# print(effect_fact_asp_strings)

asp_next_turn_effect = asp_next_turn_effect.replace("MUTABLE_FACTS", ",".join(effect_fact_asp_strings))
print(asp_next_turn_effect)

# TODO: third ASP rule for actions that change mutable fact