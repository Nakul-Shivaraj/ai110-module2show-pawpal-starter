"""
PawPal+ - Pet Care Management System
pawpal_system.py: Core logic layer (classes, scheduling, algorithms)
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date, datetime
import uuid


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    category: str               # "walk" | "feeding" | "medication" | "grooming" | "enrichment"
    duration_minutes: int
    priority: int               # 1 (low) to 5 (high)
    recurrence: str = "daily"   # "daily" | "weekly" | "none"
    preferred_time: Optional[str] = None  # e.g. "08:00"
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def is_due_today(self) -> bool:
        """Return True if this task should appear in today's plan."""
        if self.recurrence == "daily":
            return True
        if self.recurrence == "weekly":
            # Treat every Monday as the weekly recurrence day
            return date.today().weekday() == 0
        if self.recurrence == "none":
            return not self.completed
        return False

    def to_dict(self) -> dict:
        """Serialize the task to a plain dictionary (for display / storage)."""
        return {
            "task_id":          self.task_id,
            "name":             self.name,
            "category":         self.category,
            "duration_minutes": self.duration_minutes,
            "priority":         self.priority,
            "recurrence":       self.recurrence,
            "preferred_time":   self.preferred_time,
            "completed":        self.completed,
        }

    def __str__(self) -> str:
        time_str = f" @ {self.preferred_time}" if self.preferred_time else ""
        return (
            f"[P{self.priority}] {self.name} ({self.category})"
            f" — {self.duration_minutes} min{time_str}"
            f" | repeats: {self.recurrence}"
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet's task list, preventing duplicate IDs."""
        existing_ids = {t.task_id for t in self.tasks}
        if task.task_id in existing_ids:
            raise ValueError(f"Task '{task.name}' (id={task.task_id}) already exists.")
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove the first task matching the given name."""
        for i, t in enumerate(self.tasks):
            if t.name.lower() == task_name.lower():
                self.tasks.pop(i)
                return
        raise ValueError(f"No task named '{task_name}' found for {self.name}.")

    def get_tasks(self) -> list:
        """Return all tasks for this pet."""
        return list(self.tasks)

    def get_tasks_due_today(self) -> list:
        """Return only tasks that are due today."""
        return [t for t in self.tasks if t.is_due_today()]

    def __str__(self) -> str:
        return (
            f"{self.name} ({self.species}, age {self.age})"
            + (f" — Notes: {self.health_notes}" if self.health_notes else "")
        )


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    email: str
    available_hours: str        # e.g. "07:00-21:00"
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        names = [p.name.lower() for p in self.pets]
        if pet.name.lower() in names:
            raise ValueError(f"A pet named '{pet.name}' is already registered.")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        for i, p in enumerate(self.pets):
            if p.name.lower() == pet_name.lower():
                self.pets.pop(i)
                return
        raise ValueError(f"No pet named '{pet_name}' found.")

    def get_pets(self) -> list:
        """Return all pets belonging to this owner."""
        return list(self.pets)

    def get_all_tasks(self) -> list:
        """
        Return all tasks across all pets as (pet_name, Task) tuples.
        This is how the Scheduler retrieves tasks from the Owner.
        """
        result = []
        for pet in self.pets:
            for task in pet.get_tasks():
                result.append((pet.name, task))
        return result

    def available_minutes(self) -> int:
        """Parse available_hours (e.g. '07:00-21:00') and return total minutes."""
        try:
            start_str, end_str = self.available_hours.split("-")
            start = datetime.strptime(start_str.strip(), "%H:%M")
            end   = datetime.strptime(end_str.strip(),   "%H:%M")
            delta = end - start
            return max(0, int(delta.total_seconds() // 60))
        except ValueError:
            return 480  # default: 8 hours if parsing fails

    def __str__(self) -> str:
        pet_names = ", ".join(p.name for p in self.pets) or "none"
        return (
            f"Owner: {self.name} ({self.email})"
            f" | Available: {self.available_hours}"
            f" | Pets: {pet_names}"
        )


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Retrieves all due tasks from an Owner's pets, sorts them by priority,
    fits them within the available time budget, and explains the plan.
    """

    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled_tasks: list = []   # (pet_name, Task)
        self._dropped_tasks:  list = []   # tasks that didn't fit

    def _get_due_tasks(self) -> list:
        """Collect all tasks due today across every pet."""
        result = []
        for pet in self.owner.get_pets():
            for task in pet.get_tasks_due_today():
                result.append((pet.name, task))
        return result

    def sort_by_priority(self, tasks: list) -> list:
        """
        Sort (pet_name, Task) pairs:
          primary   — priority descending (5 = most urgent)
          secondary — preferred_time ascending (earlier = sooner), None goes last
        """
        def sort_key(pair):
            _, task = pair
            time_val = task.preferred_time or "99:99"
            return (-task.priority, time_val)

        return sorted(tasks, key=sort_key)

    def check_conflicts(self, tasks: list) -> list:
        """
        Walk through the priority-sorted list and keep tasks until the
        available time budget is exhausted. Dropped tasks are stored in
        self._dropped_tasks for the explanation.
        """
        budget = self.owner.available_minutes()
        accepted, dropped = [], []
        used = 0

        for pet_name, task in tasks:
            if used + task.duration_minutes <= budget:
                accepted.append((pet_name, task))
                used += task.duration_minutes
            else:
                dropped.append((pet_name, task))

        self._dropped_tasks = dropped
        return accepted

    def generate_plan(self) -> list:
        """
        Full pipeline:
          1. Collect tasks due today
          2. Sort by priority (and preferred_time)
          3. Fit within time budget
          4. Store and return the final plan
        """
        due      = self._get_due_tasks()
        sorted_  = self.sort_by_priority(due)
        accepted = self.check_conflicts(sorted_)
        self.scheduled_tasks = accepted
        return self.scheduled_tasks

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the generated plan."""
        if not self.scheduled_tasks and not self._dropped_tasks:
            return "No plan generated yet. Call generate_plan() first."

        budget = self.owner.available_minutes()
        total_used = sum(t.duration_minutes for _, t in self.scheduled_tasks)
        lines = [
            f"=== PawPal+ Daily Plan for {self.owner.name} ===",
            f"Available time : {budget} min",
            f"Scheduled      : {total_used} min across {len(self.scheduled_tasks)} task(s)",
            "",
            "SCHEDULED TASKS (highest priority first):",
        ]

        for i, (pet_name, task) in enumerate(self.scheduled_tasks, 1):
            time_note = f" @ {task.preferred_time}" if task.preferred_time else ""
            lines.append(
                f"  {i}. [{pet_name}] {task.name}"
                f" — {task.duration_minutes} min{time_note}"
                f" (priority {task.priority}, {task.category})"
            )

        if self._dropped_tasks:
            lines += ["", "DROPPED (exceeded time budget):"]
            for pet_name, task in self._dropped_tasks:
                lines.append(
                    f"  • [{pet_name}] {task.name}"
                    f" — {task.duration_minutes} min (priority {task.priority})"
                )
            lines.append(
                f"\n  Reason: adding these tasks would exceed the "
                f"{budget}-minute daily budget."
            )
        else:
            lines.append("\n  All due tasks fit within today's time budget.")

        return "\n".join(lines)