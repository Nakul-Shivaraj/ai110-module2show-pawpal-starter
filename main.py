"""
PawPal+ — main.py
Professional CLI demo using tabulate + ANSI color.
Run with: python main.py
"""

from tabulate import tabulate
from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------
import os
_COLOR = os.name != "nt" or os.environ.get("TERM") == "xterm"

def _c(code, text): return f"\033[{code}m{text}\033[0m" if _COLOR else text
def red(t):    return _c("91", t)
def yellow(t): return _c("93", t)
def amber(t):  return _c("33", t)
def green(t):  return _c("92", t)
def cyan(t):   return _c("96", t)
def bold(t):   return _c("1",  t)
def dim(t):    return _c("2",  t)

PRIORITY_DISPLAY = {
    5: red("🔴 Critical"),
    4: amber("🟠 High    "),
    3: yellow("🟡 Medium  "),
    2: green("🟢 Low     "),
    1: dim("⚪ Minimal "),
}

CATEGORY_ICONS = {
    "walk":       "🦮",
    "feeding":    "🍖",
    "medication": "💊",
    "grooming":   "✂️ ",
    "enrichment": "🧩",
}

DIVIDER = "─" * 62


# ---------------------------------------------------------------------------
# Setup — tasks added OUT OF ORDER to verify sorting
# ---------------------------------------------------------------------------

owner = Owner("Jordan Rivera", "jordan@pawpal.com", "07:00-20:00")

buddy = Pet("Buddy", "Dog", 4, "Allergic to chicken.")
luna  = Pet("Luna",  "Cat", 2, "Indoor only.")

buddy.add_task(Task("Evening Walk",    "walk",       45, priority=3, recurrence="daily",  preferred_time="18:00"))
buddy.add_task(Task("Flea Medication", "medication",  5, priority=4, recurrence="weekly", preferred_time="09:00"))
buddy.add_task(Task("Breakfast",       "feeding",    10, priority=5, recurrence="daily",  preferred_time="08:00"))
buddy.add_task(Task("Morning Walk",    "walk",       30, priority=5, recurrence="daily",  preferred_time="07:30"))

luna.add_task(Task("Breakfast",     "feeding",    10, priority=5, recurrence="daily",  preferred_time="08:00"))
luna.add_task(Task("Puzzle Feeder", "enrichment", 20, priority=3, recurrence="daily",  preferred_time="11:00"))
luna.add_task(Task("Brushing",      "grooming",   15, priority=2, recurrence="weekly", preferred_time="14:00"))

buddy.tasks[2].completed = True   # Breakfast is done

owner.add_pet(buddy)
owner.add_pet(luna)

scheduler  = Scheduler(owner)
plan       = scheduler.generate_plan()
budget     = owner.available_minutes()
total_used = sum(t.duration_minutes for _, t in plan)


# ---------------------------------------------------------------------------
# Header + progress bar
# ---------------------------------------------------------------------------

print()
print("╔══════════════════════════════════════════════════════════════╗")
print(f"║          {bold('  🐾  PawPal+ — Jordan Rivera Daily Plan  ')}            ║")
print("╚══════════════════════════════════════════════════════════════╝")
print(f"  {dim('Available:')} {budget} min   {dim('Pets:')} {', '.join(p.name for p in owner.get_pets())}")
print()

filled = int(40 * total_used / budget)
bar    = green("█" * filled) + dim("░" * (40 - filled))
pct    = int(100 * total_used / budget)
print(f"  [{bar}] {total_used}/{budget} min ({pct}%)")
print()


# ---------------------------------------------------------------------------
# Demo 1: Today's schedule
# ---------------------------------------------------------------------------

rows = []
for i, (pet_name, task) in enumerate(plan, 1):
    icon = CATEGORY_ICONS.get(task.category, "📌")
    rows.append([
        dim("·") + f" {i}",
        bold(task.preferred_time or "—"),
        f"{icon} {task.name}",
        pet_name,
        f"{task.duration_minutes:>4} min",
        PRIORITY_DISPLAY.get(task.priority, str(task.priority)),
        task.recurrence,
    ])

print(tabulate(
    rows,
    headers=["  #", "Time", "Task", "Pet", "Duration", "Priority", "Repeats"],
    tablefmt="rounded_outline",
    colalign=("left", "left", "left", "left", "right", "left", "left"),
))


# ---------------------------------------------------------------------------
# Demo 2: All tasks sorted by time with urgency score
# ---------------------------------------------------------------------------

print()
print(cyan(f"  ── All tasks — sorted by time {'─' * 32}"))

time_sorted = scheduler.sort_by_time(owner.get_all_tasks())
score_rows  = []
for pet_name, task in time_sorted:
    icon   = CATEGORY_ICONS.get(task.category, "📌")
    status = green("✓ done  ") if task.completed else dim("· pending")
    score  = scheduler.weighted_score(task)
    score_rows.append([task.preferred_time or "—", pet_name,
                       f"{icon} {task.name}", status, score])

print(tabulate(score_rows,
               headers=["Time", "Pet", "Task", "Status", "Score"],
               tablefmt="rounded_outline",
               colalign=("left", "left", "left", "left", "right")))
print(dim("  Score = priority × category weight × due-date bonus"))


# ---------------------------------------------------------------------------
# Demo 3: Filter — incomplete tasks
# ---------------------------------------------------------------------------

print()
print(cyan(f"  ── Filter — incomplete tasks {'─' * 34}"))

filter_rows = []
for pet_name, task in scheduler.filter_tasks(completed=False):
    icon = CATEGORY_ICONS.get(task.category, "📌")
    filter_rows.append([f"[{pet_name}]", f"{icon} {task.name}",
                        task.category,
                        PRIORITY_DISPLAY.get(task.priority, str(task.priority))])

print(tabulate(filter_rows,
               headers=["Pet", "Task", "Category", "Priority"],
               tablefmt="simple"))


# ---------------------------------------------------------------------------
# Demo 4: Conflict detection
# ---------------------------------------------------------------------------

print()
print(cyan(f"  ── Conflict detection demo {'─' * 36}"))

conflict_owner = Owner("Sam", "sam@pawpal.com", "07:00-20:00")
rex   = Pet("Rex",   "Dog", 2)
kitty = Pet("Kitty", "Cat", 3)
rex.add_task(Task("Walk",      "walk",     45, priority=5, recurrence="daily", preferred_time="08:00"))
rex.add_task(Task("Breakfast", "feeding",  15, priority=5, recurrence="daily", preferred_time="08:30"))
kitty.add_task(Task("Breakfast", "feeding",  20, priority=5, recurrence="daily", preferred_time="08:00"))
kitty.add_task(Task("Grooming",  "grooming", 30, priority=3, recurrence="daily", preferred_time="08:15"))
conflict_owner.add_pet(rex)
conflict_owner.add_pet(kitty)
cs = Scheduler(conflict_owner)
cs.generate_plan()

for w in cs.conflict_warnings:
    print(f"  {red('⚠')}  {w.replace('⚠️  Conflict: ', '')}")


# ---------------------------------------------------------------------------
# Demo 5: Next available slot
# ---------------------------------------------------------------------------

print()
print(cyan(f"  ── Next available slot {'─' * 40}"))

for dur in [10, 30, 60]:
    slot = scheduler.find_next_slot(dur)
    print(f"  {bold(f'{dur}-min')} task → {green(slot) if slot else red('none')}")

print()
print("═" * 62)
print()
