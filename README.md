# 🐾 PawPal+
A smart pet care planning app built with Python and Streamlit. PawPal+ helps busy pet owners stay consistent with daily care routines by generating a prioritized, conflict-aware daily schedule.

## 📸 Demo

<a href="/pawpal_screenshot.png" target="_blank">
  <img src='/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

✨ Features

Priority-based scheduling Tasks are ranked 1–5. The scheduler always selects higher-priority tasks first before applying the time budget, so medications are never dropped in favour of enrichment activities.

Chronological display After priority selection, the final plan is re-sorted by preferred time so the output reads like a real day (07:30 walk → 08:00 breakfast → 18:00 walk).

Recurring tasks Each task carries a due_date. Marking a daily task complete automatically creates a new instance due tomorrow; weekly tasks create one due in 7 days. One-time tasks are simply marked done.

Conflict detection The scheduler checks every pair of scheduled tasks for time overlap using start/end intervals. Conflicts appear as visible warnings in the UI — tasks are never silently dropped, giving the owner the information to resolve them.

Task filtering Tasks can be filtered by pet name, category (walk, feeding, medication, grooming, enrichment), or completion status — individually or combined.

Time budget enforcement The owner's available hours are parsed automatically. Tasks that would exceed the daily budget are dropped and listed separately with a clear explanation.

Scheduler reasoning Every generated plan includes a plain-language explanation of why tasks were ordered, selected, or excluded.

## Testing PawPal+
 
### Run the tests
 
```bash
python -m pytest
```
 
Or for verbose output showing each test name:
 
```bash
python -m pytest tests/test_pawpal.py -v
```
 
### What the tests cover
 
| Group | Count | What's verified |
|---|---|---|
| Sorting | 4 | Chronological order, None times last, priority order, final plan order |
| Recurrence | 7 | Daily/weekly next occurrence dates, mark complete, clone creation, unique IDs |
| Conflict detection | 5 | Overlap caught, adjacent tasks safe, None time safe, cross-pet, explain_plan output |
| Filtering | 3 | Pet name filter, nonexistent pet, completed=False |
| Budget enforcement | 3 | All exceed budget, low priority dropped, empty pet |
 
**Total: 23 tests**
 
### Confidence level ⭐⭐⭐⭐☆ (4/5)
 
Core scheduling behaviors — priority sorting, recurrence, conflict detection,
and budget enforcement — are well covered. One star deducted because the UI
layer (`app.py`) and session state behavior are not yet tested, and edge cases
around malformed time strings (e.g. `"8:00"` instead of `"08:00"`) are untested.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app
 
```bash
python -m streamlit run app.py
```
 
### Run the CLI demo
 
```bash
python main.py
```
 
### Run tests
 
```bash
python -m pytest
```

🏗 Architecture

Four core classes work together:
- Task — a single care activity with priority, recurrence, and a due date
- Pet — owns a task list; handles completion and recurrence cloning
- Owner — holds pet roster and available hours for the day
- Scheduler — the planning engine: filters, sorts, checks budget, detects conflicts

See uml_final.png for the full class diagram.

## 🧠 Optional Extensions

## Challenge 1:
Advanced Algorithmic Capability via Agent Mode

### Extension 1: Next available slot (`find_next_slot`)

Given a task duration in minutes, the scheduler scans the owner's available window minute-by-minute and returns the earliest time that fits without overlapping any existing scheduled task.
 
```python
scheduler.generate_plan()
slot = scheduler.find_next_slot(30)  # → "08:10"
```

**How it works:** builds a list of `(start, end)` busy intervals from the current plan, then walks from the window start checking each candidate slot against every busy interval using `candidate >= end OR candidate+dur <= start`.
 

### Extension 2: Weighted prioritization (`weighted_score`)

Produces a composite urgency float that goes beyond the raw 1–5 priority
integer by factoring in category importance and due-date proximity:
 
```
score = priority × category_weight × recency_bonus
```
 
| Factor | Values |
|---|---|
| `category_weight` | medication 1.5 · feeding 1.3 · walk 1.2 · grooming 1.1 · enrichment 1.0 |
| `recency_bonus` | overdue 1.5× · due today 1.0× · tomorrow 0.8× · later 0.5× |
 
