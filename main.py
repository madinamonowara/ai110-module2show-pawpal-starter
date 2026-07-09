"""CLI testing ground for PawPal+.

Demonstrates sorting, filtering, recurring regeneration, and overlap-based
conflict detection against the logic layer. Run with:  python main.py
"""

from datetime import time

from pawpal_system import Task, Pet, Owner, Scheduler


def main() -> None:
    owner = Owner(name="Alex")

    biscuit = Pet(name="Biscuit", species="Golden Retriever")
    mochi = Pet(name="Mochi", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Added deliberately OUT OF ORDER to prove sorting works.
    # Note: walk 08:00-08:30 and feeding 08:15-08:25 OVERLAP without
    # sharing a start time -- the case exact-matching used to miss.
    biscuit.add_task(Task("Evening play", time(18, 30), 20, "daily", "medium"))
    biscuit.add_task(Task("Morning walk", time(8, 0), 30, "daily", "high"))
    mochi.add_task(Task("Feeding", time(8, 15), 10, "daily", "high"))
    mochi.add_task(Task("Litter cleaning", time(19, 0), 15, "weekly", "medium"))
    biscuit.add_task(Task("Feeding", time(9, 0), 10, "daily", "high"))

    scheduler = Scheduler(owner)
    all_tasks = [task for _, task in owner.get_all_tasks()]

    # 1. Sorting by time
    print("--- Sorted by time ---")
    for t in scheduler.sort_by_time(all_tasks):
        print(f"  {t}")

    # 2. Filtering: only Mochi's tasks
    print("\n--- Filter: Mochi's tasks ---")
    for t in scheduler.filter_by_pet("Mochi"):
        print(f"  {t}")

    # 3. Filtering: only pending tasks (after completing one)
    biscuit.complete_task(biscuit.tasks[1])  # complete the morning walk
    print("\n--- Filter: still pending ---")
    pending = scheduler.filter_by_status(
        [t for _, t in owner.get_all_tasks()], completed=False
    )
    for t in pending:
        print(f"  {t}")

    # 4. Recurring: completing a daily task queued tomorrow's copy
    print("\n--- Recurring regeneration ---")
    for w in [t for t in scheduler.filter_by_pet("Biscuit")
              if t.description == "Morning walk"]:
        print(f"  Morning walk on {w.date} (completed={w.completed})")

    # 5. Conflict detection -> lightweight warnings (no crash)
    print("\n--- Conflict warnings ---")
    warnings = scheduler.conflict_warnings()
    if warnings:
        for msg in warnings:
            print(f"  WARNING: {msg}")
    else:
        print("  No conflicts.")

    # 6. Auto-resolve: shift the lower-priority task, report every move
    print("\n--- Auto-resolve conflicts ---")
    moves = scheduler.resolve_conflicts()
    for move in moves:
        print(f"  {move}")
    print(f"  Remaining conflicts: {len(scheduler.conflict_warnings())}")


if __name__ == "__main__":
    main()