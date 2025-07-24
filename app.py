
import streamlit as st
import pandas as pd
import random

st.set_page_config("Seat Rotation Planner", layout="wide")

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
STATUSES = ["Office", "Remote", "Off", "Locked"]
ICONS = {"Office": "🏢 Office", "Remote": "💻 Remote", "Off": "🌴 Off", "Locked": "🔒 Locked"}

# Initialize session state
if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]

if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame("Remote", index=st.session_state.staff, columns=DAYS)

# Sidebar settings
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=3)

staff_input = st.sidebar.text_area("Edit Staff List", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff List"):
    staff = [s.strip() for s in staff_input.split("\n") if s.strip()]
    st.session_state.staff = staff
    st.session_state.schedule = pd.DataFrame("Remote", index=staff, columns=DAYS)

# Smart assign desks
def smart_assign(schedule_df, desk_limit):
    new_schedule = schedule_df.copy()
    for day in DAYS:
        editable = [name for name in schedule_df.index if schedule_df.loc[name, day] != "Locked"]
        random.shuffle(editable)
        for i, name in enumerate(schedule_df.index):
            if schedule_df.loc[name, day] == "Locked":
                continue
            new_schedule.loc[name, day] = "Office" if i < desk_limit else "Remote"
    return new_schedule

if st.button("🔁 Smart Assign Desks"):
    st.session_state.schedule = smart_assign(st.session_state.schedule, desk_count)

# Weekly Calendar Grid View
st.markdown("### 📅 Weekly Schedule")
with st.container():
    table = []
    header = ["**Name**"] + [f"**{day}**" for day in DAYS]
    table.append(header)

    for name in st.session_state.staff:
        row = [f"**{name}**"]
        for day in DAYS:
            current = st.session_state.schedule.loc[name, day]
            label = ICONS.get(current, current)
            new_val = st.selectbox("", STATUSES, index=STATUSES.index(current),
                                   key=f"{name}_{day}", label_visibility="collapsed")
            st.session_state.schedule.loc[name, day] = new_val
            row.append(ICONS[new_val])
        table.append(row)

    # render display table
    st.markdown("#### Current View")
    styled_df = st.session_state.schedule.replace(ICONS)
    st.dataframe(styled_df, use_container_width=True)

# Daily summary table
st.markdown("### 📊 Daily Summary")
summary = {"Day": [], "🏢 Office": [], "💻 Remote": []}
for day in DAYS:
    counts = st.session_state.schedule[day].value_counts()
    summary["Day"].append(day)
    summary["🏢 Office"].append(counts.get("Office", 0))
    summary["💻 Remote"].append(counts.get("Remote", 0))
st.dataframe(pd.DataFrame(summary), use_container_width=True)

# Export
def convert_df(df):
    return df.to_csv(index=True).encode("utf-8")

csv = convert_df(st.session_state.schedule)
st.download_button("📥 Export as CSV", data=csv, file_name="weekly_schedule.csv", mime="text/csv")

# Footer
st.divider()
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown("""<div style='text-align: center; font-size: 15px;'>
    🧠 Click "Smart Assign Desks" to fill seats automatically<br>
    ✏️ Adjust each cell with dropdowns<br>
    🔒 Use "Locked" to protect a day from reassignment<br>
    📤 Export the schedule to CSV using the download button
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 13px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
