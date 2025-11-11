import json
import logging

from adv_util import fact_str_to_tuple

logger = logging.getLogger(__name__)

with open("in/instances.json", "r", encoding="utf-8") as instance_file:
    instances = json.load(instance_file)

instances = instances["experiments"][0]["game_instances"]

for instance in instances:
    initial_state_raw = instance["initial_state"]
    cur_init_state_set: set = set()
    for raw_fact in initial_state_raw:
        cur_init_state_set.add(fact_str_to_tuple(raw_fact))
    for fact in cur_init_state_set:
        if fact[0] == "needs_support":
            for fact1 in cur_init_state_set:
                if fact1[0] == "at" and fact1[1] == fact[1]:
                    for fact2 in cur_init_state_set:
                        if fact2[0] == "on" and fact2[1] == fact[1]:
                            # logger.debug("Fact2: %s", fact2)
                            if not fact2[2] == f"{fact1[2]}floor1":
                                logger.warning(
                                    "Instance %s has mismatched at/on floor: %s %s",
                                    instance["game_id"],
                                    fact1,
                                    fact2,
                                )
                        if fact2[0] == "in" and fact2[1] == fact[1]:
                            pass

    # break
