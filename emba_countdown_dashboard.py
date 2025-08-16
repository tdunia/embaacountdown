
import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Toronto")

# Exclusion window (onsite) for weekends metric only
EXCLUDE_START = pd.Timestamp("2025-10-31").tz_localize(TZ)
EXCLUDE_END   = pd.Timestamp("2025-11-09").tz_localize(TZ)

st.set_page_config(page_title="EMBA CA26 Countdown Dashboard", layout="centered")
st.title("🎓 EMBA CA26 Countdown Dashboard")

@st.cache_data
def load_schedule():
    df = pd.read_csv("class_schedule.csv")
    df.columns = ["Date", "Course Info (AM)", "Course Info (PM)"]
    # Parse date and localize to TZ
    df["Full Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce").dt.tz_localize(TZ)
    df = df.dropna(subset=["Full Date"])
    return df

def normalize_name(name: str):
    if pd.isna(name):
        return None
    s = str(name).strip().lower()
    return re.sub(r"\s+", " ", s)

def extract_base_course(name: str):
    if pd.isna(name): 
        return None
    s = str(name).lower().strip()
    s = re.split(r"\s+\d+|[-–:]", s)[0]   # base course before numbers or dash/colon
    return re.sub(r"\s+", " ", s).strip()

df = load_schedule()
now = datetime.now(TZ)

# Determine last class day from "Strategies for Sustainability 3" if present
mask_sus3 = df["Course Info (AM)"].str.contains("Strategies for Sustainability 3", case=False, na=False) | \
            df["Course Info (PM)"].str.contains("Strategies for Sustainability 3", case=False, na=False)

if mask_sus3.any():
    last_class_day = df.loc[mask_sus3, "Full Date"].max()
else:
    last_class_day = df["Full Date"].max()

# Countdown targets end of that day (adjust time here if needed)
last_class_end = last_class_day.replace(hour=23, minute=59, second=59, microsecond=0)

# Upcoming rows from "now"
upcoming = df[df["Full Date"] >= now].copy()

# 1) Classes Left (unique names per day; duplicates at different times count once)
def classes_left_unique_names(frame: pd.DataFrame) -> int:
    total = 0
    for d, g in frame.groupby(frame["Full Date"].dt.date):
        names = pd.Series([
            *g["Course Info (AM)"].dropna().apply(normalize_name).tolist(),
            *g["Course Info (PM)"].dropna().apply(normalize_name).tolist()
        ])
        total += names.dropna().nunique()
    return int(total)

classes_left_program = classes_left_unique_names(upcoming)

# Also provide Classes Left to Dec 31 for convenience
end_of_year = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=0)
classes_left_eoy = classes_left_unique_names(upcoming[upcoming["Full Date"] <= end_of_year])

# 2) Class Weekends Left (exclude onsite window)
excluded = (upcoming["Full Date"] >= EXCLUDE_START) & (upcoming["Full Date"] <= EXCLUDE_END)
upcoming_for_weekends = upcoming[~excluded].copy()
upcoming_for_weekends["WeekPeriod"] = upcoming_for_weekends["Full Date"].dt.to_period("W")
weekends_left = int(upcoming_for_weekends["WeekPeriod"].nunique())

# 3) Courses Left (group by base course name across all remaining sessions)
base_am = df["Course Info (AM)"].apply(extract_base_course)
base_pm = df["Course Info (PM)"].apply(extract_base_course)
df["Base Course"] = base_am.combine_first(base_pm)
courses_left = int(df[df["Full Date"] >= now]["Base Course"].dropna().nunique())

# 4) Live countdown to last class day (HH:MM:SS)
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
c1.metric("🎓 Classes Left to Program End", classes_left_program)
c2.metric("🎓 Classes Left to Dec 31", classes_left_eoy)

c3, c4 = st.columns(2)
c3.metric("📆 Class Weekends Left", weekends_left)
c4.metric("⏳ Time Until LAST CLASS Day Ends", fmt_delta(last_class_end - now))

st.caption(f"Last class day: {last_class_day.strftime('%A, %B %d, %Y')} — Countdown targets 23:59:59 {TZ}.")

# Optional live countdown
live = st.checkbox("⏱️ Live countdown (updates every second)", value=True)
placeholder = st.empty()
if live:
    import time
    for _ in range(60*60):  # update up to 1 hour
        now = datetime.now(TZ)
        placeholder.metric("⏳ Time Until LAST CLASS Day Ends", fmt_delta(last_class_end - now))
        if (last_class_end - now).total_seconds() <= 0:
            break
        time.sleep(1)

with st.expander("📅 Upcoming Classes (Program End)"):
    st.dataframe(upcoming[["Full Date", "Course Info (AM)", "Course Info (PM)"]].sort_values("Full Date"), use_container_width=True)

with st.expander("📅 Weekends Counted (exclusions applied)"):
    st.dataframe(upcoming_for_weekends[["Full Date", "Course Info (AM)", "Course Info (PM)", "WeekPeriod"]].sort_values("Full Date"), use_container_width=True)
