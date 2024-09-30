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
        try:
            query = "SELECT * FROM Teachers"
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    df1 = fetch_data()
    
    # Function to generate a new TeacherId
    def generate_teacher_id():
        try:
            query = "SELECT MAX(CAST(SUBSTR(TeacherID, 5) AS INTEGER)) FROM Teachers"
            result = conn.execute(query).fetchone()[0]
            if result:
                new_id = f"TEAC{int(result) + 1:04d}"
            else:
                new_id = "TEAC0001"
            return new_id
        except Exception as e:
            st.error(f"Error generating teacher ID: {e}")
            return "TEAC0001"
    
    # Function to add a new teacher
    def add_teacher(details, image):
        try:
            details["TeacherID"] = generate_teacher_id()
            columns = ", ".join(details.keys()) + ", Image"
            placeholders = ", ".join("?" * len(details)) + ", ?"
            query = f"INSERT INTO Teachers ({columns}) VALUES ({placeholders})"
            conn.execute(query, list(details.values()) + [image])
            conn.commit()
            st.success("Teacher added successfully!")
        except Exception as e:
            st.error(f"Error adding teacher: {e}")
    
    # Function to update a teacher's details
    def update_teacher(teacher_id, details, image=None):
        set_clause = ", ".join(f"{k} = ?" for k in details.keys())
        try:
            if image:
                query = f"UPDATE Teachers SET {set_clause}, Image = ? WHERE TeacherID = ?"
                conn.execute(query, list(details.values()) + [image, teacher_id])
            else:
                query = f"UPDATE Teachers SET {set_clause} WHERE TeacherID = ?"
                conn.execute(query, list(details.values()) + [teacher_id])
            conn.commit()
            st.success("Teacher details updated successfully!")
        except Exception as e:
            st.error(f"Error updating teacher: {e}")
    
    # Function to delete a teacher
    def delete_teacher(teacher_id):
        try:
            query = "DELETE FROM Teachers WHERE TeacherID = ?"
            conn.execute(query, (teacher_id,))
            conn.commit()
            st.warning("Teacher deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting teacher: {e}")
    
    # Function to export data to Excel
    def export_to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Teachers')
        writer.close()
        output.seek(0)  # Move the cursor to the start of the stream
        return output.getvalue()
    
    # Function to display Image from binary data and make it clickable
    def display_image(image_data, teacher_id):
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
        search_term = st.text_input("Search by Teacher Name")
    
        # Fetch and display data
        df = fetch_data()
    
        # Convert date columns to datetime.date and handle exceptions
        try:
            df['JoiningDate'] = pd.to_datetime(df['JoiningDate']).dt.date
        except Exception as e:
            st.warning(f"Error parsing 'JoiningDate': {e}")
    
        try:
            df['DOB'] = pd.to_datetime(df['DOB']).dt.date
        except Exception as e:
            st.warning(f"Error parsing 'DOB': {e}")
    
        # Check if 'Image' column exists
        if 'Image' in df.columns:
            df['Image'] = df.apply(lambda row: display_image(row['Image'], row['TeacherID']), axis=1)
        else:
            st.error("The 'Image' column does not exist in the database. Please check the schema.")
    
        if search_term:
            df = df[df['FirstName'].str.contains(search_term, case=False, na=False)]
    
        # Select columns to display
        columns_to_display = ['TeacherID', 'Image', 'FirstName', 'MiddleName', 'LastName', 'Qualification', 'Gender', 'Phone', 'Email', 'JoiningDate']
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
            st.download_button(label="Download XLS", data=excel_data, file_name='Teachers.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
        if st.session_state.get('show_add_form', False):
            with st.form("Add Teacher"):
                details = {
                    "FirstName": st.text_input("First Name"),
                    "MiddleName": st.text_input("Middle Name"),
                    "LastName": st.text_input("Last Name"),
                    "Qualification": st.text_input("Qualification"),
                    "Gender": st.selectbox("Gender", ["Male", "Female", "Other"]),
                    "Phone": st.text_input("Phone"),
                    "Email": st.text_input("Email"),
                    "JoiningDate": st.date_input("Joining Date"),
                    "NameInHindi": st.text_input("Name in Hindi"),
                    "Caste": st.selectbox("Caste", ["General", "ST", "SC", "OBC", "Uncategorized"], index=4),
                    "DOB": st.date_input("Date of Birth"),
                    "FatherName": st.text_input("Father's Name"),
                    "MotherName": st.text_input("Mother's Name"),
                    "Status": "unavailable"  # Default status
                }
                image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
                col1, col2 = st.columns([1, 1])
                submit = col1.form_submit_button("Submit")
                cancel = col2.form_submit_button("Cancel")
    
                if submit:
                    if all(details[key] for key in details if key not in ["MiddleName", "Status"]) and (image_file is not None):
                        image = image_file.read() if image_file else None
                        add_teacher(details, image)
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
    
        with rightcol:
            # Edit and delete buttons in the table
            for index, row in df1.iterrows():
                col1, col2 = st.columns([1, 1])
                edit_button_key = f"edit_{index}"  # Unique key for each edit button
                if col1.button("✏️", key=edit_button_key):
                    st.session_state.edit_index = index
                    st.session_state.edit_row = row
    
                if col2.button("🗑️", key=f"delete_{index}"):
                    delete_teacher(row['TeacherID'])
                    st.experimental_rerun()
    
        # Edit form for updating a teacher
        if 'edit_index' in st.session_state and 'edit_row' in st.session_state:
            index = st.session_state.edit_index
            row = st.session_state.edit_row
    
            st.write(f"Editing Teacher ID: {row['TeacherID']}")
    
            details = {
                "FirstName": st.text_input("First Name", row['FirstName']),
                "MiddleName": st.text_input("Middle Name", row.get('MiddleName', '')),
                "LastName": st.text_input("Last Name", row['LastName']),
                "Qualification": st.text_input("Qualification", row['Qualification']),
                "Gender": st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(row['Gender'])),
                "Phone": st.text_input("Phone", row['Phone']),
                "Email": st.text_input("Email", row['Email']),
                # "JoiningDate": st.date_input("Joining Date", row.get('JoiningDate', datetime.now().date())),
                "NameInHindi": st.text_input("Name in Hindi", row.get('NameInHindi', '')),
                "Caste": st.selectbox("Caste", ["General", "ST", "SC", "OBC", "Uncategorized"], index=["General", "ST", "SC", "OBC", "Uncategorized"].index(row.get('Caste', 'Uncategorized'))),
                # "DOB": st.date_input("Date of Birth", row.get('DOB', datetime.now().date())),
                "FatherName": st.text_input("Father's Name", row.get('FatherName', '')),
                "MotherName": st.text_input("Mother's Name", row.get('MotherName', '')),
                "Status": st.selectbox("Status", ["available", "unavailable"], index=["available", "unavailable"].index(row.get('Status', 'unavailable')))
            }
    
            image_file = st.file_uploader("Upload New Image (Leave blank to keep existing)", type=["png", "jpg", "jpeg"])
            col1, col2 = st.columns([1, 1])
            save_changes = col1.button("Save Changes")
            cancel_changes = col2.button("Cancel Changes")
    
            if save_changes:
                if all(details[key] for key in details if key not in ["MiddleName", "Status"]) and (image_file is not None):
                    image = image_file.read() if image_file else None
                    update_teacher(row['TeacherID'], details, image)
                    del st.session_state.edit_index
                    del st.session_state.edit_row
                    st.experimental_rerun()
                else:
                    st.error("All fields except Middle Name are required.")
    
            if cancel_changes:
                del st.session_state.edit_index
                del st.session_state.edit_row
                st.experimental_rerun()
    
    # Grid View
    with tab2:
        st.header("Grid View")
        df = fetch_data()
        
        grid_col1, grid_col2 = st.columns(2)
        
        def display_teacher_card(teacher):
            st.markdown(
                f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px; text-align: center;">
                    <h3>{teacher['FirstName']} {teacher['LastName']}</h3>
                    <p>ID: {teacher['TeacherID']}</p>
                    <img src="data:image/png;base64,{base64.b64encode(teacher['Image']).decode()}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover;" alt="Teacher Image"/>
                    <p>{teacher['Email']}</p>
                    <p>{teacher['Phone']}</p>
                    <button style="padding: 5px 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;" onclick="window.location.href='?teacher_id={teacher['TeacherID']}'">Read More</button>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        def display_teacher_details(teacher):
            st.markdown(
                f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin-bottom: 10px;">
                    <h2>{teacher['FirstName']} {teacher['LastName']}</h2>
                    <p><strong>Teacher ID:</strong> {teacher['TeacherID']}</p>
                    <img src="data:image/png;base64,{base64.b64encode(teacher['Image']).decode()}" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover;" alt="Teacher Image"/>
                    <p><strong>Email:</strong> {teacher['Email']}</p>
                    <p><strong>Phone:</strong> {teacher['Phone']}</p>
                    <p><strong>Qualification:</strong> {teacher['Qualification']}</p>
                    <p><strong>Gender:</strong> {teacher['Gender']}</p>
                    <p><strong>Date of Birth:</strong> {teacher['DOB']}</p>
                    <p><strong>Joining Date:</strong> {teacher['JoiningDate']}</p>
                    <p><strong>Name in Hindi:</strong> {teacher['NameInHindi']}</p>
                    <p><strong>Caste:</strong> {teacher['Caste']}</p>
                    <p><strong>Father's Name:</strong> {teacher['FatherName']}</p>
                    <p><strong>Mother's Name:</strong> {teacher['MotherName']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        teacher_id = st.experimental_get_query_params().get("teacher_id", None)
        if teacher_id:
            teacher_id = teacher_id[0]
            teacher = df[df['TeacherID'] == teacher_id].iloc[0]
            display_teacher_details(teacher)
        else:
            for i, teacher in df.iterrows():
                if i % 2 == 0:
                    with grid_col1:
                        display_teacher_card(teacher)
                else:
                    with grid_col2:
                        display_teacher_card(teacher)
    