An overdue P3 medication (score 6.75) correctly outranks an on-time P5 walk
(score 6.0) — raw priority alone would get this wrong.
 
```python
ranked = scheduler.sort_by_weighted_score(owner.get_all_tasks())
```

**Agent Mode usage:** Agent Mode was used to scaffold both methods — it proposed the interval overlap formula for `find_next_slot` and the multiplicative score structure for `weighted_score`. Both suggestions were reviewed and modified: the slot finder was changed from 30-minute increments to 1-minute steps for precision, and the recency bonus tiers were adjusted after testing showed the original values didn't differentiate overdue tasks strongly enough.

## 💾 Challenge 2: Data Persistence
PawPal+ remembers your pets and tasks between sessions using a local `data.json` file.
 
### How it works

Three methods handle the full persistence lifecycle:
 
**`Owner.to_dict()`** — recursively serializes the entire object graph (Owner → Pets → Tasks) into a plain Python dict, including `due_date` (as ISO string) and `task_id` (so recurring clones keep their identity across restarts).
 
**`Owner.save_to_json(filepath)`** — writes the dict to disk using `json.dumps`. Called automatically on every "Generate schedule" click, and also available via the manual **💾 Save to file** button.
 
**`Owner.load_from_json(filepath)`** — reads the file, reconstructs `Task` objects (converting `due_date` back with `date.fromisoformat()`), builds `Pet` objects, and returns a fully wired `Owner`. Called once per session on startup.
 
### In the UI
 
- On first load, if `data.json` exists, a toast notification confirms the previous session was restored and all fields pre-fill automatically.
- The **💾 Save to file** button lets you save manually at any point.
- Every schedule generation auto-saves silently.
 
### Why custom dict conversion over marshmallow
 
`marshmallow` adds a dependency and schema definition overhead for a data model this small. Since `Task.to_dict()` already existed and `date.fromisoformat()` handles the only non-trivial type, a custom approach keeps the codebase dependency-free and the serialization logic readable inline.
 
### Agent Mode usage
 
Agent Mode was used to plan the persistence strategy — it proposed both the marshmallow approach and the custom dict approach, then outlined the tradeoffs. The custom approach was chosen. Agent Mode then scaffolded the three methods and the `load_state()` / `save_state()` helpers in `app.py`, which were reviewed and adjusted to handle the species dropdown index correctly on restore and to add the `st.toast` confirmation on startup.
 
## 🔴 Challenge 3: Advanced Priority Scheduling and UI
 
Priority-based scheduling is the core of PawPal+'s decision engine. Here's
how it works end to end:
 
### Priority levels
 
| Emoji | Label | Value |
|---|---|---|
| 🔴 | Critical | 5 |
| 🟠 | High | 4 |
| 🟡 | Medium | 3 |
| 🟢 | Low | 2 |
| ⚪ | Minimal | 1 |
 
### Two-pass scheduling
 
The scheduler uses priority in two distinct ways:
 
1. **Selection pass** (`sort_by_priority`) — tasks are ranked highest-first
   before the time budget is applied. A P5 medication always makes the cut before a P3 enrichment, regardless of what time they're scheduled.
 
2. **Display pass** (`sort_by_time`) — once the plan is finalized, tasks are re-sorted chronologically so the output reads like a real day.
 
### Urgency score (weighted prioritization)
 
The task table shows a computed **urgency score** that goes beyond the raw 1–5 integer:
 
```
score = priority × category_weight × recency_bonus
```
 
An overdue P3 medication (score 6.75) correctly outranks an on-time P5 walk (score 6.0). This is surfaced in the UI task table so owners can see at a glance which tasks are most time-sensitive.
 
### Color-coding in the UI
 
Every task in the schedule display is color-coded:
- `st.success` (green) — task scheduled with no conflicts
- `st.warning` (yellow) — task has a time overlap with another task
- `st.error` (red) — task dropped due to time budget
 
The task table also shows emoji priority labels (🔴🟠🟡🟢⚪) on every row
so priority is visible before a schedule is even generated.