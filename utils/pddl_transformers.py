"""
PDDL transformer classes for AdventureGame.

This module contains Lark transformer classes for parsing PDDL action definitions,
domain definitions, and event definitions. These transformers convert parsed Lark
trees into Python dictionaries for further processing.

All transformer classes inherit from PDDLBaseTransformer which provides shared
methods for common PDDL constructs like forall, when, and, or, not, predicates, etc.
"""

import lark
from lark import Transformer


class PDDLBaseTransformer(Transformer):
    """
    PDDL parse transformer for shared base methods/grammar rules.

    Method names must match grammar rule names, thus some rules have an added -p
    to distinguish their name from a Python constant/type/default term string.
    """

    def forall(self, content):
        """Transform forall construct."""
        iterated_object = content[2]
        forall_body = content[4:]
        forall_dict = {"forall": iterated_object, "body": forall_body}
        return forall_dict

    def when(self, content):
        """Transform when construct."""
        when_items = list()
        for when_item in content:
            # ignore delimiters and whitespace:
            if type(when_item) == lark.Token and when_item.type in ["WHENL", "WS"]:
                pass
            else:
                when_items.append(when_item)
        when_dict = {"when": when_items}
        return when_dict

    def andp(self, content):
        """Transform and construct."""
        and_items = list()
        for and_item in content:
            # ignore delimiters and whitespace:
            if type(and_item) == lark.Token and and_item.type in ["ANDL", "WS"]:
                pass
            else:
                and_items.append(and_item)
        and_dict = {"and": and_items}
        return and_dict

    def orp(self, content):
        """Transform or construct."""
        or_items = list()
        for or_item in content:
            # ignore delimiters and whitespace:
            if type(or_item) == lark.Token and or_item.type in ["ORL", "WS"]:
                pass
            else:
                or_items.append(or_item)
        or_dict = {"or": or_items}
        return or_dict

    def notp(self, content):
        """Transform not construct."""
        # (not X) always wraps only one item, hence:
        return {"not": content[2]}

    def type_list(self, content):
        """Transform type list."""
        return {"type_list": content}

    def type_list_element(self, content):
        """Transform type list element."""
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

        return {"type_list_element": cat_name, "items": type_list_items}

    def pred(self, content):
        """Transform predicate."""
        if type(content[0]) == lark.Token:
            pred_type = content[0].value
        else:
            pred_type = content[0]

        # valence up to three, using None assignments to avoid downstream checks
        pred_arg1 = None
        pred_arg2 = None
        pred_arg3 = None

        if len(content) >= 3:
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

        return pred_dict

    def var(self, content):
        """Transform variable."""
        return {"variable": content[0].value}

    def function(self, content):
        """Transform function."""
        function_dict = dict()

        if content[0].type == "NUMBER":
            function_dict["function_number"] = content[0].value
        else:
            function_dict["function_id"] = content[0].value
            function_dict["function_variable"] = content[2]

        return function_dict

    def equal(self, content):
        """Transform equal comparison."""
        equal_dict = {"num_comp": "equal"}
        equal_dict["arg1"] = content[2]
        equal_dict["arg2"] = content[4]
        return equal_dict

    def greater(self, content):
        """Transform greater than comparison."""
        greater_dict = {"num_comp": "greater"}
        greater_dict["arg1"] = content[2]
        greater_dict["arg2"] = content[4]
        return greater_dict

    def greq(self, content):
        """Transform greater than or equal comparison."""
        greq_dict = {"num_comp": "greq"}
        greq_dict["arg1"] = content[2]
        greq_dict["arg2"] = content[4]
        return greq_dict

    def less(self, content):
        """Transform less than comparison."""
        less_dict = {"num_comp": "less"}
        less_dict["arg1"] = content[2]
        less_dict["arg2"] = content[4]
        return less_dict

    def leq(self, content):
        """Transform less than or equal comparison."""
        leq_dict = {"num_comp": "leq"}
        leq_dict["arg1"] = content[2]
        leq_dict["arg2"] = content[4]
        return leq_dict

    def assign(self, content):
        """Transform assign function change."""
        assign_dict = {"function_change": "assign"}
        assign_dict["arg1"] = content[2]
        assign_dict["arg2"] = content[4]
        return assign_dict

    def increase(self, content):
        """Transform increase function change."""
        increase_dict = {"function_change": "increase"}
        increase_dict["arg1"] = content[2]
        increase_dict["arg2"] = content[4]
        return increase_dict

    def decrease(self, content):
        """Transform decrease function change."""
        decrease_dict = {"function_change": "decrease"}
        decrease_dict["arg1"] = content[2]
        decrease_dict["arg2"] = content[4]
        return decrease_dict


class PDDLActionTransformer(PDDLBaseTransformer):
    """
    PDDL action definition transformer to convert Lark parse to python dict.

    Method names must match grammar rule names, thus some rules have an added -p
    to distinguish their name from a Python constant/type/default term string.
    """

    def action(self, content):
        """Transform action definition."""
        action_def_dict = {"action_name": content[1].value.lower()}

        for cont in content:
            if type(cont) == lark.Token:
                pass
            else:
                if "parameters" in cont:
                    action_def_dict["parameters"] = cont["parameters"]
                elif "precondition" in cont:
                    action_def_dict["precondition"] = cont["precondition"]
                elif "effect" in cont:
                    action_def_dict["effect"] = cont["effect"]

        return action_def_dict

    def parameters(self, content):
        """Transform parameters."""
        parameter_list = None
        if type(content[0]) == lark.Token and content[0].type == "WS":
            parameter_list = content[1]
        return {"parameters": parameter_list}

    def precondition(self, content):
        """Transform precondition."""
        return {"precondition": content[1:-1]}

    def effect(self, content):
        """Transform effect."""
        effect_dict = {"effect": content[1:-1]}
        return effect_dict


