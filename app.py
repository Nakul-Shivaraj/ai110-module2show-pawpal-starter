import streamlit as st
import os
from pawpal_system import Owner, Pet, Task, Scheduler

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart pet care planning — powered by your scheduling logic.")

st.divider()

# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def save_state():
    """Save current owner + pets + tasks to data.json."""
    if "owner" in st.session_state and st.session_state.owner:
        st.session_state.owner.save_to_json(DATA_FILE)

def load_state() -> bool:
    """Load data.json into session state. Returns True if file existed."""
    if os.path.exists(DATA_FILE):
        try:
            loaded = Owner.load_from_json(DATA_FILE)
            st.session_state.owner     = loaded
            st.session_state.owner_key = (loaded.name, loaded.email, loaded.available_hours)
            if loaded.get_pets():
                pet = loaded.get_pets()[0]
                st.session_state.pet     = pet
                st.session_state.pet_key = (pet.name, pet.species, pet.age, pet.health_notes)
                st.session_state.tasks   = [
                    {
                        "title":            t.name,
                        "category":         t.category,
                        "duration_minutes": t.duration_minutes,
                        "priority":         t.priority,
                        "recurrence":       t.recurrence,
                        "preferred_time":   t.preferred_time,
                    }
                    for t in pet.get_tasks()
                ]
            return True
        except Exception:
            return False
    return False

# Load saved data once per session
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = True
    if load_state():
        st.toast("💾 Previous session restored from data.json", icon="✅")

# ---------------------------------------------------------------------------
# Section 1: Owner + Pet Info
# ---------------------------------------------------------------------------
st.subheader("👤 Owner & Pet Info")

# Pre-fill from loaded state if available
saved_owner = st.session_state.get("owner")
saved_pet   = st.session_state.get("pet")

col1, col2 = st.columns(2)
with col1:
    owner_name      = st.text_input("Owner name",      value=saved_owner.name if saved_owner else "Jordan")
    owner_email     = st.text_input("Owner email",     value=saved_owner.email if saved_owner else "jordan@pawpal.com")
    available_hours = st.text_input("Available hours", value=saved_owner.available_hours if saved_owner else "07:00-20:00",
                                    help="Format: HH:MM-HH:MM")
with col2:
    pet_name     = st.text_input("Pet name",  value=saved_pet.name if saved_pet else "Buddy")
    species      = st.selectbox("Species",    ["dog", "cat", "rabbit", "bird", "other"],
                                index=["dog","cat","rabbit","bird","other"].index(saved_pet.species)
                                if saved_pet and saved_pet.species in ["dog","cat","rabbit","bird","other"] else 0)
    pet_age      = st.number_input("Pet age", min_value=0, max_value=30,
                                   value=saved_pet.age if saved_pet else 3)
    health_notes = st.text_input("Health notes (optional)",
                                 value=saved_pet.health_notes if saved_pet else "")

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Task Builder
# ---------------------------------------------------------------------------
st.subheader("📋 Tasks")

CATEGORY_OPTIONS   = ["walk", "feeding", "medication", "grooming", "enrichment"]
RECURRENCE_OPTIONS = ["daily", "weekly", "none"]
CATEGORY_ICONS     = {"walk":"🦮","feeding":"🍖","medication":"💊","grooming":"✂️","enrichment":"🧩"}
PRIORITY_LABELS    = {5:"🔴 Critical",4:"🟠 High",3:"🟡 Medium",2:"🟢 Low",1:"⚪ Minimal"}

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
                                   help="Format: HH:MM")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col_add, col_clear, col_save = st.columns([1, 1, 1])
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
    if st.button("🗑️ Clear tasks"):
        st.session_state.tasks = []
        st.rerun()
with col_save:
    if st.button("💾 Save to file"):
        # Build and save owner with current UI state
        owner = Owner(owner_name, owner_email, available_hours)
        pet   = Pet(pet_name, species, int(pet_age), health_notes)
        for t in st.session_state.tasks:
            pet.add_task(Task(
                name=t["title"], category=t["category"],
                duration_minutes=t["duration_minutes"], priority=t["priority"],
                recurrence=t["recurrence"], preferred_time=t.get("preferred_time"),
            ))
        owner.add_pet(pet)
        st.session_state.owner = owner
        owner.save_to_json(DATA_FILE)
        st.success(f"💾 Saved to `{DATA_FILE}`")

