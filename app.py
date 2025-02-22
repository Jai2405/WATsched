from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import re
import json

def split_days(day_str):
    day_str = day_str.upper()  # Convert to uppercase for consistency
    days = []
    i = 0
    
    while i < len(day_str):
        if day_str[i] == 'T' and i + 1 < len(day_str) and day_str[i + 1] == 'H':
            days.append('TH')
            i += 2  # Skip 'TH'
        else:
            days.append(day_str[i])
            i += 1
    
    return days

class CourseScheduleScraper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        self.wait = WebDriverWait(self.driver, 10)
        
    def scrape_schedule(self, course_number):
        try:
            # Open the website and navigate
            self.driver.get("https://cs.uwaterloo.ca/cscf/teaching/schedule/expert")
            self.wait.until(EC.frame_to_be_available_and_switch_to_it("select"))
            
            # Enter course number and submit
            course_input = self.wait.until(EC.presence_of_element_located((By.NAME, "cournum")))
            course_input.clear()
            course_input.send_keys(course_number)
            view_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='View Class Schedules']"))
            )
            view_button.click()
            
            # Switch to results frame and get content
            self.driver.switch_to.default_content()
            self.wait.until(EC.frame_to_be_available_and_switch_to_it("results"))
            
            # Get the entire text content
            content = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
            
            # Extract both LEC and TUT sections using regex
            class_pattern = r'(LEC|TUT) (\d{3}).*?(\d{1,2}:\d{2}-\d{1,2}:\d{2})([A-Za-z,]+)'
            matches = re.finditer(class_pattern, content)
            
            schedules = []
            for match in matches:
                class_type, section, time, days = match.groups()
                if not time.startswith('Reserve'):  # Skip reserve sections
                    schedules.append({
                        "section": f"{class_type} {section}",
                        "time": time,
                        "days": split_days(days.strip())
                    })
            
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
        course_number = input("Enter course number (e.g., 246): ")
        if course_number == "q":
            break
            
        # Create a new scraper for each course
        scraper = CourseScheduleScraper()
        schedules = scraper.scrape_schedule(course_number)
        
        if schedules:
            total_schedules[course_number] = schedules
            print(json.dumps(schedules, indent=2))
        else:
            print(f"No schedules found for CS {course_number}")
    
    print("TOTAL:", json.dumps(total_schedules, indent=2))

if __name__ == "__main__":
    main()