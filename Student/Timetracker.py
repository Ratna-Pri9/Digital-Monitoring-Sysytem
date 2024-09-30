import cv2
from PIL import Image
import numpy as np
import dlib
import os
import streamlit as st
import sqlite3
import time
import json
import pandas as pd
from datetime import datetime
from streamlit.components.v1 import html
from config import db_path
from config import sp_path
from config import facerec_path
from config import save_directory1
from config import saved_faces_directory1
from config import class_state
from .Pages import Calendar, Dashboard, Notifications, User, Profile

def main():
    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation", 
        ["Time Tracker", "Calendar", "Dashboard", "Notifications", "User", "Profile Settings"]
    )
    
    # Handle navigation based on the selected page
    if page == "Time Tracker":
        # Check if database exists
        if not os.path.exists(db_path):
            st.error("Database not found. Terminating the program.")
            st.stop()
        
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
                elapsed_time = (time.time() - st.session_state.start_time) / 60  # Convert to minutes
                stop_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                student_id = st.session_state.selected_student
                attendance_id = f"STUD{datetime.now().strftime('%Y%m%d')}"
                routine_id = f"{st.session_state.selected_routine_id}{datetime.now().strftime('%Y%m%d')}"
        
                data_entry = {
                    "StudentId": student_id,
                    "ClassID": routine_id,
                    "CourseID": st.session_state.selected_course_id,
                    "Date": datetime.now().strftime('%Y-%m-%d'),
                    "Out": stop_time_str,
                    "SubjectTopic": st.session_state.attendance_input,
                    "Room": st.session_state.selected_classroom,
                    "Duration": round(elapsed_time, 2),
                    "Attendance": "Present",
                    "Logs": f"Started at: {st.session_state.start_time_str}, Stopped at: {stop_time_str}",
                    "InTime": st.session_state.start_time_str,
                    "CapturedImagePath": st.session_state.captured_image_path
                }
        
                st.session_state.data.append(data_entry)
                st.session_state.attendance_input = ""  # Clear the input field
                save_to_database(data_entry)
            except Exception as e:
                st.error(f"Error stopping the timer: {e}")
        
        def save_to_database(data_entry):
            try:
                cursor.execute("""
                    INSERT INTO StudentAttendance (ClassID, CourseID, StudentId, Date, Out, SubjectTopic, Room, Duration, Attendance, Logs, InTime) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data_entry["ClassID"], data_entry["CourseID"], data_entry["StudentId"], data_entry["Date"],
                    data_entry["Out"], data_entry["SubjectTopic"], data_entry["Room"], data_entry["Duration"],
                    data_entry["Attendance"], data_entry["Logs"], data_entry["InTime"]
                ))
                conn.commit()
            except Exception as e:
                st.error(f"Error saving to database: {e}")
        
        def get_student_routine(student_id):
            try:
                query = """
                    SELECT Routine.StartTime, Routine.EndTime, Routine.Subject, Routine.Classroom, Routine.TeacherName
                    FROM Routine
                    JOIN Courses ON Routine.CourseID = Courses.CourseID
                    JOIN Students ON Courses.CourseID = Students.CourseId
                    WHERE Students.StudentID = ? AND Routine.DayOfWeek = ?
                """
                day_of_week = datetime.now().strftime('%A')
                cursor.execute(query, (student_id, day_of_week))
                return cursor.fetchall()
            except Exception as e:
                st.error(f"Error fetching student routine: {e}")
                return []
        
        def get_students():
            try:
                cursor.execute("SELECT StudentID, FirstName, LastName FROM Students")
                return cursor.fetchall()
            except Exception as e:
                st.error(f"Error fetching students: {e}")
                return []
        
        def get_today_data(student_id):
            try:
                today_date = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("SELECT * FROM StudentAttendance WHERE StudentId = ? AND Date = ?", (student_id, today_date))
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
        
        def mark_present():
            st.session_state.student_present = not st.session_state.student_present
        
        def capture_image():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("Error: No input device found. Please check your webcam.")
                return None
        
            ret, frame = cap.read()
            if not ret:
                st.error("Error: Could not read frame.")
                return None
        
            cap.release()
            return frame
        
        def save_image(image, student_id):
            # Directory to save images
            save_directory = save_directory1
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
                
            # Construct image path
            img_path = f"{save_directory}/{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(img_path, image)
            return img_path
        
        load_state()
        
        students = get_students()
        
        # Select Student
        student_ids = [student[0] for student in students]
        student_names = [f"{student[1]} {student[2]}" for student in students]
        
        
    
    
        
        selected_student=st.session_state.user_id
        st.session_state.selected_student = selected_student
        
        # Initialize session state for the timer and data storage
        if 'timer_running' not in st.session_state:
            st.session_state.timer_running = False
            st.session_state.start_time = None
            st.session_state.data = []  # Initialize a list to store data entries
            st.session_state.attendance_input = ""  # Initialize attendance input
        
        # Define timer functions
        def start_timer():
            st.session_state.timer_running = True
            st.session_state.start_time = time.time()
            st.session_state.start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        def stop_timer():
            st.session_state.timer_running = False
            elapsed_time = (time.time() - st.session_state.start_time) / 60  # Convert to minutes
            stop_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.session_state.data.append({
                "What do you learn?": st.session_state.attendance_input,
                "Start time": st.session_state.start_time_str,
                "Stop time": stop_time_str,
                "Duration( in minutes)": round(elapsed_time, 2),
                "CapturedImagePath": st.session_state.captured_image_path
            })
            st.session_state.attendance_input = ""  # Clear the input field
            save_to_excel(st.session_state.data)
        
        def save_to_excel(data):
            df = pd.DataFrame(data)
            df.to_excel("attendance_data.xlsx", index=False)
        


        # Load pre-trained face detection and face recognition models
        detector = dlib.get_frontal_face_detector()
        sp = dlib.shape_predictor(sp_path)
        facerec = dlib.face_recognition_model_v1(facerec_path)
        
        # Function to load and prepare face data from a directory
        def load_face_data(directory):
            known_face_encodings = []
            known_face_names = []
            for filename in os.listdir(directory):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    img_path = os.path.join(directory, filename)
                    img = dlib.load_rgb_image(img_path)
                    dets = detector(img, 1)
                    for k, d in enumerate(dets):
                        shape = sp(img, d)
                        face_descriptor = facerec.compute_face_descriptor(img, shape)
                        face_encoding = np.array(face_descriptor)
                        known_face_encodings.append(face_encoding)
                        known_face_names.append(filename.split(".")[0])
            return known_face_encodings, known_face_names
        
        saved_faces_directory = saved_faces_directory1
        known_face_encodings, known_face_names = load_face_data(saved_faces_directory)
        
        # Layout
        left, right = st.columns([5,1])
        
        with left:
            with st.form("Attendance Input"):
               
                col1, col2, col3 = st.columns([6, 1, 1])
                with col1:
                     st.session_state.attendance_input = st.text_input("What did you learn?", "")
                with col2:
                    add_button = st.form_submit_button(label=':heavy_plus_sign: Add')
                with col3:
                    snap_button = st.form_submit_button(label=':camera: Snap')
        
        if 'captured_image' not in st.session_state:
            st.session_state.captured_image = None
            st.session_state.captured_image_path = ""
        
        if snap_button:
            st.session_state.captured_image = capture_image()
            if st.session_state.captured_image is not None:
                image_pil = Image.fromarray(cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_BGR2RGB))
                st.image(image_pil, caption='Captured Image')
                
                # Save captured image and get path
                st.session_state.captured_image_path = save_image(st.session_state.captured_image, st.session_state.selected_student)
                
                # Face recognition
                img_rgb = cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_BGR2RGB)
                dets = detector(img_rgb, 1)
                if len(dets) == 0:
                    st.error("No face detected. Please try again.")
                else:
                    for k, d in enumerate(dets):
                        shape = sp(img_rgb, d)
                        face_descriptor = facerec.compute_face_descriptor(img_rgb, shape)
                        face_encoding = np.array(face_descriptor)
        
                        distances = np.linalg.norm(known_face_encodings - face_encoding, axis=1)
                        min_distance = np.min(distances)
                        if min_distance < 0.6:  # You can adjust the threshold as needed
                            matched_idx = np.argmin(distances)
                            matched_name = known_face_names[matched_idx]
                            st.success(f"Face recognized: {matched_name}")
                            st.session_state.student_present = True
                            st.session_state.timer_running = True  # Enable timer if face recognized
                            start_timer()
                            # HTML and JavaScript to request the user's location
                            location_script = """
                            <script>
                            function getLocation() {
                                if (navigator.geolocation) {
                                    navigator.geolocation.getCurrentPosition(showPosition, showError);
                                } else { 
                                    document.getElementById("location").innerHTML = "Geolocation is not supported by this browser.";
                                }
                            }
                            
                            function showPosition(position) {
                                document.getElementById("location").innerHTML = 
                                "Latitude: " + position.coords.latitude + 
                                "<br>Longitude: " + position.coords.longitude;
                            }
                            
                            function showError(error) {
                                switch(error.code) {
                                    case error.PERMISSION_DENIED:
                                        document.getElementById("location").innerHTML = "User denied the request for Geolocation."
                                        break;
                                    case error.POSITION_UNAVAILABLE:
                                        document.getElementById("location").innerHTML = "Location information is unavailable."
                                        break;
                                    case error.TIMEOUT:
                                        document.getElementById("location").innerHTML = "The request to get user location timed out."
                                        break;
                                    case error.UNKNOWN_ERROR:
                                        document.getElementById("location").innerHTML = "An unknown error occurred."
                                        break;
                                }
                            }
                            
                            getLocation();
                            </script>
                            <div id="location">Fetching location...</div>
                            """
                            
                            
                            # st.markdown("## Current Location")
                            html(location_script, height=100)
        
                        else:
                            st.error("Face not recognized. Please try again.")
                            st.session_state.student_present = False
                            st.session_state.timer_running = False
        
        with right:
            if st.session_state.timer_running:
                stop_button = st.button("Stop")
                if stop_button:
                    stop_timer()
            else:
                start_button = st.button("Start")
                if start_button:
                    if not st.session_state.student_present:
                        st.warning("Please take a snapshot to start the timer.")
                    else:
                        start_timer()
        
        # Display the attendance log
        st.write("### Attendance Log")
        df = pd.DataFrame(st.session_state.data)
        if df.empty:
            st.info("No attendance marked today.")
        else:
            df['CapturedImage'] = df['CapturedImagePath'].apply(lambda x: Image.open(x))
            for index, row in df.iterrows():
                st.image(row['CapturedImage'], caption=f"{row['Start time']} - {row['Stop time']}")
            st.table(df.drop(columns=['CapturedImage']))
        
        # Display today's routine
        st.write("### Today's Routine")
        routine = get_student_routine(st.session_state.selected_student)
        routine_df = pd.DataFrame(routine, columns=["StartTime", "EndTime", "Subject", "Classroom", "TeacherName"])
        st.table(routine_df)
        
        # Clean up and release webcam
        cv2.destroyAllWindows()
        conn.close()


    elif page == "Calendar":
        Calendar.main()
    elif page == "Dashboard":
        Dashboard.main()
    elif page == "Notifications":
        Notifications.main()
    elif page == "User":
        User.main()
    elif page == "Profile Settings":
        Profile.main()


    # Initialize session state for the timer and data storage
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
        st.session_state.start_time = None
        st.session_state.data = []  # Initialize a list to store data entries
        st.session_state.attendance_input = ""  # Initialize attendance input
    if 'student_present' not in st.session_state:
        st.session_state.student_present = False
    
    