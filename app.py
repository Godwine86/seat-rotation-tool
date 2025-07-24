import streamlit as st
import pandas as pd
import random

st.set_page_config("Seat Rotation Planner", layout="wide")

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
STATUSES = ["Office", "Remote", "Off", "Locked"]
ICONS = {"Office": "🏢", "Remote": "💻", "Off": "🌴", "Locked": "🔒"}

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

# Unified Interactive Table
st.markdown("### 📅 Weekly Schedule (Click any cell to change status)")
edited_schedule = st.session_state.schedule.copy()

for row_idx, name in enumerate(st.session_state.staff):
    cols = st.columns([1] + [2]*len(DAYS))
    cols[0].markdown(f"**{name}**")
    for col_idx, day in enumerate(DAYS):
        current = edited_schedule.loc[name, day]
        display = f"{ICONS.get(current, '')} {current}"
        new_status = cols[col_idx+1].selectbox(
            "", STATUSES, index=STATUSES.index(current),
            key=f"{name}_{day}_cell", label_visibility="collapsed"
        )
        edited_schedule.loc[name, day] = new_status

st.session_state.schedule = edited_schedule

# Daily summary
st.markdown("### 📊 Daily Summary")
summary = {"Day": [], "🏢 Office": [], "💻 Remote": [], "🌴 Off": [], "🔒 Locked": []}
for day in DAYS:
    counts = st.session_state.schedule[day].value_counts()
    summary["Day"].append(day)
    summary["🏢 Office"].append(counts.get("Office", 0))
    summary["💻 Remote"].append(counts.get("Remote", 0))
    summary["🌴 Off"].append(counts.get("Off", 0))
    summary["🔒 Locked"].append(counts.get("Locked", 0))
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
    🔁 Use 'Smart Assign Desks' to auto-fill seat plan<br>
    ✏️ Click any cell to change Office/Remote/Off/Locked<br>
    🔒 Locked days won't change on auto assign<br>
    📥 Export your plan using the download button
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 13px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
