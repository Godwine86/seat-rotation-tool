import streamlit as st
import pandas as pd

st.set_page_config("Seat Rotation Planner", layout="wide")

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
STATUSES = ["Office", "Remote", "Off", "Locked"]
ICONS = {"Office": "🏢 Office", "Remote": "💻 Remote", "Off": "🌴 Off", "Locked": "🔒 Locked"}

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=3)
min_office = st.sidebar.number_input("Min staff in office per day", min_value=1, max_value=5, value=2)
max_office = st.sidebar.number_input("Max staff in office per day", min_value=min_office, max_value=5, value=3)
office_days_target = st.sidebar.number_input("Target office days per person (per week)", min_value=0, max_value=5, value=3)
remote_days_target = st.sidebar.number_input("Target remote days per person (per week)", min_value=0, max_value=5, value=2)

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

# --- Smart Assign (Top of List, but respects targets as much as possible) ---
def smart_assign(schedule_df, min_office, max_office, desk_count, office_days_target, remote_days_target):
    new_schedule = schedule_df.copy()
    staff_list = list(new_schedule.index)
    office_counts = {name: (new_schedule.loc[name] == "Office").sum() for name in staff_list}
    remote_counts = {name: (new_schedule.loc[name] == "Remote").sum() for name in staff_list}
    office_slots = min(max_office, desk_count, len(staff_list))
    for day in DAYS:
        locked = [name for name in staff_list if new_schedule.loc[name, day] == "Locked"]
        available = [name for name in staff_list if name not in locked]
        # Prioritize those under their office_days_target, then fill with others if needed
        preferred = [name for name in available if office_counts[name] < office_days_target]
        others = [name for name in available if name not in preferred]
        office_today = preferred[:office_slots]
        if len(office_today) < min_office:
            # Not enough under-target? Fill remainder with next in line.
            extra_needed = min_office - len(office_today)
            office_today += others[:extra_needed]
        elif len(office_today) < office_slots:
            office_today += others[:office_slots - len(office_today)]
        # Assign statuses
        for name in available:
            if name in office_today:
                new_schedule.loc[name, day] = "Office"
                office_counts[name] += 1
            else:
                new_schedule.loc[name, day] = "Remote"
                remote_counts[name] += 1
    return new_schedule

# --- Smart Assign Button ---
if st.button("🔁 Smart Assign Desks"):
    st.session_state.schedule = smart_assign(
        st.session_state.schedule, min_office, max_office, desk_count, office_days_target, remote_days_target
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
st.markdown("""
<div style='text-align: center; font-size: 16px; line-height: 1.7;'>
<b>How to Use</b><br>
• <b>Staff order = office priority:</b> Top of the list gets office first.<br>
• Use <b>Min/Max staff in office per day</b> to control daily office numbers.<br>
• Set <b>Target office/remote days</b> to influence distribution per person.<br>
• Click <b>Smart Assign Desks</b> for an automatic fill (priority by list order).<br>
• <b>Locked</b> days are never changed by Smart Assign.<br>
• Click any cell to edit or lock manually.<br>
• Download your schedule (with daily counts) as CSV.
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align: right; font-size: 13px; color: gray;'>Created by Ahmed Abahussain</div>",
    unsafe_allow_html=True,
)
