
import streamlit as st
import pandas as pd
import random
from collections import defaultdict

st.set_page_config(page_title="Seat Rotation Plan", layout="wide")
st.title("🗓️ Weekly Seat Rotation Planner — Group Sync (Optional)")

# --- Config ---
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
GROUP_OPTIONS = ["", "A", "B", "C", "D", "E", "F", "G", "H"]
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
        [[EMOJIS["Remote"] for _ in DAYS] for _ in st.session_state.staff],
        index=st.session_state.staff,
        columns=DAYS
    )

if "groups" not in st.session_state:
    st.session_state.groups = pd.Series([""] * len(st.session_state.staff), index=st.session_state.staff)

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=DEFAULT_DESKS)
use_group_sync = st.sidebar.checkbox("Enable Group Syncing", value=True)

new_staff_input = st.sidebar.text_area("Edit Staff List (one per line)", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff List"):
    staff_list = [s.strip() for s in new_staff_input.split("\n") if s.strip()]
    st.session_state.staff = staff_list
    st.session_state.schedule = pd.DataFrame(
        [[EMOJIS["Remote"] for _ in DAYS] for _ in staff_list],
        index=staff_list,
        columns=DAYS
    )
    st.session_state.groups = pd.Series([""] * len(staff_list), index=staff_list)

# --- Editable Table ---
st.markdown("### 📅 Weekly Schedule")
combined_df = st.session_state.schedule.copy()
combined_df.insert(0, "Group", st.session_state.groups.reindex(combined_df.index).fillna(""))

edited = st.data_editor(
    combined_df,
    column_config={
        "Group": st.column_config.SelectboxColumn("Group", options=GROUP_OPTIONS)
    } | {
        day: st.column_config.SelectboxColumn(label=day, options=list(EMOJIS.values()))
        for day in DAYS
    },
    use_container_width=True,
    hide_index=False
)

# Separate schedule and groups
edited_groups = edited["Group"]
edited_schedule = edited.drop(columns=["Group"]).applymap(lambda x: REVERSE_EMOJIS.get(x, x))

# --- Smart Assignment Logic Fix ---
def smart_assign(schedule_df, group_series, max_desks, group_sync_enabled):
    updated = schedule_df.copy()
    for day in DAYS:
        locked = [name for name in schedule_df.index if schedule_df.loc[name, day] == "Locked"]
        available = [name for name in schedule_df.index if name not in locked]

        if group_sync_enabled:
            group_buckets = defaultdict(list)
            for name in available:
                group = group_series.get(name, "")
                group_buckets[group].append(name)

            seated = []
            overflow = []
            for group, members in group_buckets.items():
                if len(seated) + len(members) <= max_desks:
                    seated.extend(members)
                else:
                    overflow.extend(members)
        else:
            shuffled = available.copy()
            random.shuffle(shuffled)
            seated = shuffled[:max_desks]
            overflow = shuffled[max_desks:]

        for name in schedule_df.index:
            if name in locked:
                updated.loc[name, day] = EMOJIS["Locked"]
            elif name in seated:
                updated.loc[name, day] = EMOJIS["Office"]
            elif name in overflow:
                updated.loc[name, day] = EMOJIS["Remote"]
            else:
                updated.loc[name, day] = EMOJIS["Remote"]
    return updated

# --- Apply Smart Assignment ---
if st.button("🔄 Smart Assign Desks"):
    result = smart_assign(edited_schedule, edited_groups, desk_count, use_group_sync)
    st.session_state.schedule = result.copy()
    st.session_state.groups = edited_groups.copy()

# --- Export ---
st.divider()
st.markdown("### 📤 Export")
export_df = st.session_state.schedule.copy()
export_df.insert(0, "Name", export_df.index)
export_df.insert(1, "Group", st.session_state.groups)
csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "Seat_Rotation_With_Groups.csv", "text/csv")

# --- Footer ---
st.divider()
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown("""<div style='text-align: center; font-size: 16px;'>
    📝 **How to Use:**<br>
    1. Assign groups using the dropdown next to each name<br>
    2. Edit the weekly schedule as needed<br>
    3. Toggle group syncing ON/OFF from sidebar<br>
    4. Click Smart Assign to auto-allocate desks<br>
    5. Export the plan if needed
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 14px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
