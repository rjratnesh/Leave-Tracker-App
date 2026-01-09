import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import calendar
import plotly.express as px

# --- Constants & Configuration ---
LEAVE_TYPES = {
    'SL': {'label': 'Sick Leave', 'color': '🩺', 'value': 1},
    'PL': {'label': 'Plan Leave', 'color': '📅', 'value': 1},
    'CL': {'label': 'Casual Leave', 'color': '🌱', 'value': 1},
    'H1': {'label': 'Half Day Leave 1', 'color': '🌓', 'value': 0.5},
    'H2': {'label': 'Half Day Leave 2', 'color': '🌗', 'value': 0.5},
    'EL': {'label': 'Emergency Leave', 'color': '🆘', 'value': 1},
    'HO': {'label': 'Holiday', 'color': '🏖️', 'value': 0},
}

PAID_HOLIDAYS_2026 = {
    '2026-01-01': 'New Year',
    '2026-01-26': 'Republic Day',
    '2026-03-04': 'Holi',
    '2026-03-19': 'Gudi Padawa',
    '2026-05-01': 'Maharashtra Day/Labour Day',
    '2026-09-14': 'Ganesh Chaturthi',
    '2026-10-02': 'Gandhi Jayanti',
    '2026-10-20': 'Dussehra',
    '2026-11-09': 'Diwali Holiday',
    '2026-12-25': 'Christmas',
}

SEASONAL_ICONS = {
    1: "❄️",  # January - Winter
    2: "🌸",  # February - Spring
    3: "🎨",  # March - Holi/Colors
    4: "☀️",  # April - Summer
    5: "🍦",  # May - Peak Summer
    6: "🌧️",  # June - Monsoon
    7: "☔",  # July - Heavy Rain
    8: "☁️",  # August - Cloudy
    9: "🔱",  # September - Festivals
    10: "🪔", # October - Diwali
    11: "🌾", # November - Harvest
    12: "🎄", # December - Christmas
}

INITIAL_EMPLOYEES = [
    {'id': '1', 'name': 'Rahul', 'attendance': {k: 'HO' for k in PAID_HOLIDAYS_2026}},
    {'id': '2', 'name': 'Maksud', 'attendance': {k: 'HO' for k in PAID_HOLIDAYS_2026}},
    {'id': '3', 'name': 'Ratnesh', 'attendance': {k: 'HO' for k in PAID_HOLIDAYS_2026}},
    {'id': '4', 'name': 'Abhishek', 'attendance': {k: 'HO' for k in PAID_HOLIDAYS_2026}},
    {'id': '5', 'name': 'Aishwarya', 'attendance': {k: 'HO' for k in PAID_HOLIDAYS_2026}},
    {'id': '6', 'name': 'Prashant', 'attendance': {k: 'HO' for k in PAID_HOLIDAYS_2026}},
]

DATA_FILE = 'leave_data.json'

# --- Helper Functions ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Migration & Holiday Enforcement
            for emp in data:
                # 1. Migrate S -> SL
                for d_str, code in list(emp.get('attendance', {}).items()):
                    if code == 'S':
                        emp['attendance'][d_str] = 'SL'
                
                # 2. Enforce Paid Holidays from PAID_HOLIDAYS_2026
                for h_date in PAID_HOLIDAYS_2026:
                    emp['attendance'][h_date] = 'HO'
            return data
    return INITIAL_EMPLOYEES

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def to_bold(text):
    if text is None or str(text).strip() == "":
        return ""
    # Convert regular text to Unicode Bold for visual emphasis in grid
    bold_chars = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    normal_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold_map = str.maketrans(normal_chars, bold_chars)
    return str(text).translate(bold_map)

def get_days_in_month(year, month):
    num_days = calendar.monthrange(year, month)[1]
    days = []
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        # Filter out Saturday (5) and Sunday (6)
        if d.weekday() < 5:
            days.append({
                'date': d,
                'day_of_month': day,
                'day_of_week': d.strftime('%a'),
                'is_weekend': False,
                'date_str': d.strftime('%Y-%m-%d')
            })
    return days

