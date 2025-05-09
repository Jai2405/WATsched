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
  - "days" (e.g., ["M", "W", "F"])

🧠 Task:
- Generate all possible full, non-conflicting schedules.
- Only include **complete** schedules that satisfy all course requirements.

📤 Output:
- Return **only** a JSON list of lists.
- Each inner list should include selected section names like:
  `["CS 136 LEC 001", "CS 136 TUT 101", "MATH 136 LEC 002"]`
- Do **not** include any explanation, formatting, or notes — just the raw JSON.

✅ Example input:
{{
  "CS 136": [
    {{"section": "LEC 001", "time": "10:00-11:20", "days": ["M", "W"]}},
    {{"section": "TUT 101", "time": "11:30-12:20", "days": ["F"]}}
  ],
  "MATH 136": [
    {{"section": "LEC 001", "time": "09:00-10:00", "days": ["T", "TH"]}},
    {{"section": "TUT 102", "time": "10:30-11:20", "days": ["W"]}}
  ]
}}

✅ Example valid output:
[
  ["CS 136 LEC 001", "CS 136 TUT 101", "MATH 136 LEC 001", "MATH 136 TUT 102"]
]

---

Now here is the input:
{schedule_json}

IMPORTANT: Do not say anything else. Only return the raw JSON list. Do not include phrases like "Here is the list" or any extra text.

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
                    schedules.append({
                        "section": f"{class_type} {section}",
                        "time": time_str,
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

def main():
    total_schedules = {}
    while True:
        subject = input("Enter subject (e.g., CS) or 'q' to quit: ").strip()
        if subject.lower() == 'q':
            break

        course_number = input("Enter course number (e.g., 246): ").strip()
        scraper = CourseScheduleScraper(subject, course_number)
        schedules = scraper.scrape_schedule()

        key = f"{subject.upper()} {course_number}"
        if schedules:
            total_schedules[key] = schedules
            print(json.dumps(schedules, indent=2))
        else:
            print(f"No schedules found for {key}")

    print("\nTOTAL RESULTS:")
    print(json.dumps(total_schedules, indent=2))
    print("\nTOTAL PERMUTATIONS:")
    print(generate_schedule_with_groq(total_schedules))



    

if __name__ == "__main__":
    main()



