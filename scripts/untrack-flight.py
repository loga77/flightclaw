#!/usr/bin/env python3
"""Remove one or more routes from the price tracking list."""

import argparse
import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TRACKED_FILE = os.path.join(DATA_DIR, "tracked.json")


def load_tracked():
    if os.path.exists(TRACKED_FILE):
        with open(TRACKED_FILE, "r") as f:
            return json.load(f)
    return []


def save_tracked(tracked):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TRACKED_FILE, "w") as f:
        json.dump(tracked, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Stop tracking one or more routes")
    parser.add_argument("terms", nargs="*", help="Match term(s); a route is removed if its id contains any term (case-insensitive)")
    parser.add_argument("--all", action="store_true", help="Remove ALL tracked routes")
    parser.add_argument("--list", action="store_true", help="List current tracked route ids and exit")
    args = parser.parse_args()

    tracked = load_tracked()

    if args.list or (not args.terms and not args.all):
        if not tracked:
            print("Nothing is currently tracked.")
        else:
            print(f"Currently tracking {len(tracked)} route(s):")
            for t in tracked:
                tgt = t.get("target_price")
                tgt_str = f", target {tgt}" if tgt else ""
                print(f"  {t['id']}{tgt_str}")
        if not args.list and not args.terms and not args.all:
            print("\nPass a match term to remove (e.g. NAP), or --all to clear everything.")
        return

    if args.all:
        removed = tracked
        remaining = []
    else:
        terms = [term.lower() for term in args.terms]
        removed = [t for t in tracked if any(term in t["id"].lower() for term in terms)]
        remaining = [t for t in tracked if not any(term in t["id"].lower() for term in terms)]

    if not removed:
        print("No tracked route matched. Nothing removed.")
        print("Current ids:")
        for t in tracked:
            print(f"  {t['id']}")
        sys.exit(1)

    save_tracked(remaining)
    print(f"Removed {len(removed)} route(s):")
    for t in removed:
        print(f"  {t['id']}")
    print(f"\nStill tracking {len(remaining)} route(s).")


if __name__ == "__main__":
    main()
