"""
PawPal+ - Pet Care Management System
pawpal_system.py: Core logic layer (classes, scheduling, algorithms)
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date


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

    def is_due_today(self) -> bool:
        """Return True if this task should appear in today's plan."""
        # TODO: implement recurrence logic
        pass

    def to_dict(self) -> dict:
        """Serialize the task to a plain dictionary (for display / storage)."""
        # TODO: return a dict of all attributes
        pass


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet's task list."""
        # TODO: append task and prevent duplicates
        pass

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name."""
        # TODO: find and remove the task with the given name
        pass

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        # TODO: return the tasks list
        pass


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    email: str
    available_hours: str        # e.g. "07:00-21:00"
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        # TODO: append pet to the pets list
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        # TODO: find and remove the pet with the given name
        pass

    def get_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        # TODO: return the pets list
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, pet: Pet, available_minutes: int):
        self.pet = pet
        self.available_minutes = available_minutes
        self.scheduled_tasks: list[Task] = []

    def sort_by_priority(self) -> list[Task]:
        """Return tasks sorted highest priority first, then by preferred_time."""
        # TODO: sort pet.tasks by priority (desc), break ties with preferred_time
        pass

    def check_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Remove or flag tasks that exceed the available time budget."""
        # TODO: accumulate durations; drop tasks once budget is exhausted
        pass

    def generate_plan(self) -> list[Task]:
        """Produce an ordered, conflict-free daily task list."""
        # TODO: call is_due_today filter → sort_by_priority → check_conflicts
        # store result in self.scheduled_tasks and return it
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why tasks were ordered/excluded."""
        # TODO: build a string summarising priority order and any dropped tasks
        pass