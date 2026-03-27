"""
PawPal+ — main.py
CLI demo script to verify core logic before connecting to the Streamlit UI.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Setup — intentionally add tasks OUT OF ORDER to test sorting
# ---------------------------------------------------------------------------

owner = Owner("Jordan Rivera", "jordan@pawpal.com", "07:00-20:00")

buddy = Pet("Buddy", "Dog", 4, "Allergic to chicken.")
luna  = Pet("Luna",  "Cat", 2, "Indoor only.")

# Buddy's tasks — deliberately shuffled times
buddy.add_task(Task("Evening Walk",   "walk",       45, priority=3, recurrence="daily",  preferred_time="18:00"))
buddy.add_task(Task("Flea Medication","medication",  5, priority=4, recurrence="weekly", preferred_time="09:00"))
buddy.add_task(Task("Breakfast",      "feeding",    10, priority=5, recurrence="daily",  preferred_time="08:00"))
buddy.add_task(Task("Morning Walk",   "walk",       30, priority=5, recurrence="daily",  preferred_time="07:30"))

# Luna's tasks
luna.add_task(Task("Breakfast",    "feeding",    10, priority=5, recurrence="daily",  preferred_time="08:00"))
luna.add_task(Task("Puzzle Feeder","enrichment", 20, priority=3, recurrence="daily",  preferred_time="11:00"))
luna.add_task(Task("Brushing",     "grooming",   15, priority=2, recurrence="weekly", preferred_time="14:00"))

# Mark one task complete to test filtering
buddy.tasks[2].completed = True   # Breakfast is done

owner.add_pet(buddy)
owner.add_pet(luna)

scheduler = Scheduler(owner)

DIVIDER = "─" * 56


# ---------------------------------------------------------------------------
# Demo 1: Full schedule (priority → time-sorted output)
# ---------------------------------------------------------------------------

plan = scheduler.generate_plan()

print()
print("╔══════════════════════════════════════════════════════╗")
print("║       🐾  PawPal+ — Today's Schedule                ║")
print("╚══════════════════════════════════════════════════════╝")
print(f"  Owner : {owner.name}  |  Budget: {owner.available_minutes()} min")
print()
print(f"  {'Time':<8} {'Pet':<8} {'Task':<20} {'Dur':>5}  {'Pri':<5}")
print(f"  {DIVIDER}")
for pet_name, task in plan:
    t = task.preferred_time or "—     "
    print(f"  {t:<8} {pet_name:<8} {task.name:<20} {task.duration_minutes:>4}m  P{task.priority}")


# ---------------------------------------------------------------------------
# Demo 2: sort_by_time on all tasks (not just due-today)
# ---------------------------------------------------------------------------

print()
print(f"  {DIVIDER}")
print("  📋  All tasks sorted chronologically (sort_by_time)")
print(f"  {DIVIDER}")

all_pairs = owner.get_all_tasks()
time_sorted = scheduler.sort_by_time(all_pairs)

for pet_name, task in time_sorted:
    t = task.preferred_time or "none "
    done = "✓" if task.completed else " "
    print(f"  [{done}] {t:<8} {pet_name:<8} {task.name}")


# ---------------------------------------------------------------------------
# Demo 3: filter_tasks — incomplete tasks only
# ---------------------------------------------------------------------------

print()
print(f"  {DIVIDER}")
print("  🔍  Filter: incomplete tasks only")
print(f"  {DIVIDER}")

incomplete = scheduler.filter_tasks(completed=False)
for pet_name, task in incomplete:
    print(f"  • [{pet_name}] {task.name} ({task.category})")


# ---------------------------------------------------------------------------
# Demo 4: filter_tasks — Buddy's tasks only
# ---------------------------------------------------------------------------

print()
print(f"  {DIVIDER}")
print("  🔍  Filter: Buddy's tasks only")
print(f"  {DIVIDER}")

buddy_tasks = scheduler.filter_tasks(pet_name="Buddy")
for pet_name, task in buddy_tasks:
    done = "✓" if task.completed else " "
    print(f"  [{done}] {task.name:<22} category={task.category}")


# ---------------------------------------------------------------------------
# Demo 5: filter_tasks — walk tasks only (any pet)
# ---------------------------------------------------------------------------

print()
print(f"  {DIVIDER}")
print("  🔍  Filter: category = walk")
print(f"  {DIVIDER}")

walks = scheduler.filter_tasks(category="walk")
for pet_name, task in walks:
    print(f"  • [{pet_name}] {task.name} @ {task.preferred_time or '—'}")

print()
print("═" * 56)
print()



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

# ---------------------------------------------------------------------------
# Demo 6: Conflict detection — two tasks deliberately at the same time
# ---------------------------------------------------------------------------

from pawpal_system import Owner, Pet, Task, Scheduler

print()
print("╔══════════════════════════════════════════════════════╗")
print("║       ⚠️   Conflict Detection Demo                   ║")
print("╚══════════════════════════════════════════════════════╝")

conflict_owner = Owner("Sam", "sam@pawpal.com", "07:00-20:00")
rex   = Pet("Rex",   "Dog", 2)
kitty = Pet("Kitty", "Cat", 3)

# These two tasks both start at 08:00 and overlap each other
rex.add_task(Task("Morning Walk",  "walk",    45, priority=5,
                  recurrence="daily", preferred_time="08:00"))
rex.add_task(Task("Breakfast",     "feeding", 15, priority=5,
                  recurrence="daily", preferred_time="08:30"))   # starts inside walk

# These two overlap across pets (08:00 feeding + 08:15 grooming)
kitty.add_task(Task("Breakfast",   "feeding", 20, priority=5,
                    recurrence="daily", preferred_time="08:00"))
kitty.add_task(Task("Grooming",    "grooming", 30, priority=3,
                    recurrence="daily", preferred_time="08:15")) # starts inside Breakfast

conflict_owner.add_pet(rex)
conflict_owner.add_pet(kitty)

s = Scheduler(conflict_owner)
s.generate_plan()

print()
if s.conflict_warnings:
    for w in s.conflict_warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

print()
print("  Full explanation:")
print()
for line in s.explain_plan().split("\n"):
    print(f"  {line}")
print()
print("═" * 56)