# Task table
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
# Section 3: Filters
# ---------------------------------------------------------------------------
if st.session_state.tasks:
    with st.expander("🔍 Filter tasks", expanded=False):
        fc1, fc2 = st.columns(2)
        with fc1:
            filter_category = st.selectbox("Filter by category",
                                           ["all"] + CATEGORY_OPTIONS, key="filter_cat")
        with fc2:
            filter_status = st.selectbox("Filter by status",
                                         ["all", "incomplete", "complete"], key="filter_status")
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
            s        = Scheduler(preview_owner)
            cat_arg  = None if filter_category == "all" else filter_category
            comp_arg = None if filter_status == "all" else (filter_status == "complete")
            filtered = s.filter_tasks(category=cat_arg, completed=comp_arg)
            if filtered:
                st.write(f"**{len(filtered)} task(s) matched:**")
                for _, task in filtered:
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

    owner_key = (owner_name, owner_email, available_hours)
    if "owner" not in st.session_state or st.session_state.get("owner_key") != owner_key:
        st.session_state.owner     = Owner(owner_name, owner_email, available_hours)
        st.session_state.owner_key = owner_key

    pet_key = (pet_name, species, pet_age, health_notes)
    if "pet" not in st.session_state or st.session_state.get("pet_key") != pet_key:
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

    # Auto-save on every schedule generation
    save_state()

    scheduler = Scheduler(owner)
    plan      = scheduler.generate_plan()
    st.session_state.last_plan      = plan
    st.session_state.last_scheduler = scheduler

    if not plan:
        st.warning("No tasks are due today, or all tasks exceeded your time budget.")
        st.stop()

    budget    = owner.available_minutes()
    total_used = sum(task.duration_minutes for _, task in plan)
    dropped   = scheduler._dropped_tasks
    conflicts = scheduler.conflict_warnings

    # Conflict warnings
    if conflicts:
        st.error("⚠️ **Time conflicts detected in your schedule**")
        for w in conflicts:
            st.warning(f"🕐 {w.replace('⚠️  Conflict: ', '')}")
        st.caption("These tasks are still scheduled. Adjust times or durations to resolve.")

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏱️ Available",  f"{budget} min")
    m2.metric("✅ Scheduled",  f"{total_used} min")
    m3.metric("📌 Tasks",      len(plan))
    m4.metric("⚠️ Conflicts",  len(conflicts), delta_color="inverse")

    # Next available slot hint
    scheduler2 = Scheduler(owner)
    scheduler2.scheduled_tasks = plan
    next_slot = scheduler2.find_next_slot(30)
    if next_slot:
        st.caption(f"💡 Next free 30-min slot: **{next_slot}**")

    # Schedule table
    st.markdown("### Today's Schedule")
    st.caption("Sorted by time — priority determined which tasks made the cut.")
    for i, (_, task) in enumerate(plan, 1):
        icon         = CATEGORY_ICONS.get(task.category, "📌")
        label        = PRIORITY_LABELS.get(task.priority, "")
        time_str     = task.preferred_time or "anytime"
        is_conflicted = any(task.name in w for w in conflicts)
        col_a, col_b = st.columns([3, 1])
        with col_a:
            renderer = st.warning if is_conflicted else st.success
            renderer(f"**{i}. {icon} {task.name}** @ {time_str}"
                     f"{'  ⚠️' if is_conflicted else ''}\n\n"
                     f"{label} · {task.duration_minutes} min · {task.recurrence}")
        with col_b:
            st.caption(f"Due: {task.due_date}")

    if dropped:
        st.markdown("### 🚫 Dropped Tasks")
        for _, task in dropped:
            st.error(f"~~{task.name}~~ — {task.duration_minutes} min (priority {task.priority})")

    with st.expander("🧠 Scheduler Reasoning", expanded=False):
        st.code(scheduler.explain_plan(), language=None)

    st.caption(f"💾 Schedule auto-saved to `{DATA_FILE}`")

elif "last_plan" in st.session_state and st.session_state.last_plan:
    st.info("Showing your last generated schedule. Hit **Generate schedule** to refresh.")