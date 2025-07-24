
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Seat Rotation Plan", layout="wide")
st.title("🗓️ Weekly Seat Rotation Planner")

# --- Configuration ---
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
        [[EMOJIS[random.choice(["Office", "Remote", "Off"])] for _ in DAYS]
         for _ in st.session_state.staff],
        index=st.session_state.staff,
        columns=DAYS
    )

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=DEFAULT_DESKS)
new_staff = st.sidebar.text_area("Edit Staff List (one per line)", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff List"):
    st.session_state.staff = [s.strip() for s in new_staff.split("\n") if s.strip()]
    st.session_state.schedule = pd.DataFrame(
        [[EMOJIS["Remote"] for _ in DAYS] for _ in st.session_state.staff],
        index=st.session_state.staff,
        columns=DAYS
    )

st.markdown("### 📅 Weekly Schedule")

# --- Editable Table Display ---
schedule_df = st.session_state.schedule.copy()
edited_schedule = st.data_editor(
    schedule_df,
    column_config={day: st.column_config.SelectboxColumn(label=day, options=list(EMOJIS.values())) for day in DAYS},
    use_container_width=True,
    hide_index=False
)

# Convert emoji-labeled values to raw mode values
raw_schedule = edited_schedule.applymap(lambda x: REVERSE_EMOJIS.get(x, x))

# --- Smart Desk Assignment Logic ---
def smart_assign(schedule_df, max_desks):
    updated = schedule_df.copy()
    for day in DAYS:
        locked_staff = schedule_df[schedule_df[day] == "Locked"].index.tolist()
        office_staff = [name for name in schedule_df.index
                        if schedule_df.loc[name, day] == "Office" and name not in locked_staff]

        seated = office_staff[:max_desks]
        overflow = office_staff[max_desks:]

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

# --- Smart Assign Button ---
if st.button("🔄 Smart Assign Desks"):
    updated = smart_assign(raw_schedule, desk_count)
    st.session_state.schedule = updated.copy()

# --- Export CSV ---
st.divider()
st.markdown("### 📤 Export")
export_df = st.session_state.schedule.copy()
export_df.insert(0, "Name", export_df.index)
csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "Seat_Rotation_Week.csv", "text/csv")

# --- How to Use & Footer ---
st.divider()
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown("""<div style='text-align: center; font-size: 16px;'>
    📝 **How to Use:**<br>
    1. Edit staff list in the sidebar<br>
    2. Use the table to assign 🏢 / 💻 / 🌴 / 🔒 per day<br>
    3. Click Smart Assign to balance desks<br>
    4. Export your plan if needed
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 14px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
