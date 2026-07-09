"""Temporary CLI testing ground for PawPal+.

Verifies the logic layer works end-to-end before wiring up Streamlit.
Run with:  python main.py
"""

from datetime import time

from pawpal_system import Task, Pet, Owner, Scheduler


def main() -> None:
    # 1. Owner
    owner = Owner(name="Alex")

    # 2. Two pets
    biscuit = Pet(name="Biscuit", species="Golden Retriever")
    mochi = Pet(name="Mochi", species="Cat")

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # 3. Tasks at different times, across both pets
    biscuit.add_task(Task("Morning walk", time(8, 0), "daily", "high"))
    biscuit.add_task(Task("Feeding", time(9, 0), "daily", "high"))
    biscuit.add_task(Task("Evening play", time(18, 30), "daily", "medium"))

    mochi.add_task(Task("Feeding", time(8, 30), "daily", "high"))
    mochi.add_task(Task("Litter cleaning", time(19, 0), "daily", "medium"))
    mochi.add_task(Task("Flea meds", time(9, 0), "weekly", "high"))

    # Mark one done to show status rendering
    biscuit.tasks[0].mark_complete()

    # 4. Print today's schedule
    scheduler = Scheduler(owner)
    print(scheduler.format_schedule())


if __name__ == "__main__":
    main()