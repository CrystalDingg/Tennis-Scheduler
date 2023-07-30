from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select 
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException

import time
import multiprocessing

def main():
    # court numbers
    court_preference = [3, 4, 1, 2]
    desired_time = "time"
    username = ""
    password = ""
    choosing_courts(court_preference, desired_time, username, password)
    input("Press Enter to close the browser...")

# simultaneously books different courts
def choosing_courts(court_preferences, desired_time, username, password):
    processes = []
    for court in court_preferences:
        process = multiprocessing.Process(target=book_court, args=(court, desired_time, username, password))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()

# booking process
def book_court(court, desired_time, username, password):
    driver = webdriver.Chrome()
    driver.get("https://booknow.appointment-plus.com/b6l56ers/?fbclid=IwAR2YJN3oJc9ZlAJw-pahIDVGR47xtvB8Lfckzb9Ctzk98R195j53I_4Oe34")
    login(username, password, driver)
    selecting_preferences(court, desired_time, driver)
    # book desired time slot
    next_page = booking_timeslot(desired_time, driver)
    while not next_page:
        try:
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "next")))
            next_button.click()
            next_page = booking_timeslot(desired_time, driver)
        except TimeoutException:
            break
        except ElementClickInterceptedException:
            break
    driver.quit()

# select court, date, type preferences
def selecting_preferences(court, desired_time, driver):
    # selecting court
    court_options_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "e_id")))
    court_dropdown = Select(court_options_button)
    court_name = "court name" + str(court)
    court_dropdown.select_by_visible_text(court_name)
    # select doubles
    player_options_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "service_id")))
    player_dropdown = Select(player_options_button)
    player_dropdown.select_by_visible_text("1 1/2 Hour Doubles")
    # choosing the newest available date
    available_dates = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//td[@class='calendar-available']//a")))
    available_dates[-1].click()
    desired_time_slot = desired_time

# inputs login information
def login(username, password, driver):
    username_elem = driver.find_element(By.NAME, "loginname")
    username_elem.send_keys(username)
    password_elem = driver.find_element(By.NAME, "password")
    password_elem.send_keys(password)
    login_button = driver.find_element(By.XPATH, "//input[@value='Log In']")
    login_button.click()

# booking timeslot
def booking_timeslot(desired_time_slot, driver):
    time_slots = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//table[@class='appointment-list-style']//tbody//tr")))
    # run through timeslots and find desired one
    for time_slot in time_slots:
        try:
            time_element = time_slot.find_element(By.XPATH, ".//td//span")
            time = time_element.text
            if time == desired_time_slot:
                book_it_button = time_slot.find_element(By.XPATH, "./td/input[@value='Book it']")
                book_it_button.click()
                try:
                    finalize_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@value='Finalize  Appointment ']"))
                    )
                    finalize_button.click()
                    return True
                except TimeoutException:
                    print("An appointment has already been made for this timeslot.")
                    return False
                return True
        except NoSuchElementException:
            pass
    return False


if __name__ == "__main__":
    main()
