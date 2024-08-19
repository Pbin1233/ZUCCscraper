import os
import time
import sys
from datetime import datetime, timedelta
from config.config import download_dir, nuclei, attesa
from functions.route import route
from functions.driver_management import initialize_driver

def all_files_downloaded(missing_nuclei):
    return len(missing_nuclei) == 0

def get_missing_nuclei(change_month):
    # Determine the directory to check
    check_dir = os.path.join(download_dir, "Prossimo mese") if change_month else download_dir
    
    # Ensure the directory exists
    if not os.path.exists(check_dir):
        os.makedirs(check_dir)

    existing_files = os.listdir(check_dir)
    existing_nuclei = [file.split(" ")[1].split(".")[0] for file in existing_files if file.startswith("Nucleo")]
    return [n for n in nuclei if n not in existing_nuclei]

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
            route(driver, nucleo, attesa[nuclei.index(nucleo)], change_month)
        
        # Wait for a short period before checking again
        time.sleep(10)

    driver.quit()
    print("PDFs generated and saved to the specified directory")

    # Wait for a few minutes before closing the shell window
    time.sleep(10)  # Wait for 10 seconds before closing
    

if __name__ == "__main__":
    change_month = sys.argv[1].lower() == 'true'
    main(change_month)
