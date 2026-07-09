import streamlit as st
from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care and see it all in one schedule.")

# --- Application memory ---------------------------------------------------
# Streamlit reruns top-to-bottom on every click, so the Owner must live in
# session_state to survive. Create it once; reuse it on every rerun.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner

# --- Owner info -----------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Add a task (creates the pet on the fly if it's new) ------------------
st.subheader("Add a task")

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

col3, col4, col5 = st.columns(3)
with col3:
    task_title = st.text_input("Task", value="Morning walk")
with col4:
    task_time = st.time_input("Time of day", value=time(8, 0))
with col5:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col6, col7 = st.columns(2)
with col6:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col7:
    frequency = st.selectbox("Frequency", ["daily", "weekly"], index=0)

if st.button("Add task", type="primary"):
    if not pet_name.strip() or not task_title.strip():
        st.error("Please enter both a pet name and a task.")
    else:
        # Find the pet on this owner, or create + add it via the class method.
        pet = next((p for p in owner.pets if p.name == pet_name), None)
        if pet is None:
            pet = Pet(name=pet_name, species=species)
            owner.add_pet(pet)                       # Owner's method
        pet.add_task(                                # Pet's method
            Task(task_title, task_time, int(duration),
                 frequency=frequency, priority=priority)
        )
        st.success(f"Added '{task_title}' for {pet.name}.")

st.divider()

# --- Current tasks --------------------------------------------------------
st.subheader("Current tasks")
all_tasks = owner.get_all_tasks()

if all_tasks:
    rows = []
    for i, (pet, task) in enumerate(all_tasks):
        rows.append(
            {
                "Pet": pet.name,
                "Task": task.description,
                "Time": task.time.strftime("%H:%M"),
                "Priority": task.priority,
                "Frequency": task.frequency,
                "Status": task.status_label(),
            }
        )
    st.table(rows)

    # Let the user tick a task off, mutating the real object in session_state.
    labels = [f"{pet.name}: {task.description}" for pet, task in all_tasks]
    choice = st.selectbox("Mark a task complete", ["—"] + labels)
    if st.button("Mark complete") and choice != "—":
        pet, task = all_tasks[labels.index(choice)]
        pet.complete_task(task)                       # marks done + queues next occurrence
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate schedule ----------------------------------------------------
st.subheader("Today's schedule")
if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)                 # Scheduler does the work
        st.code(scheduler.format_schedule(), language=None)
        for warning in scheduler.conflict_warnings():
            st.warning(warning)

if st.button("Auto-resolve conflicts"):
    if not owner.pets:
        st.warning("Add some tasks first.")
    else:
        moves = Scheduler(owner).resolve_conflicts()
        if moves:
            for move in moves:
                st.info(move)
            st.rerun()
        else:
            st.success("No conflicts to resolve.")