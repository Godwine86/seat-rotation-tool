
import streamlit as st
import pandas as pd
import random
from collections import defaultdict

# --- Constants ---
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
GROUP_OPTIONS = ["", "A", "B", "C", "D", "E", "F", "G", "H"]
STATUS_ICONS = {
    "Office": "🏢",
    "Remote": "💻",
    "Off": "🌴",
    "Locked": "🔒"
}
STATUS_OPTIONS = ["Office", "Remote", "Off"]

st.set_page_config("Seat Rotation Calendar", layout="wide")
st.title("📅 Weekly Seat Rotation Planner – Phase 3 (Simplified)")

# --- State Init ---
if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]

if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame("Remote", index=st.session_state.staff, columns=DAYS)

if "groups" not in st.session_state:
    st.session_state.groups = pd.Series([""] * len(st.session_state.staff), index=st.session_state.staff)

# --- Sidebar Config ---
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=3)
group_enabled = st.sidebar.checkbox("Enable Group Syncing", value=True)

staff_input = st.sidebar.text_area("Edit Staff List (one per line)", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff"):
    new_staff = [s.strip() for s in staff_input.split("\n") if s.strip()]
    st.session_state.staff = new_staff
    st.session_state.schedule = pd.DataFrame("Remote", index=new_staff, columns=DAYS)
    st.session_state.groups = pd.Series([""] * len(new_staff), index=new_staff)

# --- Smart Logic (Simplified) ---
def smart_assign(schedule_df, group_series, desk_limit, sync_grouping):
    updated = schedule_df.copy()
    for day in DAYS:
        candidates = [name for name in schedule_df.index if schedule_df.loc[name, day] != "Locked"]
        assigned = []
        if sync_grouping:
            grouped = defaultdict(list)
            for name in candidates:
                grouped[group_series.get(name, "")].append(name)
            for group, members in grouped.items():
                if len(assigned) + len(members) <= desk_limit:
                    assigned.extend(members)
        else:
            random.shuffle(candidates)
            assigned = candidates[:desk_limit]

        for name in schedule_df.index:
            if schedule_df.loc[name, day] == "Locked":
                updated.loc[name, day] = "Locked"
            elif name in assigned:
                updated.loc[name, day] = "Office"
            else:
                updated.loc[name, day] = "Remote"
    return updated

# --- Smart Assign Button ---
if st.button("🧠 Smart Assign Desks"):
    updated_schedule = smart_assign(
        st.session_state.schedule,
        st.session_state.groups,
        desk_count,
        group_enabled
    )
    st.session_state.schedule = updated_schedule

# --- Calendar View ---
calendar = []
calendar.append(["Name", "Group"] + DAYS)
for name in st.session_state.staff:
    row = [name, st.session_state.groups[name]] + [STATUS_ICONS.get(st.session_state.schedule.loc[name, d], "❔") for d in DAYS]
    calendar.append(row)
st.markdown("### 🗂️ Calendar View")
st.dataframe(pd.DataFrame(calendar[1:], columns=calendar[0]), use_container_width=True)

# --- Daily Office & Remote Summary ---
summary = {"Day": [], "🏢 Office": [], "💻 Remote": []}
for day in DAYS:
    counts = st.session_state.schedule[day].value_counts()
    summary["Day"].append(day)
    summary["🏢 Office"].append(counts.get("Office", 0))
    summary["💻 Remote"].append(counts.get("Remote", 0))

st.markdown("### 📊 Daily Summary (People in Office & Remote)")
st.dataframe(pd.DataFrame(summary), use_container_width=True)

# --- Footer ---
st.divider()
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown("""<div style='text-align: center; font-size: 15px;'>
    ✏️ Use the dropdowns to manually update the week<br>
    ✅ Click 'Smart Assign Desks' for auto-planning<br>
    🔁 Group Sync keeps teams together (optional)
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 13px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
