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


## ⚙️ Setup Instructions

```bash
# 1. Clone the repo
git clone https://github.com/JAI2405/WATsched.git
cd WATsched

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in the root with:
# GROQ_API_KEY=your_api_key_here

# 5. Run the app
python app.py
