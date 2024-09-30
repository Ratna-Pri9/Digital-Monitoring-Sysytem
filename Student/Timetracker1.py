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
from geopy.distance import geodesic

# Set the page config
st.set_page_config(page_title="Time Tracker", page_icon=":alarm_clock:", layout="wide")

# Initialize session state
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
    st.session_state.start_time = None
    st.session_state.data = []
    st.session_state.attendance_input = ""
    st.session_state.selected_routine_id = None  # Initialize selected_routine_id
    st.session_state.selected_course_id = None   # Initialize selected_course_id
    st.session_state.selected_classroom = None   # Initialize selected_classroom
if 'student_present' not in st.session_state:
    st.session_state.student_present = False


# Database setup
db_path = 'F:/MCA PROJECT/Final/Data/university.db'
if not os.path.exists(db_path):
    st.error("Database not found. Terminating the program.")
    st.stop()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load face recognition models
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("F:/MCA PROJECT/Final/Data/shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("F:/MCA PROJECT/Final/Data/dlib_face_recognition_resnet_model_v1.dat")

# Function definitions
def start_timer():
    st.session_state.timer_running = True
    st.session_state.start_time = time.time()
    st.session_state.start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def stop_timer():
    st.session_state.timer_running = False
    elapsed_time = (time.time() - st.session_state.start_time) / 60
    stop_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    routine = get_student_routine(st.session_state.selected_student)
    if routine:
        class_start = routine[0][0]
        class_end = routine[0][1]
        attendance_status, attendance_percentage = calculate_attendance(class_start, class_end, elapsed_time)
    else:
        attendance_status = "Unknown"
        attendance_percentage = 0
    
    data_entry = {
        "StudentId": st.session_state.selected_student,
        "ClassID": f"{st.session_state.selected_routine_id}{datetime.now().strftime('%Y%m%d')}",
        "CourseID": st.session_state.selected_course_id,
        "Date": datetime.now().strftime('%Y-%m-%d'),
        "Out": stop_time_str,
        "SubjectTopic": st.session_state.attendance_input,
        "Room": st.session_state.selected_classroom,
        "Duration": round(elapsed_time, 2),
        "Attendance": attendance_status,
        "Logs": f"Started at: {st.session_state.start_time_str}, Stopped at: {stop_time_str}",
        "InTime": st.session_state.start_time_str,
        "CapturedImagePath": st.session_state.captured_image_path,
        "AttendancePercentage": f"{attendance_percentage:.2f}%"
    }
    
    st.session_state.data.append(data_entry)
    st.session_state.attendance_input = ""
    save_to_database(data_entry)
    
    if attendance_status == "Present":
        st.success("Attendance marked as Present")
    else:
        st.warning(f"Attendance marked as Absent. Duration attended: {elapsed_time:.2f} minutes ({attendance_percentage:.2f}%)")

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
    
def get_current_routine(routines):
    now = datetime.now().time()
    for routine in routines:
        start_time = datetime.strptime(routine[0], "%H:%M").time()
        end_time = datetime.strptime(routine[1], "%H:%M").time()
        if start_time <= now <= end_time:
            return routine
    return None

def get_students():
    try:
        cursor.execute("SELECT StudentID, FirstName, LastName FROM Students")
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching students: {e}")
        return []

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
    save_directory = "F:/MCA PROJECT/Final/Data/AttenImages"
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        
    img_path = f"{save_directory}/{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(img_path, image)
    return img_path

def verify_student_face(face_encoding, student_id):
    saved_faces_directory = 'F:/MCA PROJECT/Final/Data/SavedFaces'
    student_face_path = os.path.join(saved_faces_directory, f"{student_id}.jpg")
    if not os.path.exists(student_face_path):
        return False
    
    student_img = dlib.load_rgb_image(student_face_path)
    student_dets = detector(student_img, 1)
    if len(student_dets) == 0:
        return False
    
    student_shape = sp(student_img, student_dets[0])
    student_face_descriptor = facerec.compute_face_descriptor(student_img, student_shape)
    student_face_encoding = np.array(student_face_descriptor)
    
    distance = np.linalg.norm(student_face_encoding - face_encoding)
    return distance < 0.6

def verify_location(student_lat, student_lon, teacher_lat=23.391131, teacher_lon=85.300583, max_distance_km=1):
    student_coords = (student_lat, student_lon)
    teacher_coords = (teacher_lat, teacher_lon)
    
    distance = geodesic(student_coords, teacher_coords).km
    return distance <= max_distance_km

def calculate_attendance(class_start, class_end, student_duration):
    class_duration = (datetime.strptime(class_end, '%H:%M') - datetime.strptime(class_start, '%H:%M')).total_seconds() / 60
    attendance_percentage = (student_duration / class_duration) * 100
    
    if attendance_percentage >= 66.67:
        return "Present", attendance_percentage
    else:
        return "Absent", attendance_percentage

# Main app
students = get_students()

student_ids = [student[0] for student in students]
student_names = [f"{student[1]} {student[2]}" for student in students]

default_student_id = "STU961527236"
default_index = student_ids.index(default_student_id) if default_student_id in student_ids else 0

selected_student_index = st.selectbox("Selected Student", range(len(student_ids)), index=default_index, format_func=lambda x: student_names[x])
st.session_state.selected_student = student_ids[selected_student_index]

routines = get_student_routine(st.session_state.selected_student)
current_routine = get_current_routine(routines)

if current_routine:
    st.session_state.selected_routine_id = f"RTN{datetime.now().strftime('%Y%m%d')}"
    st.session_state.selected_course_id = current_routine[2]  # Subject
    st.session_state.selected_classroom = current_routine[3]
else:
    st.warning("No current routine found.")


# Fetch and set routine information
routine = get_student_routine(st.session_state.selected_student)
if routine:
    st.session_state.selected_routine_id = f"RTN{datetime.now().strftime('%Y%m%d')}"
    st.session_state.selected_course_id = routine[0][2]  # Assuming Subject is the course ID
    st.session_state.selected_classroom = routine[0][3]
else:
    st.warning("No routine found for today.")

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
        
        st.session_state.captured_image_path = save_image(st.session_state.captured_image, st.session_state.selected_student)
        
        img_rgb = cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_BGR2RGB)
        dets = detector(img_rgb, 1)
        if len(dets) == 0:
            st.error("No face detected. Please try again.")
        else:
            shape = sp(img_rgb, dets[0])
            face_descriptor = facerec.compute_face_descriptor(img_rgb, shape)
            face_encoding = np.array(face_descriptor)

            if verify_student_face(face_encoding, st.session_state.selected_student):
                st.success(f"Face recognized: {st.session_state.selected_student}")
                st.session_state.student_present = True
                st.session_state.timer_running = True
                start_timer()
                
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
                    
                    var data = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    fetch("/_stcore/stream", {
                        method: "POST",
                        body: JSON.stringify(data),
                        headers: {
                            "Content-Type": "application/json"
                        }
                    });
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
                
                html(location_script, height=100)
            else:
                st.error("Face not recognized or doesn't match selected student. Please try again.")
                st.session_state.student_present = False
                st.session_state.timer_running = False

