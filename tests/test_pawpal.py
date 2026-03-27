"""
tests/test_pawpal.py
Full test suite for PawPal+ — happy paths + edge cases.
Run with: python -m pytest
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def daily_task():
    return Task("Morning Walk", "walk", 30, priority=5,
                recurrence="daily", preferred_time="07:30")

@pytest.fixture
def weekly_task():
    return Task("Brushing", "grooming", 15, priority=2,
                recurrence="weekly", preferred_time="14:00")

@pytest.fixture
def one_off_task():
    return Task("Vet Visit", "medication", 60, priority=5,
                recurrence="none", preferred_time="10:00")

@pytest.fixture
def pet():
    return Pet("Buddy", "Dog", 4)

@pytest.fixture
def owner_with_pet(pet):
    o = Owner("Jordan", "j@pawpal.com", "07:00-20:00")
    o.add_pet(pet)
    return o

@pytest.fixture
def scheduler(owner_with_pet):
    return Scheduler(owner_with_pet)


# ---------------------------------------------------------------------------
# 1. Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order(pet, owner_with_pet, scheduler):
    """Tasks added out of order should come back sorted by preferred_time."""
    pet.add_task(Task("Evening Walk", "walk",    45, priority=3, preferred_time="18:00"))
    pet.add_task(Task("Breakfast",    "feeding", 10, priority=5, preferred_time="08:00"))
    pet.add_task(Task("Morning Walk", "walk",    30, priority=5, preferred_time="07:30"))

    all_pairs = owner_with_pet.get_all_tasks()
    sorted_pairs = scheduler.sort_by_time(all_pairs)
    times = [t.preferred_time for _, t in sorted_pairs]
    assert times == sorted(times), f"Expected chronological order, got {times}"

def test_sort_by_time_none_goes_last(pet, owner_with_pet, scheduler):
    """Tasks without a preferred_time should appear after timed tasks."""
    pet.add_task(Task("Walk",    "walk",        30, priority=5, preferred_time="08:00"))
    pet.add_task(Task("Anytime", "enrichment",  20, priority=3, preferred_time=None))

    sorted_pairs = scheduler.sort_by_time(owner_with_pet.get_all_tasks())
    last_task = sorted_pairs[-1][1]
    assert last_task.preferred_time is None

def test_sort_by_priority_highest_first(pet, owner_with_pet, scheduler):
    """Higher priority tasks must appear before lower priority ones."""
    pet.add_task(Task("Low",  "enrichment", 10, priority=1, preferred_time="09:00"))
    pet.add_task(Task("High", "walk",       10, priority=5, preferred_time="10:00"))
    pet.add_task(Task("Mid",  "feeding",    10, priority=3, preferred_time="08:00"))

    sorted_pairs = scheduler.sort_by_priority(owner_with_pet.get_all_tasks())
    priorities = [t.priority for _, t in sorted_pairs]
    assert priorities == sorted(priorities, reverse=True)

def test_generate_plan_final_order_is_chronological(pet, owner_with_pet, scheduler):
    """generate_plan() final output should be time-sorted, not priority-sorted."""
    pet.add_task(Task("Evening Walk", "walk",    45, priority=5, preferred_time="18:00"))
    pet.add_task(Task("Breakfast",    "feeding", 10, priority=5, preferred_time="08:00"))
    pet.add_task(Task("Morning Walk", "walk",    30, priority=5, preferred_time="07:30"))

    plan = scheduler.generate_plan()
    times = [t.preferred_time for _, t in plan if t.preferred_time]
    assert times == sorted(times)


# ---------------------------------------------------------------------------
# 2. Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_next_occurrence_is_tomorrow(daily_task):
    """Completing a daily task should create a clone due tomorrow."""
    next_task = daily_task.next_occurrence()
    assert next_task.due_date == date.today() + timedelta(days=1)

def test_weekly_task_next_occurrence_is_next_week(weekly_task):
    """Completing a weekly task should create a clone due in 7 days."""
    next_task = weekly_task.next_occurrence()
    assert next_task.due_date == date.today() + timedelta(weeks=1)

def test_nonrecurring_task_raises_on_next_occurrence(one_off_task):
    """Calling next_occurrence() on a none-recurrence task should raise."""
    with pytest.raises(ValueError):
        one_off_task.next_occurrence()

def test_mark_complete_daily_appends_next_task(pet, daily_task):
    """mark_task_complete on a daily task should append a new task to the pet."""
    pet.add_task(daily_task)
    before = len(pet.get_tasks())
    pet.mark_task_complete("Morning Walk")
    assert len(pet.get_tasks()) == before + 1

def test_mark_complete_none_recurrence_returns_none(pet, one_off_task):
    """mark_task_complete on a one-off task should return None."""
    pet.add_task(one_off_task)
    result = pet.mark_task_complete("Vet Visit")
    assert result is None

def test_mark_complete_sets_completed_true(pet, daily_task):
    """The original task should be marked completed after mark_task_complete."""
    pet.add_task(daily_task)
    pet.mark_task_complete("Morning Walk")
    original = pet.get_tasks()[0]
    assert original.completed is True

def test_mark_complete_twice_completes_the_clone(pet, daily_task):
    """
    Calling mark_task_complete twice on a daily task should work:
    the first call marks the original done and creates a clone,
    the second call marks that clone done (not a crash or error).
    """
    pet.add_task(daily_task)
    pet.mark_task_complete("Morning Walk")   # completes original, creates clone
    pet.mark_task_complete("Morning Walk")   # completes the clone — valid behavior
    completed = [t for t in pet.get_tasks() if t.completed]
    assert len(completed) == 2

def test_next_occurrence_has_new_task_id(daily_task):
    """Each recurrence should be a distinct object with a fresh task_id."""
    next_task = daily_task.next_occurrence()
    assert next_task.task_id != daily_task.task_id


# ---------------------------------------------------------------------------
# 3. Conflict detection
# ---------------------------------------------------------------------------

def test_overlapping_tasks_flagged(pet, owner_with_pet, scheduler):
    """Two tasks whose intervals overlap should produce a conflict warning."""
    pet.add_task(Task("Walk",      "walk",    45, priority=5, preferred_time="08:00"))
    pet.add_task(Task("Breakfast", "feeding", 15, priority=5, preferred_time="08:30"))

    warnings = scheduler.detect_conflicts(owner_with_pet.get_all_tasks())
    assert len(warnings) > 0

def test_adjacent_tasks_no_false_conflict(pet, owner_with_pet, scheduler):
    """Tasks that touch but don't overlap should NOT produce a warning."""
    pet.add_task(Task("Walk",      "walk",    30, priority=5, preferred_time="08:00"))
    pet.add_task(Task("Breakfast", "feeding", 15, priority=5, preferred_time="08:30"))

    warnings = scheduler.detect_conflicts(owner_with_pet.get_all_tasks())
    assert len(warnings) == 0

