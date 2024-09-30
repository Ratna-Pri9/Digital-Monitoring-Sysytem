import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
import base64
import xlsxwriter
import time
from config import db_path
# st.set_page_config(layout="wide")


def main():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    
    
    def fetch_data(table_name):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        return df
    
    def fetch_teachers():
        return fetch_data('Teachers')
    
    def fetch_departments():
        return fetch_data('Departments')
    
    def fetch_Courses():
        return fetch_data('Courses')
    
    def add_department(details):
        try:
            # Check if DepartmentID is unique
            if is_department_id_unique(details["DepartmentID"]):
                query = "INSERT INTO Departments (DepartmentID, Name, HeadOfDepartment, Phone, Email, TotalCourse, ActiveStudents, TotalCapacity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                conn.execute(query, (
                    details["DepartmentID"],
                    details["Name"],
                    details["HeadOfDepartment"],
                    details["Phone"],
                    details["Email"],
                    details["TotalCourse"],
                    details["ActiveStudents"],
                    details["TotalCapacity"]
                ))
                conn.commit()
                st.success("Department added successfully!")
            else:
                st.error("Department ID already exists. Please use a different ID.")
        except Exception as e:
            st.error(f"Error adding Department: {e}")
    
    def update_department(DepartmentID, details):
        try:
            # Check if DepartmentID is unique for update
            if is_department_id_unique(details["DepartmentID"], DepartmentID):
                query = "UPDATE Departments SET Name=?, HeadOfDepartment=?, Phone=?, Email=?, TotalCourse=?, ActiveStudents=?, TotalCapacity=? WHERE DepartmentID=?"
                conn.execute(query, (
                    details["Name"],
                    details["HeadOfDepartment"],
                    details["Phone"],
                    details["Email"],
                    details["TotalCourse"],
                    details["ActiveStudents"],
                    details["TotalCapacity"],
                    DepartmentID
                ))
                conn.commit()
                st.success("Department details updated successfully!")
            else:
                st.error("Department ID already exists. Please use a different ID.")
        except Exception as e:
            st.error(f"Error updating Department: {e}")
    
    def delete_department(DepartmentID):
        try:
            query = "DELETE FROM Departments WHERE DepartmentID = ?"
            conn.execute(query, (DepartmentID,))
            conn.commit()
            st.warning("Department deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting Department: {e}")
    
    def export_to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Departments')
        writer.close()
        output.seek(0)  # Move the cursor to the start of the stream
        return output.getvalue()
    
    def is_department_id_unique(department_id, current_department_id=None):
        query = "SELECT COUNT(*) FROM Departments WHERE DepartmentID = ?"
        if current_department_id:
            query += " AND DepartmentID != ?"
            result = conn.execute(query, (department_id, current_department_id)).fetchone()
        else:
            result = conn.execute(query, (department_id,)).fetchone()
        return result[0] == 0
    
    def is_hod_unique(head_of_department, current_department_id=None):
        query = "SELECT COUNT(*) FROM Departments WHERE HeadOfDepartment = ?"
        if current_department_id:
            query += " AND DepartmentID != ?"
            result = conn.execute(query, (head_of_department, current_department_id)).fetchone()
        else:
            result = conn.execute(query, (head_of_department,)).fetchone()
        return result[0] == 0
    
    
    
    df = fetch_departments()
    
    teachers_df = fetch_teachers()
    teacher_options = teachers_df.apply(lambda row: f"{row['FirstName']} {row['MiddleName']} {row['LastName']}", axis=1).tolist()
    
    
    tab1, tab2 = st.tabs(["Departments", "Cources"])
    
    with tab1:
        
    
    
        search_term = st.text_input("Search by Department Name")
        if search_term:
            df = df[df['Name'].str.contains(search_term, case=False, na=False)]
    
        # Action buttons
        col1, col2, col3, col4, col5 = st.columns(5)
        
        if col1.button("Add Department"):
            st.session_state.show_form = True
             
        if col2.button("Refresh"):
            st.experimental_rerun()
        
        
        
        if col3.button("Export to XLS"):
            excel_data = export_to_excel(df)
            st.download_button(label="Download XLS", data=excel_data, file_name='Departments.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        
        
        if st.session_state.get('show_form', False):
            with st.form("Add Department"):
                teachers_df = fetch_teachers()
                teacher_options = teachers_df.apply(lambda row: f"{row['FirstName']} {row['MiddleName']} {row['LastName']}", axis=1).tolist()
        
                details = {
                    "DepartmentID": st.text_input("Department ID"),
                    "Name": st.text_input("Name"),
                    "HeadOfDepartment": st.selectbox("Head of Department", teacher_options),
                    "Phone": st.text_input("Phone"),
                    "Email": st.text_input("Email"),
                    "TotalCourse": st.number_input("Total Course", min_value=0, step=1),
                    "ActiveStudents": st.number_input("Active Students", min_value=0, step=1),
                    "TotalCapacity": st.number_input("Total Capacity", min_value=0, step=1)
                }
        
                selected_teacher = teachers_df[teachers_df.apply(lambda row: f"{row['FirstName']} {row['MiddleName']} {row['LastName']}", axis=1)==details["HeadOfDepartment"]]
                teacher_id=selected_teacher.TeacherID
        
                col1, col2 = st.columns([1, 1])
                submit = col1.form_submit_button("Submit")
                cancel = col2.form_submit_button("Cancel")
        
                if submit:
                    if all(details.values()):
                        add_department(details)
                        success_message = st.empty()
                        success_message.success("Department added successfully!")
                        time.sleep(1)
                        success_message.empty()
                        st.session_state.show_form = False
                        st.experimental_rerun()
                    else:
                        st.error("All fields are required.")
        
                if cancel:
                    st.session_state.show_form = False
                    st.experimental_rerun()
        
       
        # Display table
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
        
        
        # Editing and Deleting Departments
        with st.expander("Edit / Delete"):
            department_to_edit = st.selectbox("Select Department to Edit / Delete", df['Name'].tolist())
        
            if department_to_edit:
                selected_department = df[df['Name'] == department_to_edit].iloc[0]
        
                st.write("Selected Department Details:")
                st.write(selected_department)
        
                edit_details = {
                    "Name": st.text_input("Name", value=selected_department['Name']),
                    "HeadOfDepartment": st.selectbox("Head of Department", teacher_options, index=teacher_options.index(selected_department['HeadOfDepartment'])),
                    "Phone": st.text_input("Phone", value=selected_department['Phone']),
                    "Email": st.text_input("Email", value=selected_department['Email']),
                    "TotalCourse": st.number_input("Total Course", value=selected_department['TotalCourse'], min_value=0, step=1),
                    "ActiveStudents": st.number_input("Active Students", value=selected_department['ActiveStudents'], min_value=0, step=1),
                    "TotalCapacity": st.number_input("Total Capacity", value=selected_department['TotalCapacity'], min_value=0, step=1)
                }
        
                col3, col4 = st.columns([1, 1])
                update = col3.button("Update Department")
                delete = col4.button("Delete Department")
                cancel_edit = st.button("Cancel Edit")
        
                if update:
                    update_department(selected_department['DepartmentID'], edit_details)
                    st.experimental_rerun()
        
                if delete:
                    delete_department(selected_department['DepartmentID'])
                    st.experimental_rerun()
        
                if cancel_edit:
                    st.session_state.show_form = False
                    st.experimental_rerun()
    
    
    
    
    
    
    
    with tab2:
        
        def generate_course_id(details, semester):
            dep_id = details["DepartmentID"][:3].upper()
            course_name = details["Name"][:3].upper()
            course_type = "UG" if details["Type"] == "Undergraduate" else "PG"
            semester = semester.replace("Semester ", "SEM")
            course_id = f"{dep_id}{course_name}{course_type}{semester}"
            return course_id
    
        def add_Courses(details):
            try:
                semesters = []
                if details["Type"] == "Undergraduate":
                    semesters = [f"Semester {i}" for i in range(1, 7)]
                else:
                    semesters = [f"Semester {i}" for i in range(1, 5)]
    
                for semester in semesters:
                    details["Semester"] = semester
                    details["CourseID"] = generate_course_id(details, semester)
                    if is_course_id_unique(details["CourseID"]):
                        query = "INSERT INTO Courses (CourseID, Name, DepartmentID, Type, Semester, ActiveStudents, StudentCapacity, CourseFee) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                        conn.execute(query, (
                            details["CourseID"],
                            details["Name"],
                            details["DepartmentID"],
                            details["Type"],
                            details["Semester"],
                            details["ActiveStudents"],
                            details["StudentCapacity"],
                            details["CourseFee"]
                        ))
                        conn.commit()
                    else:
                        st.error(f"Generated Course ID for {semester} already exists. Please check the input values.")
                        return
                st.success("Courses added successfully!")
            except Exception as e:
                st.error(f"Error adding Course: {e}")
    
        def update_Courses(course_id, details):
            try:
                if is_course_id_unique(details["CourseID"], course_id):
                    query = "UPDATE Courses SET Name=?, DepartmentID=?, Type=?, Semester=?, ActiveStudents=?, StudentCapacity=?, CourseFee=? WHERE CourseID=?"
                    conn.execute(query, (
                        details["Name"],
                        details["DepartmentID"],
                        details["Type"],
                        details["Semester"],
                        details["ActiveStudents"],
                        details["StudentCapacity"],
                        details["CourseFee"],
                        course_id
                    ))
                    conn.commit()
                    st.success("Course details updated successfully!")
                else:
                    st.error("Course ID already exists. Please use a different ID.")
            except Exception as e:
                st.error(f"Error updating Course: {e}")
    
        def delete_Course(name, course_type):
            try:
                query = "DELETE FROM Courses WHERE Name = ? AND Type = ?"
                conn.execute(query, (name, course_type))
                conn.commit()
                st.warning("Courses deleted successfully!")
            except Exception as e:
                st.error(f"Error deleting Courses: {e}")
        def export_to_excel(df1):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df1.to_excel(writer, index=False, sheet_name='Departments')
            writer.close()
            output.seek(0)  # Move the cursor to the start of the stream
            return output.getvalue()
    
        def is_course_id_unique(course_id, current_course_id=None):
            query = "SELECT COUNT(*) FROM Courses WHERE CourseID = ?"
            if current_course_id:
                query += " AND CourseID != ?"
                result = conn.execute(query, (course_id, current_course_id)).fetchone()
            else:
                result = conn.execute(query, (course_id,)).fetchone()
            return result[0] == 0
    
        def fetch_Courses():
            query = "SELECT * FROM Courses"
            df1 = pd.read_sql_query(query, conn)
    
            # Ensure appropriate data types
            df1['ActiveStudents'] = df1['ActiveStudents'].astype(int)
            df1['StudentCapacity'] = df1['StudentCapacity'].astype(int)
            df1['CourseFee'] = df1['CourseFee'].astype(int)
    
            return df1
    
        def fetch_Departments():
            query = "SELECT DepartmentID, Name FROM Departments"
            df1 = pd.read_sql_query(query, conn)
            return df1
    
        def display_courses(df1):
            df1_undergrad = df1[df1['Type'] == 'Undergraduate']
            df1_postgrad = df1[df1['Type'] == 'Postgraduate']
    
            st.write("### Undergraduate Courses")
            st.write(df1_undergrad.to_html(escape=False), unsafe_allow_html=True)
    
            st.write("### Postgraduate Courses")
            st.write(df1_postgrad.to_html(escape=False), unsafe_allow_html=True)
    
        with st.container():
            df11 = fetch_Courses()
            
    
            search_term = st.text_input("Search by Course Name")
            if search_term:
                df11 = df11[df11['Name'].str.contains(search_term, case=False, na=False)]
    
    
    
            col1, col2, col3, col4 = st.columns(4)
    
            if col1.button("Add Courses"):
                st.session_state.show_form = True
    
            if col2.button("🔄"):
                st.experimental_rerun()
    
            if col3.button("Export XLS"):
                excel_data = export_to_excel(df11)
                st.download_button(label="Download XLS", data=excel_data, file_name='Courses.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
            
            if st.session_state.get('show_form', False):
                departments_df1 = fetch_Departments()
                department_options = departments_df1['DepartmentID'].tolist()
    
                with st.form("Add Courses"):
                    details = {
                        "Name": st.text_input("Name"),
                        "DepartmentID": st.selectbox("Department ID", department_options),
                        "Type": st.selectbox("Type", ["Undergraduate", "Postgraduate"]),
                        "ActiveStudents": st.number_input("Active Students", min_value=0, step=1, format="%d"),
                        "StudentCapacity": st.number_input("Student Capacity", min_value=0, step=1, format="%d"),
                        "CourseFee": st.number_input("Course Fee", min_value=0, step=1, format="%d")
                    }
    
                    col1, col2 = st.columns([1, 1])
                    submit = col1.form_submit_button("Submit")
                    cancel = col2.form_submit_button("Cancel")
    
                    if submit:
                        if all(details.values()):
                            add_Courses(details)
                            st.session_state.show_form = False
                            st.experimental_rerun()
                        else:
                            st.error("All fields are required.")
    
                    if cancel:
                        st.session_state.show_form = False
                        st.experimental_rerun()
    
            display_courses(df11)
    
            el,er=st.columns(2)
            with el:
              with st.expander("Edit Courses"):
                  course_to_edit = st.selectbox("Select Course ID to Edit", df11['CourseID'].tolist())
    
                  if course_to_edit:
                      selected_course = df11[df11['CourseID'] == course_to_edit].iloc[0]
    
                      st.write("Selected Course Details:")
                      st.write(selected_course)
    
                      departments_df1 = fetch_Departments()
                      department_options = departments_df1['DepartmentID'].tolist()
    
                      with st.form("Edit Course"):
                          edit_details = {
                            #   "Name": st.text_input("Name", value=selected_course['Name']),
                              "DepartmentID": st.selectbox("Department ID", department_options, index=department_options.index(selected_course['DepartmentID'])),
                            #   "Type": st.selectbox("Type", ["Undergraduate", "Postgraduate"], index=["Undergraduate", "Postgraduate"].index(selected_course['Type'])),
                            #   "Semester": selected_course['Semester'],
                              "ActiveStudents": st.number_input("Active Students", value=int(selected_course['ActiveStudents']), min_value=0, step=1, format="%d"),
                              "StudentCapacity": st.number_input("Student Capacity", value=int(selected_course['StudentCapacity']), min_value=0, step=1, format="%d"),
                              "CourseFee": st.number_input("Course Fee", value=int(selected_course['CourseFee']), min_value=0, step=1, format="%d")
                          }
    
                          col1, col2, col3 = st.columns([1, 1, 1])
                          update = col1.form_submit_button("Update Course")
                          cancel_edit = col3.form_submit_button("Cancel Edit")
    
                          if update:
                              update_Courses(selected_course['CourseID'], edit_details)
                              st.experimental_rerun()
    
                          if cancel_edit:
                              st.session_state.show_form = False
                              st.experimental_rerun()
    
            with er:
            # Separate delete button with expander
              with st.expander("Delete Courses"):
                  course_to_delete = st.selectbox("Select Course ID to Delete", df11['CourseID'].tolist(), key="delete_select")
                  if course_to_delete:
                      selected_course = df11[df11['CourseID'] == course_to_delete].iloc[0]
                      if st.button("Delete Course"):
                          delete_Course(selected_course['Name'], selected_course['Type'])
                          st.experimental_rerun()
    