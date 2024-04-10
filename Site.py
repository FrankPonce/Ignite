import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import openai
from ratemyprof_api import RateMyProfApi



# Set your OpenAI API key here
openai.api_key = 'your_openai_api_key'


def analyze_reviews_with_openai(reviews):
    """
    This function takes a list of reviews and uses OpenAI's API to generate insights.
    For simplicity, we're assuming a single text response from OpenAI.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",  # You might want to use the latest available model
        prompt="Provide insights based on these professor reviews: " + " ".join(reviews),
        temperature=0.7,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()


# Assuming your API is correctly set up and callable
rate_my_prof_api = RateMyProfApi(school_id="18445")  # FIU's School ID

st.title("Professor and Class Finder")

# Get the list of departments
departments = rate_my_prof_api.get_departments()
selected_dept = st.selectbox("Select Department", departments)

# Mock preferences
preferences = {
    "No Homework": False,
    "Exam Curves": True,
    "Quality > 4": True,
    "75% Would Take Again": True,
    "More Than 10 Reviews": True
}

# Display checkboxes for preferences
for pref in preferences:
    preferences[pref] = st.checkbox(pref, value=preferences[pref])

if st.button("Find Professors"):
    # Here you would fetch professors based on selected_dept and preferences
    # This is a placeholder to demonstrate the process
    professors = rate_my_prof_api.get_professors(selected_dept, preferences)  # You need to implement this method

    if not professors:
        st.write("No professors found matching your criteria.")
    else:
        for professor in professors:
            # Assuming professor object has a list of reviews
            reviews = professor.get_reviews()  # You need to implement this method

            # Generate insights from reviews using OpenAI
            insights = analyze_reviews_with_openai(reviews)

            # Displaying professor info and insights
            st.subheader(professor.name)
            st.write(f"Rating: {professor.overall_rating}")
            st.write(f"Insights: {insights}")
