import os
from config.config import download_dir, nuclei, attesa, user_data_dir, url, username, password, mese_successivo_dir


def all_files_downloaded(missing_nuclei):
    return len(missing_nuclei) == 0

def get_missing_nuclei(change_month):
    # Determine the directory to check
    check_dir = os.path.join(download_dir, "Mese successivo") if change_month else download_dir
    
    # Ensure the directory exists
    if not os.path.exists(check_dir):
        os.makedirs(check_dir)

    existing_files = os.listdir(check_dir)
    existing_nuclei = [file.split(" ")[1].split(".")[0] for file in existing_files if file.startswith("Nucleo")]
    return [n for n in nuclei if n not in existing_nuclei]
