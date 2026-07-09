"""Quick tests for PawPal+ core behaviors."""

from datetime import time

from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task("Morning walk", time(8, 0), 30)
    assert task.completed is False          # starts pending

    task.mark_complete()

    assert task.completed is True           # now done


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Golden Retriever")
    assert len(pet.tasks) == 0              # no tasks yet

    pet.add_task(Task("Feeding", time(9, 0), 10))

    assert len(pet.tasks) == 1              # count went up by one


def test_sort_by_time_orders_earliest_first():
    owner = Owner(name="Alex")
    scheduler = Scheduler(owner)
    tasks = [
        Task("Evening play", time(18, 30), 20),
        Task("Morning walk", time(8, 0), 30),
        Task("Midday feed", time(12, 0), 10),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [t.time for t in ordered] == [time(8, 0), time(12, 0), time(18, 30)]


def test_completing_daily_task_queues_next_occurrence():
    pet = Pet(name="Biscuit")
    walk = Task("Morning walk", time(8, 0), 30, frequency="daily")
    pet.add_task(walk)

    pet.complete_task(walk)

    assert len(pet.tasks) == 2             # original + tomorrow's copy
    original, upcoming = pet.tasks
    assert original.completed is True
    assert upcoming.completed is False
    assert upcoming.date > original.date   # scheduled for a later day


def test_overlapping_tasks_conflict_even_at_different_start_times():
    owner = Owner(name="Alex")
    biscuit = Pet(name="Biscuit")
    mochi = Pet(name="Mochi")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)
    # Walk runs 08:00-08:30; feeding starts at 08:15 -> genuine overlap.
    biscuit.add_task(Task("Walk", time(8, 0), 30))
    mochi.add_task(Task("Feeding", time(8, 15), 10))

    warnings = Scheduler(owner).conflict_warnings()

    assert len(warnings) == 1
    assert "Conflict" in warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit")
    owner.add_pet(pet)
    # Walk ends exactly when feeding starts (08:30) -> no overlap.
    pet.add_task(Task("Walk", time(8, 0), 30))
    pet.add_task(Task("Feeding", time(8, 30), 10))

    assert Scheduler(owner).conflict_warnings() == []


def test_resolve_conflicts_moves_lower_priority_to_free_slot():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", time(8, 0), 30, priority="high"))
    pet.add_task(Task("Feeding", time(8, 15), 10, priority="low"))
    scheduler = Scheduler(owner)

    log = scheduler.resolve_conflicts()

    assert len(log) == 1                       # one move was made and reported
    assert scheduler.conflict_warnings() == []  # clash is gone afterward
    feeding = next(t for t in pet.tasks if t.description == "Feeding")
    assert feeding.time == time(8, 30)         # lower-priority task moved forward