def handle_location_data():
    location_data = st.query_params
    if 'lat' in location_data and 'lon' in location_data:
        student_lat = float(location_data['lat'])
        student_lon = float(location_data['lon'])
        if verify_location(student_lat, student_lon):
            st.success("Location verified successfully")
            return True
        else:
            st.error("Location authentication failed: Not within allowed range")
            st.session_state.timer_running = False
            return False
    return None

location_verified = handle_location_data()

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

st.write("### Previous Attendance Data")
df = pd.DataFrame(st.session_state.data)
if df.empty:
    st.info("No attendance marked today.")
else:
    # Filter and rename columns
    display_columns = ['Date', 'ClassID', 'SubjectTopic', 'InTime', 'Out', 'Logs', 'CapturedImagePath']
    df_display = df[display_columns].copy()
    df_display.columns = ['Date', 'RoutineID', 'Subject Topic', 'In Time', 'Out Time', 'Logs', 'Captured Image Path']
    
    # Update Logs column to include all details
    df_display['Logs'] = df_display.apply(lambda row: f"Face Authentication: Successful\n"
                                                      f"Location Authentication: {'Successful' if location_verified else 'Failed'}\n"
                                                      f"Start Time: {row['In Time']}\n"
                                                      f"End Time: {row['Out Time']}\n"
                                                      f"{row['Logs']}", axis=1)
    
    # Display images
    for index, row in df_display.iterrows():
        st.image(row['Captured Image Path'], caption=f"{row['In Time']} - {row['Out Time']}")
    
    # Display table with all columns, including CapturedImagePath
    st.table(df_display)
st.write("### Today's Routine")
routine_df = pd.DataFrame(routine, columns=["StartTime", "EndTime", "Subject", "Classroom", "TeacherName"])
st.table(routine_df)

# Clean up
cv2.destroyAllWindows()
conn.close()




