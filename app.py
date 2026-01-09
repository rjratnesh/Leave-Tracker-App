import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import calendar

# --- Constants & Configuration ---
LEAVE_TYPES = {
    'S': {'label': 'Sick Leave', 'color': '🔴', 'value': 1},
    'PL': {'label': 'Plan Leave', 'color': '🔵', 'value': 1},
    'CL': {'label': 'Casual Leave', 'color': '🟢', 'value': 1},
    'H1': {'label': 'Half Day (AM)', 'color': '🟡', 'value': 0.5},
    'H2': {'label': 'Half Day (PM)', 'color': '🟠', 'value': 0.5},
    'WO': {'label': 'Week Off', 'color': '⚪', 'value': 0},
    'HOL': {'label': 'Holiday', 'color': '🟣', 'value': 0},
}

INITIAL_EMPLOYEES = [
    {'id': '1', 'name': 'Rahul', 'attendance': {}},
    {'id': '2', 'name': 'Maksud', 'attendance': {}},
    {'id': '3', 'name': 'Ratnesh', 'attendance': {}},
    {'id': '4', 'name': 'Abhishek', 'attendance': {}},
    {'id': '5', 'name': 'Aishwarya', 'attendance': {}},
    {'id': '6', 'name': 'Prashant', 'attendance': {}},
]

DATA_FILE = 'leave_data.json'

# --- Helper Functions ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return INITIAL_EMPLOYEES

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_days_in_month(year, month):
    num_days = calendar.monthrange(year, month)[1]
    days = []
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        days.append({
            'date': d,
            'day_of_month': day,
            'day_of_week': d.strftime('%a'),
            'is_weekend': d.weekday() >= 5,
            'date_str': d.strftime('%Y-%m-%d')
        })
    return days

# --- Main App ---
st.set_page_config(page_title="LeaveTracker Pro", layout="wide")

st.title("🚀 LeaveTracker Pro")
st.markdown("### Employee Attendance & Leave Management")

# Initialize Session State
if 'employees' not in st.session_state:
    st.session_state.employees = load_data()

if 'current_date' not in st.session_state:
    st.session_state.current_date = date(2026, 1, 1)

# Sidebar for Navigation & Tools
st.sidebar.header("Navigation")
curr_date = st.sidebar.date_input("Select Month/Year", st.session_state.current_date)
if curr_date != st.session_state.current_date:
    st.session_state.current_date = curr_date
    st.rerun()

year = st.session_state.current_date.year
month = st.session_state.current_date.month

st.sidebar.divider()
st.sidebar.header("Leave Legend")
for code, config in LEAVE_TYPES.items():
    st.sidebar.markdown(f"{config['color']} **{code}**: {config['label']} ({config['value']} day)")

st.sidebar.divider()
if st.sidebar.button("🗑️ Reset All Data", type="secondary"):
    if st.sidebar.checkbox("Confirm Reset?"):
        st.session_state.employees = INITIAL_EMPLOYEES
        save_data(INITIAL_EMPLOYEES)
        st.rerun()

# --- Grid Implementation ---
days = get_days_in_month(year, month)
day_headers = [f"{d['day_of_month']} ({d['day_of_week']})" for d in days]

# Prepare Data Frame for Edit
data_list = []
for emp in st.session_state.employees:
    row = {'Employee': emp['name']}
    for d in days:
        row[f"{d['day_of_month']} ({d['day_of_week']})"] = emp['attendance'].get(d['date_str'], "")
    
    # Calculate Totals
    month_total = sum(LEAVE_TYPES.get(v, {}).get('value', 0) for k, v in emp['attendance'].items() if k.startswith(f"{year}-{month:02d}"))
    year_total = sum(LEAVE_TYPES.get(v, {}).get('value', 0) for k, v in emp['attendance'].items() if k.startswith(str(year)))
    
    row['Month Total'] = month_total
    row['Year Total'] = year_total
    data_list.append(row)

df = pd.DataFrame(data_list)

# Columns that are editable (the dates)
editable_columns = day_headers

st.markdown(f"#### Attendance for {calendar.month_name[month]} {year}")

# Data Editor
edited_df = st.data_editor(
    df,
    column_config={
        "Employee": st.column_config.TextColumn("Employee", disabled=True),
        "Month Total": st.column_config.NumberColumn("Month Total", disabled=True),
        "Year Total": st.column_config.NumberColumn("Year Total", disabled=True),
        **{col: st.column_config.SelectboxColumn(col, options=[""] + list(LEAVE_TYPES.keys())) for col in editable_columns}
    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic"
)

# Update session state and save if changed
if not edited_df.equals(df):
    new_employees = []
    # Handle existing rows
    for i, row in edited_df.iterrows():
        # Get employee ID if they exist, or create new one
        emp_id = str(i + 1)
        if i < len(st.session_state.employees):
            emp_id = st.session_state.employees[i]['id']
        
        name = row['Employee']
        attendance = {}
        # Preserve attendance from other months
        if i < len(st.session_state.employees):
            attendance = st.session_state.employees[i]['attendance'].copy()
        
        # Update current month attendance
        for d in days:
            val = row[f"{d['day_of_month']} ({d['day_of_week']})"]
            if val and val in LEAVE_TYPES:
                attendance[d['date_str']] = val
            elif not val and d['date_str'] in attendance:
                del attendance[d['date_str']]
                
        new_employees.append({'id': emp_id, 'name': name, 'attendance': attendance})
    
    st.session_state.employees = new_employees
    save_data(new_employees)
    st.rerun()

# --- Export ---
st.divider()
csv = edited_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 Download current month CSV",
    data=csv,
    file_name=f"LeaveTracker_{calendar.month_name[month]}_{year}.csv",
    mime='text/csv',
)

st.info("💡 Pro Tip: Use the legend in the sidebar to understand codes. Changes are auto-saved!")
