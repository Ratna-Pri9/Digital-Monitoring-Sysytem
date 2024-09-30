import sqlite3
import streamlit as st
from PIL import Image
import io
from config import db_path

# st.set_page_config(page_title="Profile Setting ", layout="wide")
# Function to load teacher data from the database
def main():

    def load_teacher_data(teacher_id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Teachers WHERE TeacherID = ?", (teacher_id,))
        teacher_data = cursor.fetchone()
        conn.close()
        return teacher_data
    
    # Function to update teacher data in the database
    def update_teacher_data(teacher_id, field, value):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE Teachers SET {field} = ? WHERE TeacherID = ?", (value, teacher_id))
        conn.commit()
        conn.close()
    
    # Function to reload the page to refresh data
    def reload_page():
        st.session_state.reload = True
    
    # Function to cancel edits
    def cancel_edits():
        st.session_state.edit_mode = False
        reload_page()
    
    # Connect to the database and fetch teacher IDs for the select box
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT TeacherID FROM Teachers")
    teacher_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Select box to choose teacher ID
    selected_teacher_id = st.session_state.user_id
    # Refresh button
    if st.button("Reload"):
        reload_page()
    
    
    # Load teacher data based on the selected ID
    if 'reload' not in st.session_state or st.session_state.reload:
        teacher_data = load_teacher_data(st.session_state.user_id)
        st.session_state.update(
            teacher_id = teacher_data[0],
            image_blob = teacher_data[1],
            first_name = teacher_data[2],
            middle_name = teacher_data[3],
            last_name = teacher_data[4],
            qualification = teacher_data[5],
            gender = teacher_data[6],
            phone = teacher_data[7],
            email = teacher_data[8],
            joining_date = teacher_data[9],
            status = teacher_data[10],
            name_in_hindi = teacher_data[11],
            caste = teacher_data[12],
            dob = teacher_data[13],
            father_name = teacher_data[14],
            mother_name = teacher_data[15],
        )
        st.session_state.reload = False
    
    # Unpack teacher data
    teacher_id = st.session_state.teacher_id
    image_blob = st.session_state.image_blob
    first_name = st.session_state.first_name
    middle_name = st.session_state.middle_name
    last_name = st.session_state.last_name
    qualification = st.session_state.qualification
    gender = st.session_state.gender
    phone = st.session_state.phone
    email = st.session_state.email
    joining_date = st.session_state.joining_date
    status = st.session_state.status
    name_in_hindi = st.session_state.name_in_hindi
    caste = st.session_state.caste
    dob = st.session_state.dob
    father_name = st.session_state.father_name
    mother_name = st.session_state.mother_name
    
    # Convert BLOB to image
    try:
        image = Image.open(io.BytesIO(image_blob))
    except Exception as e:
        st.error(f"Error loading image: {e}")
        image = None
    
    # Initialize session state for image size and edit mode
    if 'image_size' not in st.session_state:
        st.session_state.image_size = 100
    
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    
    # Layout of the teacher profile
    st.title("TEACHER PROFILE")
    
    
    
    # Slider to resize image
    st.session_state.image_size = 300
    
    with st.container(border=True):
        col1,col2=st.columns([1,3])
        with col1:
    # Profile Header
            if image:
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
    
    
         col1, col2 = st.columns(2)
    
         with col1:
             with st.container(border=True):
                st.write(f"**Teacher ID:** {teacher_id}")
                st.write(f"**Salary ID:** SKALOA45682")  # Placeholder value
                
    
         with col2:
             with st.container(border=True):
                st.write(f"**Highest Qualification:** {qualification}")
                st.write(f"**Date of Joining:** {joining_date}")
    
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
            name = st.text_input("Name", f"{first_name} {middle_name} {last_name}")
            name_in_hindi = st.text_input("Name in Hindi", name_in_hindi)
            # caste = st.selectbox("Caste", ["General", "OBC", "ST", "SC"], index=["General", "OBC", "ST", "SC"].index(caste))
    
        with col2:
            # gender = st.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(gender))
            dob = st.text_input("Date of Birth", dob)
    
        with col3:
            father_name = st.text_input("Father's Name", father_name)
            mother_name = st.text_input("Mother's Name", mother_name)
    
        address = st.text_input("Address", "Address not provided")  # Placeholder value
    
        # Image uploader
        uploaded_image = st.file_uploader("Upload New Image", type=["jpg", "jpeg", "png"])
    
        # Update and Cancel buttons
        if st.button("Update Profile"):
            update_teacher_data(teacher_id, "FirstName", name.split()[0])
            update_teacher_data(teacher_id, "MiddleName", name.split()[1] if len(name.split()) > 2 else "")
            update_teacher_data(teacher_id, "LastName", name.split()[-1])
            update_teacher_data(teacher_id, "NameInHindi", name_in_hindi)
            update_teacher_data(teacher_id, "Caste", caste)
            update_teacher_data(teacher_id, "Gender", gender)
            update_teacher_data(teacher_id, "DOB", dob)
            update_teacher_data(teacher_id, "FatherName", father_name)
            update_teacher_data(teacher_id, "MotherName", mother_name)
    
            if uploaded_image:
                image_bytes = uploaded_image.read()
                update_teacher_data(teacher_id, "Image", image_bytes)
    
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
    
    
            # col1,col2=st.columns(2)
            # with col1:
            #  with st.container(border=True):
            #     st.title("DOB")
            # with col2:
            #  with st.container(border=True): 
            #     st.write(f"{dob.strftime('%Y-%m-%d')}")
    
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
        
    
    
    