
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Seat Rotation Plan", layout="wide")
st.title("🪑 Weekly Seat Rotation Planner")

# --- Config ---
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
WORK_MODES = ["Office", "Remote", "Off", "Locked"]
DEFAULT_DESKS = 5

# --- Initial State ---
if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]
if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame(
        [[random.choice(WORK_MODES[:-1]) for _ in DAYS] for _ in st.session_state.staff],
        index=st.session_state.staff,
        columns=DAYS
    )

# --- Inputs ---
st.sidebar.header("Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=DEFAULT_DESKS)
new_staff = st.sidebar.text_area("Edit Staff List (one per line)", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff List"):
    st.session_state.staff = [s.strip() for s in new_staff.split("\n") if s.strip()]
    st.session_state.schedule = pd.DataFrame(
        [["Remote"] * len(DAYS) for _ in st.session_state.staff],
        index=st.session_state.staff,
        columns=DAYS
    )

st.markdown("### 📅 Weekly Schedule (click to edit)")
edited_df = st.data_editor(st.session_state.schedule, use_container_width=True, num_rows="dynamic")

# --- Smart Assignment Logic ---
def assign_desks(schedule_df, max_desks):
    assignment = []
    for day in DAYS:
        office_staff = schedule_df[schedule_df[day] == "Office"].index.tolist()
        seated = office_staff[:max_desks]
        unseated = office_staff[max_desks:]
        assignment.append((day, seated, unseated))
    return assignment

# --- Assign Button ---
if st.button("🔄 Smart Assign Desks"):
    st.session_state.schedule = edited_df.copy()
    result = assign_desks(st.session_state.schedule, desk_count)

    st.markdown("### ✅ Desk Assignment Summary")
    for day, seated, unseated in result:
        st.markdown(f"**{day}**")
        st.write(f"✔️ Seated: {', '.join(seated) if seated else 'None'}")
        if unseated:
            st.error(f"⛔ Overflow: {', '.join(unseated)}")

# --- Export Option ---
st.markdown("### 📤 Export")
export_df = edited_df.copy()
export_df.insert(0, "Name", export_df.index)
csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "Seat_Rotation_Week.csv", "text/csv")
