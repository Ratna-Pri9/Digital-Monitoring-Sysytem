import sqlite3
import streamlit as st
from PIL import Image, ImageDraw
import io
from datetime import datetime
from config import db_path

def main():
    # Initialize session state attributes
    session_state_defaults = {
        "student_id": None,
        "image_blob": None,
        "first_name": "",
        "middle_name": "",
        "last_name": "",
        "roll_no": "",
        "reg_no": "",
        "department_name": "",
        "course_name": "",
        "admission_date": "",
        "name_in_hindi": "",
        "caste": "General",
        "dob": datetime.today(),
        "gender": "Male",
        "father_name": "",
        "mother_name": "",
        "phone": "",
        "email": "",
        "session": "",
        "image_size": 100,
        "edit_mode": False,
        "reload": False
    }
    
    for key, value in session_state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Function to load student data from the database
    def load_student_data(student_id):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, d.Name AS DepartmentName, c.Name AS CourseName
                FROM Students s
                JOIN Departments d ON s.DepartmentID = d.DepartmentID
                JOIN Courses c ON s.CourseID = c.CourseID
                WHERE StudentID = ?
            """, (student_id,))
            student_data = cursor.fetchone()
            conn.close()
            return student_data
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            return None
    
    # Function to update student data in the database
    def update_student_data(student_id, field, value):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"UPDATE Students SET {field} = ? WHERE StudentID = ?", (value, student_id))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
    
    # Function to reload the page to refresh data
    def reload_page():
        st.session_state.reload = True
    
    # Function to cancel edits
    def cancel_edits():
        st.session_state.edit_mode = False
        reload_page()
    
    # Connect to the database and fetch student IDs for the select box
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT StudentID FROM Students")
        student_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        student_ids = []
    
    # Default student ID
    default_student_id = 'STU961527236'
    
    # Determine the index of the default value in the list
    default_index = student_ids.index(default_student_id) if default_student_id in student_ids else 0
    
    # Select box to choose student ID with the default value set
    selected_student_id = st.session_state.user_id

    
    # Load student data based on the selected ID
    if st.session_state.reload or st.session_state.student_id is None or selected_student_id != st.session_state.student_id:
        student_data = load_student_data(selected_student_id)
        if student_data:
            try:
                dob = datetime.strptime(student_data[12], '%Y-%m-%d').date() if student_data[12] else datetime.today().date()
            except ValueError:
                dob = datetime.today().date()
            
            st.session_state.update(
                student_id = student_data[0],
                image_blob = student_data[1],
                first_name = student_data[2],
                middle_name = student_data[3],
                last_name = student_data[4],
                roll_no = student_data[5],
                reg_no = student_data[6],
                department_id = student_data[7],
                course_id = student_data[8],
                admission_date = student_data[9],
                name_in_hindi = student_data[10],
                caste = student_data[11] if student_data[11] in ["General", "OBC", "ST", "SC"] else "General",
                dob = dob,
                gender = student_data[13] if student_data[13] in ["Male", "Female"] else "Male",
                father_name = student_data[14],
                mother_name = student_data[15],
                phone = student_data[16],
                email = student_data[17],
                session = student_data[18],
                department_name = student_data[19],
                course_name = student_data[20]
            )
        else:
            st.error("No data found for the selected student ID.")
        st.session_state.reload = False
    
    # Unpack student data
    student_id = st.session_state.student_id
    image_blob = st.session_state.image_blob
    first_name = st.session_state.first_name
    middle_name = st.session_state.middle_name
    last_name = st.session_state.last_name
    roll_no = st.session_state.roll_no
    reg_no = st.session_state.reg_no
    department_name = st.session_state.department_name
    course_name = st.session_state.course_name
    admission_date = st.session_state.admission_date
    name_in_hindi = st.session_state.name_in_hindi
    caste = st.session_state.caste
    dob = st.session_state.dob
    gender = st.session_state.gender
    father_name = st.session_state.father_name
    mother_name = st.session_state.mother_name
    phone = st.session_state.phone
    email = st.session_state.email
    session = st.session_state.session
    
    # Convert BLOB to image
    def get_image_from_blob(blob):
        try:
            if blob:
                return Image.open(io.BytesIO(blob))
            else:
                return None
        except Exception as e:
            st.error(f"Error loading image: {e}")
            return None
    
    # Create a placeholder image
    def create_placeholder_image():
        image = Image.new("RGB", (200, 200), color=(73, 109, 137))
        draw = ImageDraw.Draw(image)
        draw.text((50, 90), "No Image", fill=(255, 255, 255))
        return image
    
    image = get_image_from_blob(image_blob) or create_placeholder_image()
    
    # Layout of the student profile
    st.title("STUDENT PROFILE")
    
    
    
    # Slider to resize image
    # st.session_state.image_size = st.slider("Resize image", 50, 300, st.session_state.image_size)
    st.session_state.image_size =300
    
    
    with st.container(border=True):
      col1,col2=st.columns([1,3])
      with col1:
       st.image(image, width=st.session_state.image_size)
      
      with col2:
         st.title(f"{first_name} {middle_name} {last_name}")
         # Display Profile Information
         col1,col2,col3=st.columns(3)
         with col1:
          st.write(f"**:calendar:** {dob}")
         with col2:
          st.write(f"**:telephone_receiver:** {phone}")
         with col3:
          st.write(f"**:email:** {email}")
      
      
         
         # Columns for additional information
         col1, col2 = st.columns(2)
         
         with col1:
             with st.container(border=True):
              st.write(f"**Student ID:** {student_id}")
              st.write(f"**Roll No:** {roll_no}")
              st.write(f"**Registration No:** {reg_no}")
             
         
         with col2:
             with st.container(border=True):
              st.write(f"**Course:** {course_name}")
              st.write(f"**Department:** {department_name}")
              st.write(f"**Date of Admission:** {admission_date}")
    
    with st.container(border=True): 
     col1,col2,col3,=st.columns([3,5,1])
     with col1: 
       # Profile Details
       st.subheader("Profile Details")
     with col3:
     # Edit button
      if st.button("Edit"):
         st.session_state.edit_mode = True
       
    if st.session_state.edit_mode:
        col1, col2, col3 = st.columns(3)
    
        with col1:
            first_name = st.text_input("First Name", first_name)
            middle_name = st.text_input("Middle Name", middle_name)
            last_name = st.text_input("Last Name", last_name)
            name_in_hindi = st.text_input("Name in Hindi", name_in_hindi)
            caste = st.selectbox("Caste", ["General", "OBC", "ST", "SC"], index=["General", "OBC", "ST", "SC"].index(caste))
    
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(gender))
            dob = st.date_input("Date of Birth", dob)
    
        with col3:
            father_name = st.text_input("Father's Name", father_name)
            mother_name = st.text_input("Mother's Name", mother_name)
            phone = st.text_input("Phone", phone)
            email = st.text_input("Email", email)
    
       
        
    
        # Image uploader
        uploaded_image = st.file_uploader("Upload New Image", type=["jpg", "jpeg", "png"])
    
        # Update and Cancel buttons
        if st.button("Update Profile"):
            update_student_data(student_id, "FirstName", first_name)
            update_student_data(student_id, "MiddleName", middle_name)
            update_student_data(student_id, "LastName", last_name)
            update_student_data(student_id, "NameInHindi", name_in_hindi)
            update_student_data(student_id, "Caste", caste)
            update_student_data(student_id, "Gender", gender)
            update_student_data(student_id, "DOB", dob.strftime('%Y-%m-%d'))
            update_student_data(student_id, "FatherName", father_name)
            update_student_data(student_id, "MotherName", mother_name)
            update_student_data(student_id, "Phone", phone)
            update_student_data(student_id, "Email", email)
    
            if uploaded_image:
                image_bytes = uploaded_image.read()
                update_student_data(student_id, "Image", image_bytes)
    
            st.success("Profile updated successfully!")
            st.session_state.edit_mode = False
            reload_page()
        
        if st.button("Cancel"):
            cancel_edits()
    else:
        with st.container(border=True):
            col1,col2=st.columns(2)
            with col1:
             with st.container(border=True):
                st.title("Name")
              
            with col2:
             with st.container(border=True):  
                st.header(f"{first_name} {middle_name} {last_name}")
    
            col1,col2=st.columns(2)
            with col1:
             with st.container(border=True):
                st.title("Name in Hindi ")
            with col2:
             with st.container(border=True):
                st.write(f"{name_in_hindi}")
    
            col1,col2=st.columns(2)
            with col1:
             with st.container(border=True):
                st.title("Caste")
            with col2:
             with st.container(border=True): 
                st.write(f"{caste}")
    
    
            col1,col2=st.columns(2)
            with col1:
             with st.container(border=True):
                st.title("Gender")
            with col2:
             with st.container(border=True): 
              st.write(f"{gender}")
    
    
            col1,col2=st.columns(2)
            with col1:
             with st.container(border=True):
                st.title("DOB")
            with col2:
             with st.container(border=True): 
                st.write(f"{dob.strftime('%Y-%m-%d')}")
    
            col1,col2=st.columns(2)
            with col1:
             with st.container(border=True):
                st.title("Father's Name")
            with col2:
             with st.container(border=True): 
              st.write(f"{father_name}")
    
            col1,col2=st.columns(2)
            with col1:
             with st.container(border=True):
                st.title("Mother's Name")
            with col2:
             with st.container(border=True): 
                st.write(f" {mother_name}")
        
    
    # Refresh button
    if st.button("Refresh"):
        reload_page()
    
    
    
    
        