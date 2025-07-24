import streamlit as st
import pandas as pd

st.set_page_config("Seat Rotation Planner", layout="wide")

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
STATUSES = ["Office", "Remote", "Off", "Locked"]
ICONS = {"Office": "🏢 Office", "Remote": "💻 Remote", "Off": "🌴 Off", "Locked": "🔒 Locked"}

# --- Sidebar settings ---
st.sidebar.header("⚙️ Settings")
desk_count = st.sidebar.number_input("Available Desks", min_value=1, value=3)
min_office = st.sidebar.number_input("Min staff in office per day", min_value=1, max_value=5, value=2)
max_office = st.sidebar.number_input("Max staff in office per day", min_value=min_office, max_value=5, value=3)

# --- Staff management ---
if "staff" not in st.session_state:
    st.session_state.staff = ["Ahmed", "Reem", "Lama", "Omar", "Noura", "Faisal"]

if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame(
        [["Remote"] * len(DAYS) for _ in st.session_state.staff],
        index=st.session_state.staff, columns=DAYS
    )

# Each staff: Office/Remote targets (defaults)
if "staff_targets" not in st.session_state:
    st.session_state.staff_targets = {name: {"office": 3, "remote": 2} for name in st.session_state.staff}

staff_input = st.sidebar.text_area("Edit Staff List", value="\n".join(st.session_state.staff))
if st.sidebar.button("Update Staff List"):
    staff = [s.strip() for s in staff_input.split("\n") if s.strip()]
    st.session_state.staff = staff
    st.session_state.schedule = pd.DataFrame(
        [["Remote"] * len(DAYS) for _ in staff],
        index=staff, columns=DAYS
    )
    # Reinitialize or update staff_targets
    for name in staff:
        if name not in st.session_state.staff_targets:
            st.session_state.staff_targets[name] = {"office": 3, "remote": 2}
    for name in list(st.session_state.staff_targets.keys()):
        if name not in staff:
            del st.session_state.staff_targets[name]

# --- Smart Assign (custom targets per staff) ---
def smart_assign(schedule_df, min_office, max_office, desk_count, staff_targets):
    new_schedule = schedule_df.copy()
    staff_list = list(new_schedule.index)
    office_counts = {name: (new_schedule.loc[name] == "Office").sum() for name in staff_list}
    office_slots = min(max_office, desk_count, len(staff_list))
    for day in DAYS:
        locked = [name for name in staff_list if new_schedule.loc[name, day] == "Locked"]
        available = [name for name in staff_list if name not in locked]
        # For each staff, check if below their own target
        preferred = [name for name in available if office_counts[name] < staff_targets[name]["office"]]
        others = [name for name in available if name not in preferred]
        office_today = preferred[:office_slots]
        if len(office_today) < min_office:
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
    return new_schedule

# --- Smart Assign Button ---
if st.button("🔁 Smart Assign Desks"):
    st.session_state.schedule = smart_assign(
        st.session_state.schedule, min_office, max_office, desk_count, st.session_state.staff_targets
    )

# --- Table with per-staff targets ---
st.markdown("### 📅 Weekly Schedule (with per-staff targets)")

cols = st.columns([2, 2, 2, 12, 12, 12, 12, 12])
cols[0].markdown("**Staff**")
cols[1].markdown("**Office Days**")
cols[2].markdown("**Remote Days**")
for i, day in enumerate(DAYS):
    cols[3 + i].markdown(f"**{day}**")

for idx, name in enumerate(st.session_state.staff):
    col1, col2, col3, *day_cols = st.columns([2, 2, 2, 12, 12, 12, 12, 12])
    col1.markdown(f"**{name}**")
    office_val = col2.number_input(
        "Office", min_value=0, max_value=len(DAYS),
        value=st.session_state.staff_targets[name]["office"],
        key=f"office_{name}"
    )
    remote_val = col3.number_input(
        "Remote", min_value=0, max_value=len(DAYS),
        value=st.session_state.staff_targets[name]["remote"],
        key=f"remote_{name}"
    )
    st.session_state.staff_targets[name]["office"] = office_val
    st.session_state.staff_targets[name]["remote"] = remote_val
    for i, day in enumerate(DAYS):
        # Render as icon+label selectbox
        status = st.session_state.schedule.loc[name, day]
        new_status = day_cols[i].selectbox(
            "", STATUSES, index=STATUSES.index(status), key=f"{name}_{day}_cell",
            format_func=lambda x: ICONS[x], label_visibility="collapsed"
        )
        st.session_state.schedule.loc[name, day] = new_status

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
• Edit each staff member’s office/remote day targets beside their name.<br>
• Staff order (sidebar) sets priority if demand exceeds available slots.<br>
• Use Min/Max staff in office per day to control daily allocation.<br>
• Click <b>Smart Assign Desks</b> for automatic scheduling.<br>
• “Locked” days will not change with Smart Assign.<br>
• Edit the schedule directly, export as CSV, or adjust as needed.
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align: right; font-size: 13px; color: gray;'>Created by Ahmed Abahussain</div>",
    unsafe_allow_html=True,
)
