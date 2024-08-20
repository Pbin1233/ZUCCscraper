import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .element_interaction import slow_typing
from .driver_management import log

def login(driver, username, password):
    try:
        # Perform login operations
        username_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'username'))
        )
        slow_typing(username_field, username)
        log("Username entered", "INFO")

        password_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'password'))
        )
        slow_typing(password_field, password)
        log("Password entered", "INFO")

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']/ancestor::span[contains(@id, '-btnEl')]"))
        )
        login_button.click()
        log("Login credentials entered and login button clicked", "INFO")

    except TimeoutException:
        log("Timeout during login process. The page might not have loaded correctly.", "ERROR")
    except NoSuchElementException as e:
        log(f"Element not found during login: {e}\n{traceback.format_exc()}", "ERROR")
    except Exception as e:
        log(f"Unexpected error during login: {e}\n{traceback.format_exc()}", "ERROR")
