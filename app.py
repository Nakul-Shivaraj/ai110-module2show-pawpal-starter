import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

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
    owner_name      = st.text_input("Owner name",      value="Jordan")
    owner_email     = st.text_input("Owner email",     value="jordan@pawpal.com")
    available_hours = st.text_input("Available hours", value="07:00-20:00",
                                    help="Format: HH:MM-HH:MM  e.g. 07:00-20:00")
with col2:
    pet_name     = st.text_input("Pet name",  value="Buddy")
    species      = st.selectbox("Species",    ["dog", "cat", "rabbit", "bird", "other"])
    pet_age      = st.number_input("Pet age", min_value=0, max_value=30, value=3)
    health_notes = st.text_input("Health notes (optional)", value="")

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Task Builder
# ---------------------------------------------------------------------------
st.subheader("📋 Tasks")

CATEGORY_OPTIONS   = ["walk", "feeding", "medication", "grooming", "enrichment"]
RECURRENCE_OPTIONS = ["daily", "weekly", "none"]
CATEGORY_ICONS     = {"walk": "🦮", "feeding": "🍖", "medication": "💊",
                      "grooming": "✂️", "enrichment": "🧩"}
PRIORITY_LABELS    = {5: "🔴 Critical", 4: "🟠 High", 3: "🟡 Medium",
                      2: "🟢 Low",      1: "⚪ Minimal"}

col1, col2, col3 = st.columns(3)
with col1:
    task_title     = st.text_input("Task title",           value="Morning walk")
    category       = st.selectbox("Category",              CATEGORY_OPTIONS)
with col2:
    duration       = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
    priority       = st.slider("Priority (1=low, 5=high)", min_value=1, max_value=5, value=3)
with col3:
    recurrence     = st.selectbox("Recurrence",            RECURRENCE_OPTIONS)
    preferred_time = st.text_input("Preferred time",       value="08:00",
                                   help="Format: HH:MM  e.g. 08:00")

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
        st.success(f"✅ Added: **{task_title}**")
with col_clear:
    if st.button("🗑️ Clear all tasks"):
        st.session_state.tasks = []
        st.rerun()

