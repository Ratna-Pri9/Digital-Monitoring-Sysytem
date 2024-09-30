import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
from config import db_path

def main():
    # Function to get distinct student IDs
    def get_student_ids(conn):
        try:
            cursor = conn.cursor()
            student_ids = cursor.execute("SELECT DISTINCT StudentID FROM Students").fetchall()
            return [id[0] for id in student_ids]
        except sqlite3.Error as e:
            st.error(f"Error fetching student IDs: {e}")
            return []
    
    # Function to get attendance data for a specific student and date range
    def get_attendance_data_for_student(conn, student_id, start_date, end_date):
        query = """
            SELECT
                sa.SubjectTopic as Subject,
                SUM(CASE WHEN sa.Attendance = 'Present' THEN 1 ELSE 0 END) as Attendance,  -- Count 'Present' statuses
                COUNT(sa.AttendanceID) as Total_Class
            FROM
                StudentAttendance sa
            WHERE
                sa.StudentId = ?
                AND sa.Date BETWEEN ? AND ?
            GROUP BY
                sa.SubjectTopic
        """
        try:
            cursor = conn.cursor()
            data = cursor.execute(query, (student_id, start_date, end_date)).fetchall()
            return data
        except sqlite3.Error as e:
            st.error(f"Error fetching attendance data: {e}")
            return []
    
    # Function to get total scheduled classes for a date range
    def get_total_scheduled_classes(conn, start_date, end_date):
        query = """
            SELECT
                r.Subject,
                COUNT(*) as Total_Scheduled
            FROM
                Routine r
            WHERE
                r.DayOfWeek BETWEEN ? AND ?
            GROUP BY
                r.Subject
        """
        try:
            cursor = conn.cursor()
            data = cursor.execute(query, (start_date, end_date)).fetchall()
            return dict(data)
        except sqlite3.Error as e:
            st.error(f"Error fetching scheduled classes: {e}")
            return {}
    
    # Function to get attendance data for all students
    def get_attendance_data_all_students(conn, start_date, end_date):
        query = """
            SELECT
                sa.SubjectTopic as Subject,
                SUM(CASE WHEN sa.Attendance = 'Present' THEN 1 ELSE 0 END) as Attendance,  -- Count 'Present' statuses
                COUNT(sa.AttendanceID) as Total_Class
            FROM
                StudentAttendance sa
            WHERE
                sa.Date BETWEEN ? AND ?
            GROUP BY
                sa.SubjectTopic
        """
        try:
            cursor = conn.cursor()
            data = cursor.execute(query, (start_date, end_date)).fetchall()
            return data
        except sqlite3.Error as e:
            st.error(f"Error fetching attendance data for all students: {e}")
            return []
    
    # Connect to the database with error handling
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        st.error(f"Failed to connect to the database: {e}")
        conn = None
    
    if conn:
        # Streamlit app
        st.title('Attendance Dashboard')
    
        # Date range selection
        start_date = st.date_input('Start Date', datetime.today())
        end_date = st.date_input('End Date', datetime.today())
    
        # Fetch student IDs for the select box
        student_ids = get_student_ids(conn)
        selected_student_id = st.session_state.user_id
    
        # Fetch attendance data for the selected student
        student_attendance_data = get_attendance_data_for_student(conn, selected_student_id, start_date, end_date)
    
        if student_attendance_data:
            df_student = pd.DataFrame(student_attendance_data, columns=['Subject', 'Attendance', 'Total_Class'])
            st.subheader(f'Student Attendance Details for {selected_student_id}')
            st.table(df_student)
    
            # Fetch attendance data for all students
            all_students_attendance_data = get_attendance_data_all_students(conn, start_date, end_date)
            df_all_students = pd.DataFrame(all_students_attendance_data, columns=['Subject', 'Attendance', 'Total_Class'])
    
            # Fetch total scheduled classes
            scheduled_classes = get_total_scheduled_classes(conn, start_date, end_date)
    
            # Calculate Avg_Attendance for each subject
            df_all_students['Avg_Attendance'] = df_all_students.apply(lambda row: row['Attendance'] / scheduled_classes.get(row['Subject'], 1), axis=1)  # Avoid division by zero
    
            # Display data table for all students
            st.subheader('Comparison with Other Students')
            st.table(df_all_students[['Subject', 'Attendance', 'Avg_Attendance']])
    
            col1, col2 = st.columns(2)
    
            with col1:
                # Line chart for all students
                st.subheader('Line Chart')
                fig, ax = plt.subplots()
                ax.plot(df_all_students['Subject'], df_all_students['Attendance'], label='Attendance', marker='o', color='cyan')
                ax.plot(df_all_students['Subject'], df_all_students['Avg_Attendance'], label='Avg. Attendance', marker='o', color='orange')
                ax.plot(df_all_students['Subject'], df_all_students['Total_Class'], label='Total Class', marker='o', color='green')
                for i, txt in enumerate(df_all_students['Attendance']):
                    ax.annotate(txt, (df_all_students['Subject'][i], df_all_students['Attendance'][i]), color='cyan')
                for i, txt in enumerate(df_all_students['Avg_Attendance']):
                    ax.annotate(txt, (df_all_students['Subject'][i], df_all_students['Avg_Attendance'][i]), color='orange')
                for i, txt in enumerate(df_all_students['Total_Class']):
                    ax.annotate(txt, (df_all_students['Subject'][i], df_all_students['Total_Class'][i]), color='green')
                ax.set_facecolor("none")
                fig.patch.set_alpha(0.0)
                ax.legend()
                ax.set_title('Attendance Comparison', color='white')
                ax.tick_params(colors='white')
                ax.yaxis.label.set_color('white')
                ax.xaxis.label.set_color('white')
                for spine in ax.spines.values():
                    spine.set_edgecolor('white')
                st.pyplot(fig)
    
            with col2:
                # Bar chart for all students
                st.subheader('Bar Chart')
                fig, ax = plt.subplots()
                bar_width = 0.35
                index = np.arange(len(df_all_students))
                bar1 = ax.bar(index, df_all_students['Attendance'], bar_width, label='Attendance', color='cyan')
                bar2 = ax.bar(index, df_all_students['Avg_Attendance'], bar_width, bottom=df_all_students['Attendance'], label='Avg. Attendance', color='orange')
                for i, txt in enumerate(df_all_students['Attendance']):
                    ax.annotate(txt, (index[i], df_all_students['Attendance'][i] / 2), ha='center', va='center', color='black')
                for i, txt in enumerate(df_all_students['Avg_Attendance']):
                    ax.annotate(txt, (index[i], df_all_students['Attendance'][i] + df_all_students['Avg_Attendance'][i] / 2), ha='center', va='center', color='black')
                ax.set_facecolor("none")
                fig.patch.set_alpha(0.0)
                ax.set_xticks(index)
                ax.set_xticklabels(df_all_students['Subject'], color='white')
                ax.legend()
                ax.set_title('Attendance Comparison', color='white')
                ax.tick_params(colors='white')
                for spine in ax.spines.values():
                    spine.set_edgecolor('white')
                st.pyplot(fig)
    
            col1, col2 = st.columns(2)
            with col1:
                # Combined bar chart for all students
                st.subheader('Combined Bar Chart')
                fig, ax = plt.subplots()
                bar_width = 0.2
                index = np.arange(len(df_all_students))
    
                # Plotting the bars
                bar1 = ax.bar(index - bar_width, df_all_students['Attendance'], bar_width, label='Attendance', color='cyan')
                bar2 = ax.bar(index, df_all_students['Avg_Attendance'], bar_width, label='Avg. Attendance', color='orange')
                bar3 = ax.bar(index + bar_width, df_all_students['Total_Class'], bar_width, label='Total Class', color='green')
    
                # Adding text labels on the bars
                for i in range(len(df_all_students)):
                    ax.annotate(df_all_students['Attendance'][i], (index[i] - bar_width, df_all_students['Attendance'][i] + 0.5), ha='center', color='white')
                    ax.annotate(df_all_students['Avg_Attendance'][i], (index[i], df_all_students['Avg_Attendance'][i] + 0.5), ha='center', color='white')
                    ax.annotate(df_all_students['Total_Class'][i], (index[i] + bar_width, df_all_students['Total_Class'][i] + 0.5), ha='center', color='white')
    
                # Customizing the appearance
                ax.set_facecolor("none")
                fig.patch.set_alpha(0.0)
                ax.set_xticks(index)
                ax.set_xticklabels(df_all_students['Subject'], color='white')
                ax.legend()
                ax.set_title('Combined Attendance Comparison', color='white')
                ax.tick_params(colors='white')
                for spine in ax.spines.values():
                    spine.set_edgecolor('white')
    
                st.pyplot(fig)
    
            with col2:
                # Pie chart for all students
                st.subheader('Pie Chart')
                pie_labels = df_all_students['Subject']
                pie_sizes = df_all_students['Attendance']
                fig, ax = plt.subplots()
                ax.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=140, textprops={'color':'white'})
                ax.set_facecolor("none")
                fig.patch.set_alpha(0.0)
                ax.set_title('Attendance Distribution', color='white')
                st.pyplot(fig)
    else:
        st.error("Could not connect to the database.")
    
