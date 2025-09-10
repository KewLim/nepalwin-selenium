import time
import re
import signal
import sys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from selenium.webdriver.support.ui import Select
from datetime import datetime
from collections import defaultdict
import re
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n[WARNING] Shutdown signal received. Cleaning up...")
    try:
        driver.quit()
        print("[INFO] Browser closed successfully")
    except:
        print("[WARNING] Browser was already closed or unavailable")
    print("[INFO] Goodbye!")
    sys.exit(0)


def wait_for_overlay_to_disappear(driver, max_wait=5):
    """Fast overlay detection - only wait if overlay actually exists"""
    overlay_selectors = [
        "div.absolute.inset-0.transition-opacity.duration-300.bg-slate-900\\/60",
        ".app-preloader",
        "div.app-preloader"
    ]


def click_bank_transactions_link(driver, timeout=5):
    """
    Waits up to `timeout` seconds for the bank transactions link to appear,
    then clicks it. Returns True if clicked, False otherwise.
    """
    try:
        link = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[@href='https://www.rocketgo.asia/op/bank-transactions']")
            )
        )
        link.click()
        print("[LOG] Clicked Bank Transactions link.")
        return True
    except TimeoutException:
        print("[LOG] Bank Transactions link not found within timeout.")
        return False
    

def check_player_id_toast(driver, timeout=10):
    """
    Waits up to `timeout` seconds to see if the 'player id field is required' toast appears.
    Prints log if found, returns True/False.
    """
    try:
        toast = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'toastify') and contains(text(), 'successfully added')]")
            )
        )
        print("[LOG] Toast appeared: Player ID updated successfully.")
        return True
    except TimeoutException:
        return False





# Windows Firefox profile path (comment out if you want a fresh profile)
# profile_path = "C:\\Users\\BDC Computer ll\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\your-profile-name"
# firefox_profile = webdriver.FirefoxProfile(profile_path)

options = Options()
# options.set_preference("profile", profile_path)  # Commented out for fresh profile


service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)
driver.maximize_window()



driver.get("https://www.rocketgo.asia/login")

wait = WebDriverWait(driver, 40)
merchant_input = wait.until(EC.presence_of_element_located((By.NAME, "merchant_code")))
merchant_input.send_keys("nepalwin")

wait = WebDriverWait(driver, 40)
username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
username_input.send_keys("kewlim888_nepalwin")

wait = WebDriverWait(driver, 40)
password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
password_input.send_keys("aaaa1111"+ Keys.ENTER)


time.sleep(2)
click_bank_transactions_link(driver)
wait_for_overlay_to_disappear(driver, max_wait=5)

try:
    WebDriverWait(driver, 20, poll_frequency=0.2).until_not(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.app-preloader")
        )
    )
    print("[INFO] Preloader disappeared.")
except TimeoutException:
    print("[WARN] Preloader still visible. Trying to proceed anyway...")

    time.sleep(1)




try:
    # Wait for the 'Players Management' link to be clickable
    players_link = WebDriverWait(driver, 20, poll_frequency=0.2).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Players Management"))
    )
    time.sleep(5)
    players_link.click()
    print("[INFO] Clicked on 'Players Management' link.")
except TimeoutException:
    print("[ERROR] Timed out waiting for 'Players Management' link.")


# --- Check Table load ---
wait = WebDriverWait(driver, 30)
table_presence = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "gridjs-tr")))
print("[INFO] Table loaded")






def load_phone_records_from_file():

    filename = "selenium_project/selenium-phone-number.txt"
    pattern = re.compile(r"#\d+\s+-\s+Full Name:\s+(.*?),\s+Login ID:\s+(.*?),\s+Phone:\s+(\d+),\s+Email:\s+(.*?),\s+Registration:\s+(.*)", re.IGNORECASE)
    records = []

    with open(filename, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()][::-1]

    for line in lines:
        match = pattern.match(line)
        if match:
            full_name, login_id, phone, email, registration = (x.strip() for x in match.groups())
            records.append({
                "Full Name": full_name,
                "Login ID": login_id,
                "Phone Number": phone,
                "Email": email,
                "Registration Date": registration
            })
        else:
            print(f"⚠️ Skipping malformed line: {line}")

    return records







def add_player_details(record):

    """Fill Order ID, Phone Number, and Amount into form."""
    print(f"Processing Record: {record}")



    time.sleep(1)
    wait = WebDriverWait(driver, 20)
    add_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button[contains(text(), 'Add New Player')]"
    )))
    add_button.click()
    print("[INFO] Add Player button clicked")

    time.sleep(1)

    # ===== Player ID =====

    player_id_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Player ID']"))
    )
    player_id_input.clear()
    player_id_input.send_keys(record["Login ID"])
    print(f"[INFO] Player ID entered: {record['Login ID']}")


    # ===== Phone Number =====

    number_id_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Phone Number']"))
    )
    number_id_input.clear()
    number_id_input.send_keys(record["Phone Number"])
    print(f"[INFO] Player ID entered: {record['Phone Number']}")


    # ===== Email =====
    if record["Email"] != "-":
        number_id_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email']"))
        )
        number_id_input.clear()
        number_id_input.send_keys(record["Email"])
        print(f"[INFO] Email entered: {record['Email']}")
    else:
        print("[INFO] Skipped Email input (value was '-')")


    # ===== Remarks (Full Name) =====
    print(f"[DEBUG] Full Name from record: '{record['Full Name']}'")
    
    number_id_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Remarks']"))
    )
    number_id_input.clear()
    number_id_input.send_keys(record["Full Name"])
    
    # Verify what was actually entered
    entered_value = number_id_input.get_attribute("value")
    print(f"[DEBUG] Value entered in Remarks field: '{entered_value}'")
    print(f"[INFO] Full Name entered: {record['Full Name']}")



    time.sleep(1)
    
    # Submit the form using Enter key
    try:
        # Find the last input field (affiliate ID) and press Enter
        last_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter affiliate ID']")
        last_input.send_keys(Keys.ENTER)
        print("[INFO] Form submitted via Enter key")
    except Exception as e:
        print(f"[ERROR] Could not submit form with Enter key: {e}")
    
    # time.sleep(2)


    # Check for player ID toast after form submission
    
    if check_player_id_toast(driver):
        print("\033[92m[APPROVED]\033[0m Player ID form done submitted")
        
        
    else:
        print("\033[91m[WARN]\033Player ID not added - form submission failed")
        # Try pressing Enter up to 5 times with 2s interval
        for attempt in range(5):
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ENTER)
                print(f"[INFO] Sent ENTER key to dismiss toast (attempt {attempt+1}/5)")
                time.sleep(3)
            except Exception as e:
                print(f"[ERROR] Could not send ENTER key: {e}")
    


    time.sleep(3)
    
    # time.sleep(6)





def main():
    records = load_phone_records_from_file()

    for record in records:
        add_player_details(record)

    time.sleep(5)  
    driver.quit()

if __name__ == "__main__":
    # Set up signal handlers for stopping
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Kill command
    print("🚦 Press Ctrl+C to stop the automation at any time")
    print("   (Note: On macOS terminal, use Ctrl+C, not Cmd+C)")
    main()