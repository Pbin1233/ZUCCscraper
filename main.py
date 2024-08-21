import os
import time
import sys
import traceback
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.config import download_dir, user_data_dir, url, username, password, mese_successivo_dir, attesa, nuclei
from functions.driver_management import initialize_driver, log
from functions.element_interaction import slow_typing, select_next_month, select_next_year_if_december
from functions.pdf_handling import savepdf
from functions.login import login
from functions.case_specific import get_missing_nuclei, all_files_downloaded


def start_route(driver, nucleo, Attesa, change_month):
    while True:  # Retry loop in case of a timeout
        log(f"Navigating to URL: {url}", "INFO")
        driver.get(url)
        log(f"Current URL after navigation: {driver.current_url}", "DEBUG")
        time.sleep(5)

        try:
            # Wait until either the username field or the Azioni di Reparto button is visible
            element_present = WebDriverWait(driver, 30).until(
                EC.any_of(
                    EC.visibility_of_element_located((By.NAME, 'username')),
                    EC.presence_of_element_located((By.XPATH, "//span[text()='Azioni di Reparto']/ancestor::span[contains(@id, 'button-') and contains(@id, '-btnEl')]"))
                )
            )

            # Check which element became visible
            if EC.visibility_of_element_located((By.NAME, 'username'))(driver):
                log("Username field is visible, proceeding with login operations.", "INFO")
                login(driver, username, password)
                time.sleep(10)
                post_login_operations(driver, nucleo, Attesa, change_month)
                break  # Exit the loop since operations are complete
            elif EC.presence_of_element_located((By.XPATH, "//span[text()='Azioni di Reparto']/ancestor::span[contains(@id, 'button-') and contains(@id, '-btnEl')]"))(driver):
                log("Azioni di Reparto button is present. User is already logged in. Proceeding with post-login operations.", "INFO")
                post_login_operations(driver, nucleo, Attesa, change_month)
                break  # Exit the loop since operations are complete
            else:
                log("Neither username nor Azioni di Reparto button became visible. Retrying.", "WARNING")

        except TimeoutException:
            log("Timeout occurred while waiting for elements. Retrying from the beginning.", "WARNING")
            continue  # Retry the process from the start
        except Exception as e:
            log(f"Unexpected error: {e}\n{traceback.format_exc()}", "ERROR")
            break  # Exit loop if an unexpected error occurs

        finally:
            time.sleep(5)
            
def post_login_operations(driver, nucleo, Attesa, change_month):
    try:
        time.sleep(10)
        WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.ID, "ext-element-27")))
        azionib = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Azioni di Reparto']/ancestor::span[contains(@id, 'button-') and contains(@id, '-btnEl')]"))
        )
        log(f"Element found for 'Azioni di Reparto': {azionib}", "DEBUG")
        azionib.click()
        log("Clicked on Azioni di Reparto", "INFO")
        time.sleep(5)


        magnifying_glass_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label[contains(text(), 'Stampe')]/following-sibling::img[@src='/cba/css/generali/images/generali/open-details.svg']")
            )
        )
        magnifying_glass_icon.click()
        log("Clicked on lente d'ingrandimento", "INFO")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Stampa Terapie')]"))
        ).click()
        log("Clicked on Stampa Terapie", "INFO")

        label_text = 'Stampa rilevazione mensile'
        label = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//label[contains(text(), '{label_text}') or contains(text(), '{label_text.replace(' ', '\xa0')}')]"))
        )
        time.sleep(2)
        driver.find_element(By.ID, label.get_attribute("for")).click()
        log(f"Clicked on '{label_text}'", "INFO")
        time.sleep(2)
        
        checkbox_name = 'noteMensili'
        checkbox_id = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//input[@name='{checkbox_name}']"))
        ).get_attribute("id")

        log(f"Checkbox with name '{checkbox_name}' has ID '{checkbox_id}'", "DEBUG")

        driver.find_element(By.ID, checkbox_id).click()
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

        log(f"Starting Stampa function for Nucleo {nucleo}", "DEBUG")

        # Locate and click the print button
        try:
            button_element = driver.find_element(By.XPATH, "//div[contains(@id, 'CSSButtonsPanel')]//a[1]")
            button_element.click()
            log("Clicked on the print button", "INFO")
        except TimeoutException as e:
            log(f"Timeout while trying to find the print button: {e}\n{traceback.format_exc()}", "ERROR")
        except Exception as e:
            log(f"Error clicking the print button: {e}\n{traceback.format_exc()}", "ERROR")

        savepdf(driver, nucleo, Attesa, change_month)
        time.sleep(5)
    except TimeoutException as e:
        log(f"Timeout while trying to find element: {e}\n{traceback.format_exc()}", "ERROR")
    except NoSuchElementException as e:
        log(f"Element not found: {e}\n{traceback.format_exc()}", "ERROR")
    except Exception as e:
        log(f"Unexpected error: {e}\n{traceback.format_exc()}", "ERROR")


def main(change_month):
    driver = initialize_driver()

    # Record the start time
    start_time = datetime.now()
    
    while True:
        current_time = datetime.now()
        elapsed_time = current_time - start_time
        
        # Check if the elapsed time is greater than two hours
        if elapsed_time > timedelta(hours=2):
            print("Time limit exceeded. Stopping the script.")
            break
        
        missing_nuclei = get_missing_nuclei(change_month)
        print(f"Missing nuclei: {missing_nuclei}")

        if all_files_downloaded(missing_nuclei):
            break

        for nucleo in missing_nuclei:
            start_route(driver, nucleo, attesa[nuclei.index(nucleo)], change_month)
        
        # Wait for a short period before checking again
        time.sleep(10)

    driver.quit()
    print("PDFs generated and saved to the specified directory")

    # Wait for a few minutes before closing the shell window
    time.sleep(120)
    

if __name__ == "__main__":
    change_month = sys.argv[1].lower() == 'true'
    main(change_month)
