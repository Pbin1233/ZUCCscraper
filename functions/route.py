import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .driver_management import initialize_driver, log
from .element_interaction import (
    click_radio_button_by_label,
    click_checkbox_by_name,
    wait_for_element_to_be_visible,
    slow_typing
)
from .pdf_handling import savepdf
from config.config import download_dir, user_data_dir, url, username, password, prossimo_mese_dir


def route(driver, nucleo, Attesa, change_month):
    log(f"Navigating to URL: {url}", "INFO")
    driver.get(url)
    log(f"Current URL after navigation: {driver.current_url}", "DEBUG")
    time.sleep(10)

    try:
        azionib = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Azioni di Reparto']/ancestor::span[contains(@id, 'button-') and contains(@id, '-btnEl')]"))
        )
        log("Azioni di Reparto button is present, clicking it", "INFO")
        azionib.click()
        log("Clicked on Azioni di Reparto", "INFO")
    except TimeoutException:
        log("Azioni di Reparto button not found, proceeding to login", "INFO")
        username_field = wait_for_element_to_be_visible(driver, By.NAME, 'username')
        slow_typing(username_field, username)
        log("Username entered", "INFO")
        password_field = wait_for_element_to_be_visible(driver, By.NAME, 'password')
        slow_typing(password_field, password)
        log("Password entered", "INFO")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']/ancestor::span[contains(@id, '-btnEl')]"))
        )
        login_button.click()
        log("Login credentials entered and login button clicked", "INFO")
        time.sleep(10)

        azionib = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Azioni di Reparto']/ancestor::span[contains(@id, 'button-') and contains(@id, '-btnEl')]"))
        )
        log(f"Element found for 'Azioni di Reparto': {azionib}", "DEBUG")
        azionib.click()
        log("Clicked on Azioni di Reparto", "INFO")

    try:
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

        click_radio_button_by_label(driver, "Stampa rilevazione mensile")
        time.sleep(2)
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
    finally:
        time.sleep(5)

if __name__ == "__main__":
    driver = initialize_driver()
    try:
        SRM(driver, "Sample Nucleo", 5, False)
    finally:
        log("Quitting the driver", "INFO")
        driver.quit()
