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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
