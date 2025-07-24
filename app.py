
import streamlit as st
import pandas as pd
import random
from collections import defaultdict

st.set_page_config(page_title="Seat Rotation Plan", layout="wide")
st.title("🗓️ Weekly Seat Rotation Planner — Group Sync Enabled")

# --- Config ---
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
EMOJIS = {
    "Office": "🏢 Office",
    "Remote": "💻 Remote",
    "Off": "🌴 Off",
    "Locked": "🔒 Locked"
}
REVERSE_EMOJIS = {v: k for k, v in EMOJIS.items()}
DEFAULT_DESKS = 5

# --- Initial State ---
if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]
if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame(
        [[EMOJIS[random.choice(["Office", "Remote", "Off"])] for _ in DAYS] for _ in st.session_state.staff],
        index=st.session_state.staff,
        columns=DAYS
    )
if "groups" not in st.session_state:
    st.session_state.groups = {name: "" for name in st.session_state.staff}

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=DEFAULT_DESKS)

st.sidebar.markdown("### 👥 Assign Groups")
for name in st.session_state.staff:
    st.session_state.groups[name] = st.sidebar.text_input(f"{name}'s Group", st.session_state.groups.get(name, ""))

new_staff_input = st.sidebar.text_area("Edit Staff List (one per line)", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff List"):
    st.session_state.staff = [s.strip() for s in new_staff_input.split("\n") if s.strip()]
    st.session_state.schedule = pd.DataFrame(
        [[EMOJIS["Remote"] for _ in DAYS] for _ in st.session_state.staff],
        index=st.session_state.staff,
        columns=DAYS
    )
    st.session_state.groups = {name: "" for name in st.session_state.staff}

# --- Weekly Schedule ---
st.markdown("### 📅 Weekly Schedule")
display_schedule = st.session_state.schedule.copy()
edited_schedule = st.data_editor(
    display_schedule,
    column_config={day: st.column_config.SelectboxColumn(label=day, options=list(EMOJIS.values())) for day in DAYS},
    use_container_width=True,
    hide_index=False
)
raw_schedule = edited_schedule.applymap(lambda x: REVERSE_EMOJIS.get(x, x))

# --- Smart Group-Based Assignment ---
def smart_assign_with_groups(schedule_df, group_dict, max_desks):
    updated = schedule_df.copy()
    for day in DAYS:
        locked = schedule_df[schedule_df[day] == "Locked"].index.tolist()
        group_buckets = defaultdict(list)

        for name in schedule_df.index:
            if schedule_df.loc[name, day] == "Office" and name not in locked:
                group = group_dict.get(name, "ungrouped")
                group_buckets[group].append(name)

        seated = []
        overflow = []

        for group, members in group_buckets.items():
            if len(seated) + len(members) <= max_desks:
                seated.extend(members)
            else:
                overflow.extend(members)

        for name in schedule_df.index:
            current_mode = schedule_df.loc[name, day]
            if current_mode == "Locked":
                updated.loc[name, day] = EMOJIS["Locked"]
            elif name in seated:
                updated.loc[name, day] = EMOJIS["Office"]
            elif name in overflow:
                updated.loc[name, day] = EMOJIS["Remote"]
            else:
                updated.loc[name, day] = EMOJIS[current_mode]

    return updated

# --- Apply Smart Assignment ---
if st.button("🔄 Smart Assign Desks (Group Sync)"):
    updated = smart_assign_with_groups(raw_schedule, st.session_state.groups, desk_count)
    st.session_state.schedule = updated.copy()

# --- Export Section ---
st.divider()
st.markdown("### 📤 Export")
export_df = st.session_state.schedule.copy()
export_df.insert(0, "Name", export_df.index)
export_df.insert(1, "Group", export_df["Name"].map(st.session_state.groups))
csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "Seat_Rotation_Grouped.csv", "text/csv")

# --- How to Use + Footer ---
st.divider()
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown("""<div style='text-align: center; font-size: 16px;'>
    📝 **How to Use:**<br>
    1. Assign groups in the sidebar<br>
    2. Edit the weekly table as needed<br>
    3. Click Smart Assign to group-schedule desks<br>
    4. Export if needed
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 14px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
