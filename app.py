
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
st.title("📅 Weekly Seat Rotation Planner – Phase 3 (Full Version)")

# --- State Init ---
if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]

if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame("Remote", index=st.session_state.staff, columns=DAYS)

if "groups" not in st.session_state:
    st.session_state.groups = pd.Series([""] * len(st.session_state.staff), index=st.session_state.staff)

if "fairness" not in st.session_state:
    st.session_state.fairness = pd.Series([0] * len(st.session_state.staff), index=st.session_state.staff)

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
    st.session_state.fairness = pd.Series([0] * len(new_staff), index=new_staff)

# --- Calendar UI Table ---
def draw_calendar():
    edited = []
    with st.form("calendar_form"):
        st.markdown("### 🧾 Weekly Schedule (Calendar View)")
        grid = []
        header = ["Name", "Group"] + DAYS
        grid.append(header)
        for name in st.session_state.staff:
            row = [name]
            row.append(st.selectbox("", GROUP_OPTIONS, key=f"group_{name}", index=GROUP_OPTIONS.index(st.session_state.groups.get(name, ""))))
            for day in DAYS:
                current = st.session_state.schedule.loc[name, day]
                emoji = STATUS_ICONS.get(current, "")
                row.append(st.selectbox(f"{name}_{day}", STATUS_OPTIONS, key=f"{name}_{day}_status", index=STATUS_OPTIONS.index(current)))
            edited.append(row)
        st.form_submit_button("Apply Manual Changes")
    return edited

# --- Smart Logic (Final Version) ---
def smart_assign(schedule_df, group_series, fairness_scores, desk_limit, sync_grouping):
    updated = schedule_df.copy()
    fair = fairness_scores.copy()
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
            sorted_candidates = sorted(candidates, key=lambda name: fair[name])
            assigned = sorted_candidates[:desk_limit]

        for name in schedule_df.index:
            if schedule_df.loc[name, day] == "Locked":
                updated.loc[name, day] = "Locked"
            elif name in assigned:
                updated.loc[name, day] = "Office"
                fair[name] += 1
            else:
                updated.loc[name, day] = "Remote"
    return updated, fair

# --- Smart Assign Button ---
if st.button("🧠 Smart Assign Desks"):
    updated_schedule, updated_fairness = smart_assign(
        st.session_state.schedule,
        st.session_state.groups,
        st.session_state.fairness,
        desk_count,
        group_enabled
    )
    st.session_state.schedule = updated_schedule
    st.session_state.fairness = updated_fairness

# --- Render Weekly Calendar Grid ---
calendar = []
calendar.append(["Name", "Group"] + DAYS)
for name in st.session_state.staff:
    row = [name, st.session_state.groups[name]] + [STATUS_ICONS.get(st.session_state.schedule.loc[name, d], "❔") for d in DAYS]
    calendar.append(row)
st.markdown("### 🗂️ Calendar View")
st.dataframe(pd.DataFrame(calendar[1:], columns=calendar[0]), use_container_width=True)

# --- Fairness Table ---
st.markdown("### ⚖️ Fairness Scoring")
st.dataframe(st.session_state.fairness.sort_values(ascending=False).rename("Desk Count"))

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
