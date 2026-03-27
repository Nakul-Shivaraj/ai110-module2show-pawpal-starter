# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial design includes four core classes:
- **Owner** — stores the pet owner's name and contact preferences. Acts as the entry point; an Owner has one or more Pets.

- **Pet** — stores pet-specific details (name, species, age, health notes). A Pet owns a list of Tasks associated with its care routine.

- **Task** — represents a single care activity (e.g., walk, feeding, medication).Each Task has a name, duration, priority level, and optional recurrence.

- **Scheduler** — takes a Pet's task list and the owner's available time window,then produces an ordered daily plan. It is responsible for sorting by priority,checking for time conflicts, and explaining its decisions.

The three core user actions are:
1. Enter owner and pet info to personalize the care plan.
2. Add and edit tasks (with duration and priority) for a pet.
3. Generate a daily schedule that orders tasks by priority and time constraints with a brief explanation of the reasoning.

**b. Design changes**

After reviewing the skeleton with AI, two potential gaps were identified:
1. **Scheduler has no direct reference to Owner** — available_minutes is passed in manually, but Owner already holds available_hours as a string (e.g."07:00-21:00"). A cleaner design would pass Owner into Scheduler directly and parse the hours automatically. For now, manual passing keeps Scheduler simple and independently testable.

2. **No Task unique ID** — tasks are identified only by name, meaning two tasks with the same name could cause silent bugs in remove_task(). Adding a short UUID or auto-increment ID would make removal safer. This is noted as a Phase 3 improvement once logic is implemented.

Both changes were deferred to avoid over-engineering the skeleton before any logic exists.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints in order: recurrence/due date (only today's tasks are included), priority (highest-priority tasks are accepted first), and time budget (tasks are dropped once the owner's available minutes are exhausted).

**b. Tradeoffs**

The conflict detector warns about overlapping tasks but does not remove them. This keeps the scheduler transparent — an owner who sees a conflict warning can fix it themselves, rather than having the system silently delete a task they asked for. For a planning tool, informing is more appropriate than overriding.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used across every phase: brainstorming class responsibilities in Phase 1, generating method stubs and docstrings in Phase 2, suggesting algorithmic approaches (timedelta for recurrence, interval math for conflict detection) in Phase 4, and drafting test cases in Phase 5.

The most effective prompts were specific and file-anchored — asking "based on this skeleton, how should Scheduler retrieve tasks from Owner?" produced a concrete, usable answer. Vague prompts like "help me with scheduling" did not. Using #file: references kept AI suggestions grounded in the actual code rather than generic patterns.

**b. Judgment and verification**

In Phase 4 Step 5, AI suggested replacing the nested loop in detect_conflicts with itertools.combinations. The suggestion was valid Python but was rejected because the explicit range(len) loop makes the O(n²) complexity visible to future maintainers — a readability advantage that outweighs the marginal conciseness gain. The decision was evaluated by asking: does this change make the code clearer to a reader who hasn't seen it before? The answer was no.

A second example: in Phase 5, AI generated a test asserting that calling mark_task_complete twice on the same task name should raise a ValueError. After running the suite, that test failed — not because the code was broken, but because the assumption was wrong. The first call creates a clone with the same name, so the second call completes the clone, which is correct behavior. The test was rewritten to assert that two completions produce two completed tasks.

---

## 4. Testing and Verification

**a. What you tested**

23 tests across five groups: sorting correctness (chronological order, priority order), recurrence logic (daily/weekly next occurrence dates, clone creation), conflict detection (overlap caught, adjacent tasks safe, cross-pet detection), filtering (by pet name, category, completion status), and budget enforcement (tasks dropped when budget exceeded, empty pet graceful).

These behaviors were chosen because they represent the scheduler's core guarantees — if any of them break silently, the owner gets a wrong plan with no indication of the error.

**b. Confidence**

⭐⭐⭐⭐☆ (4/5). Core scheduling logic is well covered. The UI layer (app.py session state behavior) and malformed input edge cases (e.g. "8:00" instead of "08:00" in preferred_time) are untested. Those would be the next targets.

---

## 5. Reflection

**a. What went well**

The CLI-first workflow was the most valuable structural decision. Having main.py as a verification layer meant every algorithm was confirmed working before touching the UI. Bugs were caught in isolation rather than tangled with Streamlit's rerun behavior.

**b. What you would improve**

The preferred_time field is a plain string with no validation. A malformed entry like "8:00" or "8am" would silently break sort_by_time and detect_conflicts. In the next iteration I would add a validator on Task creation and surface a clear error in the UI rather than letting it fail downstream.

**c. Key takeaway**

The lead architect role means deciding what AI suggestions to accept, modify, or reject — not just accepting whatever is generated. AI accelerated every phase of this project, but every structural decision (Scheduler takes Owner directly, conflict detection warns rather than drops, explicit loop over itertools) required a human judgment call that AI could not make on its own. The quality of the final system reflects those decisions more than the speed at which the code was produced.

## Multi-Model Prompt Comparison

**Comparison and judgment**

Claude's solution was more modular and more Pythonic on two counts: it used dataclasses.replace() which is the stdlib-correct way to copy a dataclass with targeted changes, and it extracted the date math into a named helper that makes the intent readable without needing a comment. Gemini's manual constructor approach works but is fragile — it would break silently if Task gained a new field with no default. Gemini also missed the completed=False reset, which is a real behavioral bug: a task that was marked done last week would stay done after rescheduling. Neither solution was used verbatim; Claude's structure was kept and the date math was verified against the existing next_occurrence() logic already in pawpal_system.py.

**Key takeaway**

Claude defaulted to stdlib idioms (dataclasses.replace) while Gemini defaulted to explicit reconstruction — both produce working code, but Claude's approach is more resilient to future changes in the data model.