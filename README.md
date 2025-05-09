# WatSched
AI-powered class schedule generator for UW students
 
WATsched is a university class scheduler that generates all possible **non-conflicting schedules** based on selected courses at the University of Waterloo.

## 🚀 Features

- Input course data via dictionary format
- Automatically considers LECs and TUTs
- Ensures no overlapping classes on any day
- Returns all valid full schedules (LEC + TUT if required)
- Uses Groq API + Python backend

## 🧠 How It Works

1. You input a dictionary of courses with available sections (LECs/TUTs).
2. The system generates all valid schedule combinations using a prompt sent to Groq.
3. The output is a JSON list of all full, non-conflicting schedules.

## 🛠️ Tech Stack

- Python (Flask backend)
- Groq API (Generative AI scheduling)
- HTML/CSS/JS (for frontend)

## 📦 Example Input Format

```json
{
  "CS 246": [
    { "section": "LEC 001", "time": "11:30-12:50", "days": ["M", "W", "F"] },
    { "section": "TUT 102", "time": "14:30-15:20", "days": ["F"] }
  ],
  "MATH 239": [
    { "section": "LEC 001", "time": "13:00-14:20", "days": ["T", "Th"] }
  ]
}
