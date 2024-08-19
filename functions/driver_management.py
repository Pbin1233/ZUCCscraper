# driver_management.py

import os
import time
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.config import download_dir, user_data_dir

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO,  # Capture all log levels
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler()  # Also log to console
    ]
)

def log(message, level="INFO"):
    logger = logging.getLogger(__name__)
    if level == "INFO":
        logger.info(message)
    elif level == "DEBUG":
        logger.debug(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)

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
