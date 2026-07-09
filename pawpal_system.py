"""PawPal+ logic layer.

Four classes, CLI-first (no Streamlit here):
- Task:      a single activity for one pet.
- Pet:       pet details + its own list of tasks.
- Owner:     manages multiple pets, exposes all their tasks.
- Scheduler: the "brain" that pulls, sorts, filters, and checks tasks.

The key relationship: Scheduler doesn't reach into each Pet itself. It asks
the Owner (Owner.get_all_tasks()), which aggregates across pets.
"""

from dataclasses import dataclass, field
from datetime import time, date, datetime, timedelta


# Priority ranking used when two tasks share the same time slot.
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

# How far ahead the next occurrence of a recurring task lands.
FREQUENCY_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    description: str
    time: time                          # time of day the task starts
    duration: int                       # length in minutes (required)
    frequency: str = "daily"            # "daily" | "weekly" | "once"
    priority: str = "medium"            # "high" | "medium" | "low"
    completed: bool = False
    date: date = field(default_factory=date.today)   # which day it's due

    def start_datetime(self) -> datetime:
        """Return the full start moment (date + time) for range math."""
        return datetime.combine(self.date, self.time)

    def end_datetime(self) -> datetime:
        """Return when the task finishes (start + duration)."""
        return self.start_datetime() + timedelta(minutes=self.duration)

    def overlaps(self, other: "Task") -> bool:
        """True if this task's time range collides with another's."""
        return (self.start_datetime() < other.end_datetime()
                and other.start_datetime() < self.end_datetime())

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not yet done."""
        self.completed = False

    def status_label(self) -> str:
        """Return 'done' or 'pending' for display."""
        return "done" if self.completed else "pending"

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy for the next date, or None if one-off."""
        delta = FREQUENCY_DELTA.get(self.frequency)
        if delta is None:               # e.g. "once" -> no repeat
            return None
        return Task(
            description=self.description,
            time=self.time,
            duration=self.duration,
            frequency=self.frequency,
            priority=self.priority,
            completed=False,
            date=self.date + delta,     # timedelta handles month/year rollover
        )

    def __str__(self) -> str:
        """Return a short 'HH:MM - description (Nm) [priority]' summary."""
        return (f"{self.time.strftime('%H:%M')} - {self.description} "
                f"({self.duration}m) [{self.priority}]")


@dataclass
class Pet:
    name: str
    species: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet's task list."""
        self.tasks.append(task)

    def complete_task(self, task: Task) -> None:
        """Mark a task done and, if it recurs, queue its next occurrence."""
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            self.tasks.append(upcoming)

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
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieves, sorts, filters, and checks tasks across an owner's pets."""

    def __init__(self, owner: Owner):
        """Store the owner whose pets this scheduler will plan for."""
        self.owner = owner

    # --- sorting ----------------------------------------------------------
    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by date then start time (earliest first)."""
        return sorted(tasks, key=lambda t: (t.date, t.time))

    # --- filtering --------------------------------------------------------
    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return only tasks whose completed flag matches `completed`."""
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to the pet with this name."""
        return [t for p, t in self.owner.get_all_tasks() if p.name == pet_name]

    # --- conflict detection ----------------------------------------------
    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose time ranges overlap."""
        conflicts = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].overlaps(tasks[j]):
                    conflicts.append((tasks[i], tasks[j]))
        return conflicts

    def conflict_warnings(self) -> list[str]:
        """Return human-readable warnings for overlapping tasks across pets.

        Lightweight: builds messages instead of raising, so the caller can
        display them and keep running. Empty list means no conflicts.
        """
        pairs = self.owner.get_all_tasks()
        warnings = []
        for i in range(len(pairs)):
            for j in range(i + 1, len(pairs)):
                pet_a, a = pairs[i]
                pet_b, b = pairs[j]
                if a.overlaps(b):
                    warnings.append(
                        f"Conflict: {pet_a.name}'s '{a.description}' "
                        f"({a.time.strftime('%H:%M')}-{a.end_datetime().strftime('%H:%M')}) "
                        f"overlaps {pet_b.name}'s '{b.description}' "
                        f"({b.time.strftime('%H:%M')}-{b.end_datetime().strftime('%H:%M')})."
                    )
        return warnings

    # --- conflict resolution ---------------------------------------------
    def _first_conflict(self, tasks: list[Task]) -> "tuple[Task, Task] | None":
        """Return the first overlapping pair found, or None."""
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].overlaps(tasks[j]):
                    return tasks[i], tasks[j]
        return None

    def _lower_priority(self, a: Task, b: Task) -> Task:
        """Pick which task should yield: lower priority, else the later start."""
        rank_a = PRIORITY_RANK.get(a.priority, 0)
        rank_b = PRIORITY_RANK.get(b.priority, 0)
        if rank_a != rank_b:
            return a if rank_a < rank_b else b
        return b if b.time >= a.time else a   # tie -> move the later one

    def _find_free_slot(self, task: Task, others: list[Task],
                        step_minutes: int) -> "time | None":
        """Scan forward from the task's start for the first gap that fits it."""
        same_day = [o for o in others if o is not task and o.date == task.date]
        candidate = task.start_datetime()
        end_of_day = datetime.combine(task.date, time(23, 59))
        while candidate <= end_of_day:
            cand_end = candidate + timedelta(minutes=task.duration)
            clash = any(candidate < o.end_datetime() and o.start_datetime() < cand_end
                        for o in same_day)
            if not clash:
                return candidate.time()
            candidate += timedelta(minutes=step_minutes)
        return None

    def resolve_conflicts(self, step_minutes: int = 5, max_passes: int = 20) -> list[str]:
        """Shift lower-priority clashing tasks to the next free slot.

        Returns a log of every move (or failure to move), so the owner sees
        exactly what changed rather than tasks being reordered silently.
        """
        tasks = [t for _, t in self.owner.get_all_tasks()]
        log: list[str] = []
        for _ in range(max_passes):
            conflict = self._first_conflict(tasks)
            if conflict is None:
                break                         # nothing left to resolve
            mover = self._lower_priority(*conflict)
            old = mover.time
            new_start = self._find_free_slot(mover, tasks, step_minutes)
            if new_start is None:
                log.append(f"No free slot for '{mover.description}'; "
                           f"left at {old.strftime('%H:%M')}.")
                break                         # can't place it; stop to avoid looping
            mover.time = new_start
            log.append(f"Moved '{mover.description}' from {old.strftime('%H:%M')} "
                       f"to {new_start.strftime('%H:%M')} to avoid a clash.")
        return log

    # --- display ----------------------------------------------------------
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
            lines.append(f"  {check} {task.time.strftime('%H:%M')}  "
                         f"{pet.name}: {task.description} "
                         f"({task.duration}m, {task.priority}, {task.frequency})")
        return "\n".join(lines)