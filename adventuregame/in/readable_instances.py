import json
import logging

logger = logging.getLogger(__name__)

instances_file_path = "instances.json"

with open(instances_file_path, "r", encoding="utf-8") as instances_file:
    instances = json.load(instances_file)

logger.debug("Loaded instances: %s", instances)

with open(instances_file_path, "w", encoding="utf-8") as instances_file:
    json.dump(instances, instances_file, indent=2)
