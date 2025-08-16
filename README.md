
# EMBA CA26 Countdown Dashboard (Static Data)

This Streamlit app reads the bundled `class_schedule.csv` (no upload needed) and shows:
- 🎓 **Classes Left (unique names, per day)** to Program End and to Dec 31
- 📆 **Class Weekends Left** (excludes onsite window Oct 31–Nov 9, 2025)
- 📚 **Courses Left** (grouped by base course name)
- ⏳ **Live countdown** (days/hours/minutes/seconds) to the last class day
  - The last class day is taken from **"Strategies for Sustainability 3"**, if present; otherwise the latest date in the file.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud
1. Create a public GitHub repo and upload: `app.py`, `class_schedule.csv`, `requirements.txt`, `README.md`.
2. On https://streamlit.io/cloud → New app → select the repo.
3. Set main file path to `app.py` → Deploy.

## CSV Format
`class_schedule.csv` must have columns:
```
Date,Course Info (AM),Course Info (PM)
YYYY-MM-DD,Title A,Title B
```
Dates must be `YYYY-MM-DD`. Times and countdown use **America/Toronto** timezone.
