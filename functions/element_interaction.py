import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .driver_management import log

def slow_typing(element, text, delay=0.1):
    log(f"Typing text '{text}' into element {element}", "DEBUG")
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

def select_next_month(driver):
    # Locate the input element with an ID containing 'mese'
    month_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'mese') and contains(@id, '-inputEl')]"))
    )
    current_month = month_input.get_attribute("value")
    log(f"Current month: {current_month}", "INFO")
    
    # List of months in Italian
    months_in_italian = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                         "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
    
    # Determine the index of the current month
    current_index = months_in_italian.index(current_month)
    
    # Determine the next month
    next_index = (current_index + 1) % 12
    next_month = months_in_italian[next_index]
    
    log(f"Next month to select: {next_month}", "INFO")
    
    # Open the dropdown by finding the trigger with ID containing 'mese'
    dropdown_trigger = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(@id, 'mese') and contains(@id, '-trigger-picker')]"))
    )
    dropdown_trigger.click()
    log("Dropdown opened", "INFO")
    
    # Select the next month
    next_month_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{next_month}')]"))
    )
    next_month_option.click()
    log(f"Selected {next_month} from the dropdown", "INFO")

def select_next_year_if_december(driver):
    # Get the current month
    current_month = datetime.now().month
    
    if current_month == 12:
        # Locate the year input element
        year_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'anno') and contains(@id, '-inputEl')]"))
        )
        current_year = int(year_input.get_attribute("value"))
        next_year = current_year + 1
        
        log(f"Current year is {current_year}, incrementing to {next_year}", "INFO")
        
        # Locate the spinner up button (to increment the year)
        spinner_up_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(@id, 'anno') and contains(@id, '-trigger-spinner')]//*[contains(@class, 'x-form-spinner-up')]"))
        )
        spinner_up_button.click()
        
        # Wait for the year to update
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element_value((By.XPATH, "//*[contains(@id, 'anno') and contains(@id, '-inputEl')]"), str(next_year))
        )
        
        log(f"Year successfully incremented to {next_year}", "INFO")
