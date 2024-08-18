import os
import time
import requests
import urllib3
import logging
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.common.exceptions import ElementNotVisibleException, ElementClickInterceptedException
from config.config import download_dir, user_data_dir, url, username, password, prossimo_mese_dir


# Import your config variables
from config.config import download_dir, user_data_dir, url, username, password

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log(message, level="INFO"):
    if level == "ERROR":
        logging.error(message)
    elif level == "DEBUG":
        logging.debug(message)
    else:
        logging.info(message)

def initialize_driver():
    log("Initializing web driver with the provided options", "DEBUG")
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-first-run-ui')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")

    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })

    try:
        chrome_service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        log("Driver initialized successfully", "INFO")
    except Exception as e:
        log(f"Error initializing driver: {e}\n{traceback.format_exc()}", "ERROR")
        raise

    return driver

def slow_typing(element, text, delay=0.1):
    log(f"Typing text '{text}' into element {element}", "DEBUG")
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

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
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", radio_button)
            log(f"Scrolled radio button into view", "DEBUG")
            
            # Force click via JavaScript without checking visibility
            driver.execute_script("arguments[0].click();", radio_button)
            log(f"Clicked on Stampa rilevazione mensile", "INFO")
            
        else:
            log(f"No 'for' attribute found for label with text '{label_text}'", "ERROR")
            
    except (TimeoutException, NoSuchElementException) as e:
        log(f"Error clicking radio button with label '{label_text}': {e}\n{traceback.format_exc()}", "ERROR")
        
def click_checkbox_by_name(driver, checkbox_name):
    try:
        log(f"Attempting to find checkbox with name '{checkbox_name}'", "DEBUG")
        # Locate the checkbox element by its name attribute
        checkbox_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//input[@name='{checkbox_name}']"))
        )

        # Get the ID of the checkbox
        checkbox_id = checkbox_element.get_attribute("id")
        log(f"Checkbox found with ID: {checkbox_id}", "DEBUG")

        if checkbox_id:
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", checkbox_element)
            log("Scrolled checkbox into view", "DEBUG")
            
            # Click the checkbox by ID
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

def Stampa(driver, Nucleo, Attesa, change_month):
    try:
        log(f"Starting Stampa function for Nucleo {Nucleo}", "INFO")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'button-1376-btnEl'))
        ).click()
        log("Clicked on the print button", "INFO")

        iframe = WebDriverWait(driver, Attesa).until(
            EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
        )
        driver.switch_to.frame(iframe)
        log("Switched to the iframe", "INFO")

        pdf_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.pdf')]"))
        )
        pdf_url = pdf_link.get_attribute('href')
        log(f"PDF link found: {pdf_url}", "INFO")

        # Choose the appropriate directory
        save_dir = prossimo_mese_dir if change_month else download_dir

        response = requests.get(pdf_url, verify=False)
        if response.status_code == 200:
            file_path = os.path.join(save_dir, f"Nucleo {Nucleo}.pdf")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            log(f"PDF downloaded and saved as {file_path}", "INFO")
        else:
            log(f"Failed to download PDF. Status code: {response.status_code}", "ERROR")

        time.sleep(5)  # Keep if necessary for UI consistency

    except TimeoutException as e:
        log(f"Timeout during Stampa function for Nucleo {Nucleo}: {e}\n{traceback.format_exc()}", "ERROR")
    except NoSuchElementException as e:
        log(f"Element not found during Stampa function for Nucleo {Nucleo}: {e}\n{traceback.format_exc()}", "ERROR")
    except Exception as e:
        log(f"Error during Stampa function for Nucleo {Nucleo}: {e}\n{traceback.format_exc()}", "ERROR")

def SRM(driver, nucleo, Attesa, change_month):
    try:
        log(f"Navigating to URL: {url}", "INFO")
        driver.get(url)
        log(f"Current URL after navigation: {driver.current_url}", "DEBUG")
        time.sleep(15)  # Reduce this if login loads faster

        try:
            login_present = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, 'button-1026-btnEl'))
            )
            log("Login page loaded", "INFO")

            if login_present:
                username_field = wait_for_element_to_be_visible(driver, By.ID, 'textfield-1018-inputEl')
                password_field = wait_for_element_to_be_visible(driver, By.ID, 'textfield-1019-inputEl')
                login_button = wait_for_element_to_be_visible(driver, By.ID, 'button-1026-btnEl')

                if username_field and password_field and login_button:
                    slow_typing(username_field, username)
                    log("Username entered", "INFO")
                    slow_typing(password_field, password)
                    log("Password entered", "INFO")
                    time.sleep(5)
                    login_button.click()
                    log("Login credentials entered and login button clicked", "INFO")

                    time.sleep(20)
        except TimeoutException:
            log("Login page not present, proceeding without login", "INFO")

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, 'button-1119-btnEl'))
        )

        element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'button-1119-btnEl'))
        )
        log(f"Element found for 'Azioni di Reparto': {element}", "DEBUG")
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        log("Clicked on Azioni di Reparto", "INFO")

        time.sleep(10)
        magnifying_glass_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label[contains(text(), 'Stampe')]/following-sibling::img[@src='/cba/css/generali/images/generali/open-details.svg']")
            )
        )
        magnifying_glass_icon.click()
        log("Clicked on lente d'ingrandimento", "INFO")

        time.sleep(10)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Stampa Terapie')]"))
        ).click()
        log("Clicked on Stampa Terapie", "INFO")

        click_radio_button_by_label(driver, "Stampa rilevazione mensile")

        click_checkbox_by_name(driver, 'noteMensili')
        log(f"Clicked on Stampa anche note", "INFO")

        parent_div = driver.find_element(By.XPATH, f"//span[text()='NUCLEO {nucleo}']/parent::div")
        checkbox = parent_div.find_element(By.CLASS_NAME, "x-tree-checkbox")
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(checkbox)
        ).click()
        log(f"Selected Nucleo {nucleo}", "INFO")

        if change_month:
            select_next_month(driver)
            select_next_year_if_december(driver)

        Stampa(driver, nucleo, Attesa, change_month)
        driver.refresh()
        log("Refreshed driver after Stampa", "INFO")
        time.sleep(20)

    except Exception as e:
        log(f"Error during processing Nucleo {nucleo}: {e}\n{traceback.format_exc()}", "ERROR")
        driver.refresh()
        time.sleep(20)

if __name__ == "__main__":
    driver = initialize_driver()
    try:
        SRM(driver, "Sample Nucleo", 5)
    finally:
        log("Quitting the driver", "INFO")
        driver.quit()  # Ensure the driver is properly closed after the operations
