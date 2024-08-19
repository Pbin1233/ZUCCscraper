from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration for download directory and Chrome user data directory
download_dir = os.getenv('DOWNLOAD_DIR')
prossimo_mese_dir = os.path.join(download_dir, "Prossimo mese")
user_data_dir = os.getenv('USER_DATA_DIR')

# URL for the login page
url = 'https://pvc003.zucchettihc.it:4445/cba/login.html'

# User credentials
username = os.getenv('APP_USERNAME')
password = os.getenv('PASSWORD')

# Nuclei and their respective wait times
nuclei = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I']
attesa = [90, 200, 200, 200, 200, 200, 200, 200]
