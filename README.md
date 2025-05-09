# WatSched
AI-powered class schedule generator for UW students
 
WATsched is a university class scheduler that generates all possible **non-conflicting schedules** based on selected courses at the University of Waterloo.

## Tech Stack
- **Frontend:** Next.js
- **Backend:** FastAPI
- **Automation & Scraping:** Selenium
- **AI Scheduling Engine:** Groq API

## How It Works
1. User enters course names (e.g., `CS 136`, `MATH 135`).
2. Selenium scrapes schedule data from the University of Waterloo website.
3. The backend sends this data to the Groq API with a custom prompt to generate valid class schedules.
4. The frontend displays all possible non-overlapping schedule combinations.
