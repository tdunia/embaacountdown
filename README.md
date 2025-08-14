
# EMBA CA26 Countdown Dashboard (Streamlit, Static Data)

This app reads the bundled **class_schedule.csv** (no upload required) and shows:
- 🎓 Classes Left (until Dec 31 of the current year)
- 📆 Class Weekends Left
- 📚 Courses Left (grouped by base course name)
- ⏳ Live countdown (days/hours/minutes/seconds) to end of the last class day

## Files
- `emba_countdown_dashboard.py` — Streamlit application
- `class_schedule.csv` — Static class schedule
- `requirements.txt` — Python dependencies

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud
1. Push these files to a **public GitHub repo** (e.g., `emba-countdown-dashboard`).
2. Go to https://streamlit.io/cloud → **New app**.
3. Select your repo, branch `main`, and set main file path to `app.py`.
4. Deploy.

## CSV format
The app expects `class_schedule.csv` with three columns:
```
Date,Course Info (AM),Course Info (PM)
2025-09-06,Some Course 1,Some Course 2
...
```
Dates must be `YYYY-MM-DD`. Times are interpreted in `America/Toronto` timezone, and the countdown targets **23:59:59** on the final class date.
