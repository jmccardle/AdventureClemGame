import json
import os
from copy import deepcopy
from typing import List, Set, Union

import jinja2
import lark
from adv_util import fact_str_to_tuple, fact_tuple_to_str
from lark import Lark, Transformer

# PDDL ACTIONS

with open("resources/pddl_events.lark") as grammar_file:
    event_grammar = grammar_file.read()

# print(action_grammar)

event_parser = Lark(event_grammar, start="event")

test_pddl_event = "test_pddl_event.txt"

with open(test_pddl_event) as event_file:
    event_raw = event_file.read()


parsed_event = event_parser.parse(event_raw)

print(parsed_event)


class PDDLEventTransformer(Transformer):
    """PDDL event definition transformer to convert Lark parse to python dict for further use.
    Method names must match grammar rule names, thus some rules have an added -p to distinguish their name from a python
    constant/type/default term string.
    """

    def event(self, content):
        # print("event content:", content)

        event_id = content[2].value
        # print("event_id:", event_id)

        event_dict = {"event_id": content[2].value}

        for event_item in content[4:]:
            # print("event_item:", event_item)
            if "parameters" in event_item:
                event_dict["event_parameters"] = event_item["parameters"]
            if "precondition" in event_item:
                event_dict["event_precondition"] = event_item["precondition"]
            if "effect" in event_item:
                event_dict["event_effect"] = event_item["effect"]

        # print("event_dict:", event_dict)

        return event_dict

    def types(self, content):
        # print("types cont:", content)
        types_list = list()
        for cont in content:
            if "type_list_element" in cont:
                types_list.append(cont)
        types_dict = dict()
        for type_list in types_list:
            # print(type_list)
            types_dict[f'{type_list["type_list_element"]}'] = type_list["items"]
        # print("types return:", {'types': types_list})
        return {"types": types_dict}

    def type_list(self, content):
        # print(content)
        return {"type_list": content}

    def type_list_element(self, content):
        # print("type_list_item cont:", content)
        type_list_items = list()
        for item_element in content:
            if "variable" in item_element:
                type_list_items.append(item_element)
            elif type(item_element) == lark.Token:
                if item_element.type == "WORDP":
                    type_list_items.append(item_element.value)
                elif item_element.type == "DASH":
                    break

        if content[-1].type == "WS":
            cat_name = content[-2].value
        else:
            cat_name = content[-1].value
        # print("type_list_item return:", {'type_list_item': cat_name, 'items': type_list_items})
        return {"type_list_element": cat_name, "items": type_list_items}

    def parameters(self, content):
        parameter_list = None
        if type(content[0]) == lark.Token and content[0].type == "WS":
            parameter_list = content[1]
        # print("parameters:", parameter_list)

        return {"parameters": parameter_list}

    def precondition(self, content):
        # print("precond cont:", content)
        # print("precond cont:", content[1][1:])
        return {"precondition": content[1:-1]}

    def effect(self, content):
        # print("effect cont:", content)
        effect_dict = {"effect": content[1:-1]}
        # print("effect returns:", effect_dict)
        return effect_dict

    def forall(self, content):
        # print("forall cont:", content)
        iterated_object = content[2]
        # print("iterated object:", iterated_object)
        forall_body = content[4:]
        # print("forall body:", forall_body)

        forall_dict = {"forall": iterated_object, "body": forall_body}
        # print("forall returns:", forall_dict)
        return forall_dict

    def when(self, content):
        # print("when cont:", content)
        when_items = list()
        for when_item in content:
            # ignore delimiters and whitespace:
            if type(when_item) == lark.Token and when_item.type in ["WHENL", "WS"]:
                pass
            else:
                when_items.append(when_item)
        when_dict = {"when": when_items}
        # print("when returns:", when_dict)
        return when_dict

    def andp(self, content):
        # print("andp cont:", content)
        and_items = list()
        for and_item in content:
            # ignore delimiters and whitespace:
            if type(and_item) == lark.Token and and_item.type in ["ANDL", "WS"]:
                pass
            else:
                and_items.append(and_item)
        and_dict = {"and": and_items}
        # print("andp returns:", and_dict, "\n")
        return and_dict

    def orp(self, content):
        # print("orp cont:", content)
        or_items = list()
        for or_item in content:
            # ignore delimiters and whitespace:
            if type(or_item) == lark.Token and or_item.type in ["ORL", "WS"]:
                pass
            else:
                or_items.append(or_item)
        or_dict = {"or": or_items}
        # print("orp returns:", or_dict, "\n")
        return or_dict

    def notp(self, content):
        # print("notp cont:", content)
        # (not X) always wraps only one item, hence:
        return {"not": content[2]}

    def pred(self, content):
        # print("pred content:", content)
        if type(content[0]) == lark.Token:
            pred_type = content[0].value
        else:
            pred_type = content[0]
        # valence up to three, using None assignments to avoid downstream checks
        pred_arg1 = None
        pred_arg2 = None
        pred_arg3 = None

        if len(content) >= 3:
            # print('pred arg 1:', content[2])
            if type(content[2]) == lark.Token:
                pred_arg1 = content[2].value
            else:
                pred_arg1 = content[2]
        if len(content) >= 5:
            if type(content[4]) == lark.Token:
                pred_arg2 = content[4].value
            else:
                pred_arg2 = content[4]
        if len(content) >= 7:
            if type(content[6]) == lark.Token:
                pred_arg3 = content[6].value
            else:
                pred_arg3 = content[6]

        pred_dict = {
            "predicate": pred_type,
            "arg1": pred_arg1,
            "arg2": pred_arg2,
            "arg3": pred_arg3,
        }
        # print(pred_dict, "\n")

        return pred_dict

    def var(self, content):
        # print(content[0])
        return {"variable": content[0].value}

    def functions(self, content):
        # print("functions content:", content)
        functions_dict = {"functions": list()}
        for functions_item in content:
            if "function_def_predicate" in functions_item:
                functions_dict["functions"].append(functions_item)

        return functions_dict

    def function_list_element(self, content):
        # print("function_list_element content:", content)

        # for function_item in content:
        #    print("function_list_element item:", function_item)

        function_def_predicate = content[0].value
        # print("function_predicate:", function_predicate)

        function_def_variable = content[2]
        # print("function_variable:", function_variable)

        function_def_type = content[6].value
        # print("function_type:", function_type)

        function_dict = {
            "function_def_predicate": function_def_predicate,
            "function_def_variable": function_def_variable,
            "function_def_type": function_def_type,
        }

        return function_dict

    def function(self, content):
        # print("function content:", content)

        function_dict = dict()

        if content[0].type == "NUMBER":
            # print("function NUMBER:", content[0].value)
            function_dict["function_number"] = content[0].value
        else:
            function_dict["function_id"] = content[0].value
            function_dict["function_variable"] = content[2]

        # print("function_dict:", function_dict)

        return function_dict

    def equal(self, content):
        # print("greq content:", content)

        equal_dict = {"num_comp": "equal"}

        equal_dict["arg1"] = content[2]
        equal_dict["arg2"] = content[4]

        # print("greq_dict:", greq_dict)

        return equal_dict

    def greater(self, content):
        # print("greq content:", content)

        greater_dict = {"num_comp": "greater"}

        greater_dict["arg1"] = content[2]
        greater_dict["arg2"] = content[4]

        # print("greq_dict:", greq_dict)

        return greater_dict

    def greq(self, content):
        # print("greq content:", content)

        greq_dict = {"num_comp": "greq"}

        greq_dict["arg1"] = content[2]
        greq_dict["arg2"] = content[4]

        # print("greq_dict:", greq_dict)

        return greq_dict

    def less(self, content):
        # print("greq content:", content)

        less_dict = {"num_comp": "less"}

        less_dict["arg1"] = content[2]
        less_dict["arg2"] = content[4]

        # print("greq_dict:", greq_dict)

        return less_dict

    def leq(self, content):
        # print("greq content:", content)

        leq_dict = {"num_comp": "leq"}

        leq_dict["arg1"] = content[2]
        leq_dict["arg2"] = content[4]

        # print("greq_dict:", greq_dict)

        return leq_dict

    def assign(self, content):
        # print("greq content:", content)

        assign_dict = {"function_change": "assign"}

        assign_dict["arg1"] = content[2]
        assign_dict["arg2"] = content[4]

        # print("greq_dict:", greq_dict)

        return assign_dict

    def increase(self, content):
        # print("greq content:", content)

        increase_dict = {"function_change": "increase"}

        increase_dict["arg1"] = content[2]
        increase_dict["arg2"] = content[4]

        # print("greq_dict:", greq_dict)

        return increase_dict

    def decrease(self, content):
        # print("greq content:", content)

        decrease_dict = {"function_change": "decrease"}

        decrease_dict["arg1"] = content[2]
        decrease_dict["arg2"] = content[4]

        # print("greq_dict:", greq_dict)

        return decrease_dict


event_def_transformer = PDDLEventTransformer()

event_def = event_def_transformer.transform(parsed_event)

# print(event_def)


def pretty_pddl_dict(pddl_dict: dict):
    for key, value in pddl_dict.items():
        print(f"{key}:", value)


pretty_pddl_dict(event_def)
