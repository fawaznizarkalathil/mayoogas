from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, Any

DATA_FILE: Path = Path(__file__).parent / "productivity_data.json"

DIFFICULTY_POINTS: Dict[str, int] = {
    "easy": 10,
    "medium": 20,
    "hard": 30,
    "very hard": 50,
}


def calculate_points(base: int, status: str) -> int:
    status = (status or "").strip().lower()
    if status == "early":
        return int(base * 1.2)
    if status == "on time":
        return base
    if status == "late":
        return int(base * 0.5)
    return 0


def load_data() -> Dict[str, Any]:
    default = {"last_date": None, "streak": 0, "total_points": 0, "achievements": []}
    if not DATA_FILE.exists():
        return default
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: could not read data file ({e}). Creating a fresh dataset.")
        return default


def save_data(data: Dict[str, Any]) -> None:
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        print(f"Error: failed to save data ({e}).")


def update_streak(data: Dict[str, Any]) -> None:
    today_str = date.today().isoformat()

    if data.get("last_date") == today_str:
        return

    last_date = data.get("last_date")
    if not last_date:
        data["streak"] = 1
    else:
        try:
            last = date.fromisoformat(last_date)
            delta = (date.today() - last).days
            data["streak"] = data.get("streak", 0) + 1 if delta == 1 else 1
        except ValueError:
            data["streak"] = 1

    data["last_date"] = today_str


def check_achievements(data: Dict[str, Any]) -> None:
    achievements = data.setdefault("achievements", [])

    def unlock(name: str) -> None:
        if name not in achievements:
            achievements.append(name)
            print(f" Achievement Unlocked: {name}")

    # Only unlock First Step if the user has at least one point
    if data.get("total_points", 0) > 0:
        unlock(" First Step")

    if data.get("streak", 0) >= 3:
        unlock(" Consistency Starter")

    if data.get("streak", 0) >= 7:
        unlock(" Weekly Warrior")

    if data.get("total_points", 0) >= 100:
        unlock(" Point Master")


def prompt_int(prompt: str, default: int = 0) -> int:
    while True:
        try:
            raw = input(prompt).strip()
            if raw == "":
                return default
            val = int(raw)
            if val < 0:
                print("Please enter a non-negative number.")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")


def prompt_choice(prompt: str, choices: list[str], default: str) -> str:
    choices_lower = [c.lower() for c in choices]
    while True:
        raw = input(prompt).strip().lower()
        if raw == "":
            return default
        if raw in choices_lower:
            return raw
        print(f"Invalid choice. Expected one of: {', '.join(choices)}")


def main() -> None:
    print("\n Task Planning & Productivity Assistant")

    data = load_data()
    update_streak(data)

    print(f"\n Current Streak: {data.get('streak', 0)} day(s)")
    print(f" Achievements: {len(data.get('achievements', []))}")

    tasks = prompt_int("\nHow many tasks did you complete today? ", default=0)
    today_points = 0

    if tasks == 0:
        print("No tasks recorded today. Nice rest — see you tomorrow!")
    for i in range(tasks):
        print(f"\nTask {i+1}")
        name = input("Task name (optional): ").strip() or f"Task {i+1}"

        difficulty = prompt_choice(
            "Difficulty (easy/medium/hard/very hard) [easy]: ",
            list(DIFFICULTY_POINTS.keys()),
            default="easy",
        )

        status = prompt_choice(
            "Status (early/on time/late) [on time]: ", ["early", "on time", "late"], default="on time"
        )

        base = DIFFICULTY_POINTS.get(difficulty, 10)
        earned = calculate_points(base, status)

        today_points += earned
        print(f" Earned {earned} points for '{name}'")

    data["total_points"] = data.get("total_points", 0) + today_points

    print(f"\n Points Earned Today: {today_points}")
    print(f" Total Points: {data.get('total_points', 0)}")

    check_achievements(data)
    save_data(data)

    if data.get("achievements"):
        print("\nYour Achievements:")
        for a in data["achievements"]:
            print(f" - {a}")

    print("\n Keep the streak alive! See you tomorrow!")


if __name__ == "__main__":
    main()
