
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Seat Rotation Plan", layout="wide")
st.title("🗓️ Weekly Seat Rotation Planner")

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

# --- Inputs ---
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

# --- Editable Table ---
schedule_df = st.session_state.schedule.copy()
edited_schedule = st.data_editor(
    schedule_df,
    column_config={day: st.column_config.SelectboxColumn(label=day, options=list(EMOJIS.values())) for day in DAYS},
    use_container_width=True,
    hide_index=False
)

# Convert to raw (non-emoji) values
raw_schedule = edited_schedule.applymap(lambda x: REVERSE_EMOJIS.get(x, x))

# --- Smart Assignment Logic ---
def apply_smart_balance(schedule_df, max_desks):
    updated = schedule_df.copy()
    for day in DAYS:
        office_candidates = schedule_df[schedule_df[day] == "Office"].index.tolist()
        seated = office_candidates[:max_desks]
        overflow = office_candidates[max_desks:]
        for person in schedule_df.index:
            if schedule_df.loc[person, day] == "Locked":
                continue  # Preserve locked
            elif person in seated:
                updated.loc[person, day] = "🏢 Office"
            elif person in overflow:
                updated.loc[person, day] = "💻 Remote"  # Push overflowed to Remote
            else:
                updated.loc[person, day] = EMOJIS[schedule_df.loc[person, day]]
    return updated

# --- Smart Balance Button ---
if st.button("🔄 Smart Assign Desks"):
    st.session_state.schedule = apply_smart_balance(raw_schedule, desk_count)

# --- Export Section ---
st.divider()
st.markdown("### 📤 Export")
export_df = st.session_state.schedule.copy()
export_df.insert(0, "Name", export_df.index)
csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "Seat_Rotation_Week.csv", "text/csv")

# --- Instructions & Credits ---
st.divider()
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown("""<div style='text-align: center; font-size: 16px;'>
    📝 **How to Use:**<br>
    1. Edit staff list in the sidebar<br>
    2. Assign 🏢 / 💻 / 🌴 / 🔒 per day<br>
    3. Click Smart Assign to balance desk use<br>
    4. Download the plan as CSV
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 14px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
