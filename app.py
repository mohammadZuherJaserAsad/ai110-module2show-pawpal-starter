"""
PawPal+ Streamlit Application
A smart pet care management UI connected to the PawPal+ scheduling engine.
"""

import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session State Initialization ---
# Streamlit reruns the script on every interaction, so we use session_state
# to persist our Owner object and Scheduler across reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

owner = st.session_state.owner
today = datetime.now().strftime("%Y-%m-%d")

# --- Header ---
st.title("🐾 PawPal+")
st.caption("Smart pet care management — keep your furry friends happy and healthy!")

# --- Owner Setup ---
with st.expander("Owner Setup", expanded=not bool(owner.name)):
    owner_name = st.text_input("Your name", value=owner.name if owner.name else "")
    if st.button("Set Owner Name"):
        owner.name = owner_name
        st.session_state.scheduler = Scheduler(owner=owner)
        st.rerun()

if not owner.name:
    st.info("Enter your name above to get started!")
    st.stop()

# Ensure scheduler exists
if st.session_state.scheduler is None:
    st.session_state.scheduler = Scheduler(owner=owner)
scheduler = st.session_state.scheduler

st.markdown(f"**Welcome, {owner.name}!** You have **{len(owner.pets)}** pet(s) registered.")

# --- Add Pet Section ---
st.divider()
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="", key="pet_name_input")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "fish", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)

if st.button("Add Pet"):
    if pet_name:
        existing = owner.get_pet(pet_name)
        if existing:
            st.warning(f"A pet named '{pet_name}' already exists!")
        else:
            new_pet = Pet(name=pet_name, species=species, age=age)
            owner.add_pet(new_pet)
            st.success(f"Added {pet_name} the {species}!")
            st.rerun()
    else:
        st.warning("Please enter a pet name.")

# --- Display Pets ---
if owner.pets:
    st.divider()
    st.subheader("Your Pets")
    for pet in owner.pets:
        with st.expander(f"{'🐕' if pet.species == 'dog' else '🐈' if pet.species == 'cat' else '🐾'} {pet.name} ({pet.species}, age {pet.age}) — {len(pet.tasks)} tasks"):
            if pet.tasks:
                for i, task in enumerate(pet.tasks):
                    status_icon = "✅" if task.completed else "⏳"
                    priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
                    freq_label = f" [{task.frequency}]" if task.frequency != "once" else ""

                    col_status, col_info, col_action = st.columns([1, 6, 2])
                    with col_status:
                        st.write(f"{status_icon} {priority_color}")
                    with col_info:
                        st.write(f"**{task.time}** — {task.description}{freq_label} ({task.duration_minutes}min)")
                    with col_action:
                        if not task.completed:
                            if st.button("Complete", key=f"complete_{pet.name}_{i}"):
                                new_task = scheduler.mark_task_complete(task)
                                if new_task:
                                    st.toast(f"Recurring task rescheduled for {new_task.date}")
                                st.rerun()
            else:
                st.info("No tasks yet. Add one below!")

# --- Add Task Section ---
if owner.pets:
    st.divider()
    st.subheader("Schedule a Task")

    col1, col2 = st.columns(2)
    with col1:
        task_pet = st.selectbox("For which pet?", [p.name for p in owner.pets])
    with col2:
        task_desc = st.text_input("Task description", value="Morning walk")

    col3, col4, col5, col6 = st.columns(4)
    with col3:
        task_time = st.time_input("Time", value=None)
    with col4:
        task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
    with col5:
        task_priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
    with col6:
        task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add Task"):
        if task_desc and task_time:
            pet = owner.get_pet(task_pet)
            if pet:
                time_str = task_time.strftime("%H:%M")
                new_task = Task(
                    description=task_desc,
                    time=time_str,
                    duration_minutes=int(task_duration),
                    priority=task_priority,
                    frequency=task_frequency,
                    date=today,
                )
                pet.add_task(new_task)
                st.success(f"Added '{task_desc}' for {task_pet} at {time_str}!")
                st.rerun()
        else:
            st.warning("Please fill in the task description and time.")

# --- Generate Schedule ---
if owner.pets and any(p.tasks for p in owner.pets):
    st.divider()
    st.subheader("Today's Schedule")

    # Conflict warnings
    all_tasks = owner.get_all_tasks()
    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        for conflict in conflicts:
            st.warning(f"⚠️ {conflict}")

    # Sorted schedule
    schedule = scheduler.get_todays_schedule()
    if schedule:
        # Display as a clean table
        table_data = []
        for task in schedule:
            priority_icon = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}.get(task.priority, task.priority)
            status = "✅ Done" if task.completed else "⏳ Pending"
            freq = task.frequency.capitalize()
            table_data.append({
                "Time": task.time,
                "Task": task.description,
                "Pet": task.pet_name,
                "Priority": priority_icon,
                "Duration": f"{task.duration_minutes} min",
                "Frequency": freq,
                "Status": status,
            })
        st.table(table_data)

        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            total = len(schedule)
            done = sum(1 for t in schedule if t.completed)
            st.metric("Tasks", f"{done}/{total} done")
        with col2:
            total_min = sum(t.duration_minutes for t in schedule if not t.completed)
            st.metric("Time Remaining", f"{total_min} min")
        with col3:
            high_priority = sum(1 for t in schedule if t.priority == "high" and not t.completed)
            st.metric("High Priority", high_priority)
    else:
        st.info("No tasks scheduled for today.")

# --- Footer ---
st.divider()
st.caption("PawPal+ — Built with Python, Streamlit, and love for pets 🐾")
