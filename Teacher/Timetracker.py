import streamlit as st
import sqlite3
import time
import json
import pandas as pd
from datetime import datetime
from config import db_path
from config import sp_path
from config import facerec_path
from config import save_directory1
from config import saved_faces_directory1
from config import class_state


from .Pages import Calendar, Dashboard, Notification, User,Profile
def main():

    
    page = st.sidebar.radio("", ["Time Tracker","Calendar", "Dashboard", "Notifications", "User", "Profile Settings"])
    if page == "Time Teracker":
        
        # Initialize session state for the timer and data storage
        if 'timer_running' not in st.session_state:
            st.session_state.timer_running = False
            st.session_state.start_time = None
            st.session_state.data = []  # Initialize a list to store data entries
            st.session_state.attendance_input = ""  # Initialize attendance input
        if 'teacher_present' not in st.session_state:
            st.session_state.teacher_present = False
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Define timer functions
        def start_timer():
            st.session_state.timer_running = True
            st.session_state.start_time = time.time()
            st.session_state.start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        def stop_timer():
            try:
                st.session_state.timer_running = False
                elapsed_time = time.time() - st.session_state.start_time
                stop_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                teacher_id = st.session_state.selected_teacher
                attendance_id = f"ATT{datetime.now().strftime('%Y%m%d%H%M%S')}"
                routine_id = f"{st.session_state.selected_routine_id}{datetime.now().strftime('%Y%m%d')}"
        
                data_entry = {
                    "AttendanceID": attendance_id,
                    "TeacherId": teacher_id,
                    "ClassID": routine_id,
                    "CourseID": st.session_state.selected_course_id,
                    "Date": datetime.now().strftime('%Y-%m-%d'),
                    "Out": stop_time_str,
                    "SubjectTopic": st.session_state.attendance_input,
                    "Room": st.session_state.selected_classroom,
                    "Duration": round(elapsed_time, 2),
                    "Attendance": "Present",
                    "Logs": f"Started at: {st.session_state.start_time_str}, Stopped at: {stop_time_str}",
                    "InTime": st.session_state.start_time_str
                }
        
                st.session_state.data.append(data_entry)
                st.session_state.attendance_input = ""  # Clear the input field
                save_to_database(data_entry)
            except Exception as e:
                st.error(f"Error stopping the timer: {e}")
        
        def save_to_database(data_entry):
            try:
                cursor.execute("""
                    INSERT INTO TeacherAttendance (AttendanceID, ClassID, CourseID, TeacherId, Date, Out, SubjectTopic, Room, Duration, Attendance, Logs, InTime) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data_entry["AttendanceID"], data_entry["ClassID"], data_entry["CourseID"], data_entry["TeacherId"], data_entry["Date"],
                    data_entry["Out"], data_entry["SubjectTopic"], data_entry["Room"], data_entry["Duration"],
                    data_entry["Attendance"], data_entry["Logs"], data_entry["InTime"]
                ))
                conn.commit()
            except Exception as e:
                st.error(f"Error saving to database: {e}")
        
        def get_teacher_routine(teacher_name):
            try:
                query = """
                    SELECT Routine.StartTime, Routine.EndTime, Routine.Subject, Routine.Classroom, Routine.TeacherName
                    FROM Routine
                    WHERE Routine.TeacherName = ? AND Routine.DayOfWeek = ?
                """
                day_of_week = datetime.now().strftime('%A')
                cursor.execute(query, (teacher_name, day_of_week))
                return cursor.fetchall()
            except Exception as e:
                st.error(f"Error fetching teacher routine: {e}")
                return []
        
        def get_teachers():
            try:
                cursor.execute("SELECT TeacherID, FirstName, LastName FROM Teachers")
                return cursor.fetchall()
            except Exception as e:
                st.error(f"Error fetching teachers: {e}")
                return []
        
        def get_today_data(teacher_id):
            try:
                today_date = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("SELECT * FROM TeacherAttendance WHERE TeacherId = ? AND Date = ?", (teacher_id, today_date))
                return cursor.fetchall()
            except Exception as e:
                st.error(f"Error fetching today's data: {e}")
                return []
        
        # Load class state
        def load_state():
            try:
                with open(class_state, 'r') as f:
                    state = json.load(f)
                    st.session_state.class_started = state['class_started']
                    st.session_state.timer_start = state['timer_start']
            except FileNotFoundError:
                st.session_state.class_started = False
                st.session_state.timer_start = 0
        
        def mark_present_teacher():
            st.session_state.teacher_present = not st.session_state.teacher_present
        
        load_state()
        
        teachers = get_teachers()
        
        # Select Teacher
        teacher_ids = [teacher[0] for teacher in teachers]
        teacher_names = [f"{teacher[1]} {teacher[2]}" for teacher in teachers]
        # selected_teacher_index = st.selectbox("Select Teacher", range(len(teacher_ids)), format_func=lambda x: teacher_names[x])
        st.session_state.selected_teacher = st.session_state.user_id
        selected_teacher_name = st.session_state.user_id
        
        # Time tracker section
        st.write("### Time Tracker")
        left, right = st.columns([3, 1])
        with left:
            with st.form(key='attendance_form'):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.session_state.attendance_input = st.text_input("What did you teach?", "")
                with col2:
                    add_button = st.form_submit_button(label=':heavy_plus_sign: Add')
                with col3:
                    snap_button = st.form_submit_button(label=':camera: Snap')
        
        with right:
            col1, col2 = st.columns(2)
            with col1:
                timer_placeholder = st.empty()
        
            with col2:
                if st.session_state.timer_running:
                    stop_button = st.button("STOP")
                    while st.session_state.timer_running:
                        elapsed_time = time.time() - st.session_state.start_time
                        minutes, seconds = divmod(elapsed_time, 60)
                        timer_placeholder.markdown(f"Duration: {int(minutes):02d}:{int(seconds):02d} minutes")
                        time.sleep(0.1)
                        if stop_button and st.session_state.attendance_input != "":
                            stop_timer()
                            st.experimental_rerun()
                else:
                    start_button = st.button(
                        "START",
                        disabled=not (st.session_state.class_started and st.session_state.teacher_present)
                    )
                    if start_button:
                        if st.session_state.attendance_input != "":
                            start_timer()
                            st.experimental_rerun()
        
        # Teacher Section
        
        # Display routine for today
        routine_teacher = get_teacher_routine(selected_teacher_name)
        if routine_teacher:
            st.write("### Routine for Today (Teacher)")
            routine_teacher_df = pd.DataFrame(routine_teacher, columns=["StartTime", "EndTime", "Subject", "Classroom", "TeacherName"])
            st.table(routine_teacher_df)
        else:
            st.write("No classes today ")
        
        # # Display the data table for today
        # today_data = get_today_data(st.session_state.selected_teacher)
        # if today_data:
        #     st.write("### Today's Attendance Data")
        #     df = pd.DataFrame(today_data, columns=["AttendanceID", "ClassID", "CourseID", "TeacherId", "Date", "Out", "SubjectTopic", "Room", "Duration", "Attendance", "Logs", "InTime"])
        #     st.table(df)
        # else:
        #     st.write("No data for today")
        
        # Close the database connection
        conn.close()
    





    if page == "Calendar":
        Calendar.main()
    elif page == "Dashboard":
        Dashboard.main()
    elif page == "Notifications":
        Notification.main()
    elif page == "User":
        User.main()
    elif page == "Profile Settings":
        Profile.main()

