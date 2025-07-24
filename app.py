
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Seat Rotation Plan", layout="wide")
st.title("🪑 Weekly Seat Rotation Planner")

# --- Config ---
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
WORK_MODES = {
    "🏢 Office": "Office",
    "💻 Remote": "Remote",
    "🌴 Off": "Off",
    "🔒 Locked": "Locked"
}
DEFAULT_DESKS = 5

# --- Initial State ---
if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]
if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame(
        [[random.choice(list(WORK_MODES.values())[:-1]) for _ in DAYS] for _ in st.session_state.staff],
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
        [[random.choice(list(WORK_MODES.values())[:-1]) for _ in DAYS] for _ in st.session_state.staff],
        index=st.session_state.staff,
        columns=DAYS
    )

st.markdown("### 📅 Weekly Schedule (click to edit)")

# Dropdown display using icons
def display_mode_selector(row):
    return {day: st.selectbox(f"{staff} - {day}", list(WORK_MODES.keys()), index=list(WORK_MODES.values()).index(row[day]), key=f"{staff}_{day}")
            for day in DAYS}

updated_schedule = {}
for staff in st.session_state.staff:
    row = st.session_state.schedule.loc[staff]
    updated_schedule[staff] = display_mode_selector(row)

# Convert back to DataFrame with actual values
new_schedule_df = pd.DataFrame({staff: {day: WORK_MODES[mode] for day, mode in days.items()} for staff, days in updated_schedule.items()}).T

# --- Smart Assignment Logic ---
def assign_desks(schedule_df, max_desks):
    assignment = []
    for day in DAYS:
        office_staff = schedule_df[schedule_df[day] == "Office"].index.tolist()
        seated = office_staff[:max_desks]
        overflow = office_staff[max_desks:]
        assignment.append((day, seated, overflow))
    return assignment

# --- Assign Button ---
if st.button("🔄 Smart Assign Desks"):
    st.session_state.schedule = new_schedule_df.copy()
    result = assign_desks(st.session_state.schedule, desk_count)

    st.markdown("### ✅ Desk Assignment Summary")
    for day, seated, overflow in result:
        st.markdown(f"**📅 {day}**")
        st.success(f"✔️ Seated (desk): {', '.join(seated) if seated else 'None'}")
        if overflow:
            st.warning(f"⚠️ Overflow (no desk): {', '.join(overflow)}")

# --- Export Option ---
st.markdown("### 📤 Export")
export_df = new_schedule_df.copy()
export_df.insert(0, "Name", export_df.index)
csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "Seat_Rotation_Week.csv", "text/csv")
