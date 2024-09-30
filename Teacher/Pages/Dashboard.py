import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from config import db_path
# st.set_page_config(page_title="Teacher Time Tracker", page_icon=":alarm_clock:", layout="wide")



def main():
    st.header("Dashboard")
    def create_connection():
        conn = sqlite3.connect(db_path)
        return conn
    
    # Function to fetch data from a table
    def fetch_data(table_name):
        conn = create_connection()
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    
    # Function to fetch departments
    def fetch_departments():
        conn = create_connection()
        c = conn.cursor()
        c.execute('SELECT DepartmentID, Name FROM Departments')
        departments = c.fetchall()
        conn.close()
        return {d[1]: d[0] for d in departments}
    
    # Function to fetch pending students based on department
    def fetch_pending_students(department_id):
        conn = create_connection()
        query = '''
            SELECT StudentID, first_name, middle_name, last_name, Email, CourseId, DepartmentID, RollNo, RegNo, AdmissionDate, Session, DOB, Phone 
            FROM StudentLogin 
            WHERE DepartmentID = ? AND approval_status = 'pending'
        '''
        df = pd.read_sql(query, conn, params=(department_id,))
        conn.close()
        return df
    
    # Function to accept a student
    def accept_student(student_id):
        conn = create_connection()
        c = conn.cursor()
        
        # Fetch the student's data from StudentLogin table
        c.execute('''
            SELECT * FROM StudentLogin WHERE StudentID = ?
        ''', (student_id,))
        student_data = c.fetchone()
        
        if student_data:
            # Insert into Students table
            c.execute('''
                INSERT INTO Students (StudentID, FirstName, MiddleName, LastName, RollNo, RegNo, DepartmentID, CourseId, AdmissionDate, DOB, Phone, Email, Session)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_data[0], student_data[1], student_data[2], student_data[3], student_data[8], student_data[9], 
                student_data[7], student_data[6], student_data[10], student_data[13], student_data[14], student_data[4], student_data[11]
            ))
            
            # Update approval status in StudentLogin table
            c.execute('''
                UPDATE StudentLogin 
                SET approval_status = 'accepted' 
                WHERE StudentID = ?
            ''', (student_id,))
            
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    
    # Function to reject a student
    def reject_student(student_id):
        conn = create_connection()
        c = conn.cursor()
        c.execute('DELETE FROM StudentLogin WHERE StudentID = ?', (student_id,))
        conn.commit()
        conn.close()
    
    
    
    
    
    # Sample data
    data = {
        'Subject': ['HUMENGUGSEM1', 'SOS ANUGSEM1', 'VOCCAPUGSEM1', 'SCIBOTPGSEM3'],
        'Class_Taken': [25, 25, 23, 10],
        'Delayed_Class': [24, 15, 22, 21],
        'Total_Class': [30, 30, 25, 22]
    }
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Streamlit app
    
    #  # Table
    # st.subheader('Data Table')
    # st.table(df)
    
    col1,col2=st.columns(2)
    
    with col1:
    
        # Line chart
        st.subheader('Line Chart')
        fig, ax = plt.subplots()
        ax.plot(df['Subject'], df['Class_Taken'], label='Class_Taken', marker='o', color='cyan')
        ax.plot(df['Subject'], df['Delayed_Class'], label='Delayed_Class', marker='o', color='orange')
        ax.plot(df['Subject'], df['Total_Class'], label='Total Class', marker='o', color='green')
        for i, txt in enumerate(df['Class_Taken']):
            ax.annotate(txt, (df['Subject'][i], df['Class_Taken'][i]), color='cyan')
        for i, txt in enumerate(df['Delayed_Class']):
            ax.annotate(txt, (df['Subject'][i], df['Delayed_Class'][i]), color='orange')
        for i, txt in enumerate(df['Total_Class']):
            ax.annotate(txt, (df['Subject'][i], df['Total_Class'][i]), color='green')
        ax.set_facecolor("none")
        fig.patch.set_alpha(0.0)
        ax.legend()
        ax.set_title('Semester 1', color='white')
        ax.tick_params(colors='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        st.pyplot(fig)
    
    with col2:
        # Bar chart
        st.subheader('Bar Chart')
        fig, ax = plt.subplots()
        bar_width = 0.35
        index = np.arange(len(df))
        bar1 = ax.bar(index, df['Class_Taken'], bar_width, label='Class_Taken', color='cyan')
        bar2 = ax.bar(index, df['Delayed_Class'], bar_width, bottom=df['Class_Taken'], label='Delayed_Class', color='orange')
        for i, txt in enumerate(df['Class_Taken']):
            ax.annotate(txt, (index[i], df['Class_Taken'][i] / 2), ha='center', va='center', color='black')
        for i, txt in enumerate(df['Delayed_Class']):
            ax.annotate(txt, (index[i], df['Class_Taken'][i] + df['Delayed_Class'][i] / 2), ha='center', va='center', color='black')
        ax.set_facecolor("none")
        fig.patch.set_alpha(0.0)
        ax.set_xticks(index)
        ax.set_xticklabels(df['Subject'], color='white')
        ax.legend()
        ax.set_title('Semester 1', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        st.pyplot(fig)
    
    
    
    
    
    col1,col2=st.columns(2)
    with col1:
        # Combined bar chart
        st.subheader('Combined Bar Chart')
        fig, ax = plt.subplots()
        bar_width = 0.2
        index = np.arange(len(df))
        
        # Plotting the bars
        bar1 = ax.bar(index - bar_width, df['Class_Taken'], bar_width, label='Class_Taken', color='cyan')
        bar2 = ax.bar(index, df['Delayed_Class'], bar_width, label='Delayed_Class', color='orange')
        bar3 = ax.bar(index + bar_width, df['Total_Class'], bar_width, label='Total Class', color='green')
        
        # Adding text labels on the bars
        for i in range(len(df)):
            ax.annotate(df['Class_Taken'][i], (index[i] - bar_width, df['Class_Taken'][i] + 0.5), ha='center', color='white')
            ax.annotate(df['Delayed_Class'][i], (index[i], df['Delayed_Class'][i] + 0.5), ha='center', color='white')
            ax.annotate(df['Total_Class'][i], (index[i] + bar_width, df['Total_Class'][i] + 0.5), ha='center', color='white')
        
        # Customizing the appearance
        ax.set_facecolor("none")
        fig.patch.set_alpha(0.0)
        ax.set_xticks(index)
        ax.set_xticklabels(df['Subject'], color='white')
        ax.legend()
        ax.set_title('Semester 1 Combined', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        
        st.pyplot(fig)    
          
       
        
    with col2:
           # Pie chart
           st.subheader('Pie Chart')
           pie_labels = df['Subject']
           pie_sizes = df['Class_Taken']
           fig, ax = plt.subplots()
           ax.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=140, textprops={'color':'white'})
           ax.set_facecolor("none")
           fig.patch.set_alpha(0.0)
           ax.set_title('Attendance Distribution', color='white')
           st.pyplot(fig)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # # Select box to select TeacherId
    # tab1,tab2=st.tabs(["User","Department"])
    
    # with tab1:
    #     st.subheader("User")
    
    
    #display this part only if is teacher is hod
    # with tab2:
    #     Course,Aproval,Leave=st.tabs(["Course","Approval","Leave"])
    #     # select box to select course Type,CourseId
    #     with Course:
    #           st.write("Attendance")
    #         #   print Course
    
            
    
    
    
    
    
    
        # # with Aproval:
        # #     # Streamlit UI
        # #     st.title("Student Application Approval")
            
        # #     departments = fetch_departments()
        # #     department_name = st.selectbox("Select Department", list(departments.keys()))
        # #     department_id = departments[department_name]
            
        # #     pending_students = fetch_pending_students(department_id)
            
        # #     if pending_students.empty:
        # #         st.write("No pending applications")
        # #     else:
        # #         st.write("Pending Applications")
        # #         for idx, student in pending_students.iterrows():
        # #             with st.expander(f"Student ID: {student['StudentID']} - {student['first_name']} {student['middle_name']} {student['last_name']}"):
        # #                 col1, col2, col3 = st.columns(3)
        # #                 col1.write(f"**First Name:** {student['first_name']}")
        # #                 col1.write(f"**Middle Name:** {student['middle_name']}")
        # #                 col1.write(f"**Last Name:** {student['last_name']}")
        # #                 col1.write(f"**Email:** {student['Email']}")
        # #                 col1.write(f"**Course ID:** {student['CourseId']}")
        # #                 col1.write(f"**Department ID:** {student['DepartmentID']}")
                        
        # #                 col2.write(f"**Roll No:** {student['RollNo']}")
        # #                 col2.write(f"**Reg No:** {student['RegNo']}")
        # #                 col2.write(f"**Admission Date:** {student['AdmissionDate']}")
        # #                 col2.write(f"**Session:** {student['Session']}")
        # #                 col2.write(f"**DOB:** {student['DOB']}")
        # #                 col2.write(f"**Phone:** {student['Phone']}")
            
        # #                 col3.write(f"**Approval Status:** pending")
        # #                 if col3.button("Accept", key=f"accept_{student['StudentID']}"):
        # #                     accept_student(student['StudentID'])
        # #                     st.success(f"Accepted student {student['StudentID']}")
        # #                     st.experimental_rerun()
        # #                 if col3.button("Reject", key=f"reject_{student['StudentID']}"):
        # #                     reject_student(student['StudentID'])
        # #                     st.success(f"Rejected student {student['StudentID']}")
        # #                     st.experimental_rerun()
            
    
    
    
    
        # # with Leave:
        # #     st.write("Leave")
                     
    
        # #     def create_connection(db_path):
        # #         conn = None
        # #         try:
        # #             conn = sqlite3.connect(db_path)
        # #         except sqlite3.Error as e:
        # #             st.error(f"Error connecting to database: {e}")
        # #         return conn
    
        # #     # Function to load students and leave applications data
        # #     def load_students_and_applications(conn):
        # #         query = """
        # #         SELECT S.StudentID, (S.FirstName || ' ' || S.LastName) AS StudentName, L.rowid AS ApplicationID, L.*
        # #         FROM LeaveApplications L
        # #         JOIN Students S ON L.UserID = S.StudentID
        # #         WHERE L.UserType = 'Student' AND L.Status = 'pending'
        # #         """
        # #         return pd.read_sql_query(query, conn)
            
        # #     # Function to update leave application status
        # #     def update_leave_application_status(conn, application_id, status):
        # #         query = "UPDATE LeaveApplications SET Status = ? WHERE rowid = ?"
        # #         try:
        # #             cur = conn.cursor()
        # #             cur.execute(query, (status, application_id))
        # #             conn.commit()
        # #             return True
        # #         except sqlite3.Error as e:
        # #             st.error(f"Error updating data: {e}")
        # #             return False
            
        # #     # Streamlit application layout
        # #     st.title('Student Leave Application Approval')
            
        # #     # Establish database connection
        # #     conn = create_connection(db_path)
        # #     if conn is None:
        # #         st.stop()
            
        # #     # Load students and leave applications data
        # #     applications_df = load_students_and_applications(conn)
            
        # #     # Check if there are any pending applications
        # #     if applications_df.empty:
        # #         st.info("No pending applications.")
        # #     else:
        # #         # Select box to choose a student and application ID
        # #         applications_df['Display'] = applications_df.apply(lambda row: f"{row['StudentName']} - Application ID: {row['ApplicationID']}", axis=1)
        # #         selected_application = st.selectbox("Select Application", applications_df['Display'])
                
        # #         selected_row = applications_df[applications_df['Display'] == selected_application].iloc[0]
        # #         application_id = selected_row['ApplicationID']
            
        # #         # Display the selected application details
        # #         st.write("### Application Details")
        # #         st.write(f"**Student Name:** {selected_row['StudentName']}")
        # #         st.write(f"**Application ID:** {application_id}")
        # #         st.write(f"**Apply Date:** {selected_row['ApplyDate']}")
        # #         st.write(f"**From Date:** {selected_row['FromDate']}")
        # #         st.write(f"**To Date:** {selected_row['ToDate']}")
        # #         st.write(f"**No. of Days:** {selected_row['NoOfDays']}")
        # #         st.write(f"**Reason:** {selected_row['Reason']}")
        # #         if selected_row['Attachments']:
        # #             attachment_data = selected_row['Attachments']
        # #             if attachment_data:
        # #                 st.download_button("Download Attachment", data=attachment_data, file_name=f"attachment_{application_id}.bin")
            
        # #         # Dropdown to choose action
        # #         action = st.selectbox("Action", ["Select Action", "Approve", "Reject", "Cancel"])
            
        # #         # Submit button to process the action
        # #         submit = st.button("Submit")
            
        # #         if submit:
        # #             if action == "Approve":
        # #                 if update_leave_application_status(conn, application_id, 'approved'):
        # #                     st.success("Application approved successfully")
        # #                     st.experimental_rerun()
        # #             elif action == "Reject":
        # #                 if update_leave_application_status(conn, application_id, 'rejected'):
        # #                     st.success("Application rejected successfully")
        # #                     st.experimental_rerun()
        # #             elif action == "Cancel":
        # #                 st.info("Action cancelled")
        # #             else:
        # #                 st.warning("Please select a valid action")
            
        #     # Close the database connection
        #     conn.close()
    