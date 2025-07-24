
import streamlit as st
import pandas as pd
import random

# --- Constants ---
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
STATUS_ICONS = {
    "Office": "🏢 Office",
    "Remote": "💻 Remote",
    "Off": "🌴 Off",
    "Locked": "🔒 Locked"
}
STATUS_OPTIONS = ["Office", "Remote", "Off", "Locked"]

st.set_page_config("Seat Rotation Planner", layout="wide")
st.title("🪑 Weekly Seat Rotation Planner")

# --- Initialize State ---
if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]

if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame("Remote", index=st.session_state.staff, columns=DAYS)

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=3)

staff_input = st.sidebar.text_area("Edit Staff List (one per line)", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff List"):
    staff = [s.strip() for s in staff_input.split("\n") if s.strip()]
    st.session_state.staff = staff
    st.session_state.schedule = pd.DataFrame("Remote", index=staff, columns=DAYS)

# --- Smart Assignment Logic ---
def smart_assign(schedule_df, desk_limit):
    new_schedule = schedule_df.copy()
    for day in DAYS:
        editable_staff = [name for name in new_schedule.index if new_schedule.loc[name, day] != "Locked"]
        random.shuffle(editable_staff)
        for i, name in enumerate(new_schedule.index):
            if new_schedule.loc[name, day] == "Locked":
                continue
            new_schedule.loc[name, day] = "Office" if i < desk_limit else "Remote"
    return new_schedule

if st.button("🔁 Smart Assign Desks"):
    st.session_state.schedule = smart_assign(st.session_state.schedule, desk_count)

# --- Editable Calendar Table ---
st.markdown("### 📅 Weekly Schedule")
edited_schedule = st.session_state.schedule.copy()

for name in st.session_state.staff:
    cols = st.columns(len(DAYS) + 1)
    cols[0].markdown(f"**{name}**")
    for i, day in enumerate(DAYS):
        current = st.session_state.schedule.loc[name, day]
        new_status = cols[i+1].selectbox("", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current), key=f"{name}_{day}")
        edited_schedule.loc[name, day] = new_status

st.session_state.schedule = edited_schedule

# --- Daily Summary ---
st.markdown("### 📊 Daily Summary (Office vs Remote)")
summary = {"Day": [], "🏢 Office": [], "💻 Remote": []}
for day in DAYS:
    counts = st.session_state.schedule[day].value_counts()
    summary["Day"].append(day)
    summary["🏢 Office"].append(counts.get("Office", 0))
    summary["💻 Remote"].append(counts.get("Remote", 0))
st.dataframe(pd.DataFrame(summary), use_container_width=True)

# --- Export Feature ---
def convert_df(df):
    return df.to_csv(index=True).encode("utf-8")

csv = convert_df(st.session_state.schedule)
st.download_button("📥 Export as CSV", data=csv, file_name="weekly_schedule.csv", mime="text/csv")

# --- Footer Instructions ---
st.divider()
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown("""<div style='text-align: center; font-size: 15px;'>
    🧠 Click "Smart Assign Desks" to fill seats automatically<br>
    ✏️ Manually adjust status per staff/day using the dropdowns<br>
    🔒 Use "Locked" to prevent Smart Assign from overriding a day<br>
    📤 Export the schedule to CSV using the download button
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 13px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
