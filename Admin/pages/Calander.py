import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import calendar
import sqlite3
from sqlalchemy import create_engine
from io import BytesIO
import re
from config import db_path


# st.set_page_config(page_title="Calendar", layout="wide")
def main():
    # Database connection
    engine = create_engine(f'sqlite:///{db_path}')
    
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
                    col1,col2=st.columns(2)
                    with col1:
                        st.button("Edit", key=f"edit_{event['EventId']}", on_click=edit_event, args=(event['EventId'],))
                    with col2:
                        st.button("Delete", key=f"delete_{event['EventId']}", on_click=delete_event, args=(event['EventId'],))
    
        def edit_event(event_id):
            for idx, event in enumerate(st.session_state["events"]):
                if event["EventId"] == event_id:
                    st.session_state["edit_event_index"] = idx
                    st.session_state["show_event_form"] = True
                    break
                
        def delete_event(event_id):
            st.session_state["events"] = [event for event in st.session_state["events"] if event["EventId"] != event_id]
            save_events(st.session_state["events"])
            st.success("Event deleted!")
    
        left_col, right_col = st.columns([2, 4])
        with left_col:
            # Toggle buttons for categories
            st.header("Categories")
            for category in categories:
                if category not in st.session_state:
                    st.session_state[category] = True
                st.checkbox(category, key=category)
    
            if st.button("Add Event"):
                st.session_state["edit_event_index"] = None
                st.session_state["show_event_form"] = True
    
            # Event addition/editing form
            if st.session_state["show_event_form"]:
                st.write("### Add/Edit Event")
                if st.session_state["edit_event_index"] is not None:
                    event_to_edit = st.session_state["events"][st.session_state["edit_event_index"]]
                    event_name = st.text_input("Event name", event_to_edit["EventName"])
                    start_date = st.date_input("Start date", datetime.strptime(event_to_edit["StartDate"], '%Y-%m-%d'))
                    end_date = st.date_input("End date", datetime.strptime(event_to_edit["EndDate"], '%Y-%m-%d'))
                    event_category = st.selectbox("Select a category", list(categories.keys()), index=list(categories.keys()).index(event_to_edit["EventType"]))
                    description = st.text_area("Description", event_to_edit["Description"])
                else:
                    event_name = st.text_input("Event name")
                    start_date = st.date_input("Start date", datetime.now())
                    end_date = st.date_input("End date", datetime.now())
                    event_category = st.selectbox("Select a category", list(categories.keys()))
                    description = st.text_area("Description")
    
                if st.button("Submit Event"):
                    new_event = {
                        "EventId": max(events_data["EventId"]) + 1 if not events_data.empty else 1,
                        "EventName": event_name,
                        "EventType": event_category,
                        "StartDate": start_date.strftime("%Y-%m-%d"),
                        "EndDate": end_date.strftime("%Y-%m-%d"),
                        "Description": description
                    }
                    if st.session_state["edit_event_index"] is not None:
                        st.session_state["events"][st.session_state["edit_event_index"]] = new_event
                        st.session_state["edit_event_index"] = None
                    else:
                        st.session_state["events"].append(new_event)
                    save_events(st.session_state["events"])
                    st.success("Event added/updated!")
                    st.session_state["show_event_form"] = False
    
        with right_col:
            tab1, tab2 = st.tabs(["Month", "List"])
            with tab1:
                sel_date()
                render_mcalendar(st.session_state["current_year"], st.session_state["current_month"], get_events_df(), categories)
    
            with tab2:
                render_list_view(get_events_df(), categories)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    with rout:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
           # Fetch departments, courses, and teachers
        departments = pd.read_sql_query("SELECT * FROM Departments", conn)
        courses = pd.read_sql_query("SELECT * FROM Courses", conn)
        teachers = pd.read_sql_query("SELECT * FROM Teachers", conn)
    
        # Combine teacher names
        teachers['FullName'] = teachers['FirstName'].astype(str) + ' ' + teachers['MiddleName'].fillna('').astype(str) + ' ' + teachers['LastName'].astype(str)
    
    
    
        # Dropdowns for selecting Department, Course, Course Type, and Semester
        col1,col2,col3,col4=st.columns(4)
        with col1:
                selected_department = st.selectbox("Select Department", departments['Name'].unique())
                selected_department_id = departments[departments['Name'] == selected_department]['DepartmentID'].values[0]
                filtered_courses = courses[courses['DepartmentID'] == selected_department_id]
    
        with col2:
                selected_course_type = st.selectbox("Select Course Type", filtered_courses['Type'].unique())
    
        with col3:
                selected_course = st.selectbox("Select Course", filtered_courses['Name'].unique())
                selected_course_id = filtered_courses[filtered_courses['Name'] == selected_course]['CourseID'].values[0]
    
        with col4:
                selected_semester = st.selectbox("Select Semester", filtered_courses['Semester'].unique())
    
    
        # Fetch Routine Data
        routine_query = """
        SELECT * FROM Routine
        WHERE DepartmentID = ? AND CourseID = ? AND EXISTS (
            SELECT 1 FROM Courses 
            WHERE Routine.CourseID = Courses.CourseID 
            AND Courses.Type = ? 
            AND Courses.Semester = ?
        )
        """
        routine_data = pd.read_sql_query(routine_query, conn, params=(selected_department_id, selected_course_id, selected_course_type, selected_semester))
        routine_data['StartTime'] = pd.to_datetime(routine_data['StartTime'], format='%H:%M')
        routine_data['EndTime'] = pd.to_datetime(routine_data['EndTime'], format='%H:%M')
        routine_data.sort_values(by=['DayOfWeek', 'StartTime'], inplace=True)
    
        # Display Routine Data
        st.header(f"Routine for {selected_course} - {selected_course_type} - {selected_semester}")
    
        def format_time(time_obj):
            return time_obj.strftime('%H:%M')
    
        left,right=st.columns(2)
    
        # Adding new routine entry
        if left.button("Add New Routine"):
            st.session_state['show_add_form'] = True
    
        # Refresh button
        if right.button("Refresh Page"):
            st.experimental_rerun()
    
    
        # Tabs for Week, Day, and List views
        tab1, tab2, tab3 = st.tabs(["Week", "Day", "List"])
    
        with tab1:
            st.write("### Weekly View")
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
    
                
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            week_data = {day: routine_data[routine_data['DayOfWeek'] == day] for day in days_of_week}
    
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            cols = [col1, col2, col3, col4, col5, col6, col7]
    
            for col, day in zip(cols, days_of_week):
                with col:
                    st.subheader(day)
                    for index, row in week_data[day].iterrows():
                        with st.container(border=True):
                            st.markdown(f"""
                            **{format_time(row['StartTime'])} - {format_time(row['EndTime'])}**
                            - **Subject:** {row['Subject']}
                            - **Room:** {row['Classroom']}
                            - **Teacher:** {row['TeacherName']}
                            """)
                            le,ri=st.columns(2)
    
                            if le.button('Edit', key=f"edit_{row['RoutineID']}_{index}"):
                                st.session_state['edit_routine_id'] = row['RoutineID']
                            if ri.button('Delete', key=f"delete_{row['RoutineID']}_{index}"):
                                delete_query = "DELETE FROM Routine WHERE RoutineID = ?"
                                cursor.execute(delete_query, (row['RoutineID'],))
                                conn.commit()
                                st.success("Entry deleted. Please refresh the page.")
    
    
    
        with tab2:
            st.write("### Daily View")
            selected_day = st.selectbox("Select Day", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
            day_routine = routine_data[routine_data['DayOfWeek'] == selected_day]
    
            for index, row in day_routine.iterrows():
                with st.container(border=True):
                    st.markdown(f"""
                    **{format_time(row['StartTime'])} - {format_time(row['EndTime'])}**
                    - **Subject:** {row['Subject']}
                    - **Room:** {row['Classroom']}
                    - **Teacher:** {row['TeacherName']}
                    """)
                    if st.button('Edit', key=f"edit_{row['RoutineID']}_{index}_day"):
                        st.session_state['edit_routine_id'] = row['RoutineID']
                    if st.button('Delete', key=f"delete_{row['RoutineID']}_{index}_day"):
                        delete_query = "DELETE FROM Routine WHERE RoutineID = ?"
                        cursor.execute(delete_query, (row['RoutineID'],))
                        conn.commit()
                        st.success("Entry deleted. Please refresh the page.")
    
        with tab3:
            st.write("### List View")
            selected_list_day = st.selectbox("Select Day for List View", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
            list_day_routine = routine_data[routine_data['DayOfWeek'] == selected_list_day]
    
            st.dataframe(list_day_routine)
    
        # Editing form
        if 'edit_routine_id' in st.session_state:
            edit_routine_id = st.session_state['edit_routine_id']
            edit_routine = routine_data[routine_data['RoutineID'] == edit_routine_id].iloc[0]
    
            st.header(f"Editing Routine ID: {edit_routine_id}")
            with st.form(key=f"edit_form_{edit_routine_id}"):
                new_subject = st.text_input("Subject", value=edit_routine['Subject'])
                new_day = st.selectbox("Day of Week", options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], index=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].index(edit_routine['DayOfWeek']))
                new_start_time = st.time_input("Start Time", value=edit_routine['StartTime'].time())
                new_end_time = st.time_input("End Time", value=edit_routine['EndTime'].time())
                new_classroom = st.text_input("Classroom", value=edit_routine['Classroom'])
                new_teacher = st.selectbox("Teacher", teachers['FullName'], index=teachers[teachers['FullName'] == edit_routine['TeacherName']].index[0])
    
                submit_button = st.form_submit_button("Save")
                cancel_button = st.form_submit_button("Cancel")
    
                if submit_button:
                    # Check for scheduling conflicts
                    conflict_query = """
                    SELECT * FROM Routine WHERE (TeacherName = ? OR Classroom = ?) AND DayOfWeek = ? AND (
                        (StartTime BETWEEN ? AND ?) OR (EndTime BETWEEN ? AND ?)
                    ) AND RoutineID != ?
                    """
                    conflicts = pd.read_sql_query(conflict_query, conn, params=(new_teacher, new_classroom, new_day, new_start_time.strftime('%H:%M'), new_end_time.strftime('%H:%M'), new_start_time.strftime('%H:%M'), new_end_time.strftime('%H:%M'), edit_routine_id))
    
                    if conflicts.empty:
                        update_query = """
                        UPDATE Routine
                        SET Subject = ?, DayOfWeek = ?, StartTime = ?, EndTime = ?, Classroom = ?, TeacherName = ?
                        WHERE RoutineID = ?
                        """
                        cursor.execute(update_query, (new_subject, new_day, new_start_time.strftime('%H:%M'), new_end_time.strftime('%H:%M'), new_classroom, new_teacher, edit_routine_id))
                        conn.commit()
                        st.success("Entry updated. Please refresh the page.")
                        del st.session_state['edit_routine_id']
                    else:
                        st.error("Scheduling conflict: The teacher or room is already booked during this time.")
    
                if cancel_button:
                    del st.session_state['edit_routine_id']
    
    
    
        if 'show_add_form' in st.session_state and st.session_state['show_add_form']:
            st.header("Add New Routine")
            with st.form(key="add_routine_form"):
                new_subject = st.text_input("Subject")
                new_day = st.selectbox("Day of Week", options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
                new_start_time = st.time_input("Start Time",value=None)
                new_end_time = st.time_input("End Time",value=None)
                new_classroom = st.text_input("Classroom")
                new_teacher = st.selectbox("Teacher", teachers['FullName'])
    
                submit_button = st.form_submit_button("Add")
                cancel_button = st.form_submit_button("Cancel")
    
                if submit_button:
                    # Check for scheduling conflicts
                    conflict_query = """
                    SELECT * FROM Routine WHERE (TeacherName = ? OR Classroom = ?) AND DayOfWeek = ? AND (
                        (StartTime BETWEEN ? AND ?) OR (EndTime BETWEEN ? AND ?)
                    )
                    """
                    conflicts = pd.read_sql_query(conflict_query, conn, params=(new_teacher, new_classroom, new_day, new_start_time.strftime('%H:%M'), new_end_time.strftime('%H:%M'), new_start_time.strftime('%H:%M'), new_end_time.strftime('%H:%M')))
    
                    if conflicts.empty:
                        # Generate a unique RoutineID
                        # max_id = cursor.execute("SELECT MAX(RoutineID) FROM Routine").fetchone()[0]
                        # new_routine_id =selected_course_id+ str(int(max_id) + 1) if max_id else '1'
                        def extract_numeric_part(id_str):
                           match = re.search(r'\d+$', id_str)
                           return int(match.group()) if match else 0
                       
                                           # Fetch the max RoutineID
                        max_id = cursor.execute("SELECT MAX(RoutineID) FROM Routine").fetchone()[0]
                        
                        # Extract the numeric part of max_id
                        numeric_part = extract_numeric_part(max_id) if max_id else 0
                        
                        # Generate the new routine ID
                        new_routine_id = selected_course_id + str(numeric_part + 1)
    
    
    
                        insert_query = """
                        INSERT INTO Routine (RoutineID, CourseID, DepartmentID, Subject, DayOfWeek, StartTime, EndTime, Classroom, TeacherName)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(insert_query, (new_routine_id, selected_course_id, selected_department_id, new_subject, new_day, new_start_time.strftime('%H:%M'), new_end_time.strftime('%H:%M'), new_classroom, new_teacher))
                        conn.commit()
                        st.success("New routine entry added. Please refresh the page.")
                        del st.session_state['show_add_form']
                    else:
                        st.error("Scheduling conflict: The teacher or room is already booked during this time.")
    
                if cancel_button:
                    del st.session_state['show_add_form']
    
    
    
        # Close the database connection
        conn.close()
    