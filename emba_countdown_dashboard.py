
import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="EMBA Countdown Dashboard", layout="centered")
st.title("🎓 EMBA CA26 Countdown Dashboard")

uploaded_file = st.file_uploader("📂 Upload the latest class schedule (CSV format)", type="csv")

if uploaded_file:
    # Load data
    df = pd.read_csv(uploaded_file)

    # Rename expected columns
    df.columns = ['Date', 'Course Info (AM)', 'Course Info (PM)']
    df['Full Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d", errors='coerce')
    df = df.dropna(subset=['Full Date'])

    today = pd.to_datetime(datetime.today().date())

    # Filter upcoming classes
    upcoming_df = df[df['Full Date'] >= today]

    # 🎓 Classes Left
    classes_left = upcoming_df.shape[0]

    # 📆 Class Weekends Left
    df['Weekend'] = df['Full Date'].dt.to_period('W')
    weekends_left = upcoming_df['Full Date'].dt.to_period('W').nunique()

    # 📚 Courses Left (grouped by base name)
    def extract_base_course(name):
        if pd.isna(name): return None
        name = name.lower().strip()
        name = re.split(r'\s+\d+|[-–:]', name)[0]
        return name.strip()

    base_am = df['Course Info (AM)'].apply(extract_base_course)
    base_pm = df['Course Info (PM)'].apply(extract_base_course)
    df['Base Course'] = base_am.combine_first(base_pm)
    future_courses = df[df['Full Date'] >= today]['Base Course'].dropna().unique()
    courses_left = len(future_courses)

    # ⏳ Days Until Last Class
    last_class_day = df['Full Date'].max()
    days_until_last_class = (last_class_day - today).days

    # Display metrics
    st.subheader("📊 Countdown Summary")
    col1, col2 = st.columns(2)
    col1.metric("🎓 Classes Left", classes_left)
    col2.metric("📆 Class Weekends Left", weekends_left)

    col3, col4 = st.columns(2)
    col3.metric("📚 Courses Left", courses_left)
    col4.metric("⏳ Days Until Last Class", f"{days_until_last_class} days")

    with st.expander("📅 View Upcoming Classes"):
        st.dataframe(upcoming_df[['Full Date', 'Course Info (AM)', 'Course Info (PM)']])
else:
    st.info("Upload your class schedule CSV to begin.")
