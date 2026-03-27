import streamlit as st

# ---------------------------------------------------------------------------
# Step 1: Import backend classes from pawpal_system.py
# ---------------------------------------------------------------------------
from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Smart pet care planning — powered by your scheduling logic.")

st.divider()

# ---------------------------------------------------------------------------
# Section 1: Owner + Pet Info
# ---------------------------------------------------------------------------
st.subheader("👤 Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner_name        = st.text_input("Owner name",        value="Jordan")
    owner_email       = st.text_input("Owner email",       value="jordan@pawpal.com")
    available_hours   = st.text_input("Available hours",   value="07:00-20:00",
                                      help="Format: HH:MM-HH:MM  e.g. 07:00-20:00")
with col2:
    pet_name    = st.text_input("Pet name",   value="Buddy")
    species     = st.selectbox("Species",     ["dog", "cat", "rabbit", "bird", "other"])
    pet_age     = st.number_input("Pet age",  min_value=0, max_value=30, value=3)
    health_notes = st.text_input("Health notes (optional)", value="")

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Task Builder
# ---------------------------------------------------------------------------
st.subheader("📋 Tasks")

CATEGORY_OPTIONS  = ["walk", "feeding", "medication", "grooming", "enrichment"]
RECURRENCE_OPTIONS = ["daily", "weekly", "none"]

col1, col2, col3 = st.columns(3)
with col1:
    task_title    = st.text_input("Task title",          value="Morning walk")
    category      = st.selectbox("Category",             CATEGORY_OPTIONS)
with col2:
    duration      = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
    priority      = st.slider("Priority (1=low, 5=high)", min_value=1, max_value=5, value=3)
with col3:
    recurrence    = st.selectbox("Recurrence",            RECURRENCE_OPTIONS)
    preferred_time = st.text_input("Preferred time",      value="08:00",
                                   help="Format: HH:MM  e.g. 08:00")

# Initialise task list in session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

col_add, col_clear = st.columns([1, 5])
with col_add:
    if st.button("➕ Add task"):
        st.session_state.tasks.append({
            "title":            task_title,
            "category":         category,
            "duration_minutes": int(duration),
            "priority":         priority,
            "recurrence":       recurrence,
            "preferred_time":   preferred_time or None,
        })
        st.success(f"Added: {task_title}")
with col_clear:
    if st.button("🗑️ Clear all tasks"):
        st.session_state.tasks = []

# Show current task table
if st.session_state.tasks:
    st.write("**Current tasks:**")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("📅 Build Schedule")

CATEGORY_ICONS = {
    "walk":       "🦮",
    "feeding":    "🍖",
    "medication": "💊",
    "grooming":   "✂️",
    "enrichment": "🧩",
}

PRIORITY_LABELS = {
    5: "🔴 Critical",
    4: "🟠 High",
    3: "🟡 Medium",
    2: "🟢 Low",
    1: "⚪ Minimal",
}

if st.button("🗓️ Generate schedule", type="primary"):

    # --- Validate inputs ------------------------------------------------
    if not st.session_state.tasks:
        st.warning("Please add at least one task before generating a schedule.")
        st.stop()

    # --- Build Owner: only create if not already in session state,
    #     or if the owner info has changed since last run.
    #     This prevents wiping out the object on every rerun.
    owner_key = (owner_name, owner_email, available_hours)
    if "owner" not in st.session_state or st.session_state.owner_key != owner_key:
        st.session_state.owner = Owner(
            name=owner_name,
            email=owner_email,
            available_hours=available_hours,
        )
        st.session_state.owner_key = owner_key   # remember what we built it from

    owner = st.session_state.owner

    # --- Build Pet: same pattern — only rebuild if pet info changed -----
    pet_key = (pet_name, species, pet_age, health_notes)
    if "pet" not in st.session_state or st.session_state.pet_key != pet_key:
        st.session_state.pet = Pet(
            name=pet_name,
            species=species,
            age=int(pet_age),
            health_notes=health_notes,
        )
        st.session_state.pet_key = pet_key

    pet = st.session_state.pet

    # --- Sync tasks from session_state onto the Pet object --------------
    # Always rebuild the pet's task list from st.session_state.tasks
    # so the task table and the backend stay in sync.
    pet.tasks = []
    for t in st.session_state.tasks:
        pet.add_task(Task(
            name=t["title"],
            category=t["category"],
            duration_minutes=t["duration_minutes"],
            priority=t["priority"],
            recurrence=t["recurrence"],
            preferred_time=t.get("preferred_time"),
        ))

    # Register pet on owner (clear first to avoid duplicates on rerun)
    owner.pets = []
    owner.add_pet(pet)

    # Store the fully wired owner back into session state
    st.session_state.owner = owner

    # --- Run scheduler --------------------------------------------------
    scheduler = Scheduler(owner)
    plan      = scheduler.generate_plan()

    # Store the last plan so it survives reruns too
    st.session_state.last_plan      = plan
    st.session_state.last_scheduler = scheduler

    # --- Display results ------------------------------------------------
    if not plan:
        st.warning("No tasks are due today, or all tasks exceeded your time budget.")
        st.stop()

    budget     = owner.available_minutes()
    total_used = sum(task.duration_minutes for _, task in plan)
    dropped    = scheduler._dropped_tasks

    # Summary metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("⏱️ Available",  f"{budget} min")
    m2.metric("✅ Scheduled",  f"{total_used} min")
    m3.metric("📌 Tasks",      len(plan))

    st.markdown("### Scheduled Tasks")
    for i, (pet_name_out, task) in enumerate(plan, 1):
        icon  = CATEGORY_ICONS.get(task.category, "📌")
        label = PRIORITY_LABELS.get(task.priority, "Unknown")
        time_str = f"@ {task.preferred_time}" if task.preferred_time else ""
        st.markdown(
            f"**{i}. {icon} {task.name}** {time_str}  \n"
            f"{label} &nbsp;|&nbsp; {task.duration_minutes} min "
            f"&nbsp;|&nbsp; {task.category} &nbsp;|&nbsp; repeats: {task.recurrence}"
        )

    if dropped:
        st.markdown("### ⚠️ Dropped Tasks *(exceeded time budget)*")
        for pet_name_out, task in dropped:
            st.markdown(
                f"- ~~{task.name}~~ — {task.duration_minutes} min "
                f"(priority {task.priority})"
            )

    # Reasoning expander
    with st.expander("🧠 Scheduler Reasoning", expanded=False):
        st.code(scheduler.explain_plan(), language=None)

# ---------------------------------------------------------------------------
# Show last plan if it exists (persists across reruns without regenerating)
# ---------------------------------------------------------------------------
elif "last_plan" in st.session_state and st.session_state.last_plan:
    st.info("Showing your last generated schedule. Hit **Generate schedule** to refresh.")