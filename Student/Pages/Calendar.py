import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import calendar
import sqlite3
from sqlalchemy import create_engine
from io import BytesIO
from config import db_path

# Database connection
# db_path = ("F:/MCA PROJECT/Final/Data/university.db")
engine = create_engine(f'sqlite:///{db_path}')

def main():
    def load_data():
        query = "SELECT EventId, EventName, EventType, StartDate, EndDate, Description FROM EventCalendar"
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    
    events_data = load_data()
    
    cal, rout = st.tabs(["Calendar", "Routine"])
    
    with cal:
        # Define categories and their colors
        categories = {
            "University": "blue",
            "Personal": "green",
            "Important": "purple",
            "Holiday": "red",
            "Friends": "orange"
        }
    
        # Load events from the database
        def load_events():
            return events_data.to_dict(orient="records")
    
        # Save events to the database
        def save_events(events):
            df = pd.DataFrame(events)
            with engine.connect() as conn:
                df.to_sql('EventCalendar', conn, if_exists='replace', index=False)
    
        # Initial event list
        if "events" not in st.session_state:
            st.session_state["events"] = load_events()
    
        # To control the visibility of the event addition form
        if "show_event_form" not in st.session_state:
            st.session_state["show_event_form"] = False
    
        # To control the visibility of the event editing form
        if "edit_event_index" not in st.session_state:
            st.session_state["edit_event_index"] = None
    
        # To track the current month and year
        if "current_year" not in st.session_state:
            st.session_state["current_year"] = datetime.now().year
    
        if "current_month" not in st.session_state:
            st.session_state["current_month"] = datetime.now().month
    
        if "current_date" not in st.session_state:
            st.session_state["current_date"] = datetime.now()
    
        # Create a DataFrame for events
        def get_events_df():
            return pd.DataFrame(st.session_state["events"])
    
        # Function to render the calendar
        def render_mcalendar(year, month, events_df, categories):
            cal = calendar.Calendar()
            days = list(cal.itermonthdays(year, month))
    
            st.write(f"### {calendar.month_name[month]} {year}")
    
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            cols = [col1, col2, col3, col4, col5, col6, col7]
    
            days_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for col, day_abbr in zip(cols, days_abbr):
                col.write(f"**{day_abbr}**")
    
            for i, day in enumerate(days):
                if day == 0:
                    cols[i % 7].write(" ")
                else:
                    date_str = f"{year}-{month:02}-{day:02}"
                    events_today = events_df[(events_df["StartDate"] <= date_str) & (events_df["EndDate"] >= date_str)]
                    day_display = f"**{day}**"
                    for _, event in events_today.iterrows():
                        if st.session_state[event['EventType']]:
                            day_display += f"<br><span style='color: {categories[event['EventType']]}'>{event['EventName']}</span>"
                    cols[i % 7].markdown(day_display, unsafe_allow_html=True)
    
        def sel_date():
            # Navigation buttons for months with date selection
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            with col1:
                if st.button("◀️"):
                    if st.session_state["current_month"] == 1:
                        st.session_state["current_month"] = 12
                        st.session_state["current_year"] -= 1
                    else:
                        st.session_state["current_month"] -= 1
    
            with col3:
                selected_date = st.date_input("Select a date", datetime(st.session_state["current_year"], st.session_state["current_month"], 1))
                st.session_state["current_year"] = selected_date.year
                st.session_state["current_month"] = selected_date.month
    
            with col5:
                if st.button("▶️"):
                    if st.session_state["current_month"] == 12:
                        st.session_state["current_month"] = 1
                        st.session_state["current_year"] += 1
                    else:
                        st.session_state["current_month"] += 1
    
        def render_list_view(events_df, categories):
            st.write("### List of Events")
            # Sort events by StartDate
            events_df = events_df.sort_values(by="StartDate")
            for _, event in events_df.iterrows():
                if st.session_state[event['EventType']]:
                    st.write(f"{event['StartDate']} to {event['EndDate']} - <span style='color: {categories[event['EventType']]}'>{event['EventName']}- {event['Description']}</span> ", unsafe_allow_html=True)
                    
        left_col, right_col = st.columns([2, 4])
        with left_col:
            # Toggle buttons for categories
            st.header("Categories")
            for category in categories:
                if category not in st.session_state:
                    st.session_state[category] = True
                st.checkbox(category, key=category)
    
           
        with right_col:
            tab1, tab2 = st.tabs(["Month", "List"])
            with tab1:
                sel_date()
                render_mcalendar(st.session_state["current_year"], st.session_state["current_month"], get_events_df(), categories)
    
            with tab2:
                render_list_view(get_events_df(), categories)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    with rout:
            # Connect to the database
        conn = sqlite3.connect(db_path)
        
        def fetch_data(table_name):
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, conn)
            return df
        
        def fetch_students():
            return fetch_data('students')
        
        def fetch_routine():
            return fetch_data('Routine')
        
        # Fetch data
        students = fetch_students()
        routine = fetch_routine()
        
        # Combine student names
        students['FullName'] = students['FirstName'].astype(str) + ' ' + students['MiddleName'].fillna('').astype(str) + ' ' + students['LastName'].astype(str)
       
        # Create the selectbox with the default value
        selected_student_id = st.session_state.user_id
        
        # Filter routine data based on selected StudentID
        selected_student_name = students[students['StudentID'] == selected_student_id]['FullName'].values[0]
        selected_course_id = students[students['StudentID'] == selected_student_id]['CourseId'].values[0]
        routine_data = routine[routine['CourseID'] == selected_course_id]
        routine_data['StartTime'] = pd.to_datetime(routine_data['StartTime'], format='%H:%M')
        routine_data['EndTime'] = pd.to_datetime(routine_data['EndTime'], format='%H:%M')
        routine_data.sort_values(by=['DayOfWeek', 'StartTime'], inplace=True)
        
        # Display Routine Data
        st.header(f"Routine for {selected_student_name}")
        
        def format_time(time_obj):
            return time_obj.strftime('%H:%M')
        
        # Tabs for Week, Day, and List views
        tab1, tab2, tab3 = st.tabs(["Week", "Day", "List"])
        
        with tab1:
            st.write("### Weekly View")
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            week_data = {day: routine_data[routine_data['DayOfWeek'] == day] for day in days_of_week}
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            cols = [col1, col2, col3, col4, col5]
            for col, day in zip(cols, days_of_week):
                with col:
                    st.subheader(day)
                    if week_data[day].empty:
                        st.write("No scheduled classes")
                    else:
                        for index, row in week_data[day].iterrows():
                            with st.container(border=True):
                                st.markdown(f"""
                                **{format_time(row['StartTime'])} - {format_time(row['EndTime'])}**
                                - **Subject:** {row['Subject']}
                                - **Room:** {row['Classroom']}
                                - **Teacher:** {row['TeacherName']}
                               
                                """)
                           
        
            # Export to Excel
            if st.button("Export to Excel"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    routine_data.to_excel(writer, index=False, sheet_name='Routine')
                    writer.close()
                output.seek(0)
                st.download_button(
                    label="Download Excel file",
                    data=output,
                    file_name='routine.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        
        with tab2:
            st.write("### Daily View")
            selected_day = st.selectbox("Select Day", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
            day_routine = routine_data[routine_data['DayOfWeek'] == selected_day]
            if day_routine.empty:
                st.write("No scheduled classes")
            else:
                for index, row in day_routine.iterrows():
                    with st.container(border=True):
                        st.markdown(f"""
                        **{format_time(row['StartTime'])} - {format_time(row['EndTime'])}**
                        - **Subject:** {row['Subject']}
                        - **Room:** {row['Classroom']}
                        - **Teacher:** {row['TeacherName']}
                        """)
        
        with tab3:
            st.write("### List View")
            selected_list_day = st.selectbox("Select Day for List View", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
            list_day_routine = routine_data[routine_data['DayOfWeek'] == selected_list_day]
            if list_day_routine.empty:
                st.write("No scheduled classes")
            else:
                st.dataframe(list_day_routine)
        
        # Close the database connection
        conn.close()