class PDDLDomainTransformer(PDDLBaseTransformer):
    """
    PDDL domain definition transformer to convert Lark parse to python dict.

    Method names must match grammar rule names, thus some rules have an added -p
    to distinguish their name from a Python constant/type/default term string.
    """

    def define(self, content):
        """Transform domain definition."""
        domain_def_dict = dict()

        for cont in content:
            if type(cont) == lark.Token:
                pass
            else:
                if "domain_id" in cont:
                    domain_def_dict["domain_id"] = cont["domain_id"]
                if "types" in cont:
                    domain_def_dict["types"] = cont["types"]
                if "functions" in cont:
                    domain_def_dict["functions"] = cont["functions"]
                if "event_id" in cont:
                    if "events" not in domain_def_dict:
                        domain_def_dict["events"] = [cont]
                    else:
                        domain_def_dict["events"].append(cont)

        return domain_def_dict

    def domain_id(self, content):
        """Transform domain identifier."""
        return {"domain_id": content[-1].value}

    def types(self, content):
        """Transform types definition."""
        types_list = list()
        for cont in content:
            if "type_list_element" in cont:
                types_list.append(cont)
        types_dict = dict()
        for type_list in types_list:
            types_dict[f'{type_list["type_list_element"]}'] = type_list["items"]
        return {"types": types_dict}

    def parameters(self, content):
        """Transform parameters."""
        parameter_list = None
        if type(content[0]) == lark.Token and content[0].type == "WS":
            parameter_list = content[1]
        return {"parameters": parameter_list}

    def precondition(self, content):
        """Transform precondition."""
        return {"precondition": content[1:-1]}

    def effect(self, content):
        """Transform effect."""
        effect_dict = {"effect": content[1:-1]}
        return effect_dict

    def functions(self, content):
        """Transform functions definition."""
        functions_dict = {"functions": list()}
        for functions_item in content:
            if "function_def_predicate" in functions_item:
                functions_dict["functions"].append(functions_item)
        return functions_dict

    def function_list_element(self, content):
        """Transform function list element."""
        function_def_predicate = content[0].value
        function_def_variable = content[2]
        function_def_type = content[6].value

        function_dict = {
            "function_def_predicate": function_def_predicate,
            "function_def_variable": function_def_variable,
            "function_def_type": function_def_type,
        }

        return function_dict

    def event(self, content):
        """Transform event definition (in domain context)."""
        event_dict = {"event_id": content[2].value}

        for event_item in content[4:]:
            if "parameters" in event_item:
                event_dict["event_parameters"] = event_item["parameters"]
            if "precondition" in event_item:
                event_dict["event_precondition"] = event_item["precondition"]
            if "effect" in event_item:
                event_dict["event_effect"] = event_item["effect"]

        return event_dict


class PDDLEventTransformer(PDDLBaseTransformer):
    """
    PDDL event definition transformer to convert Lark parse to python dict.

    Method names must match grammar rule names, thus some rules have an added -p
    to distinguish their name from a Python constant/type/default term string.
    """

    def event(self, content):
        """Transform event definition."""
        event_dict = {"event_id": content[2].value}

        for event_item in content[4:]:
            if "parameters" in event_item:
                event_dict["parameters"] = event_item["parameters"]
            if "precondition" in event_item:
                event_dict["precondition"] = event_item["precondition"]
            if "effect" in event_item:
                event_dict["effect"] = event_item["effect"]

        return event_dict

    def types(self, content):
        """Transform types definition."""
        types_list = list()
        for cont in content:
            if "type_list_element" in cont:
                types_list.append(cont)
        types_dict = dict()
        for type_list in types_list:
            types_dict[f'{type_list["type_list_element"]}'] = type_list["items"]
        return {"types": types_dict}

    def parameters(self, content):
        """Transform parameters."""
        parameter_list = None
        if type(content[0]) == lark.Token and content[0].type == "WS":
            parameter_list = content[1]
        return {"parameters": parameter_list}

    def precondition(self, content):
        """Transform precondition."""
        return {"precondition": content[1:-1]}

    def effect(self, content):
        """Transform effect."""
        effect_dict = {"effect": content[1:-1]}
        return effect_dict

    def functions(self, content):
        """Transform functions definition."""
        functions_dict = {"functions": list()}
        for functions_item in content:
            if "function_def_predicate" in functions_item:
                functions_dict["functions"].append(functions_item)
        return functions_dict

    def function_list_element(self, content):
        """Transform function list element."""
        function_def_predicate = content[0].value
        function_def_variable = content[2]
        function_def_type = content[6].value

        function_dict = {
            "function_def_predicate": function_def_predicate,
            "function_def_variable": function_def_variable,
            "function_def_type": function_def_type,
        }

        return function_dict
