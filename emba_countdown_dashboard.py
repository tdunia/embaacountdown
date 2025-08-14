
import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Toronto")

st.set_page_config(page_title="EMBA CA26 Countdown Dashboard", layout="centered")
st.title("🎓 EMBA CA26 Countdown Dashboard")

@st.cache_data
def load_schedule():
    df = pd.read_csv("class_schedule.csv")
    df.columns = ["Date", "Course Info (AM)", "Course Info (PM)"]
    # Parse date as local midnight
    df["Full Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce").dt.tz_localize(TZ)
    df = df.dropna(subset=["Full Date"])
    return df

def extract_base_course(name: str):
    if pd.isna(name): 
        return None
    s = name.lower().strip()
    # split at first number or dash/colon
    s = re.split(r"\s+\d+|[-–:]", s)[0]
    return s.strip()

df = load_schedule()

now = datetime.now(TZ)

# Last class date (assume countdown to END of that day, 23:59:59 local)
last_class_day = df["Full Date"].max()
last_class_end = last_class_day.replace(hour=23, minute=59, second=59, microsecond=0)

# === Metrics ===
# 1) Classes left UNTIL END OF THIS YEAR
end_of_year = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=0)
classes_left_eoy = df[(df["Full Date"] >= now) & (df["Full Date"] <= end_of_year)].shape[0]

# 2) Class weekends left (for all remaining classes to program end)
df["WeekPeriod"] = df["Full Date"].dt.to_period("W")
weekends_left = df[df["Full Date"] >= now]["WeekPeriod"].nunique()

# 3) Courses left (group by base course name for remaining classes)
base_am = df["Course Info (AM)"].apply(extract_base_course)
base_pm = df["Course Info (PM)"].apply(extract_base_course)
df["Base Course"] = base_am.combine_first(base_pm)
courses_left = df[df["Full Date"] >= now]["Base Course"].dropna().nunique()

# 4) Live countdown to last class end-of-day
def fmt_delta(delta: timedelta):
    if delta.total_seconds() < 0:
        return "🎉 Completed"
    secs = int(delta.total_seconds())
    days = secs // 86400
    secs %= 86400
    hours = secs // 3600
    secs %= 3600
    minutes = secs // 60
    seconds = secs % 60
    return f"{days}d {hours}h {minutes}m {seconds}s"

st.subheader("📊 Countdown Summary")

c1, c2 = st.columns(2)
c1.metric("🎓 Classes Left (to Dec 31)", classes_left_eoy)
c2.metric("📆 Class Weekends Left", weekends_left)

c3, c4 = st.columns(2)
c3.metric("📚 Courses Left", courses_left)

# Live countdown
count_placeholder = c4.empty()

# Checkbox to enable/disable live ticking
live = st.checkbox("⏱️ Live countdown (updates every second)", value=True)

# Draw once first
count_placeholder.metric("⏳ Time Until Last Class Day Ends", fmt_delta(last_class_end - now))

if live:
    import time
    # Update for up to 12 hours or until event passes (session-level)
    for _ in range(60 * 60 * 12):
        now = datetime.now(TZ)
        remaining = last_class_end - now
        count_placeholder.metric("⏳ Time Until Last Class Day Ends", fmt_delta(remaining))
        if remaining.total_seconds() <= 0:
            break
        time.sleep(1)

with st.expander("📅 Upcoming Classes"):
    upcoming = df[df["Full Date"] >= now][["Full Date", "Course Info (AM)", "Course Info (PM)"]].sort_values("Full Date")
    st.dataframe(upcoming, use_container_width=True)

st.caption("Times shown in America/Toronto time. 'Classes Left' counts sessions through Dec 31 of the current year.")
