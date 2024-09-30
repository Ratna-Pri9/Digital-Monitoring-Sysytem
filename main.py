import streamlit as st
from Login import Login1
from Student import Timetracker as StudentTimetracker
# from Teacher import Timetracker as TeacherTimetracker
# from Admin import dashboard as AdminDashboard

st.set_page_config(layout="wide")


PAGES = {
    "Student": StudentTimetracker,
#     "Teacher": TeacherTimetracker,
#     "Admin": AdminDashboard,
}

def main():
   
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_type = None

    if not st.session_state.authenticated:
        Login1.main()
    else:
        # Redirect based on user type
        user_type = st.session_state.user_type
        if user_type and user_type in PAGES:
            page = PAGES[user_type]
            st.sidebar.write(f"Logged in as: {st.session_state.user_id} ({user_type})")
            page.main()
        else:
            st.error("Invalid user type or no page found")

        # Display logout button
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_type = None
            st.experimental_rerun()  # Refresh to navigate to the login page

if __name__ == "__main__":
    main()
