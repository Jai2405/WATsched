# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# # Setup WebDriver
# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # Open the website
# driver.get("https://cs.uwaterloo.ca/cscf/teaching/schedule/expert")
# time.sleep(2)  # Wait for page to load

# # Switch to the "select" frame
# driver.switch_to.frame("select")


# subject_input = driver.find_element(By.NAME, "subject")
# subject_input.send_keys("CS")

# # Locate the "Course" input field and enter CS246
# course_input = driver.find_element(By.NAME, "cournum")
# course_input.send_keys("246")

# # Locate and click the "View Class Schedules" button
# view_button = driver.find_element(By.XPATH, "//input[@value='View Class Schedules']")
# view_button.click()



# # Switch to the "results" frame to extract the class schedule data
# driver.switch_to.default_content()  # Go back to the main page
# driver.switch_to.frame("results")

# # Extract the text from the results frame
# results_text = driver.find_element(By.TAG_NAME, "body").text
# print(results_text)  # Print the class schedule details

# # Wait before closing
# time.sleep(60)
# driver.quit()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the website
driver.get("https://cs.uwaterloo.ca/cscf/teaching/schedule/expert")
time.sleep(2)  # Wait for page to load

# Switch to the "select" frame
driver.switch_to.frame("select")

# Locate the "Course" input field and enter CS246
course_input = driver.find_element(By.NAME, "cournum")
course_input.send_keys("246")

# Locate and click the "View Class Schedules" button
view_button = driver.find_element(By.XPATH, "//input[@value='View Class Schedules']")
view_button.click()

# Wait for the results to load
time.sleep(3)

# Switch to the "results" frame
driver.switch_to.default_content()
driver.switch_to.frame("results")

# Locate the schedule table
table_rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

# Extract LEC and TUT timings
for row in table_rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) > 8:  # Ensure it's a valid row
        class_type = cells[1].text.strip()  # Get LEC/TUT
        if "LEC" in class_type or "TUT" in class_type:
            days_time = cells[9].text.strip()  # Get the Days/Time column
            print(f"{class_type}: {days_time}")

# Close the browser
time.sleep(5)
driver.quit()
