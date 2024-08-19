# element_interaction.py

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

def click_radio_button_by_label(driver, label_text):
    try:
        log(f"Attempting to click radio button with label '{label_text}'", "DEBUG")
        label = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//label[contains(text(), '{label_text}') or contains(text(), '{label_text.replace(' ', '\xa0')}')]"))
        )
        radio_id = label.get_attribute("for")
        log(f"Label found with 'for' attribute: {radio_id}", "DEBUG")
        
        if radio_id:
            radio_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, radio_id))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", radio_button)
            log(f"Scrolled radio button into view", "DEBUG")
            driver.execute_script("arguments[0].click();", radio_button)
            log(f"Clicked on Stampa rilevazione mensile", "INFO")
            
        else:
            log(f"No 'for' attribute found for label with text '{label_text}'", "ERROR")
            
    except (TimeoutException, NoSuchElementException) as e:
        log(f"Error clicking radio button with label '{label_text}': {e}\n{traceback.format_exc()}", "ERROR")
        
def click_checkbox_by_name(driver, checkbox_name):
    try:
        log(f"Attempting to find checkbox with name '{checkbox_name}'", "DEBUG")
        checkbox_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//input[@name='{checkbox_name}']"))
        )
        checkbox_id = checkbox_element.get_attribute("id")
        log(f"Checkbox found with ID: {checkbox_id}", "DEBUG")

        if checkbox_id:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", checkbox_element)
            log("Scrolled checkbox into view", "DEBUG")
            checkbox_element.click()
            log(f"Clicked checkbox with name '{checkbox_name}' and ID '{checkbox_id}'", "DEBUG")
        else:
            log(f"No ID attribute found for checkbox with name '{checkbox_name}'", "ERROR")
            
    except (TimeoutException, NoSuchElementException) as e:
        log(f"Error finding or clicking checkbox with name '{checkbox_name}': {e}\n{traceback.format_exc()}", "ERROR")

def wait_for_element_to_be_visible(driver, by, value, timeout=30):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        log(f"Timeout waiting for element {value} to be visible", "ERROR")
        return None
