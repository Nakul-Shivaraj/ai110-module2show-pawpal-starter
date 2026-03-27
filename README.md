# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

Smarter Scheduling

PawPal+ goes beyond a simple task list with four algorithmic features:

Sorting — Tasks are first ranked by priority (1–5) to decide which ones make the cut, then re-sorted chronologically by preferred time so the final plan reads like a real day (07:30 walk → 08:00 breakfast → 18:00 walk).

Filtering — Any view of tasks can be filtered by pet name, category (walk, feeding, medication, grooming, enrichment), or completion status. Filters can be combined (e.g. Buddy's incomplete medication tasks only).

Recurring tasks — Each task carries a due_date. When a daily or weekly task is marked complete, a new instance is automatically created for the next occurrence using timedelta (daily → +1 day, weekly → +7 days). One-time tasks are simply marked done with no follow-up.

Conflict detection — The scheduler checks every pair of scheduled tasks for time overlap using start/end intervals in minutes-since-midnight. Conflicts surface as warning messages rather than silent drops or crashes, keeping the owner informed without overriding their data.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