# Task table — formatted with icons instead of raw dicts
if st.session_state.tasks:
    st.write("**Current tasks:**")
    display_rows = []
    for t in st.session_state.tasks:
        icon = CATEGORY_ICONS.get(t["category"], "📌")
        display_rows.append({
            "Task":       f"{icon} {t['title']}",
            "Category":   t["category"],
            "Duration":   f"{t['duration_minutes']} min",
            "Priority":   PRIORITY_LABELS.get(t["priority"], t["priority"]),
            "Recurrence": t["recurrence"],
            "Time":       t["preferred_time"] or "—",
        })
    st.table(display_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Filters (shown only when tasks exist)
# ---------------------------------------------------------------------------
if st.session_state.tasks:
    with st.expander("🔍 Filter tasks", expanded=False):
        fc1, fc2 = st.columns(2)
        with fc1:
            filter_category = st.selectbox(
                "Filter by category", ["all"] + CATEGORY_OPTIONS, key="filter_cat")
        with fc2:
            filter_status = st.selectbox(
                "Filter by status", ["all", "incomplete", "complete"], key="filter_status")

        # Build temporary objects just for filtering preview
        if st.button("Apply filter"):
            preview_owner = Owner(owner_name, owner_email, available_hours)
            preview_pet   = Pet(pet_name, species, int(pet_age), health_notes)
            for t in st.session_state.tasks:
                preview_pet.add_task(Task(
                    name=t["title"], category=t["category"],
                    duration_minutes=t["duration_minutes"], priority=t["priority"],
                    recurrence=t["recurrence"], preferred_time=t.get("preferred_time"),
                ))
            preview_owner.add_pet(preview_pet)
            s = Scheduler(preview_owner)

            cat_arg    = None if filter_category == "all" else filter_category
            comp_arg   = None if filter_status == "all" else (filter_status == "complete")
            filtered   = s.filter_tasks(category=cat_arg, completed=comp_arg)

            if filtered:
                st.write(f"**{len(filtered)} task(s) matched:**")
                for pname, task in filtered:
                    icon = CATEGORY_ICONS.get(task.category, "📌")
                    st.markdown(f"- {icon} **{task.name}** — {task.duration_minutes} min "
                                f"({PRIORITY_LABELS.get(task.priority, '')})")
            else:
                st.info("No tasks match that filter.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("📅 Build Schedule")

if st.button("🗓️ Generate schedule", type="primary"):

    if not st.session_state.tasks:
        st.warning("Please add at least one task before generating a schedule.")
        st.stop()

    # Build backend objects (session-state cached)
    owner_key = (owner_name, owner_email, available_hours)
    if "owner" not in st.session_state or st.session_state.owner_key != owner_key:
        st.session_state.owner     = Owner(owner_name, owner_email, available_hours)
        st.session_state.owner_key = owner_key

    pet_key = (pet_name, species, pet_age, health_notes)
    if "pet" not in st.session_state or st.session_state.pet_key != pet_key:
        st.session_state.pet     = Pet(pet_name, species, int(pet_age), health_notes)
        st.session_state.pet_key = pet_key

    owner = st.session_state.owner
    pet   = st.session_state.pet

    pet.tasks = []
    for t in st.session_state.tasks:
        pet.add_task(Task(
            name=t["title"], category=t["category"],
            duration_minutes=t["duration_minutes"], priority=t["priority"],
            recurrence=t["recurrence"], preferred_time=t.get("preferred_time"),
        ))

    owner.pets = []
    owner.add_pet(pet)
    st.session_state.owner = owner

    scheduler = Scheduler(owner)
    plan      = scheduler.generate_plan()
    st.session_state.last_plan      = plan
    st.session_state.last_scheduler = scheduler

    if not plan:
        st.warning("No tasks are due today, or all tasks exceeded your time budget.")
        st.stop()

    budget     = owner.available_minutes()
    total_used = sum(task.duration_minutes for _, task in plan)
    dropped    = scheduler._dropped_tasks
    conflicts  = scheduler.conflict_warnings

    # --- Conflict warnings — shown prominently at the top ---
    if conflicts:
        st.error("⚠️ **Time conflicts detected in your schedule**")
        for w in conflicts:
            # strip the emoji prefix we add in the backend
            clean = w.replace("⚠️  Conflict: ", "")
            st.warning(f"🕐 {clean}")
        st.caption("These tasks are still scheduled. Adjust their times or durations to resolve.")

    # --- Summary metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏱️ Available",  f"{budget} min")
    m2.metric("✅ Scheduled",  f"{total_used} min")
    m3.metric("📌 Tasks",      len(plan))
    m4.metric("⚠️ Conflicts",  len(conflicts),
              delta=None if not conflicts else "fix times",
              delta_color="inverse")

    # --- Scheduled tasks table ---
    st.markdown("### Today's Schedule")
    st.caption("Sorted by time — priority was used to select which tasks made the cut.")

    for i, (pet_name_out, task) in enumerate(plan, 1):
        icon     = CATEGORY_ICONS.get(task.category, "📌")
        label    = PRIORITY_LABELS.get(task.priority, "")
        time_str = task.preferred_time or "anytime"

        # Highlight if this task is part of a conflict
        is_conflicted = any(task.name in w for w in conflicts)
        col_a, col_b = st.columns([3, 1])
        with col_a:
            if is_conflicted:
                st.warning(
                    f"**{i}. {icon} {task.name}** @ {time_str} ⚠️\n\n"
                    f"{label} · {task.duration_minutes} min · {task.recurrence}"
                )
            else:
                st.success(
                    f"**{i}. {icon} {task.name}** @ {time_str}\n\n"
                    f"{label} · {task.duration_minutes} min · {task.recurrence}"
                )
        with col_b:
            st.caption(f"Due: {task.due_date}")

    # --- Dropped tasks ---
    if dropped:
        st.markdown("### 🚫 Dropped Tasks")
        st.caption("These tasks were excluded because the time budget ran out.")
        for _, task in dropped:
            st.error(
                f"~~{task.name}~~ — {task.duration_minutes} min "
                f"(priority {task.priority})"
            )

    # --- Scheduler reasoning ---
    with st.expander("🧠 Scheduler Reasoning", expanded=False):
        st.code(scheduler.explain_plan(), language=None)

elif "last_plan" in st.session_state and st.session_state.last_plan:
    st.info("Showing your last generated schedule. Hit **Generate schedule** to refresh.")