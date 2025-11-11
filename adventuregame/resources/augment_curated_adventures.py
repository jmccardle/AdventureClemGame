import json
import logging

logger = logging.getLogger(__name__)

with open("curated_home_deliver_three_adventures_v2.json") as infile:
    curated_adventures = json.load(infile)


for difficulty in curated_adventures:
    logger.info("Processing difficulty: %s", difficulty)
    for adventure in curated_adventures[difficulty]:
        adventure["prompt_template_set"] = "home_delivery"
        logger.debug("Adventure: %s", adventure)

with open("curated_home_deliver_three_adventures_v2_2.json", "w") as outfile:
    json.dump(curated_adventures, outfile)