def test_no_preferred_time_skipped_by_conflict_detector(pet, owner_with_pet, scheduler):
    """Tasks without preferred_time should not crash the conflict detector."""
    pet.add_task(Task("Anytime", "enrichment", 30, priority=3, preferred_time=None))
    pet.add_task(Task("Walk",    "walk",        30, priority=5, preferred_time="08:00"))

    warnings = scheduler.detect_conflicts(owner_with_pet.get_all_tasks())
    assert isinstance(warnings, list)

def test_cross_pet_conflict_detected():
    """Overlapping tasks on different pets should still be flagged."""
    owner = Owner("Sam", "s@s.com", "07:00-20:00")
    rex   = Pet("Rex",   "Dog", 2)
    kitty = Pet("Kitty", "Cat", 3)
    rex.add_task(  Task("Walk",      "walk",    45, priority=5, preferred_time="08:00"))
    kitty.add_task(Task("Breakfast", "feeding", 20, priority=5, preferred_time="08:00"))
    owner.add_pet(rex)
    owner.add_pet(kitty)

    s = Scheduler(owner)
    warnings = s.detect_conflicts(owner.get_all_tasks())
    assert len(warnings) > 0

def test_conflict_warnings_in_explain_plan():
    """explain_plan() should mention conflicts when they exist."""
    owner = Owner("Sam", "s@s.com", "07:00-20:00")
    pet   = Pet("Rex", "Dog", 2)
    pet.add_task(Task("Walk",      "walk",    45, priority=5, preferred_time="08:00"))
    pet.add_task(Task("Breakfast", "feeding", 15, priority=5, preferred_time="08:30"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.generate_plan()
    explanation = s.explain_plan()
    assert "Conflict" in explanation or "conflict" in explanation


# ---------------------------------------------------------------------------
# 4. Filtering
# ---------------------------------------------------------------------------

def test_filter_by_pet_name_returns_only_that_pet():
    """filter_tasks(pet_name=X) should only return tasks for pet X."""
    owner = Owner("Jordan", "j@j.com", "07:00-20:00")
    buddy = Pet("Buddy", "Dog", 4)
    luna  = Pet("Luna",  "Cat", 2)
    buddy.add_task(Task("Walk",      "walk",    30, priority=5))
    luna.add_task( Task("Breakfast", "feeding", 10, priority=5))
    owner.add_pet(buddy)
    owner.add_pet(luna)

    s = Scheduler(owner)
    results = s.filter_tasks(pet_name="Buddy")
    assert all(name == "Buddy" for name, _ in results)

def test_filter_nonexistent_pet_returns_empty():
    """Filtering by a pet name that doesn't exist should return []."""
    owner = Owner("Jordan", "j@j.com", "07:00-20:00")
    owner.add_pet(Pet("Buddy", "Dog", 4))
    s = Scheduler(owner)
    assert s.filter_tasks(pet_name="Ghost") == []

def test_filter_by_completed_false_excludes_done(pet, owner_with_pet, daily_task):
    """filter_tasks(completed=False) should exclude completed tasks."""
    pet.add_task(daily_task)
    pet.mark_task_complete("Morning Walk")

    s = Scheduler(owner_with_pet)
    incomplete = s.filter_tasks(completed=False)
    assert all(not t.completed for _, t in incomplete)


# ---------------------------------------------------------------------------
# 5. Time budget enforcement
# ---------------------------------------------------------------------------

def test_all_tasks_exceed_budget_gives_empty_plan():
    """If every task exceeds the budget, the plan should be empty."""
    owner = Owner("Jordan", "j@j.com", "08:00-08:10")  # only 10 min
    pet   = Pet("Buddy", "Dog", 4)
    pet.add_task(Task("Long Walk", "walk", 60, priority=5, preferred_time="08:00"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    plan = s.generate_plan()
    assert plan == []

def test_low_priority_dropped_when_budget_tight():
    """A low-priority task should be dropped when budget is nearly full."""
    owner = Owner("Jordan", "j@j.com", "08:00-08:35")  # 35 min
    pet   = Pet("Buddy", "Dog", 4)
    pet.add_task(Task("High Task", "walk",       30, priority=5, preferred_time="08:00"))
    pet.add_task(Task("Low Task",  "enrichment", 20, priority=1, preferred_time="08:30"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    plan = s.generate_plan()
    names = [t.name for _, t in plan]
    assert "High Task" in names
    assert "Low Task"  not in names

def test_pet_with_no_tasks_gives_empty_plan():
    """A pet with no tasks should produce an empty plan without crashing."""
    owner = Owner("Jordan", "j@j.com", "07:00-20:00")
    owner.add_pet(Pet("Buddy", "Dog", 4))
    s = Scheduler(owner)
    assert s.generate_plan() == []