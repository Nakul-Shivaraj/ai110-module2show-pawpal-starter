"""
PawPal+ - Pet Care Management System
pawpal_system.py: Core logic layer (classes, scheduling, algorithms)
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date, datetime, timedelta
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
    due_date: date = field(default_factory=date.today)  # defaults to today

    def is_due_today(self) -> bool:
        """Return True if this task's due_date matches today and it isn't complete."""
        if self.completed:
            return False
        return self.due_date == date.today()

    def next_occurrence(self) -> "Task":
        """
        Return a fresh Task clone due on the next occurrence date.
        Uses timedelta: daily → today + 1 day, weekly → today + 7 days.
        Raises ValueError for non-recurring tasks.
        """
        if self.recurrence == "none":
            raise ValueError(
                f"Task '{self.name}' is non-recurring — no next occurrence."
            )
        delta = timedelta(days=1) if self.recurrence == "daily" else timedelta(weeks=1)
        return Task(
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
            preferred_time=self.preferred_time,
            completed=False,
            due_date=date.today() + delta,
            # task_id is auto-generated — every occurrence is a distinct object
        )

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
            "due_date":         self.due_date.isoformat(),
        }

    def __str__(self) -> str:
        time_str = f" @ {self.preferred_time}" if self.preferred_time else ""
        return (
            f"[P{self.priority}] {self.name} ({self.category})"
            f" — {self.duration_minutes} min{time_str}"
            f" | repeats: {self.recurrence} | due: {self.due_date}"
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

    def mark_task_complete(self, task_name: str) -> Optional["Task"]:
        """
        Mark a task as complete by name.
        For recurring tasks (daily/weekly), automatically appends a new
        instance due on the next occurrence using timedelta.
        Returns the next Task if one was created, else None.
        """
        for task in self.tasks:
            if task.name.lower() == task_name.lower() and not task.completed:
                task.completed = True
                if task.recurrence != "none":
                    next_task = task.next_occurrence()
                    self.tasks.append(next_task)
                    return next_task
                return None
        raise ValueError(
            f"No incomplete task named '{task_name}' found for {self.name}."
        )

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
        self.scheduled_tasks: list   = []   # (pet_name, Task)
        self._dropped_tasks:  list   = []   # tasks that didn't fit
        self.conflict_warnings: list = []   # overlap warnings from detect_conflicts

    def _get_due_tasks(self) -> list:
        """Collect all tasks due today across every pet."""
        result = []
        for pet in self.owner.get_pets():
            for task in pet.get_tasks_due_today():
                result.append((pet.name, task))
        return result

    def sort_by_priority(self, tasks: list) -> list:
        """
        Sort (pet_name, Task) pairs by priority descending, then preferred_time
        ascending as a tiebreaker. Uses a tuple lambda key — same pattern as
        sort_by_time — so both methods are visually consistent.
        None times use sentinel '99:99' so they sort to the end.
        """
        return sorted(
            tasks,
            key=lambda pair: (-pair[1].priority, pair[1].preferred_time or "99:99")
        )

    def sort_by_time(self, tasks: list) -> list:
        """
        Sort (pet_name, Task) pairs chronologically by preferred_time (HH:MM).
        Tasks with no preferred_time are placed at the end.
        Uses a lambda with a sentinel value so None sorts last naturally.
        """
        return sorted(
            tasks,
            key=lambda pair: pair[1].preferred_time or "99:99"
        )

    @staticmethod
    def _to_minutes(time_str: str) -> int:
        """Convert 'HH:MM' string to minutes since midnight (e.g. '08:30' → 510)."""
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    def detect_conflicts(self, tasks: list) -> list[str]:
        """
        Lightweight overlap detection — returns warning strings instead of crashing.
        Strategy: convert each task to a (start, end) interval in minutes-since-
        midnight, then check every pair using the overlap formula:
            start_A < end_B  AND  start_B < end_A
        Tasks without a preferred_time are skipped (no fixed start = no conflict).
        Returns a list of human-readable warning messages (empty = no conflicts).
        """
        warnings = []

        # Build interval list — only tasks that have a preferred_time
        intervals = []
        for pet_name, task in tasks:
            if task.preferred_time is None:
                continue
            start = self._to_minutes(task.preferred_time)
            end   = start + task.duration_minutes
            intervals.append((pet_name, task, start, end))

        # Check every unique pair (i, j) — O(n²) is fine for daily task counts
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                pet_a, task_a, start_a, end_a = intervals[i]
                pet_b, task_b, start_b, end_b = intervals[j]

                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"⚠️  Conflict: [{pet_a}] '{task_a.name}' "
                        f"({task_a.preferred_time}, {task_a.duration_minutes} min) "
                        f"overlaps with [{pet_b}] '{task_b.name}' "
                        f"({task_b.preferred_time}, {task_b.duration_minutes} min)"
                    )

        return warnings

    def filter_tasks(
        self,
        pet_name: str = None,
        category: str = None,
        completed: bool = None,
    ) -> list:
        """
        Filter all tasks across owner's pets by any combination of:
          pet_name  — exact match (case-insensitive)
          category  — e.g. 'walk', 'feeding', 'medication'
          completed — True / False
        Returns a flat list of (pet_name, Task) tuples.
        """
        results = []
        for pet in self.owner.get_pets():
            # Skip this pet entirely if a pet_name filter is active
            if pet_name and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.get_tasks():
                if category and task.category.lower() != category.lower():
                    continue
                if completed is not None and task.completed != completed:
                    continue
                results.append((pet.name, task))
        return results

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
          2. Detect and store time-overlap conflicts (warnings only — no crash)
          3. Sort by priority (and preferred_time tiebreaker)
          4. Fit within time budget
          5. Re-sort accepted tasks chronologically by preferred_time
          6. Store and return the final plan
        """
        due                   = self._get_due_tasks()
        self.conflict_warnings = self.detect_conflicts(due)   # stored for explain_plan
        by_prio               = self.sort_by_priority(due)
        accepted              = self.check_conflicts(by_prio)
        self.scheduled_tasks  = self.sort_by_time(accepted)
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

        if self.conflict_warnings:
            lines += ["", "TIME CONFLICTS DETECTED:"]
            for w in self.conflict_warnings:
                lines.append(f"  {w}")
            lines.append(
                "\n  Note: conflicting tasks are still scheduled — "
                "consider adjusting their preferred_time or duration."
            )

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Extension 1: Next available slot
    # -----------------------------------------------------------------------

    def find_next_slot(self, duration_minutes: int):
        """
        Find the earliest open time window in today's schedule that can fit
        a task of the given duration without conflicting with existing tasks.
        Returns a 'HH:MM' string or None if no slot is available.
        """
        if not self.scheduled_tasks:
            return self.owner.available_hours.split("-")[0].strip()

        busy = []
        for _, task in self.scheduled_tasks:
            if task.preferred_time:
                s = self._to_minutes(task.preferred_time)
                busy.append((s, s + task.duration_minutes))

        try:
            start_str, end_str = self.owner.available_hours.split("-")
            window_start = self._to_minutes(start_str.strip())
            window_end   = self._to_minutes(end_str.strip())
        except ValueError:
            return None

        for candidate in range(window_start, window_end - duration_minutes + 1):
            cand_end = candidate + duration_minutes
            if all(candidate >= b_end or cand_end <= b_start
                   for b_start, b_end in busy):
                h, m = divmod(candidate, 60)
                return f"{h:02d}:{m:02d}"

        return None

    # -----------------------------------------------------------------------
    # Extension 2: Weighted prioritization
    # -----------------------------------------------------------------------

    CATEGORY_WEIGHTS = {
        "medication": 1.5,
        "feeding":    1.3,
        "walk":       1.2,
        "grooming":   1.1,
        "enrichment": 1.0,
    }

    def weighted_score(self, task) -> float:
        """
        Compute a composite urgency score:
            score = priority x category_weight x recency_bonus
        Overdue tasks get 1.5x bonus, due-today 1.0x, tomorrow 0.8x, later 0.5x.
        """
        from datetime import date
        days_out = (task.due_date - date.today()).days
        if days_out < 0:
            recency = 1.5
        elif days_out == 0:
            recency = 1.0
        elif days_out == 1:
            recency = 0.8
        else:
            recency = 0.5
        return round(task.priority * self.CATEGORY_WEIGHTS.get(task.category, 1.0) * recency, 3)

    def sort_by_weighted_score(self, tasks: list) -> list:
        """Sort (pet_name, Task) pairs by weighted_score descending."""
        return sorted(tasks, key=lambda pair: self.weighted_score(pair[1]), reverse=True)