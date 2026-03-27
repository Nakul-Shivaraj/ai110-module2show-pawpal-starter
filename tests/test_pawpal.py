"""
tests/test_pawpal.py
Basic tests for PawPal+ core logic.
Run with: python -m pytest
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers — reusable fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_task():
    """A basic daily walk task."""
    return Task(
        name="Morning Walk",
        category="walk",
        duration_minutes=30,
        priority=5,
        recurrence="daily",
        preferred_time="07:30",
    )

@pytest.fixture
def sample_pet():
    """A pet with no tasks yet."""
    return Pet(name="Buddy", species="Dog", age=3)

@pytest.fixture
def sample_owner(sample_pet):
    """An owner with one pet already registered."""
    owner = Owner(
        name="Jordan",
        email="jordan@pawpal.com",
        available_hours="07:00-20:00",
    )
    owner.add_pet(sample_pet)
    return owner


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_task_completion_changes_status(sample_task):
    """mark_complete() should set completed to True."""
    assert sample_task.completed is False
    sample_task.completed = True
    assert sample_task.completed is True

def test_task_completed_false_by_default(sample_task):
    """A newly created task should not be marked complete."""
    assert sample_task.completed is False

def test_task_to_dict_contains_all_keys(sample_task):
    """to_dict() should include every expected field."""
    d = sample_task.to_dict()
    for key in ["task_id", "name", "category", "duration_minutes",
                "priority", "recurrence", "preferred_time", "completed"]:
        assert key in d, f"Missing key: {key}"

def test_task_is_due_today_daily(sample_task):
    """A daily task should always be due today."""
    assert sample_task.is_due_today() is True

def test_task_is_due_today_none_recurrence_not_completed():
    """A one-time task that isn't completed should be due today."""
    task = Task("Vet Visit", "medication", 60, priority=5, recurrence="none")
    assert task.is_due_today() is True

def test_task_is_due_today_none_recurrence_already_completed():
    """A one-time task that IS completed should NOT be due today."""
    task = Task("Vet Visit", "medication", 60, priority=5,
                recurrence="none", completed=True)
    assert task.is_due_today() is False


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count(sample_pet, sample_task):
    """Adding a task to a pet should increase its task count by 1."""
    before = len(sample_pet.get_tasks())
    sample_pet.add_task(sample_task)
    assert len(sample_pet.get_tasks()) == before + 1

def test_add_multiple_tasks(sample_pet):
    """Adding three tasks should result in exactly three tasks."""
    for i in range(3):
        sample_pet.add_task(Task(f"Task {i}", "feeding", 10, priority=i + 1))
    assert len(sample_pet.get_tasks()) == 3

def test_add_duplicate_task_raises(sample_pet, sample_task):
    """Adding the same task object twice should raise a ValueError."""
    sample_pet.add_task(sample_task)
    with pytest.raises(ValueError):
        sample_pet.add_task(sample_task)

def test_remove_task_decreases_count(sample_pet, sample_task):
    """Removing a task should decrease the task count by 1."""
    sample_pet.add_task(sample_task)
    before = len(sample_pet.get_tasks())
    sample_pet.remove_task("Morning Walk")
    assert len(sample_pet.get_tasks()) == before - 1

def test_remove_nonexistent_task_raises(sample_pet):
    """Removing a task that doesn't exist should raise a ValueError."""
    with pytest.raises(ValueError):
        sample_pet.remove_task("Ghost Task")


# ---------------------------------------------------------------------------
# Owner tests
# ---------------------------------------------------------------------------

def test_owner_add_pet_increases_count(sample_owner):
    """Adding a second pet should bring the count to 2."""
    sample_owner.add_pet(Pet("Luna", "Cat", 2))
    assert len(sample_owner.get_pets()) == 2

def test_owner_duplicate_pet_raises(sample_owner):
    """Registering a pet with the same name should raise a ValueError."""
    with pytest.raises(ValueError):
        sample_owner.add_pet(Pet("Buddy", "Dog", 5))

def test_owner_available_minutes_parses_correctly(sample_owner):
    """07:00-20:00 should equal 780 minutes."""
    assert sample_owner.available_minutes() == 780

def test_owner_get_all_tasks_returns_tuples(sample_owner, sample_pet, sample_task):
    """get_all_tasks() should return (pet_name, Task) tuples."""
    sample_pet.add_task(sample_task)
    all_tasks = sample_owner.get_all_tasks()
    assert len(all_tasks) == 1
    pet_name, task = all_tasks[0]
    assert pet_name == "Buddy"
    assert task.name == "Morning Walk"


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def test_scheduler_generate_plan_returns_list(sample_owner, sample_pet, sample_task):
    """generate_plan() should return a list."""
    sample_pet.add_task(sample_task)
    scheduler = Scheduler(sample_owner)
    plan = scheduler.generate_plan()
    assert isinstance(plan, list)

def test_scheduler_sorts_higher_priority_first(sample_owner, sample_pet):
    """Higher priority tasks should appear before lower priority ones."""
    sample_pet.add_task(Task("Low Task",  "enrichment", 10, priority=1))
    sample_pet.add_task(Task("High Task", "walk",       10, priority=5))
    scheduler = Scheduler(sample_owner)
    plan = scheduler.generate_plan()
    priorities = [task.priority for _, task in plan]
    assert priorities == sorted(priorities, reverse=True)

def test_scheduler_drops_tasks_exceeding_budget():
    """Tasks that exceed the time budget should be dropped."""
    owner = Owner("Test", "t@t.com", "08:00-08:30")  # only 30 min
    pet   = Pet("Rex", "Dog", 2)
    pet.add_task(Task("Long Task",  "walk", 25, priority=5))
    pet.add_task(Task("Short Task", "walk",  5, priority=3))
    pet.add_task(Task("Over Task",  "walk", 20, priority=1))  # won't fit
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    total = sum(t.duration_minutes for _, t in plan)
    assert total <= 30

def test_scheduler_explain_plan_is_string(sample_owner, sample_pet, sample_task):
    """explain_plan() should return a non-empty string after generate_plan()."""
    sample_pet.add_task(sample_task)
    scheduler = Scheduler(sample_owner)
    scheduler.generate_plan()
    explanation = scheduler.explain_plan()
    assert isinstance(explanation, str)
    assert len(explanation) > 0
    