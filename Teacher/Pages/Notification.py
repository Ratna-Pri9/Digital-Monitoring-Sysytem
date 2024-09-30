import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64
from config import db_path

# st.set_page_config(layout="wide")
def main():
    # Initialize connection to SQLite database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Function to fetch departments
    def fetch_departments():
        c.execute('SELECT DepartmentID, Name, HeadOfDepartment FROM Departments')
        return c.fetchall()
    
    # Function to fetch teachers
    def fetch_teachers():
        c.execute('SELECT TeacherID, FirstName, MiddleName, LastName FROM Teachers')
        return c.fetchall()
    
    # Function to fetch courses
    def fetch_courses():
        c.execute('SELECT CourseID, Name, DepartmentID FROM Courses')
        return c.fetchall()
    
    # Function to fetch notifications
    def fetch_notifications():
        c.execute('SELECT * FROM Notifications')
        return c.fetchall()
    
    # Function to insert a new notification
    def insert_notification(notification_id, date, description, type_, course_id, attachments):
        c.execute('''
        INSERT INTO Notifications (NotificationID, Date, Description, Type, DepartmentName, Attachments)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (notification_id, date, description, type_, course_id, attachments))
        conn.commit()
    
    # Function to update a notification
    def update_notification(notification_id, date, description, type_, course_id, attachments):
        c.execute('''
        UPDATE Notifications
        SET Date = ?, Description = ?, Type = ?, DepartmentName = ?, Attachments = ?
        WHERE NotificationID = ?
        ''', (date, description, type_, course_id, attachments, notification_id))
        conn.commit()
    
    # Function to delete a notification
    def delete_notification(notification_id):
        c.execute('DELETE FROM Notifications WHERE NotificationID = ?', (notification_id,))
        conn.commit()
    
    # Generate NotificationID
    def generate_notification_id(type_, course_name):
        count = 1
        while True:
            notification_id = f"{type_[:3].upper()}{course_name[:3].upper()}{count}"
            c.execute('SELECT 1 FROM Notifications WHERE NotificationID = ?', (notification_id,))
            if c.fetchone() is None:
                return notification_id
            count += 1
    
    # Function to generate download link for attachments
    def get_download_link(file_data, filename):
        b64 = base64.b64encode(file_data).decode()
        href = f'<a href="data:file/;base64,{b64}" download="{filename}">{filename}</a>'
        return href
    
    # Fetch departments, teachers, and courses
    departments = fetch_departments()
    teachers = fetch_teachers()
    courses = fetch_courses()
    teacher_dict = {f"{id_} - {first_name} {middle_name} {last_name}": id_ for id_, first_name, middle_name, last_name in teachers}
    teacher_options = [f"{id_} - {first_name} {middle_name} {last_name}" for id_, first_name, middle_name, last_name in teachers]
    
    department_dict = {name: id_ for id_, name, _ in departments}
    hod_dict = {hod: id_ for id_, _, hod in departments}
    department_options = ["All Departments"] + [name for _, name, _ in departments]
    
    # Session state initialization
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False
    if 'show_edit_form' not in st.session_state:
        st.session_state.show_edit_form = False
    if 'selected_notification_id' not in st.session_state:
        st.session_state.selected_notification_id = None
    
    # Select teacher ID
    # selected_teacher = st.selectbox("Select Teacher", teacher_options)
    selected_teacher_id = st.session_state.user_id
    
    # Check if selected teacher is HOD
    selected_teacher_name = st.session_state.user_id
    is_hod = selected_teacher_name in hod_dict
    
    col1, col2, col3 = st.columns(3)
    
    if is_hod:
        # Filter courses for the HOD's department
        hod_department_id = hod_dict[selected_teacher_name]
        filtered_courses = [course for course in courses if course[2] == hod_department_id]
        course_dict = {f"{course_id} - {course_name}": course_id for course_id, course_name, _ in filtered_courses}
        course_options = ["All Courses"] + [f"{course_id} - {course_name}" for course_id, course_name, _ in filtered_courses]
    
        # Toggle add form visibility
        if col1.button("Add Notification"):
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.session_state.show_edit_form = False
    
        # Toggle edit form visibility
        if col3.button("Edit/Delete Notification"):
            st.session_state.show_edit_form = not st.session_state.show_edit_form
            st.session_state.show_add_form = False
    
        # Refresh button
        if col2.button("Refresh"):
            st.experimental_rerun()
    
        # Notification form
        if st.session_state.show_add_form:
            with st.form("notification_form"):
                description = st.text_input("Description")
                type_ = st.selectbox("Type", ["Exam", "Holiday", "Event", "Placement"])
                course_selection = st.selectbox("Course", course_options)
                attachments = st.file_uploader("Attachments (image or PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])
    
                col1, col2 = st.columns(2)
                with col1:
                    submit_button = st.form_submit_button(label="Add Notification")
                with col2:
                    cancel_button = st.form_submit_button(label="Cancel")
    
                if submit_button:
                    if course_selection != "All Courses":
                        course_id, course_name = course_selection.split(" - ")
                        notification_id = generate_notification_id(type_, course_name)
                    else:
                        course_id = "ALL"
                        notification_id = generate_notification_id(type_, "ALL")
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    attachments_data = attachments.read() if attachments else None
                    try:
                        insert_notification(notification_id, date, description, type_, course_id, attachments_data)
                        st.success(f"Notification {notification_id} added successfully!")
                        st.session_state.show_add_form = False
                    except sqlite3.IntegrityError:
                        st.error("Failed to add notification. Please try again.")
    
                if cancel_button:
                    st.session_state.show_add_form = False
    
        # Edit or Delete Notifications
        if st.session_state.show_edit_form:
            notifications = fetch_notifications()
            notification_ids = [row[0] for row in notifications]
            selected_notification_id = st.selectbox("Select Notification ID to Edit/Delete", notification_ids)
    
            if selected_notification_id:
                st.session_state.selected_notification_id = selected_notification_id
                selected_notification = next(row for row in notifications if row[0] == st.session_state.selected_notification_id)
                st.write("Edit Notification")
                with st.form("edit_form"):
                    new_description = st.text_input("Description", value=selected_notification[2])
                    new_type = st.selectbox("Type", ["Exam", "Holiday", "Event", "Placement"], index=["Exam", "Holiday", "Event", "Placement"].index(selected_notification[3]))
                    new_course_selection = st.selectbox("Course", course_options, index=course_options.index(f"{selected_notification[4]} - {next(course[1] for course in courses if course[0] == selected_notification[4])}" if selected_notification[4] != "ALL" else "All Courses"))
                    new_attachments = st.file_uploader("Attachments (image or PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])
    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        update_button = st.form_submit_button("Update Notification")
                    with col2:
                        delete_button = st.form_submit_button("Delete Notification")
                    with col3:
                        cancel_button = st.form_submit_button("Cancel")
    
                    if update_button:
                        if new_course_selection != "All Courses":
                            new_course_id, new_course_name = new_course_selection.split(" - ")
                        else:
                            new_course_id = "ALL"
                        new_attachments_data = new_attachments.read() if new_attachments else selected_notification[5]
                        update_notification(st.session_state.selected_notification_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), new_description, new_type, new_course_id, new_attachments_data)
                        st.success(f"Notification {st.session_state.selected_notification_id} updated successfully!")
                        st.session_state.show_edit_form = False
                        st.session_state.selected_notification_id = None
    
                    if delete_button:
                        delete_notification(st.session_state.selected_notification_id)
                        st.success(f"Notification {st.session_state.selected_notification_id} deleted successfully!")
                        st.session_state.show_edit_form = False
                        st.session_state.selected_notification_id = None
    
                    if cancel_button:
                        st.session_state.show_edit_form = False
                        st.session_state.selected_notification_id = None
    
    
    # Display all notifications
    st.write("## Previous Notifications")
    notifications = fetch_notifications()
    notifications_list = []
    for notification in notifications:
        notification_id, date, description, type_, course_id, attachments = notification
        if attachments:
            filename = f"attachment_{notification_id}"
            download_link = get_download_link(attachments, filename)
        else:
            download_link = "No attachment"
        notifications_list.append([notification_id, date, description, type_, course_id, download_link])
    
    notifications_df = pd.DataFrame(notifications_list, columns=["NotificationID", "Date", "Description", "Type", "CourseID", "Attachments"])
    st.markdown(notifications_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    
    
    