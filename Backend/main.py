from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import re
import json
import time

def split_days(day_str):
    day_str = day_str.upper()
    days = []
    i = 0
    while i < len(day_str):
        if day_str[i] == 'T' and i + 1 < len(day_str) and day_str[i + 1] == 'H':
            days.append('TH')
            i += 2
        else:
            days.append(day_str[i])
            i += 1
    return days



from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_schedule_with_groq(schedule_data):
    schedule_json = json.dumps(schedule_data, indent=2)

    prompt = f"""
You are a university class scheduling assistant. Your job is to generate all possible valid, non-conflicting schedules based on course offerings.

📌 Rules:
- Each course may have multiple LEC (lecture) and TUT (tutorial) sections.
- If a course has both LECs and TUTs, a valid schedule **must include one LEC and one TUT**.
- If a course only has LECs, include exactly one LEC.
- ❗ Do not include schedules that are missing a required LEC or TUT.
- No two selected classes can overlap in time on any day.

📥 Input:
You will receive a dictionary where:
- Keys are course names.
- Values are lists of sections.
- Each section has:
  - "section" (e.g., "LEC 001", "TUT 101")
  - "time" (e.g., "10:30-11:50")
  - "start" (e.g., "10:30")
  - "end" (e.g., "11:50")
  - "days" (e.g., ["M", "W", "F"])

🧠 Task:
- Generate all possible full, non-conflicting schedules.
- Only include **complete** schedules that satisfy all course requirements.
- Each valid schedule should be returned as a list of class **objects** with:
  - "course" (e.g., "CS 136")
  - "section" (e.g., "LEC 001")
  - "start" (e.g., "10:30")
  - "end" (e.g., "11:50")
  - "days" (e.g., ["M", "W"])

📤 Output:
Return only a JSON list of lists.
Each inner list represents one valid schedule and contains objects like:

[
  [
    {{
      "course": "CS 136",
      "section": "LEC 001",
      "start": "10:00",
      "end": "11:20",
      "days": ["M", "W"]
    }},
    {{
      "course": "CS 136",
      "section": "TUT 101",
      "start": "11:30",
      "end": "12:20",
      "days": ["F"]
    }},
    {{
      "course": "MATH 136",
      "section": "LEC 001",
      "start": "09:00",
      "end": "10:00",
      "days": ["T", "TH"]
    }},
    {{
      "course": "MATH 136",
      "section": "TUT 102",
      "start": "10:30",
      "end": "11:20",
      "days": ["W"]
    }}
  ]
]

---

Here is the input:
{schedule_json}

IMPORTANT: Do not say anything else. Return **only** the raw JSON list of lists with the structure shown above.
"""



    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
        stream=False,
    )

    return chat_completion.choices[0].message.content




class CourseScheduleScraper:
    def __init__(self, subject, course_number):
        self.subject = subject.strip()
        self.course_number = course_number.strip()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_schedule(self):
        try:
            self.driver.get("https://cs.uwaterloo.ca/cscf/teaching/schedule/expert")
            self.wait.until(EC.frame_to_be_available_and_switch_to_it("select"))

            # Select subject from dropdown
            dropdown = Select(self.wait.until(EC.presence_of_element_located((By.NAME, "subject"))))
            subject_normalized = self.subject.lower()
            match = next((opt.text for opt in dropdown.options if opt.text.strip().lower().startswith(subject_normalized)), None)

            if not match:
                print(f"❌ Could not find subject '{self.subject}' in dropdown.")
                return []

            dropdown.select_by_visible_text(match)

            # Enter course number
            course_input = self.wait.until(EC.presence_of_element_located((By.NAME, "cournum")))
            course_input.clear()
            course_input.send_keys(self.course_number)

            # Submit form
            view_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='View Class Schedules']")))
            view_btn.click()

            # Switch to results frame
            self.driver.switch_to.default_content()
            self.wait.until(EC.frame_to_be_available_and_switch_to_it("results"))
            time.sleep(2)

            # Get and parse content
            content = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
            class_pattern = r'(LEC|TUT) (\d{3}).*?(\d{1,2}:\d{2}-\d{1,2}:\d{2})([A-Za-z,]+)'
            matches = re.finditer(class_pattern, content)

            schedules = []
            for match in matches:
                class_type, section, time_str, days = match.groups()
                if not time_str.startswith('Reserve'):
                    start_time, end_time = time_str.split("-")
                    schedules.append({
                        "section": f"{class_type} {section}",
                        "time": time_str,
                        "start": start_time,
                        "end": end_time,
                        "days": split_days(days.strip())
                    })

            print(f"\n✅ Results for {self.subject.upper()} {self.course_number} loaded:")
            print(content)
            return schedules

        except Exception as e:
            print(f"Error: {str(e)}")
            return []
        finally:
            self.cleanup()

    def cleanup(self):
        if self.driver:
            self.driver.quit()








from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (React) to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 👈 Match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Courses(BaseModel):
    courses: List[str]


@app.post("/generate")
def root(courses: Courses):
    all_courses = []
    for i in courses.courses:
        all_courses.append(i.split())
    print(all_courses)

    total_schedules = {}
    for i in all_courses:
        subject = i[0]
        course_number = i[1]
        scraper = CourseScheduleScraper(subject, course_number)
        schedules = scraper.scrape_schedule()

        key = f"{subject.upper()} {course_number}"
        if schedules:
            total_schedules[key] = schedules
            print(json.dumps(schedules, indent=2))
        else:
            print(f"No schedules found for {key}")

    # print("\nTOTAL RESULTS:")
    # print(json.dumps(total_schedules, indent=2))
    # print("\nTOTAL PERMUTATIONS:")
    all_schedules = generate_schedule_with_groq(total_schedules)
    print("ALL SCEHDULES ",all_schedules)
    return {"schedules": all_schedules}

