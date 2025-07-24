
import streamlit as st
import pandas as pd
import random

st.title("🪑 Desk Rotation Planner")

staff = st.text_area("Enter staff names (one per line)").split("\n")
desk_count = st.number_input("Number of available desks", min_value=1, value=3)
days = st.date_input("Select work days", [])

if st.button("Generate Plan"):
    if not staff or not days:
        st.warning("Please enter staff and select dates.")
    else:
        plan = []
        for day in days:
            seated_today = random.sample(staff, min(desk_count, len(staff)))
            for person in staff:
                plan.append({
                    "Date": day.strftime('%Y-%m-%d'),
                    "Staff": person,
                    "Assigned": "Yes" if person in seated_today else "No"
                })
        df = pd.DataFrame(plan)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download as CSV", csv, "Seat_Rotation_Plan.csv", "text/csv")
