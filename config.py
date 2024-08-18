# config.py
import os

# Configuration for download directory and Chrome user data directory
download_dir = "C:/Users/pbpao/Desktop/Stampe"
prossimo_mese_dir = os.path.join(download_dir, "Prossimo mese")  # New subfolder for 'Prossimo mese'
user_data_dir = "C:/Users/pbpao/Desktop/ChromeProfile"

# Ensure the directories exist
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
if not os.path.exists(prossimo_mese_dir):
    os.makedirs(prossimo_mese_dir)
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

# URL for the login page
url = 'https://pvc003.zucchettihc.it:4445/cba/login.html'

# User credentials
username = 'Terapia Vera'
password = 'RBorromea2024'

# Nuclei and their respective wait times
nuclei = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I']
attesa = [90, 200, 200, 200, 200, 200, 200, 200]
