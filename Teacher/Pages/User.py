import sqlite3
import pandas as pd
import streamlit as st
import datetime
from datetime import date
from config import db_path


# st.set_page_config(page_title="Teacher ", layout="wide")





# Function to load data from the SQLite database
def load_data_from_db(db_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # SQL query to select data from TeacherAttendance table
    query = "SELECT * FROM TeacherAttendance"
    
    # Read the data into a DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Close the connection
    conn.close()
    
    return df

# Function to generate the monthly summary
def generate_summary(df, start_date, end_date):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day'] = df['Date'].dt.strftime('%a, %b %d')
    df['InTime'] = pd.to_datetime(df['InTime'], format='%H:%M:%S').dt.time
    df['Out'] = pd.to_datetime(df['Out'], format='%H:%M:%S').dt.time
    
    summary_data = []
    date_range = pd.date_range(start=start_date, end=end_date)
    
    for date in date_range:
        if date.weekday() == 6:  # Sunday
            summary_data.append({
                'DAY/DATE': date.strftime('%a, %b %d'),
                'FIRST IN': '',
                'LAST OUT': '',
                'SUBJECTS': '',
                'ATTENDANCE': 'Holiday'
            })
        else:
            day_data = df[df['Date'].dt.date == date.date()]
            if not day_data.empty:
                first_in = day_data['InTime'].min()
                last_out = day_data['Out'].max()
                subjects = ','.join(day_data['SubjectTopic'].unique())
                attendance_list = day_data['Attendance']
                attendance = ''.join(['✅' if status == 'Present' else '❌' for status in attendance_list])
            else:
                first_in, last_out, subjects, attendance = 'Absent', 'Absent', 'Absent', 'Absent'

            summary_data.append({
                'DAY/DATE': date.strftime('%a, %b %d'),
                'FIRST IN': first_in,
                'LAST OUT': last_out,
                'SUBJECTS': subjects,
                'ATTENDANCE': attendance
            })
    
    summary_df = pd.DataFrame(summary_data)
    return summary_df

# Streamlit app
def main():
    st.title('Monthly Attendance Summary')

    # Load the data from the database
    df = load_data_from_db(db_path)
    
    # Get the current date and set the minimum date
    today = datetime.date.today()
    min_date = datetime.date(2021, 1, 1)
    
    # Adjust the default start and end dates to be within the min and max values
    default_start_date = max(min_date, today.replace(day=1))
    default_end_date = min(today, (today.replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date())
    
    # Display a date range picker with max and min dates
    date_range = st.date_input("Select a date range", [default_start_date, default_end_date],
                               min_value=min_date,
                               max_value=today)
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        # Generate the summary
        summary_df = generate_summary(df, start_date, end_date)
        
        # Display the selected date range
        st.header(f"Summary from {start_date.strftime('%A, %B %d, %Y')} to {end_date.strftime('%A, %B %d, %Y')}")
        
        # Display the summary dataframe
        st.dataframe(summary_df, width=10000)
    else:
        st.write("Please select a date range to view the summary.")

if __name__ == "__main__":
    tab1, tab2, tab3 = st.tabs(["Summary", "Detailed", "Leave"])

    with tab1:
        main()


    with tab2:
      
      
      # Function to load data from the SQLite database
      def load_data_from_db(db_path):
          # Connect to the database
          conn = sqlite3.connect(db_path)
          
          # SQL query to select data from TeacherAttendance table
          query = "SELECT * FROM TeacherAttendance"
          
          # Read the data into a DataFrame
          df = pd.read_sql_query(query, conn)
          
          # Close the connection
          conn.close()
          
          return df
      
      with st.container():
          # Load the data
          df = load_data_from_db(db_path)
          
          # Ensure the 'Date' column is in datetime format
          df['Date'] = pd.to_datetime(df['Date'])
          
          # Display a date picker
          selected_date = st.date_input("Select a date")
          
          # Display the selected date with day name and date
          st.header(selected_date.strftime("%A, %B %d, %Y"))
          
          # Filter the DataFrame based on the selected date
          filtered_df = df[df['Date'].dt.date == selected_date]
          
          # Display the filtered dataframe
          st.dataframe(filtered_df, width=10000)
      
      
      




    with tab3:
        
        
        # Database connection
        
        
        def create_connection(db_path):
            conn = None
            try:
                conn = sqlite3.connect(db_path)
            except sqlite3.Error as e:
                st.error(f"Error connecting to database: {e}")
            return conn
        
        # Function to load Teachers data
        def load_Teachers(conn):
            query = "SELECT TeacherID, FirstName || ' ' || LastName AS Name FROM Teachers"
            return pd.read_sql_query(query, conn)
        
        # Function to save leave application data
        def save_leave_application(conn, data):
            query = """
            INSERT INTO LeaveApplications (UserID, UserType, ApplyDate, FromDate, ToDate, NoOfDays, Reason, Status, Attachments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            try:
                cur = conn.cursor()
                cur.execute(query, data)
                conn.commit()
                return True
            except sqlite3.Error as e:
                st.error(f"Error inserting data: {e}")
                return False
        
        # Function to update leave application data
        def update_leave_application(conn, application_id, data):
            query = """
            UPDATE LeaveApplications
            SET FromDate = ?, ToDate = ?, NoOfDays = ?, Reason = ?, Attachments = ?
            WHERE rowid = ? AND Status = 'pending'
            """
            try:
                cur = conn.cursor()
                cur.execute(query, (*data, application_id))
                conn.commit()
                return True
            except sqlite3.Error as e:
                st.error(f"Error updating data: {e}")
                return False
        
        # Function to delete leave application
        def delete_leave_application(conn, application_id):
            query = "DELETE FROM LeaveApplications WHERE rowid = ? AND Status = 'pending'"
            try:
                cur = conn.cursor()
                cur.execute(query, (application_id,))
                conn.commit()
                return True
            except sqlite3.Error as e:
                st.error(f"Error deleting data: {e}")
                return False
        
        # Streamlit application layout
        st.title('Teacher Leave Application')
        
        # Establish database connection
        conn = create_connection(db_path)
        if conn is None:
            st.stop()
        
        # Load Teachers data
        Teachers_df = load_Teachers(conn)
        
        # Teacher selection box
        Teacher_id = st.session_state.user_id

        # Initialize session state for edit mode
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False
            st.session_state.edit_application_id = None
        
        # Form to submit a new leave application
        with st.form("leave_form"):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                reason = st.text_input("Reason For Leave")
            
            with col2:
                from_date = st.date_input("From Date", min_value=date.today())
            
            with col3:
                to_date = st.date_input("To Date", min_value=from_date)
            
            attachment = st.file_uploader("Attach File")
            
            submit = st.form_submit_button("Submit")
            
            if submit:
                # Calculate number of days
                no_of_days = (to_date - from_date).days + 1
                
                # Save the uploaded file as BLOB
                attachment_data = None
                if attachment:
                    attachment_data = attachment.read()
                
                # Create a new application entry
                new_application = (
                    Teacher_id,
                    "Teacher",  # Default user type
                    date.today().strftime('%Y-%m-%d'),
                    from_date.strftime('%Y-%m-%d'),
                    to_date.strftime('%Y-%m-%d'),
                    no_of_days,
                    reason,
                    "pending",  # Ensure status is lowercase to meet the constraint
                    attachment_data
                )
                
                # Save the new application to the database
                if save_leave_application(conn, new_application):
                    st.success("Leave application submitted successfully")
        
        # Display the leave applications for the selected Teacher
        st.write("### Leave Applications")
        
        # Ensure TeacherID is properly quoted in the SQL query
        query = f"SELECT rowid, * FROM LeaveApplications WHERE UserID = '{Teacher_id}' AND UserType = 'Teacher'"
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            st.info("No applications submitted.")
        else:
            # Pagination
            col1, col2 = st.columns(2)
            with col1:
                items_per_page = st.selectbox("Items per page", [5, 10, 15], index=0)
        
            total_items = len(df)
            total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page != 0 else 0)
            with col2:
                page_number = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
        
            start_index = (page_number - 1) * items_per_page
            end_index = start_index + items_per_page
            paged_df = df.iloc[start_index:end_index]
        
            # Display the paginated dataframe in columns
            for index, row in paged_df.iterrows():
                st.write("----")
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                with col1:
                    st.write(f"**Application ID:** {row['rowid']}")
                    st.write(f"**Apply Date:** {row['ApplyDate']}")
                    st.write(f"**From Date:** {row['FromDate']}")
                
                with col2:
                    st.write(f"**To Date:** {row['ToDate']}")
                    st.write(f"**No. of Days:** {row['NoOfDays']}")
                    st.write(f"**Reason:** {row['Reason']}")
                
                with col3:
                    st.write(f"**Status:** {row['Status']}")
                
                with col4:
                    if row['Attachments'] is not None:
                        attachment_data = row['Attachments']
                        st.download_button("Download Attachment", data=attachment_data, file_name=f"attachment_{row['rowid']}.bin")
                
                if row['Status'] == 'pending':
                    if not st.session_state.edit_mode or st.session_state.edit_application_id != row['rowid']:
                        edit_button = st.button("Edit", key=f"edit_{row['rowid']}")
                        delete_button = st.button("Delete", key=f"delete_{row['rowid']}")
                        
                        if edit_button:
                            st.session_state.edit_mode = True
                            st.session_state.edit_application_id = row['rowid']
                            st.session_state.edit_from_date = row['FromDate']
                            st.session_state.edit_to_date = row['ToDate']
                            st.session_state.edit_reason = row['Reason']
                            st.session_state.edit_attachment = row['Attachments']
                            st.experimental_rerun()
                        
                        if delete_button:
                            if delete_leave_application(conn, row['rowid']):
                                st.success("Application deleted successfully")
                                st.experimental_rerun()
                    else:
                        st.write("### Edit Leave Application")
                        with st.form("edit_form"):
                            new_from_date = st.date_input("From Date", value=pd.to_datetime(st.session_state.edit_from_date))
                            new_to_date = st.date_input("To Date", value=pd.to_datetime(st.session_state.edit_to_date))
                            new_reason = st.text_input("Reason", value=st.session_state.edit_reason)
                            new_attachment = st.file_uploader("Attach File", key="new_attach")
                            
                            update = st.form_submit_button("Update")
                            cancel = st.form_submit_button("Cancel")
                            
                            if update:
                                new_no_of_days = (new_to_date - new_from_date).days + 1
                                new_attachment_data = st.session_state.edit_attachment
                                if new_attachment:
                                    new_attachment_data = new_attachment.read()
                                updated_data = (
                                    new_from_date.strftime('%Y-%m-%d'),
                                    new_to_date.strftime('%Y-%m-%d'),
                                    new_no_of_days,
                                    new_reason,
                                    new_attachment_data
                                )
                                if update_leave_application(conn, st.session_state.edit_application_id, updated_data):
                                    st.success("Application updated successfully")
                                    st.session_state.edit_mode = False
                                    st.session_state.edit_application_id = None
                                    st.experimental_rerun()
                            
                            if cancel:
                                st.session_state.edit_mode = False
                                st.session_state.edit_application_id = None
                                st.experimental_rerun()
        
        # Close the database connection
        conn.close()
        
        
        
        
        
        