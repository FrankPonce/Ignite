from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Set up the Selenium WebDriver
driver = webdriver.Chrome('/path/to/chromedriver')

# Navigate to the RateMyProfessors listing for the university
driver.get('https://www.ratemyprofessors.com/search/professors/18445?q=*')

# Wait for the page to load and for the list of professors to appear
professors_list = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'CSS_SELECTOR_FOR_PROFESSOR_LIST'))
)

# Get a list of all professors on the page
professors = driver.find_elements(By.CSS_SELECTOR, 'CSS_SELECTOR_FOR_INDIVIDUAL_PROFESSORS')

# Loop through each professor and scrape their data
for professor in professors:
    # Click the professor's link to navigate to their profile page
    professor.find_element(By.CSS_SELECTOR, 'CSS_SELECTOR_FOR_PROFESSOR_LINK').click()

    # Wait for the professor's page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'CSS_SELECTOR_FOR_REVIEWS_SECTION'))
    )

    # Scrape the data you need, similar to how you would with the API
    professor_data = {
        'name': driver.find_element(By.CSS_SELECTOR, 'CSS_SELECTOR_FOR_NAME').text,
        'quality_rating': driver.find_element(By.CSS_SELECTOR, 'CSS_SELECTOR_FOR_QUALITY_RATING').text,
        # ... other fields ...
    }

    # Scrape the reviews
    reviews = driver.find_elements(By.CSS_SELECTOR, 'CSS_SELECTOR_FOR_INDIVIDUAL_REVIEWS')
    for review in reviews:
        # Extract data for each review
        professor_data['reviews'].append({
            'comment': review.find_element(By.CSS_SELECTOR, 'CSS_SELECTOR_FOR_REVIEW_COMMENT').text,
            # ... other review fields ...
        })

    # You could write the data to a CSV here, or add it to a larger data structure

    # Navigate back to the list of professors
    driver.back()

# Clean up: close the browser window
driver.quit()
