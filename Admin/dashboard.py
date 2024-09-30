import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator

# st.set_page_config(page_title="Dashboard ", layout="wide")


from .pages import Calander,Department,Notification,Students,Teachers
def main():
    page = st.sidebar.radio("", ["dashboard","Calander", "Department", "Notification", "Students", "Teachers"])
    if page == "dashboard":
        # Sample data for the graphs
        post_graduation_data = {
            'MCA': [85, 80, 75, 80],
            'MBA': [60, 70, 60, 85],
            'MSC.PHY': [58, 69, 60, 77],
            'MSC.MATH': [58, 59, 57, 54],
            'MSC.CHEM': [65, 87, 85, 85],
            'M.A -FD': [88, 98, 89, 97],
            'DPFM': [57, 69, 65, 69]
        }
        
        under_graduation_data = {
            'BSC.IT': [85, 80, 75, 80, 75, 80],
            'BBA': [60, 70, 60, 85, 70, 85],
            'BSC. CA': [58, 69, 60, 77, 69, 77],
            'BSC.MATH': [58, 59, 57, 54, 57, 59],
            'BIO TEC': [65, 87, 85, 85, 85, 87],
            'B.A -FD': [88, 98, 89, 97, 98, 89],
            'BA HINDI': [57, 69, 65, 69, 57, 65]
        }
        
        teachers_attendance = {
            'DIPTI PRASAD': 80,
            'ANUBHUTI SHRIWASTAVA': 80,
            'SONALI BENDRE': 95,
            'SONAKSHI SINHA': 87,
            'DR.R.R.SHARMA': 99,
            'SHIVNANDAN': 77,
            'DR. GHANSHYAM PRASAD': 85,
            'PROF. SHUBHANKAR': 89
        }
        
        # Function to create a bar chart
        def create_bar_chart(data, title, ylabel, xlabel, size=(10, 6)):
            fig, ax = plt.subplots(figsize=size)
            fig.patch.set_alpha(0)  # Make the figure background transparent
            ax.patch.set_alpha(0)   # Make the axes background transparent
            categories = list(data.keys())
            values = np.array(list(data.values())).T
            x = np.arange(len(categories)) * 1.5  # Increase spacing between categories
        
            for i, semester in enumerate(values):
                bars = ax.bar(x + i*0.2, semester, width=0.2, label=f'SEM {i+1}')
                # Annotate each bar with its value
                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center', color='white')
        
            ax.set_xlabel(xlabel, color='white')
            ax.set_ylabel(ylabel, color='white')
            ax.set_title(title, color='white')
            ax.set_xticks(x + 0.2)
            ax.xaxis.set_major_locator(FixedLocator(x + 0.2))
            ax.set_xticklabels(categories, rotation=45, color='white')
            ax.legend()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.title.set_color('white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.legend().get_frame().set_alpha(0)  # Make legend background transparent
            for text in ax.legend().get_texts():
                text.set_color('white')
            st.pyplot(fig)
        
        # Function to create a single bar chart
        def create_single_bar_chart(data, title, ylabel, xlabel, size=(10, 6)):
            fig, ax = plt.subplots(figsize=size)
            fig.patch.set_alpha(0)  # Make the figure background transparent
            ax.patch.set_alpha(0)   # Make the axes background transparent
            categories = list(data.keys())
            values = list(data.values())
        
            bars = ax.bar(categories, values)
            # Annotate each bar with its value
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center', color='white')
        
            ax.set_xlabel(xlabel, color='white')
            ax.set_ylabel(ylabel, color='white')
            ax.set_title(title, color='white')
            ax.set_xticks(np.arange(len(categories)))
            ax.xaxis.set_major_locator(FixedLocator(np.arange(len(categories))))
            ax.set_xticklabels(categories, rotation=45, color='white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.title.set_color('white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            st.pyplot(fig)
        
        # Function to create a pie chart
        def create_pie_chart(data, title, size=(8, 8)):
            fig, ax = plt.subplots(figsize=size)
            fig.patch.set_alpha(0)  # Make the figure background transparent
            ax.patch.set_alpha(0)   # Make the axes background transparent
            labels = list(data.keys())
            sizes = list(data.values())
            colors = plt.cm.Paired(np.arange(len(labels)))
        
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
            ax.set_title(title, color='white')
            for text in ax.texts:
                text.set_color('white')
            st.pyplot(fig)
        
        # Title of the dashboard
        st.title("Attendance Charts Dashboard")
        
        col1,col2=st.columns(2)
        with col1:
            # Display Post Graduation Attendance Chart
            st.header("Post Graduation Attendance Chart")
            create_bar_chart(post_graduation_data, 'Post Graduation Attendance', 'Attendance Percentage', 'Courses', size=(10, 8))
        
        with col2:
          # Display Under Graduation Attendance Chart
          st.header("Under Graduation Attendance Chart")
          create_bar_chart(under_graduation_data, 'Under Graduation Attendance', 'Attendance Percentage', 'Courses', size=(10, 8))
        
        # Display Teacher's Attendance Chart
        st.header("Teacher's Attendance Chart")
        create_single_bar_chart(teachers_attendance, "Teacher's Attendance", 'Attendance Percentage', 'Teachers', size=(10, 8))
        
        col1,col2=st.columns(2)
        with col1:
           # Display Pie Charts for each category
           st.header("Post Graduation Attendance Distribution")
           create_pie_chart({k: sum(v) for k, v in post_graduation_data.items()}, 'Post Graduation Attendance Distribution', size=(10, 10))
        with col2:
           st.header("Under Graduation Attendance Distribution")
           create_pie_chart({k: sum(v) for k, v in under_graduation_data.items()}, 'Under Graduation Attendance Distribution', size=(10, 10))
        
        st.header("Teacher's Attendance Distribution")
        create_pie_chart(teachers_attendance, "Teacher's Attendance Distribution", size=(5, 5))
    



    if page == "Calander":
        Calander.main()
    elif page == "Department":
        Department.main()
    elif page == "Notification":
        Notification.main()
    elif page == "Students":
        Students.main()
    elif page == "Teachers":
        Teachers.main()
   