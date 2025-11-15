#!/usr/bin/env python3
"""
Standalone interactive player for AdventureGame.

Proof-of-concept implementation showing that human play is possible
outside the full clemgame framework.

Usage:
    python play_adventure.py                    # Play first instance
    python play_adventure.py --instance 5       # Play specific instance number
    python play_adventure.py --debug            # Show detailed metadata

TODO:
    - Add --file option for custom adventure JSON
    - Implement save/load functionality
    - Add rich metadata display
    - Support standalone mode (decouple from clemgame paths)
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path to import adventuregame modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_instance(instance_number: int = 0) -> Dict[str, Any]:
    """Load a game instance from instances.json.

    Args:
        instance_number: Index of instance to load (default: 0)

    Returns:
        Game instance dictionary

    Raises:
        FileNotFoundError: If instances.json not found
        IndexError: If instance_number is out of range
    """
    instances_path = Path(__file__).parent / "in" / "instances.json"

    if not instances_path.exists():
        raise FileNotFoundError(f"Could not find {instances_path}")

    with open(instances_path) as f:
        data = json.load(f)

    experiments = data.get("experiments", [])
    if not experiments:
        raise ValueError("No experiments found in instances.json")

    instances = experiments[0].get("game_instances", [])
    if not instances:
        raise ValueError("No game instances found in first experiment")

    if instance_number >= len(instances):
        raise IndexError(
            f"Instance {instance_number} not found (only {len(instances)} instances available)"
        )

    return instances[instance_number]


def print_metadata(
    goals_achieved: set, info: Dict[str, Any], total_goals: int, turn: int, max_turns: int
) -> None:
    """Print detailed metadata about the action result.

    Args:
        goals_achieved: Set of achieved goal states
        info: Info dictionary from process_action (either fail dict or extra_action_info)
        total_goals: Total number of goals required
        turn: Current turn number
        max_turns: Maximum allowed turns
    """
    print("\n" + "=" * 50)
    print("METADATA")
    print("=" * 50)
    print(f"Turn: {turn}/{max_turns}")

    # Action type and success status
    if "action_type" in info:
        print(f"Action Type: {info['action_type']}")
        status = "✓ SUCCESS"
    elif "fail_type" in info:
        print(f"Failure Type: {info.get('fail_type', 'unknown')}")
        status = "✗ FAILED"
    else:
        status = "? UNKNOWN"
    print(f"Action Status: {status}")

    # Goal progress
    achieved = len(goals_achieved)
    required = total_goals
    progress = "⬛" * achieved + "⬜" * (required - achieved)
    print(f"Goals Progress: [{achieved}/{required}] {progress}")

    # Exploration info (if available)
    if "exploration_info" in info:
        exp = info["exploration_info"]
        print(f"Visited Rooms: {len(exp.get('visited_rooms', []))}")
        print(f"Known Entities Ratio: {exp.get('known_entities_ratio', 0):.2%}")

    print("=" * 50 + "\n")


def play_game(instance: Dict[str, Any], debug: bool = False) -> None:
    """Run interactive game loop.

    Args:
        instance: Game instance dictionary
        debug: If True, show detailed metadata after each action
    """
    from adventuregame.if_wrapper import AdventureIFInterpreter

    print("\n" + "=" * 70)
    print("ADVENTUREGAME - Interactive Player")
    print("=" * 70)

    print("\n" + instance["prompt"])
    print("\nGame ID:", instance.get("game_id", "unknown"))
    print("Variant:", instance.get("variant", "unknown"))
    print("Max Turns:", instance.get("max_turns", "unknown"))
    print("Optimal Turns:", instance.get("optimal_turns", "unknown"))

    if debug:
        print("\n" + "-" * 70)
        print("INITIAL STATE (sample):")
        for i, fact in enumerate(instance.get("initial_state", [])[:10]):
            print(f"  {fact}")
        if len(instance.get("initial_state", [])) > 10:
            print(f"  ... and {len(instance['initial_state']) - 10} more facts")

        print("\nGOAL STATE:")
        for goal in instance.get("goal_state", []):
            print(f"  {goal}")
        print("-" * 70)

    # Initialize interpreter
    game_path = str(Path(__file__).parent)
    interpreter = AdventureIFInterpreter(game_path, instance)

    print("\n" + "=" * 70)
    print("STARTING GAME")
    print("=" * 70)
    print("Commands: Type actions, or 'quit' to exit")
    print("=" * 70 + "\n")

    # Show initial room description
    initial_desc = interpreter.get_full_room_desc()
    print(initial_desc)

    turn = 0
    max_turns = instance.get("max_turns", 20)
    total_goals = len(instance.get("goal_state", []))

    while turn < max_turns:
        turn += 1
        action = input(f"\n[Turn {turn}] > ")

        if action.lower() in ["quit", "exit", "q"]:
            print("\nExiting game...")
            break

        # Process action - returns (goals_achieved, feedback, info)
        goals_achieved, feedback, info = interpreter.process_action(action)

        # Show feedback
        print("\n" + feedback)

        # Show metadata if debug mode
        if debug:
            print_metadata(goals_achieved, info, total_goals, turn, max_turns)

        # Check if goal achieved
        if len(goals_achieved) >= total_goals:
            print("\n" + "=" * 70)
            print("🎉 GOAL ACHIEVED!")
            print("=" * 70)
            print(f"Turns taken: {turn}")
            print(f"Optimal turns: {instance.get('optimal_turns', 'unknown')}")
            break

        # Check if done action was used
        if info.get("done_action"):
            print("\n" + "=" * 70)
            if len(goals_achieved) >= total_goals:
                print("🎉 GOAL ACHIEVED!")
            else:
                print("GAME ENDED (goals not fully achieved)")
            print("=" * 70)
            print(f"Turns taken: {turn}")
            print(f"Goals achieved: {len(goals_achieved)}/{total_goals}")
            break

    if turn >= max_turns:
        print("\n" + "=" * 70)
        print("TURN LIMIT REACHED")
        print("=" * 70)
        print(f"Goals achieved: {len(goals_achieved)}/{total_goals}")


def main() -> None:
    """Run the interactive adventure game player."""
    parser = argparse.ArgumentParser(
        description="Interactive player for AdventureGame",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python play_adventure.py                    # Play first instance
  python play_adventure.py --instance 5       # Play instance #5
  python play_adventure.py --debug            # Show detailed metadata

See docs/INTERACTIVE_ROADMAP.md for full implementation roadmap.
        """,
    )

    parser.add_argument(
        "--instance",
        type=int,
        default=0,
        help="Instance number to play (default: 0)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed metadata after each action",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available instances and exit",
    )

    args = parser.parse_args()

    # List instances mode
    if args.list:
        try:
            instances_path = Path(__file__).parent / "in" / "instances.json"
            with open(instances_path) as f:
                data = json.load(f)
            instances = data["experiments"][0]["game_instances"]
            print(f"\nAvailable instances: {len(instances)}")
            for i, inst in enumerate(instances):
                variant = inst.get("variant", "unknown")
                game_id = inst.get("game_id", "unknown")
                print(f"  {i}: game_id={game_id}, variant={variant}")
        except Exception as e:
            print(f"Error listing instances: {e}")
        return

    # Load and play instance
    try:
        instance = load_instance(args.instance)
        play_game(instance, debug=args.debug)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
