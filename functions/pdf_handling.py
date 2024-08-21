import os
import time
import requests
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .driver_management import log
from config.config import download_dir, mese_successivo_dir

def savepdf(driver, Nucleo, Attesa, change_month):
    try:
        # Wait until the iframe with the PDF is present
        iframe = WebDriverWait(driver, Attesa).until(
            EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
        )
        log("Iframe detected", "INFO")

        # Get the src attribute of the iframe which contains the PDF URL
        pdf_url = iframe.get_attribute('src')
        log(f"PDF link found: {pdf_url}", "INFO")

        # Determine the save directory based on change_month flag
        save_dir = mese_successivo_dir if change_month else download_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Download the PDF file
        response = requests.get(pdf_url, verify=False)
        if response.status_code == 200:
            file_path = os.path.join(save_dir, f"Nucleo {Nucleo}.pdf")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            log(f"PDF downloaded and saved as {file_path}", "INFO")
        else:
            log(f"Failed to download PDF. Status code: {response.status_code}", "ERROR")

        time.sleep(5)


    except TimeoutException as e:
        log(f"Timeout during Stampa function for Nucleo {Nucleo}: {e}\n{traceback.format_exc()}", "ERROR")
    except NoSuchElementException as e:
        log(f"Element not found during Stampa function for Nucleo {Nucleo}: {e}\n{traceback.format_exc()}", "ERROR")
    except Exception as e:
        log(f"Error during Stampa function for Nucleo {Nucleo}: {e}\n{traceback.format_exc()}", "ERROR")
