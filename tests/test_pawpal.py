"""Quick tests for PawPal+ core behaviors."""

from datetime import time

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task("Morning walk", time(8, 0))
    assert task.completed is False          # starts pending

    task.mark_complete()

    assert task.completed is True           # now done


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Golden Retriever")
    assert len(pet.tasks) == 0              # no tasks yet

    pet.add_task(Task("Feeding", time(9, 0)))

    assert len(pet.tasks) == 1              # count went up by one