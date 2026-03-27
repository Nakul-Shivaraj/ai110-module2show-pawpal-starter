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
