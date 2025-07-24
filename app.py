
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
        [[EMOJIS[random.choice(list(EMOJIS.keys())[:-1])] for _ in DAYS] for _ in st.session_state.staff],
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

st.markdown("### 📅 Weekly Schedule (interactive grid below)")

# --- Display Editable Schedule Table ---
schedule_df = st.session_state.schedule.copy()
edited_schedule = st.data_editor(
    schedule_df,
    column_config={day: st.column_config.SelectboxColumn(label=day, options=list(EMOJIS.values())) for day in DAYS},
    use_container_width=True,
    hide_index=False
)

# Convert back to raw values (no emojis)
raw_schedule = edited_schedule.applymap(lambda x: REVERSE_EMOJIS.get(x, x))

# --- Smart Assignment Logic ---
def assign_desks(schedule_df, max_desks):
    assignment = []
    for day in DAYS:
        office_staff = schedule_df[schedule_df[day] == "Office"].index.tolist()
        seated = office_staff[:max_desks]
        overflow = office_staff[max_desks:]
        assignment.append((day, seated, overflow))
    return assignment

if st.button("🔄 Smart Assign Desks"):
    st.session_state.schedule = edited_schedule.copy()
    result = assign_desks(raw_schedule, desk_count)

    st.markdown("### ✅ Desk Assignment Summary")
    for day, seated, overflow in result:
        st.markdown(f"**📅 {day}**")
        st.success(f"✔️ Seated (desk): {', '.join(seated) if seated else 'None'}")
        if overflow:
            st.warning(f"⚠️ Overflow (no desk): {', '.join(overflow)}")

# --- Export Option ---
st.markdown("### 📤 Export")
export_df = edited_schedule.copy()
export_df.insert(0, "Name", export_df.index)
csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "Seat_Rotation_Week.csv", "text/csv")
