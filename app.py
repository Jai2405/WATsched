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

    prompt = ("""
You are a university class scheduler assistant. Your job is to create all possible non-conflicting schedules based on course offerings.

Rules:
- Each course may have multiple lectures (LECs) and tutorials (TUTs).
- If a course offers both LECs and TUTs, one LEC and one TUT must be selected together.
- If a course offers only LECs, selecting just one LEC is sufficient.
- No two selected classes may overlap in time on any day.

Input:
- You will receive a dictionary where keys are course names and values are lists of class options.
- Each class option has a "section" name (e.g., "LEC 001" or "TUT 102"), a "time" string (e.g., "11:30-12:50"), and a list of days (e.g., ["M", "W", "F"]).

Task:
- Generate all possible full schedules.
- A full schedule must pick exactly one LEC (and one TUT if required) for each course.
- Do not include partial schedules (missing LEC or required TUT).
- Ensure no classes overlap in timing.

Output:
- Return all valid schedules as a list of lists.
- Each schedule is a list of sections (e.g., ["CS 246 LEC 001", "CS 246 TUT 102", "MATH 239 LEC 001"]).

Examples:
- If no possible schedule exists for some course combinations, exclude them from the output.
- Minimize redundancy in your answer.

Now, here is the input:
{your_total_schedules_here}

    """)

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
    print(generate_schedule_with_groq(total_schedules))



    

if __name__ == "__main__":
    main()