# --- Main App ---
st.set_page_config(
    page_title="LeaveTracker Pro",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit Menu and Footer + Hover Sidebar Logic
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppDeployButton {display:none;}
            
            /* Glassmorphism Sidebar */
            [data-testid="stSidebar"] {
                transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
                transform: translateX(-100%) !important;
                position: fixed !important;
                z-index: 10000 !important;
                width: 320px !important;
                height: 100vh !important;
                background: rgba(38, 39, 48, 0.85) !important;
                backdrop-filter: blur(15px) !important;
                -webkit-backdrop-filter: blur(15px) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
                box-shadow: 10px 0 30px rgba(0,0,0,0.3) !important;
            }
            
            /* App Background Gradient */
            .stApp {
                background: radial-gradient(circle at top right, #1e1e2f 0%, #0d0d12 100%) !important;
            }
            
            /* Ensure sidebar content visibility */
            [data-testid="stSidebar"] .stMarkdown, 
            [data-testid="stSidebar"] h1, 
            [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3, 
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] span {
                color: #f0f2f6 !important;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            [data-testid="stSidebar"]:hover,
            [data-testid="stSidebar"]:focus-within {
                transform: translateX(0) !important;
            }
            
            /* Premium MENU Trigger */
            [data-testid="stSidebar"]::after {
                content: "MENU";
                writing-mode: vertical-rl;
                text-orientation: mixed;
                position: absolute;
                top: 50%;
                right: -30px;
                transform: translateY(-50%);
                width: 30px;
                height: 120px;
                background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
                color: #0d0d12;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 3px;
                border-radius: 0 12px 12px 0;
                cursor: pointer;
                box-shadow: 4px 0 15px rgba(0,242,254,0.3);
                pointer-events: auto !important;
                visibility: visible !important;
                transition: all 0.3s ease;
            }
            
            [data-testid="stSidebar"]:hover::after {
                opacity: 0;
            }

            /* Responsive Adjustments */
            @media (max-width: 768px) {
                [data-testid="stSidebar"] {
                    width: 280px !important;
                }
                [data-testid="stSidebar"]::after {
                    right: -25px;
                    width: 25px;
                    height: 100px;
                    font-size: 10px;
                }
                .main .block-container {
                    padding: 1rem !important;
                    padding-top: 4rem !important;
                }
                .stTitle h1 {
                    font-size: 1.8rem !important;
                }
            }

            /* Table Header Bold Styling */
            [data-testid="stColumnHeader"] span {
                font-weight: 800 !important;
                color: #FFFFFF !important;
            }
            
            /* General aesthetics for the main container */
            .main .block-container {
                padding-top: 2rem !important;
            }

            /* Hide Glide Data Grid Icons (Sort/Menu) */
            [data-testid="stDataFrame"] {
                --gdg-fg-icon-header: transparent !important;
                --gdg-bg-icon-header: transparent !important;
            }
            
            /* Hide the popup menu if it somehow triggers */
            [data-testid="stDataFrameColumnMenu"] {
                display: none !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Floating Employee Logo
st.markdown("""
    <div class="floating-logo">
        <span style="font-size: 24px;">👥</span>
    </div>
    <style>
    .floating-logo {
        position: fixed;
        top: 25px;
        right: 30px;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 50%;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(0, 242, 254, 0.3);
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
        transition: all 0.3s ease;
    }
    @media (max-width: 768px) {
        .floating-logo {
            top: 15px;
            right: 15px;
            width: 40px;
            height: 40px;
        }
        .floating-logo span {
            font-size: 18px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗓️ LeaveTracker Pro")
st.markdown("### Employee Attendance & Leave Management")

# Sidebar for Page Navigation
st.sidebar.markdown("""
    <div style='text-align: center; padding-bottom: 20px;'>
        <h1 style='color: #00f2fe; margin-bottom: 0;'>🗓️</h1>
        <h3 style='color: #f0f2f6; margin-top: 5px; font-weight: 300; letter-spacing: 1px;'>LEAVE TRACKER PRO</h3>
    </div>
    <hr style='border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 0 0 20px 0;'>
""", unsafe_allow_html=True)

st.sidebar.header("📁 Menu")
page = st.sidebar.selectbox("Go to", ["Attendance Tracker", "Yearly Analytics"])

# Initialize Session State
if 'employees' not in st.session_state:
    st.session_state.employees = load_data()

if 'current_date' not in st.session_state:
    st.session_state.current_date = date(2026, 1, 1)

if page == "Attendance Tracker":
    # Sidebar for Navigation & Tools
    st.sidebar.divider()
    st.sidebar.header("Navigation")
    
    # Month Dropdown
    month_names = list(calendar.month_name)[1:]  # ["January", "February", ...]
    selected_month_name = st.sidebar.selectbox(
        "Select Month", 
        month_names, 
        index=st.session_state.current_date.month - 1
    )
    selected_month = month_names.index(selected_month_name) + 1
    
    # Year Dropdown
    years = list(range(2024, 2031))
    selected_year = st.sidebar.selectbox(
        "Select Year", 
        years, 
        index=years.index(st.session_state.current_date.year)
    )
    
    # Update session state if changed
    if (selected_month != st.session_state.current_date.month or 
        selected_year != st.session_state.current_date.year):
        st.session_state.current_date = date(selected_year, selected_month, 1)
        st.rerun()
    
    year = st.session_state.current_date.year
    month = st.session_state.current_date.month
    
    st.sidebar.divider()
    st.sidebar.divider()
    st.sidebar.header("Leave Legend")
    for code, config in LEAVE_TYPES.items():
        st.sidebar.markdown(f"{config['color']} **{code}**: {config['label']} ({config['value']} day)")

    st.sidebar.divider()
    st.sidebar.header("Add New Employee")
    new_emp_name = st.sidebar.text_input("Employee Name", placeholder="Enter name...")
    if st.sidebar.button("➕ Add Employee", use_container_width=True):
        if new_emp_name:
            # Generate new ID
            new_id = "1"
            if st.session_state.employees:
                new_id = str(max(int(emp['id']) for emp in st.session_state.employees) + 1)
            
            # Create new employee object with holidays pre-filled
            new_emp = {
                'id': new_id,
                'name': new_emp_name,
                'attendance': {k: 'HO' for k in PAID_HOLIDAYS_2026}
            }
            
            # Update state and save
            st.session_state.employees.append(new_emp)
            save_data(st.session_state.employees)
            st.sidebar.success(f"Added {new_emp_name}!")
            st.rerun()
        else:
            st.sidebar.error("Please enter a name")

    st.sidebar.divider()
    st.sidebar.header("Remove Employee")
    remove_options = [emp['name'] for emp in st.session_state.employees]
    emp_to_remove = st.sidebar.selectbox("Select Employee to Remove", [""] + remove_options)
    if st.sidebar.button("🗑️ Remove Employee", type="primary", use_container_width=True):
        if emp_to_remove:
            # Filter out the selected employee
            st.session_state.employees = [emp for emp in st.session_state.employees if emp['name'] != emp_to_remove]
            save_data(st.session_state.employees)
            st.sidebar.success(f"Removed {emp_to_remove}!")
            st.rerun()
        else:
            st.sidebar.error("Please select an employee")

    st.sidebar.divider()
    st.sidebar.header("Reset Attendance")
    
    # Reset Selection
    reset_options = ["All Employees"] + [emp['name'] for emp in st.session_state.employees]
    reset_target = st.sidebar.selectbox("Reset target", reset_options)
    
    # Reset Button with confirmation logic that works in Streamlit
    if st.sidebar.button("🗑️ Clear Attendance", type="secondary", use_container_width=True):
        if reset_target == "All Employees":
            st.session_state.employees = INITIAL_EMPLOYEES
            save_data(INITIAL_EMPLOYEES)
            st.sidebar.success("All data cleared!")
        else:
            new_employees = []
            for emp in st.session_state.employees:
                if emp['name'] == reset_target:
                    new_employees.append({'id': emp['id'], 'name': emp['name'], 'attendance': {}})
                else:
                    new_employees.append(emp)
            st.session_state.employees = new_employees
            save_data(new_employees)
            st.sidebar.success(f"Cleared {reset_target}'s attendance!")
        st.rerun()

else:  # Yearly Analytics Page
    st.header("📊 Yearly Leave Analytics")
    
    selected_year = st.sidebar.selectbox("Select Year for Analysis", list(range(2024, 2031)), index=2)
    
    # Prepare data for chart
    analytics_data = []
    month_names = list(calendar.month_name)[1:]
    
    for emp in st.session_state.employees:
        monthly_counts = {m: 0.0 for m in month_names}
        for date_str, code in emp['attendance'].items():
            if date_str.startswith(str(selected_year)):
                m_idx = int(date_str.split('-')[1])
                monthly_counts[month_names[m_idx-1]] += LEAVE_TYPES.get(code, {}).get('value', 0)
        
        for month_name, count in monthly_counts.items():
            analytics_data.append({
                'Employee': emp['name'],
                'Month': month_name,
                'Leaves': count
            })
    
    if analytics_data:
        df_ana = pd.DataFrame(analytics_data)
        
        # Ensure Month is treated as a categorical so charts stay in order
        df_ana['Month'] = pd.Categorical(df_ana['Month'], categories=month_names, ordered=True)
        
        st.subheader(f"Leave Trends for {selected_year}")
        
        # Total Yearly Leaves (Bar Chart)
        total_leaves = df_ana.groupby('Employee')['Leaves'].sum().reset_index()
        st.markdown("#### Total Yearly Leaves")
        st.bar_chart(total_leaves.set_index('Employee'))
        
        st.divider()
        
        # Monthly Pie Chart Section
        st.markdown("#### Monthly Breakdown per Employee (Pie Chart)")
        
        col1, col2 = st.columns(2)
        with col1:
            sel_emp = st.selectbox("Select Employee", [emp['name'] for emp in st.session_state.employees])
        with col2:
            sel_month = st.selectbox("Select Month", month_names, index=st.session_state.current_date.month - 1)
        
        # Get data for the specific employee and month
        pie_data = []
        for emp in st.session_state.employees:
            if emp['name'] == sel_emp:
                m_idx = month_names.index(sel_month) + 1
                month_str = f"{selected_year}-{m_idx:02d}"
                
                # Count occurances of each leave type in that month
                counts = {}
                for date_str, code in emp['attendance'].items():
                    if date_str.startswith(month_str):
                        label = LEAVE_TYPES.get(code, {}).get('label', code)
                        counts[label] = counts.get(label, 0) + LEAVE_TYPES.get(code, {}).get('value', 0)
                
                for label, count in counts.items():
                    pie_data.append({'Leave Type': label, 'Days': count})
        
        if pie_data:
            df_pie = pd.DataFrame(pie_data)
            fig = px.pie(df_pie, values='Days', names='Leave Type', 
                         title=f"Leave Distribution for {sel_emp} in {sel_month} {selected_year}",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No leaves recorded for {sel_emp} in {sel_month} {selected_year}.")

    else:
        st.warning(f"No attendance data found for the year {selected_year}.")
    
    # Return to tracker logic if needed
    st.sidebar.divider()
    st.sidebar.info("Tip: Switch back to 'Attendance Tracker' to mark more leaves.")

# --- Grid Implementation (only if Attendance Tracker) ---
if page == "Attendance Tracker":
    days = get_days_in_month(year, month)
    day_headers = [f"{d['day_of_month']} ({d['day_of_week']})" for d in days]
    
    # Mapping for Display (Color + Short Form)
    DISPLAY_TO_CODE = {f"{v['color']} {k}": k for k, v in LEAVE_TYPES.items()}
    CODE_TO_DISPLAY = {k: f"{v['color']} {k}" for k, v in LEAVE_TYPES.items()}
    
    # Prepare Data Frame for Edit
    data_list = []
    for emp in st.session_state.employees:
        # Use Unicode Bold for Name
        row = {'Employee': to_bold(emp['name'])}
        for d in days:
            code = emp['attendance'].get(d['date_str'], "")
            # Ensure we return empty string for missing codes
            display_val = CODE_TO_DISPLAY.get(code, "")
            row[f"{d['day_of_month']} ({d['day_of_week']})"] = display_val if display_val else ""
        
        # Calculate Totals
        month_total = sum(LEAVE_TYPES.get(v, {}).get('value', 0) for k, v in emp['attendance'].items() if k.startswith(f"{year}-{month:02d}"))
        year_total = sum(LEAVE_TYPES.get(v, {}).get('value', 0) for k, v in emp['attendance'].items() if k.startswith(str(year)))
        
        row['Month Total'] = month_total
        row['Year Total'] = year_total
        data_list.append(row)
    
    df = pd.DataFrame(data_list)
    df = df.fillna("")  # Replace any NaN/None with empty string
    
    # Columns that are editable (the dates)
    editable_columns = day_headers
    
    # Attractive Seasonal Header
    month_icon = SEASONAL_ICONS.get(month, "📅")
    st.markdown(f"""
        <div class="seasonal-header">
            <h3 class="seasonal-title">
                <span style="font-size: 28px;">{month_icon}</span>
                <span>{calendar.month_name[month]} <span class="seasonal-year">{year}</span></span>
            </h3>
            <p class="seasonal-subtitle">Attendance Tracker</p>
        </div>
        <style>
        .seasonal-header {{
            background: rgba(255,255,255,0.05); 
            padding: 12px 20px; 
            border-radius: 12px; 
            border-left: 4px solid #00f2fe; 
            margin-bottom: 15px;
        }}
        .seasonal-title {{
            margin:0; 
            color: #00f2fe; 
            display: flex; 
            align-items: center; 
            gap: 12px;
        }}
        .seasonal-year {{
            font-weight: 300; 
            opacity: 0.7; 
            font-size: 18px;
        }}
        .seasonal-subtitle {{
            margin:2px 0 0 42px; 
            opacity: 0.7; 
            font-size: 12px;
        }}
        @media (max-width: 768px) {{
            .seasonal-header {{
                padding: 10px 15px;
            }}
            .seasonal-title {{
                font-size: 1.2rem !important;
            }}
            .seasonal-year {{
                font-size: 14px;
            }}
            .seasonal-subtitle {{
                margin-left: 38px;
            }}
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Data Editor
    edited_df = st.data_editor(
        df,
        column_config={
            "Employee": st.column_config.TextColumn(to_bold("Employee"), disabled=True, pinned=True),
            "Month Total": st.column_config.NumberColumn(to_bold("Month Total"), disabled=True),
            "Year Total": st.column_config.NumberColumn(to_bold("Year Total"), disabled=True),
            **{col: st.column_config.SelectboxColumn(to_bold(col), options=[""] + list(CODE_TO_DISPLAY.values())) for col in editable_columns}
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
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
                display_val = row[f"{d['day_of_month']} ({d['day_of_week']})"]
                code_val = DISPLAY_TO_CODE.get(display_val, "")
                
                if code_val:
                    attendance[d['date_str']] = code_val
                elif not display_val and d['date_str'] in attendance:
                    del attendance[d['date_str']]
                    
            new_employees.append({'id': emp_id, 'name': name, 'attendance': attendance})
        
        st.session_state.employees = new_employees
        save_data(new_employees)
        # We don't rerun here to keep the UI smooth for the next click
        # The editor will update visually on its own
    
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
