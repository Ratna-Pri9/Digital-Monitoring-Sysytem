import streamlit as st
import sqlite3
import uuid
from datetime import datetime
import pandas as pd
import subprocess as sp
from config import db_path



def main():
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_id = None  
        st.session_state.user_type = None 


    if st.session_state.authenticated:
        st.write(f"Logged in as: {st.session_state.user_id} ({st.session_state.user_type})")
        st.write("Redirecting to your dashboard...")
        st.experimental_rerun()  
        return
    
    
    # Function to create a connection to the database
    def create_connection():
        conn = sqlite3.connect(db_path)
        return conn
    
    # Function to generate a random ID
    def generate_id(prefix):
        random_int = uuid.uuid4().int & (1<<31)-1  
        return f"{prefix}{random_int}"
    
    def fetch_data(table_name):
        conn = create_connection()
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    
    def fetch_teachers():
        return fetch_data('Teachers')
    
    def fetch_departments():
        return fetch_data('Departments')
    
    def fetch_courses():
        return fetch_data('Courses')
    
    df_teachers = fetch_teachers()
    df_departments = fetch_departments()
    df_courses = fetch_courses()
    

    
    # Function to add a new student
    def add_student(student_data):
        conn = create_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO StudentLogin (StudentID, first_name, middle_name, last_name, Email, password, CourseId, DepartmentID, RollNo, RegNo, AdmissionDate, Session, approval_status, DOB, Phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', student_data)
        conn.commit()
        conn.close()
    
    # Function to add a new teacher
    def add_teacher(teacher_data):
        conn = create_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO TeacherLogin (TeacherID, first_name, middle_name, last_name, email, password, qualification, approval_status, dob, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', teacher_data)
        conn.commit()
        conn.close()
    
    # Function to check login credentials
    def check_credentials(user_id, password, user_type):
        conn = create_connection()
        c = conn.cursor()
        table = "StudentLogin" if user_type == "Student" else "TeacherLogin"
        c.execute(f'SELECT * FROM {table} WHERE {table[:-5]}ID = ? AND password = ?', (user_id, password))
        user = c.fetchone()
        conn.close()
        return user
    
    # Function to update password
    def update_password(user_id, new_password, user_type):
        conn = create_connection()
        c = conn.cursor()
        table = "StudentLogin" if user_type == "Student" else "TeacherLogin"
        c.execute(f'UPDATE {table} SET password = ? WHERE {table[:-5]}ID = ?', (new_password, user_id))
        conn.commit()
        conn.close()
    
    # Function to fetch department names and IDs
    def fetch_department_names():
        conn = create_connection()
        c = conn.cursor()
        c.execute('SELECT DepartmentID, Name FROM Departments')
        departments = c.fetchall()
        conn.close()
        return {d[1]: d[0] for d in departments}
    
    # Function to fetch course IDs based on department ID
    def fetch_course_ids_by_department(department_id):
        conn = create_connection()
        c = conn.cursor()
        c.execute('SELECT CourseID FROM Courses WHERE DepartmentID = ?', (department_id,))
        courses = c.fetchall()
        conn.close()
        return [c[0] for c in courses]
    
    # Initialize session state
    if 'login_user' not in st.session_state:
        st.session_state['login_user'] = None
    
    if 'show_signup_form' not in st.session_state:
        st.session_state['show_signup_form'] = False
    
    if 'show_teacher_signup_form' not in st.session_state:
        st.session_state['show_teacher_signup_form'] = False
    
    # Streamlit UI
    st.title("Digital Monitoring System")
    
    # Tabs for user roles
    tab1, tab2, tab3 = st.tabs(["Student", "Teacher", "Admin"])
    
    # Student tab
    with tab1:
        st.header("Student Login")
        student_id = st.text_input("Student ID", key="student_id_input")
        student_password = st.text_input("Student Password", type="password", key="student_password_input")
        if st.button("Login", key="student_login_button"):
            user = check_credentials(st.session_state.student_id_input, st.session_state.student_password_input, "Student")
            if user:
                if user[12] == 'pending':  
                    st.warning("Your ID approval is pending")
                else:
                    st.success(f"Welcome {user[1]} {user[2]}")
                    st.session_state['login_user'] = user
                    st.session_state.authenticated = True
                    st.session_state.user_id = student_id
                    st.session_state.user_type = "Student"  
                    st.experimental_rerun()
            else:
                st.error("Invalid credentials")
        
        col1, col2 = st.columns(2)
        if col1.button("Signup", key="student_signup_button"):
            st.session_state['show_signup_form'] = True
    
        if col2.button("Cancel", key="student_signup_cancel_button"):
            st.session_state['show_signup_form'] = False
    
        if st.session_state.get('show_signup_form', False):
            departments = fetch_department_names()
            department_name = st.selectbox("Department Name", list(departments.keys()), key="student_department_name")
            department_id = departments[department_name]
            courses = fetch_course_ids_by_department(department_id)
            with st.form("Register Student"):
                student_id = generate_id("STU")
                st.text_input("First Name", key="student_first_name")
                st.text_input("Middle Name", key="student_middle_name")
                st.text_input("Last Name", key="student_last_name")
                st.text_input("Email", key="student_email")
                st.text_input("Password", type="password", key="student_reg_password")
                st.selectbox("Course ID", courses, key="student_course_id")
                st.text_input("Roll No", key="student_roll_no")
                st.text_input("Reg No", key="student_reg_no")
                st.date_input("Admission Date", key="student_admission_date", value=datetime.today(), min_value=datetime(1950, 1, 1), max_value=datetime.today())
                st.text_input("Session", key="student_session")
                st.date_input("DOB", key="student_dob", value=datetime(2000, 1, 1), min_value=datetime(1950, 1, 1))
                st.text_input("Phone", key="student_phone")
                if st.form_submit_button("Register"):
                    student_data = (
                        student_id, st.session_state.student_first_name, st.session_state.student_middle_name, st.session_state.student_last_name,
                        st.session_state.student_email, st.session_state.student_reg_password, st.session_state.student_course_id,
                        department_id, st.session_state.student_roll_no, st.session_state.student_reg_no,
                        st.session_state.student_admission_date.strftime("%Y-%m-%d"), st.session_state.student_session,
                        'pending', st.session_state.student_dob.strftime("%Y-%m-%d"), st.session_state.student_phone
                    )
                    add_student(student_data)
                    st.success(f"Student registered successfully. Your ID is {student_id}")
                    st.session_state['show_signup_form'] = False
    
    # Teacher tab
    with tab2:
        st.header("Teacher Login")
        teacher_id = st.text_input("Teacher ID", key="teacher_id_input")
        teacher_pass = st.text_input("Teacher Password", type="password", key="teacher_password_input")
        if st.button("Login", key="teacher_login_button"):
            user = check_credentials(st.session_state.teacher_id_input, st.session_state.teacher_password_input, "Teacher")
            if user:
                if user[7] == 'pending':  # Approval status column
                    st.warning("Your ID approval is pending")
                else:
                    st.success(f"Welcome {user[1]} {user[2]}")
                    st.session_state['login_user'] = user
                    st.session_state.authenticated = True
                    st.session_state.user_id = teacher_id
                    st.session_state.user_type = "Teacher"  # Store the user type
                    st.experimental_rerun()
            else:
                st.error("Invalid credentials")
        
        col1, col2 = st.columns(2)
        if col1.button("Signup", key="teacher_signup_button"):
            st.session_state['show_teacher_signup_form'] = True
    
        if col2.button("Cancel", key="teacher_signup_cancel_button"):
            st.session_state['show_teacher_signup_form'] = False
    
        if st.session_state.get('show_teacher_signup_form', False):
            with st.form("Register Teacher"):
                teacher_id = generate_id("TEA")
                st.text_input("First Name", key="teacher_first_name")
                st.text_input("Middle Name", key="teacher_middle_name")
                st.text_input("Last Name", key="teacher_last_name")
                st.text_input("Email", key="teacher_email")
                st.text_input("Password", type="password", key="teacher_reg_password")
                st.text_input("Qualification", key="teacher_qualification")
                st.date_input("DOB", key="teacher_dob", value=datetime(1980, 1, 1), min_value=datetime(1950, 1, 1))
                st.text_input("Phone", key="teacher_phone")
                if st.form_submit_button("Register"):
                    teacher_data = (
                        teacher_id, st.session_state.teacher_first_name, st.session_state.teacher_middle_name,
                        st.session_state.teacher_last_name, st.session_state.teacher_email, st.session_state.teacher_reg_password,
                        st.session_state.teacher_qualification, 'pending', st.session_state.teacher_dob.strftime("%Y-%m-%d"), st.session_state.teacher_phone
                    )
                    add_teacher(teacher_data)
                    st.success(f"Teacher registered successfully. Your ID is {teacher_id}")
                    st.session_state['show_teacher_signup_form'] = False
    
    # Admin tab
    with tab3:
        st.header("Admin Login")
        Admin_id=st.text_input("Admin Username", key="admin_username_input")
        Admin_pass=st.text_input("Admin Password", type="password", key="admin_password_input")
        if st.button("Login", key="admin_login_button"):
            user = check_credentials(st.session_state.admin_username_input,st.session_state.admin_password_input, "Admin")
            st.session_state['login_user'] = user
            st.session_state.authenticated = True
            st.session_state.user_id = Admin_id
            st.session_state.user_type = "Admin"  # Store the user type
            st.experimental_rerun()
            
    
    # Reset Password functionality
    st.sidebar.header("Reset Password")
    st.sidebar.text_input("Enter your User ID", key="reset_user_id")
    st.sidebar.text_input("Enter new password", type="password", key="reset_password")
    st.sidebar.selectbox("Select user type", ["Student", "Teacher"], key="reset_user_type")
    if st.sidebar.button("Reset Password", key="reset_button"):
        update_password(st.session_state.reset_user_id, st.session_state.reset_password, st.session_state.reset_user_type)
        st.sidebar.success("Password reset successfully")
    

if __name__ == "__main__":
    main()