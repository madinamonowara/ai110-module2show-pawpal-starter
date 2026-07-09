"""PawPal+ logic layer.

Four classes, CLI-first (no Streamlit here):
- Task:      a single activity for one pet.
- Pet:       pet details + its own list of tasks.
- Owner:     manages multiple pets, exposes all their tasks.
- Scheduler: the "brain" that pulls tasks across pets and organizes them.

The key relationship: Scheduler doesn't reach into each Pet itself. It asks
the Owner (Owner.get_all_tasks()), which aggregates across pets. That keeps the
Scheduler decoupled from how pets are stored.
"""

from dataclasses import dataclass, field
from datetime import time


# Priority ranking used when two tasks share the same time slot.
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    description: str
    time: time                 # time of day the task should happen
    frequency: str = "daily"   # e.g. "daily", "weekly"
    priority: str = "medium"   # "high" | "medium" | "low"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not yet done."""
        self.completed = False

    def status_label(self) -> str:
        """Return 'done' or 'pending' for display."""
        return "done" if self.completed else "pending"

    def __str__(self) -> str:
        """Return a short 'HH:MM - description [priority]' summary."""
        stamp = self.time.strftime("%H:%M")
        return f"{stamp} - {self.description} [{self.priority}]"


@dataclass
class Pet:
    name: str
    species: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet's task list."""
        self.tasks.append(task)

    def __str__(self) -> str:
        """Return the pet's name, with species in parentheses if set."""
        extra = f" ({self.species})" if self.species else ""
        return f"{self.name}{extra}"


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets, each paired with its pet."""
        pairs: list[tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.tasks:
                pairs.append((pet, task))
        return pairs


class Scheduler:
    """Retrieves, organizes, and manages tasks across an owner's pets."""

    def __init__(self, owner: Owner):
        """Store the owner whose pets this scheduler will plan for."""
        self.owner = owner

    def todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return today's tasks sorted by time, then priority (high first)."""
        pairs = self.owner.get_all_tasks()
        pairs.sort(key=lambda pt: (pt[1].time, -PRIORITY_RANK.get(pt[1].priority, 0)))
        return pairs

    def format_schedule(self) -> str:
        """Return the day's schedule as a printable, human-readable string."""
        pairs = self.todays_schedule()
        if not pairs:
            return f"No tasks scheduled for {self.owner.name}'s pets."

        lines = [f"Today's Schedule for {self.owner.name}", "=" * 40]
        for pet, task in pairs:
            check = "[x]" if task.completed else "[ ]"
            stamp = task.time.strftime("%H:%M")
            lines.append(f"  {check} {stamp}  {pet.name}: {task.description} "
                         f"({task.priority}, {task.frequency})")
        return "\n".join(lines)