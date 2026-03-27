"""
PawPal+ — main.py
CLI demo script to verify core logic before connecting to the Streamlit UI.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# 1. Create Owner
# ---------------------------------------------------------------------------

owner = Owner(
    name="Jordan Rivera",
    email="jordan@pawpal.com",
    available_hours="07:00-20:00",   # 780 minutes available today
)


# ---------------------------------------------------------------------------
# 2. Create Pets
# ---------------------------------------------------------------------------

buddy = Pet(
    name="Buddy",
    species="Dog",
    age=4,
    health_notes="Allergic to chicken. Takes flea meds weekly.",
)

luna = Pet(
    name="Luna",
    species="Cat",
    age=2,
    health_notes="Indoor only. Needs daily enrichment.",
)


# ---------------------------------------------------------------------------
# 3. Add Tasks
# ---------------------------------------------------------------------------

# --- Buddy's tasks ---
buddy.add_task(Task(
    name="Morning Walk",
    category="walk",
    duration_minutes=30,
    priority=5,
    recurrence="daily",
    preferred_time="07:30",
))

buddy.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration_minutes=10,
    priority=5,
    recurrence="daily",
    preferred_time="08:00",
))

buddy.add_task(Task(
    name="Flea Medication",
    category="medication",
    duration_minutes=5,
    priority=4,
    recurrence="weekly",
    preferred_time="09:00",
))

buddy.add_task(Task(
    name="Evening Walk",
    category="walk",
    duration_minutes=45,
    priority=3,
    recurrence="daily",
    preferred_time="18:00",
))

# --- Luna's tasks ---
luna.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration_minutes=10,
    priority=5,
    recurrence="daily",
    preferred_time="08:00",
))

luna.add_task(Task(
    name="Puzzle Feeder",
    category="enrichment",
    duration_minutes=20,
    priority=3,
    recurrence="daily",
    preferred_time="11:00",
))

luna.add_task(Task(
    name="Brushing",
    category="grooming",
    duration_minutes=15,
    priority=2,
    recurrence="weekly",
    preferred_time="14:00",
))


# ---------------------------------------------------------------------------
# 4. Register pets with owner
# ---------------------------------------------------------------------------

owner.add_pet(buddy)
owner.add_pet(luna)


# ---------------------------------------------------------------------------
# 5. Generate schedule
# ---------------------------------------------------------------------------

scheduler = Scheduler(owner)
plan = scheduler.generate_plan()


# ---------------------------------------------------------------------------
# 6. Pretty-print Today's Schedule
# ---------------------------------------------------------------------------

CATEGORY_ICONS = {
    "walk":        "🦮",
    "feeding":     "🍖",
    "medication":  "💊",
    "grooming":    "✂️ ",
    "enrichment":  "🧩",
}

PRIORITY_LABELS = {
    5: "Critical",
    4: "High    ",
    3: "Medium  ",
    2: "Low     ",
    1: "Minimal ",
}

def print_schedule(plan: list, scheduler: Scheduler) -> None:
    budget     = scheduler.owner.available_minutes()
    total_used = sum(t.duration_minutes for _, t in plan)
    dropped    = scheduler._dropped_tasks

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print(f"║        🐾  PawPal+ — Today's Schedule               ║")
    print(f"║        Owner : {scheduler.owner.name:<38}║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Available time : {budget} min")
    print(f"  Scheduled      : {total_used} min  |  Tasks: {len(plan)}")
    print()

    if not plan:
        print("  ⚠️  No tasks due today.")
    else:
        print(f"  {'#':<3} {'Time':<7} {'Pet':<8} {'Task':<20} {'Duration':<10} {'Priority':<10} {'Category'}")
        print(f"  {'─'*3} {'─'*7} {'─'*8} {'─'*20} {'─'*10} {'─'*10} {'─'*12}")

        for i, (pet_name, task) in enumerate(plan, 1):
            icon     = CATEGORY_ICONS.get(task.category, "📌")
            priority = PRIORITY_LABELS.get(task.priority, "Unknown ")
            time_str = task.preferred_time or "—      "
            print(
                f"  {i:<3} {time_str:<7} {pet_name:<8} "
                f"{task.name:<20} {task.duration_minutes:>4} min    "
                f"{priority} {icon} {task.category}"
            )

    if dropped:
        print()
        print("  ── Dropped tasks (exceed time budget) ──────────────")
        for pet_name, task in dropped:
            print(f"  ✗  [{pet_name}] {task.name} — {task.duration_minutes} min (priority {task.priority})")

    print()
    print("  ── Scheduler Reasoning ─────────────────────────────")
    reasoning_lines = scheduler.explain_plan().split("\n")
    # Print only the reasoning section (skip the header we already printed)
    for line in reasoning_lines[5:]:
        print(f"  {line}")
    print()
    print("═" * 56)
    print()


print_schedule(plan, scheduler)