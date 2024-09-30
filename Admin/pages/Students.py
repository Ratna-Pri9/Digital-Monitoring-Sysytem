import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
import base64
import xlsxwriter
from datetime import datetime
from config import db_path

# st.set_page_config(layout="wide")
def main():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Function to fetch data from the database
    @st.cache_data
    def fetch_data():
        query = "SELECT * FROM Students"
        df = pd.read_sql(query, conn)
        return df
    
    df1 = fetch_data()
    
    # Function to generate a new StudentId
    def generate_student_id():
        query = "SELECT MAX(CAST(SUBSTR(StudentID, 5) AS INTEGER)) FROM Students"
        result = conn.execute(query).fetchone()[0]
        if result:
            new_id = f"STUD{int(result) + 1:04d}"
        else:
            new_id = "STUD0001"
        return new_id
    
    # Function to add a new student
    def add_student(details, image):
        try:
            details["StudentID"] = generate_student_id()
            columns = ", ".join(details.keys()) + ", Image"
            placeholders = ", ".join("?" * len(details)) + ", ?"
            query = f"INSERT INTO Students ({columns}) VALUES ({placeholders})"
            conn.execute(query, list(details.values()) + [image])
            conn.commit()
            st.success("Student added successfully!")
        except Exception as e:
            st.error(f"Error adding student: {e}")
    
    # Function to update a student's details
    def update_student(student_id, details, image=None):
        set_clause = ", ".join(f"{k} = ?" for k in details.keys())
        try:
            if image:
                query = f"UPDATE Students SET {set_clause}, Image = ? WHERE StudentID = ?"
                conn.execute(query, list(details.values()) + [image, student_id])
            else:
                query = f"UPDATE Students SET {set_clause} WHERE StudentID = ?"
                conn.execute(query, list(details.values()) + [student_id])
            conn.commit()
            st.success("Student details updated successfully!")
        except Exception as e:
            st.error(f"Error updating student: {e}")
    
    # Function to delete a student
    def delete_student(student_id):
        try:
            query = "DELETE FROM Students WHERE StudentID = ?"
            conn.execute(query, (student_id,))
            conn.commit()
            st.warning("Student deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting student: {e}")
    
    # Function to export data to Excel
    def export_to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df1.to_excel(writer, index=False, sheet_name='Students')
        writer.close()
        output.seek(0)  # Move the cursor to the start of the stream
        return output.getvalue()
    
    # Function to display Image from binary data and make it clickable
    def display_image(image_data, student_id):
        if image_data:
            encoded_image = base64.b64encode(image_data).decode()
            href = f"data:image/png;base64,{encoded_image}"
            return f'<a href="{href}" target="_blank"><img src="{href}" width="50" height="50"/></a>'
        return "No Image"
    
    # Tabs for List View and Grid View
    tab1, tab2 = st.tabs(["List View", "Grid View"])
    
    # List View
    with tab1:
        # Search box
        search_term = st.text_input("Search by Student Name")
    
        # Fetch and display data
        df = fetch_data()
    
        # Convert date columns to datetime.date
        df['AdmissionDate'] = pd.to_datetime(df['AdmissionDate']).dt.date
        df['DOB'] = pd.to_datetime(df['DOB']).dt.date
    
        # Check if 'Image' column exists
        if 'Image' in df.columns:
            df['Image'] = df.apply(lambda row: display_image(row['Image'], row['StudentID']), axis=1)
        else:
            st.error("The 'Image' column does not exist in the database. Please check the schema.")
    
        if search_term:
            df = df[df['FirstName'].str.contains(search_term, case=False, na=False)]
    
        # Select columns to display
        columns_to_display = ['StudentID', 'Image', 'FirstName', 'MiddleName', 'LastName', 'RollNo', 'RegNo', 'DepartmentID', 'CourseId', 'AdmissionDate', 'Gender', 'Phone', 'Email']
        df = df[columns_to_display]
    
        df['Action'] = '   '
    
        # Action buttons for adding, refreshing, and exporting
        col1, col2, col3 = st.columns(3)
    
        if col1.button("➕"):
            st.session_state.show_add_form = True
    
        if col2.button("🔄"):
            st.experimental_rerun()
    
        if col3.button("Export to XLS"):
            excel_data = export_to_excel(df)
            st.download_button(label="Download XLS", data=excel_data, file_name='Students.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
        if st.session_state.get('show_add_form', False):
            with st.form("Add Student"):
                details = {
                    "FirstName": st.text_input("First Name"),
                    "MiddleName": st.text_input("Middle Name"),
                    "LastName": st.text_input("Last Name"),
                    "RollNo": st.text_input("Roll Number"),
                    "RegNo": st.text_input("Registration Number"),
                    "DepartmentID": st.text_input("Department ID"),
                    "CourseId": st.text_input("Course ID"),
                    "AdmissionDate": st.date_input("Admission Date"),
                    "NameInHindi": st.text_input("Name in Hindi"),
                    "Caste": st.selectbox("Caste", ["General", "ST", "SC", "OBC", "Uncategorized"], index=4),
                    "DOB": st.date_input("Date of Birth"),
                    "Gender": st.selectbox("Gender", ["Male", "Female", "Other"]),
                    "FatherName": st.text_input("Father's Name"),
                    "MotherName": st.text_input("Mother's Name"),
                    "Phone": st.text_input("Phone"),
                    "Email": st.text_input("Email"),
                    "Session": st.text_input("Session")
                }
                image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
                col1, col2 = st.columns([1, 1])
                submit = col1.form_submit_button("Submit")
                cancel = col2.form_submit_button("Cancel")
    
                if submit:
                    if all(details[key] for key in details if key not in ["MiddleName"]) and (image_file is not None):
                        image = image_file.read() if image_file else None
                        add_student(details, image)
                        st.session_state.show_add_form = False
                        st.experimental_rerun()
                    else:
                        st.error("All fields except Middle Name are required and an Image must be uploaded.")
                if cancel:
                    st.session_state.show_add_form = False
                    st.experimental_rerun()
    
        leftcol, rightcol = st.columns([8, 1])
        with leftcol:
            # Display the table
            st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
    
        # with rightcol:
        #     # Edit and delete buttons in the table
        #     for index, row in df1.iterrows():
        #         col1, col2 = st.columns([1, 1])
        #         edit_button_key = f"edit_{index}"  # Unique key for each edit button
        #         if col1.button("✏️", key=edit_button_key):
        #             st.session_state.edit_index = index
        #             st.session_state.edit_row = row
    
        #         if col2.button("🗑️", key=f"delete_{index}"):
        #             delete_student(row['StudentID'])
        #             st.experimental_rerun()
    
        # Edit form for updating a student
        if 'edit_index' in st.session_state and 'edit_row' in st.session_state:
            index = st.session_state.edit_index
            row = st.session_state.edit_row
    
            st.write(f"Editing Student ID: {row['StudentID']}")
    
            details = {
                "FirstName": st.text_input("First Name", row['FirstName']),
                "MiddleName": st.text_input("Middle Name", row.get('MiddleName', '')),
                "LastName": st.text_input("Last Name", row['LastName']),
                "RollNo": st.text_input("Roll Number", row['RollNo']),
                "RegNo": st.text_input("Registration Number", row['RegNo']),
                # "DepartmentID": st.text_input("Department ID", row['DepartmentID']),
                # "CourseId": st.text_input("Course ID", row['CourseId']),
                # "AdmissionDate": st.date_input("Admission Date", row['AdmissionDate']),
                # "NameInHindi": st.text_input("Name in Hindi", row.get('NameInHindi', '')),
                # "Caste": st.selectbox("Caste", ["General", "ST", "SC", "OBC", "Uncategorized"], index=["General", "ST", "SC", "OBC", "Uncategorized"].index(row.get('Caste', 'Uncategorized'))),
                # "DOB": st.date_input("Date of Birth", row['DOB']),
                # "Gender": st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(row['Gender'])),
                "FatherName": st.text_input("Father's Name", row.get('FatherName', '')),
                "MotherName": st.text_input("Mother's Name", row.get('MotherName', '')),
                "Phone": st.text_input("Phone", row['Phone']),
                "Email": st.text_input("Email", row['Email']),
                "Session": st.text_input("Session", row.get('Session', ''))
            }
            image_file = st.file_uploader("Upload New Image (optional)", type=["png", "jpg", "jpeg"])
            col1, col2 = st.columns([1, 1])
            submit = col1.button("Update")
            cancel = col2.button("Cancel")
    
            if submit:
                image = image_file.read() if image_file else None
                update_student(row['StudentID'], details, image)
                del st.session_state.edit_index
                del st.session_state.edit_row
                st.experimental_rerun()
            if cancel:
                del st.session_state.edit_index
                del st.session_state.edit_row
    
    # Grid View
    with tab2:
        # Grid view to be implemented here, similar logic as the list view
        pass
    
    conn.close()
    