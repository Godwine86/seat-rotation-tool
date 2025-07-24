import streamlit as st
import pandas as pd
import random

st.set_page_config("Seat Rotation Planner", layout="wide")

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
STATUSES = ["Office", "Remote", "Off", "Locked"]
ICONS = {"Office": "🏢 Office", "Remote": "💻 Remote", "Off": "🌴 Off", "Locked": "🔒 Locked"}

# --- Sidebar settings ---
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=3)
office_days_target = st.sidebar.number_input(
    "Days per person in Office (per week)", min_value=0, max_value=5, value=3
)
remote_days_target = st.sidebar.number_input(
    "Days per person Remote/Online (per week)", min_value=0, max_value=5, value=2
)

if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]
if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame(
        [["Remote"] * len(DAYS) for _ in st.session_state.staff],
        index=st.session_state.staff, columns=DAYS
    )

staff_input = st.sidebar.text_area("Edit Staff List", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff List"):
    staff = [s.strip() for s in staff_input.split("\n") if s.strip()]
    st.session_state.staff = staff
    st.session_state.schedule = pd.DataFrame(
        [["Remote"] * len(DAYS) for _ in staff],
        index=staff, columns=DAYS
    )

# --- Fair Smart Assign ---
def smart_assign(schedule_df, desk_limit, office_days_target, remote_days_target):
    new_schedule = schedule_df.copy()
    staff_list = list(new_schedule.index)
    office_counts = {name: (new_schedule.loc[name] == "Office").sum() for name in staff_list}
    for day in DAYS:
        # Respect locked cells
        locked = [name for name in staff_list if new_schedule.loc[name, day] == "Locked"]
        # Only assign Office to those who haven't hit their target yet
        available = [name for name in staff_list if name not in locked and office_counts[name] < office_days_target]
        # Sort by fewest office days (fair), shuffle to break ties
        random.shuffle(available)
        sorted_candidates = sorted(available, key=lambda n: office_counts[n])
        office_today = sorted_candidates[:desk_limit]
        for name in staff_list:
            if new_schedule.loc[name, day] == "Locked":
                continue
            if name in office_today:
                new_schedule.loc[name, day] = "Office"
                office_counts[name] += 1
            else:
                new_schedule.loc[name, day] = "Remote"
    return new_schedule

# --- Smart Assign Button ---
if st.button("🔁 Smart Assign Desks"):
    st.session_state.schedule = smart_assign(
        st.session_state.schedule, desk_count, office_days_target, remote_days_target
    )

# --- SMART TABLE ---
st.markdown("### 📅 Weekly Schedule (Smart Table)")

icon_schedule = st.session_state.schedule.replace(ICONS)

edited = st.data_editor(
    icon_schedule,
    column_config={
        day: st.column_config.SelectboxColumn(
            label=day, 
            options=list(ICONS.values())
        ) for day in DAYS
    },
    key="main_table",
    use_container_width=True,
    hide_index=False,
    num_rows="dynamic"
)

# Update session state with selected values (convert back to raw status)
reverse_icons = {v: k for k, v in ICONS.items()}
for name in st.session_state.staff:
    for day in DAYS:
        value = edited.loc[name, day]
        if value in reverse_icons:
            st.session_state.schedule.loc[name, day] = reverse_icons[value]

# --- Export with Office/Remote counts ---
export_df = st.session_state.schedule.copy()
office_counts = []
remote_counts = []
for day in DAYS:
    col = export_df[day]
    office_counts.append((col == "Office").sum())
    remote_counts.append((col == "Remote").sum())
export_df.loc["Office Count"] = office_counts
export_df.loc["Remote Count"] = remote_counts

def convert_df(df):
    return df.to_csv(index=True).encode("utf-8")
csv = convert_df(export_df)
st.download_button("📥 Export as CSV", data=csv, file_name="weekly_schedule.csv", mime="text/csv")

# --- Daily summary table below the smart table ---
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

# --- Footer instructions ---
st.divider()
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown("""<div style='text-align: center; font-size: 15px;'>
    🔁 Use 'Smart Assign Desks' to auto-fill seat plan with your targets<br>
    ✏️ Click any cell to edit (icon + label)<br>
    🔒 Locked days won't change on auto assign<br>
    📥 Export your plan (with summary) using the download button
    </div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown("""<div style='text-align: right; font-size: 13px; color: gray;'>
    Created by Ahmed Abahussain
    </div>""", unsafe_allow_html=True)
