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
import platform
import re
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
import subprocess
import threading
import queue
from terminal_utils import setup_automation_terminal, cleanup_terminal, print_status



def wait_for_overlay_to_disappear(driver, max_wait=5):
    """Fast overlay detection - only wait if overlay actually exists"""
    overlay_selectors = [
        "div.absolute.inset-0.transition-opacity.duration-300.bg-slate-900\\/60",
        ".app-preloader",
        "div.app-preloader"
    ]
    
    overlay_found = False
    for selector in overlay_selectors:
        try:
            # Quick check if overlay exists
            overlays = driver.find_elements(By.CSS_SELECTOR, selector)
            if overlays and overlays[0].is_displayed():
                enhanced_print(f"[INFO] {selector} overlay detected, waiting...")
                WebDriverWait(driver, max_wait).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                overlay_found = True
                enhanced_print(f"[INFO] {selector} overlay disappeared")
        except:
            continue
    
    if overlay_found:
        time.sleep(0.3)  # Brief wait for DOM stability
        return True
    return False


def smart_click(element, verify_callback=None):
    """
    Smart click with minimal retries - only retry if overlay blocks
    """
    try:
        # Try normal click first
        element.click()
        
        # Quick verification if callback provided
        if verify_callback:
            time.sleep(0.3)
            if verify_callback():
                return True
            else:
                # Only retry if overlay is blocking
                if wait_for_overlay_to_disappear(driver, max_wait=3):
                    element.click()
                    time.sleep(0.3)
                    return verify_callback()
                return False
        return True
        
    except Exception as click_error:
        error_msg = str(click_error)
        # Only retry if it's an overlay blocking issue
        if "obscures it" in error_msg or "not clickable" in error_msg:
            enhanced_print("[INFO] Overlay blocking click, trying JS click...")
            if wait_for_overlay_to_disappear(driver, max_wait=3):
                try:
                    driver.execute_script("arguments[0].click();", element)
                    if verify_callback:
                        time.sleep(0.3)
                        return verify_callback()
                    return True
                except Exception as js_click_error:
                    enhanced_print(f"[INFO] JS click also failed: {js_click_error}")
                    enhanced_print("[INFO] Pressing Enter to dismiss modal/overlay...")
                    element.send_keys(Keys.ENTER)
                    time.sleep(0.5)
                    if verify_callback:
                        return verify_callback()
                    return True
        raise click_error


def reliable_click_with_locator(locator, max_attempts=3, delay=1, verify_callback=None):
    """
    Click element using locator to handle stale elements
    """
    for attempt in range(max_attempts):
        try:
            enhanced_print(f"[INFO] Attempting click with locator (attempt {attempt + 1}/{max_attempts})")
            
            # Wait for any overlays to disappear
            wait_for_overlay_to_disappear(driver, max_wait=3)
            
            # Re-find element to avoid stale reference
            element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(locator)
            )
            
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            
            # Try normal click first
            try:
                element.click()
                enhanced_print("[INFO] Normal click successful")
            except Exception as click_error:
                enhanced_print(f"[WARN] Normal click failed: {click_error}")
                # Fallback to JavaScript click
                enhanced_print("[INFO] Trying JavaScript click...")
                driver.execute_script("arguments[0].click();", element)
                enhanced_print("[INFO] JavaScript click successful")
            
            time.sleep(0.5)
            
            # If verification callback provided, use it
            if verify_callback and not verify_callback():
                if attempt < max_attempts - 1:
                    enhanced_print(f"[WARN] Click verification failed, retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    enhanced_print("[ERROR] Click verification failed after all attempts")
                    return False
            
            enhanced_print("[INFO] Click successful")
            return True
            
        except Exception as e:
            enhanced_print(f"[WARN] Click attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
            else:
                enhanced_print(f"[ERROR] All click attempts failed: {e}")
                raise e
    return False


def reliable_click(element, max_attempts=3, delay=1, verify_callback=None):
    """
    Click element with retry mechanism, overlay handling, and stale element recovery
    """
    for attempt in range(max_attempts):
        try:
            enhanced_print(f"[INFO] Attempting click (attempt {attempt + 1}/{max_attempts})")
            
            # Wait for any overlays to disappear
            wait_for_overlay_to_disappear(driver, max_wait=3)
            
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            
            # Try normal click first
            try:
                element.click()
                enhanced_print("[INFO] Normal click successful")
            except Exception as click_error:
                enhanced_print(f"[WARN] Normal click failed: {click_error}")
                # Fallback to JavaScript click
                enhanced_print("[INFO] Trying JavaScript click...")
                driver.execute_script("arguments[0].click();", element)
                enhanced_print("[INFO] JavaScript click successful")
            
            time.sleep(0.5)
            
            # If verification callback provided, use it
            if verify_callback and not verify_callback():
                if attempt < max_attempts - 1:
                    enhanced_print(f"[WARN] Click verification failed, retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    enhanced_print("[ERROR] Click verification failed after all attempts")
                    return False
            
            enhanced_print("[INFO] Click successful")
            return True
            
        except Exception as e:
            error_msg = str(e)
            enhanced_print(f"[WARN] Click attempt {attempt + 1} failed: {e}")
            
            # Check if it's a stale element error
            if "stale" in error_msg.lower() or "not connected to the DOM" in error_msg:
                enhanced_print("[WARN] Stale element detected - element needs to be re-found")
                
            if attempt < max_attempts - 1:
                time.sleep(delay)
            else:
                enhanced_print(f"[ERROR] All click attempts failed: {e}")
                raise e
    return False


def verify_dropdown_opened(driver):
    """Verify dropdown is opened by checking for dropdown options"""
    try:
        dropdown_options = driver.find_elements(By.CSS_SELECTOR, ".ts-dropdown, .dropdown-menu, [role='listbox']")
        return len(dropdown_options) > 0
    except:
        return False


def verify_modal_opened(driver):
    """Verify modal/popup window is opened"""
    try:
        modal = driver.find_elements(By.CSS_SELECTOR, ".flex.justify-between.px-4.py-3.rounded-t-lg.bg-slate-200.dark\\:bg-navy-800.sm\\:px-5")
        return len(modal) > 0 and modal[0].is_displayed()
    except:
        return False


def verify_calendar_opened(driver):
    """Verify calendar popup is opened"""
    try:
        calendar = driver.find_elements(By.CLASS_NAME, "flatpickr-calendar")
        return len(calendar) > 0 and "open" in calendar[0].get_attribute("class")
    except:
        return False


def check_player_id_toast(driver, timeout=10):
    """
    Waits up to `timeout` seconds to see if the 'player id field is required' toast appears.
    Prints log if found, returns True/False.
    """
    try:
        toast = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'toastify') and contains(text(), 'The player id field is required.')]")
            )
        )
        enhanced_print("[LOG] Toast appeared: Player ID field is required.")
        return True
    except TimeoutException:
        return False

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
        enhanced_print("[LOG] Clicked Bank Transactions link.")
        return True
    except TimeoutException:
        enhanced_print("[LOG] Bank Transactions link not found within timeout.")
        return False



# Windows Firefox profile path (comment out if you want a fresh profile)
# profile_path = "C:\\Users\\BDC Computer ll\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\your-profile-name"
# firefox_profile = webdriver.FirefoxProfile(profile_path)

options = Options()
# options.set_preference("profile", profile_path)  # Commented out for fresh profile
# Optional: Use a separate Firefox profile
# Replace 'selenium-profile' with the name of a Firefox profile you’ve created
# or comment out if you want a fresh profile every time
# options.profile = "/Users/admin/Library/Application Support/Firefox/Profiles/xxxxxxxx.selenium-profile"

# Headless mode if needed
# options.add_argument('--headless')

# Setup the driver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

# Maximize window
driver.maximize_window()



# ======== Status Terminal Setup ========
status_queue = queue.Queue()
status_process = None

def create_status_terminal():
    """Create a separate Windows terminal for status display"""
    global status_process
    try:
        # Create a batch file to keep the terminal open with custom size
        batch_content = '''@echo off
mode con: cols=80 lines=25
title Selenium Status Monitor
echo ========================================
echo     SELENIUM DEPOSIT AUTOMATION STATUS
echo ========================================
echo.
echo Waiting for status updates...
echo.
python -c "import sys, time; exec(open('status_monitor.py').read())" 2>nul
if not exist status_monitor.py (
    python -c "import time; [print(f'[{time.strftime(\"%%H:%%M:%%S\")}] Status monitor running... Press Ctrl+C to close') or time.sleep(2) for _ in iter(int, 1)]"
)
pause
'''

        with open('status_terminal.bat', 'w') as f:
            f.write(batch_content)

        # Start the terminal with custom size
        status_process = subprocess.Popen(
            ['cmd', '/c', 'start', 'status_terminal.bat'],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        enhanced_print("[INFO] Status terminal window opened")
        return True
    except Exception as e:
        enhanced_print(f"[WARNING] Could not create status terminal: {e}")
        return False

def log_to_status_terminal(message):
    """Log message to the status terminal"""
    try:
        # Write to a status file that the terminal monitors (without timestamp)
        with open('status_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    except Exception as e:
        pass  # Fail silently if status logging fails

def enhanced_print(message, status_only=False):
    """Print to both main console and status terminal"""
    # Remove emojis from message
    import re
    clean_message = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]', '', message)

    if not status_only:
        print(clean_message)
    log_to_status_terminal(clean_message)

# ======== Website Configuration ========
website_configs = {
    "1": {
        "name": "NepalWin",
        "merchant_code": "nepalwin",
        "username": "kewlim888_nepalwin",
        "password": "aaaa1111"
    },
    "2": {
        "name": "95np",
        "merchant_code": "95np",
        "username": "alex_95np",
        "password": "asdf8888"
    }
}

def select_website():
    """Display menu and get user selection"""
    print("\n" + "="*50)
    print("           SELECT WEBSITE")
    print("="*50)

    for key, config in website_configs.items():
        print(f"{key}. {config['name']}")

    print("="*50)

    while True:
        try:
            choice = input("Enter your choice (1-2): ").strip()
            if choice in website_configs:
                selected_config = website_configs[choice]
                enhanced_print(f"\nSelected: {selected_config['name']}")
                enhanced_print(f"Merchant: {selected_config['merchant_code']}")
                enhanced_print(f"Username: {selected_config['username']}")
                enhanced_print("-"*50)
                return selected_config
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            exit(0)

# Initialize status logging
enhanced_print("Starting Selenium Deposit Automation")

# Create status terminal
if create_status_terminal():
    enhanced_print("Status monitoring terminal opened")
else:
    enhanced_print("Status terminal creation failed - continuing without separate window")

# Setup terminal with custom settings
setup_automation_terminal("Add Deposit")

# Select website configuration
config = select_website()
enhanced_print(f"Selected website: {config['name']}")

# Login with selected configuration
enhanced_print(f"\nConnecting to RocketGo for {config['name']}...")
driver.get("https://www.rocketgo.asia/login")
enhanced_print("Loading login page...")

wait = WebDriverWait(driver, 40)
merchant_input = wait.until(EC.presence_of_element_located((By.NAME, "merchant_code")))
merchant_input.send_keys(config['merchant_code'])

wait = WebDriverWait(driver, 40)
username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
username_input.send_keys(config['username'])

wait = WebDriverWait(driver, 40)
password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
password_input.send_keys(config['password'] + Keys.ENTER)

enhanced_print(f"Login attempted for {config['name']}")

time.sleep(3)

enhanced_print("Navigating to Bank Transactions...")
click_bank_transactions_link(driver)
wait_for_overlay_to_disappear(driver, max_wait=5)
enhanced_print("Bank Transactions page loaded")


def remove_bom(line):
    BOM = '\ufeff'
    if line.startswith(BOM):
        return line.lstrip(BOM)
    return line





def gateway_setup_movement(gateway_name):
    enhanced_print(f"\033[93m[Gateway Setup] Executing setup for {gateway_name}\033[0m")

    gateway_map = {
        "Esewa_bank_Shankar Yadav_20250612": "ESEWA SHANKAR YADAV",
        "Laxmi_bank_Baijianath_20250407": "LAXMI BANK BAIJANATH YADAV",
        "Laxmi_bank_Subash Sunar_20250806": "LAXMI BANK SUBASH SUNAR"
    }

    if gateway_name in gateway_map:
        enter_gateway_name(gateway_map[gateway_name])



def enter_gateway_name(gateway_text):
    # Step 1: Wait for preloader to disappear
    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "app-preloader"))
    )

    # Step 2: Click container to open dropdown using locator-based approach
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)  # Optional: wait for any sticky headers to settle
    
    # Click dropdown container to open it
    container = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ts-control"))
    )
    smart_click(container, verify_callback=lambda: verify_dropdown_opened(driver))
    time.sleep(0.5)

    # Step 3: Find actual input (not always interactable)
    gateway_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "selectBank-ts-control"))
    )

    # Optional: Scroll it into view
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gateway_input)
    time.sleep(0.3)

    # enhanced_print("Displayed:", gateway_input.is_displayed())
    # enhanced_print("Enabled:", gateway_input.is_enabled())
    # enhanced_print("Size:", gateway_input.size)
    # enhanced_print("Location:", gateway_input.location)

    try:
        # Try normal input method first
        gateway_input.send_keys(gateway_text)
    except Exception as e:
        enhanced_print(f"[WARN] Normal input failed, using JS. Reason: {e}")
        # Fallback to JS-based input
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, gateway_input, gateway_text)

    time.sleep(2)  # Wait for dropdown options

    # Step 4: Check if dropdown has valid options before selection
    try:
        # Check for dropdown options
        dropdown_options = driver.find_elements(By.CSS_SELECTOR, ".ts-dropdown .option, .ts-dropdown-content .option, [data-selectable='true'], .dropdown-item")
        
        if len(dropdown_options) == 0:
            enhanced_print("[WARN] No dropdown options found, checking for alternative selectors...")
            # Try alternative selectors for dropdown options
            alternative_selectors = [
                ".ts-dropdown [data-value]",
                ".dropdown-menu li",
                ".select-dropdown li",
                "[role='option']",
                ".ts-dropdown > div"
            ]
            
            for selector in alternative_selectors:
                dropdown_options = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(dropdown_options) > 0:
                    enhanced_print(f"[INFO] Found {len(dropdown_options)} options with selector: {selector}")
                    break
        
        if len(dropdown_options) > 0:
            enhanced_print(f"[INFO] Found {len(dropdown_options)} dropdown options")
            # Press Enter to select the first matching option
            gateway_input.send_keys(Keys.ENTER)
            enhanced_print(f"[INFO] Gateway '{gateway_text}' entered and selected.")
        else:
            enhanced_print("[WARN] No dropdown options available - the dropdown might be undefined/empty")
            enhanced_print("[INFO] Trying to proceed without selection...")
            # Try pressing Enter anyway in case the input is accepted
            gateway_input.send_keys(Keys.ENTER)
            enhanced_print(f"[INFO] Attempted to enter '{gateway_text}' without dropdown options.")
            
    except Exception as e:
        enhanced_print(f"[WARN] Error checking dropdown options: {e}")
        # Fallback - try pressing Enter anyway
        gateway_input.send_keys(Keys.ENTER)
        enhanced_print(f"[INFO] Fallback: Attempted to enter '{gateway_text}'.")
    
    time.sleep(0.5)





    # --- Check Table load with multiple selectors ---
    enhanced_print("[INFO] Waiting for table to load...")
    table_selectors = [
        (By.CLASS_NAME, "gridjs-wrapper"),
        (By.CSS_SELECTOR, ".gridjs-wrapper"),
        (By.CSS_SELECTOR, "table"),
        (By.CSS_SELECTOR, ".table"),
        (By.CSS_SELECTOR, "[role='table']"),
        (By.CSS_SELECTOR, ".data-table"),
        (By.CSS_SELECTOR, ".grid-table")
    ]
    
    table_loaded = False
    wait = WebDriverWait(driver, 45)  # Increased timeout
    
    for selector in table_selectors:
        try:
            wait.until(EC.presence_of_element_located(selector))
            enhanced_print(f"[INFO] Table loaded with selector: {selector}")
            table_loaded = True
            break
        except Exception as e:
            enhanced_print(f"[DEBUG] Table selector {selector} failed: {e}")
            continue
    
    if not table_loaded:
        enhanced_print("[WARN] Table loading timeout - proceeding anyway")
    
    time.sleep(2)  # Additional wait for table content to populate



# ======== Add Details HERE =======


def add_transaction_details(record):

    """Fill Order ID, Phone Number, and Amount into form."""
    enhanced_print(f"Processing Record: Order ID \033[92m{record.get('Order ID', 'Unknown')}\033[0m")
    enhanced_print(f"   Amount: {record.get('Amount', 'Unknown')}")
    enhanced_print(f"   Phone: {record.get('Phone Number', 'Unknown')}")

    # Wait briefly for page load
    time.sleep(1)
    
    # Find Add button quickly
    wait = WebDriverWait(driver, 20)
    add_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button[contains(text(), 'Add New Bank Transaction')]"
    )))
    
    # Single smart click with modal verification
    smart_click(add_button, verify_callback=lambda: verify_modal_opened(driver))
    enhanced_print("[INFO] Add Transaction button clicked")

    # === Wait for the window UI to appear ===
    WebDriverWait(driver, 20, poll_frequency=0.2).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR, ".flex.justify-between.px-4.py-3.rounded-t-lg.bg-slate-200.dark\\:bg-navy-800.sm\\:px-5"
        ))
    )
    enhanced_print("[INFO] Target Window element appeared — proceeding...")

    # Check transaction type and execute category/subcategory selection only for ADJUSTMENTADD
    transaction_type = record.get("Transaction Type", "")
    
    if transaction_type.upper() in ("ADJUSTMENTADD", "CASH_IN"):
        enhanced_print(f"[INFO] {transaction_type} detected - executing category and subcategory selection")
        
        # ======================= Click on 'category' combobox and select 'Advance' =======================

        try:
            # 1. Wait for and click the GAME div
            game_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.item[data-value="GAME"]'))
            )
            game_div.click()
            enhanced_print("Clicked the GAME element.")

            # 2. Track and work with the GAME div element
            # enhanced_print(f"[DEBUG] GAME div element: {game_div}")
            # enhanced_print(f"[DEBUG] GAME div data-value: {game_div.get_attribute('data-value')}")
            # enhanced_print(f"[DEBUG] GAME div class: {game_div.get_attribute('class')}")
            # enhanced_print(f"[DEBUG] GAME div text: {game_div.text}")
            
            # # 3. Try to input 'Advance' directly on the GAME element
            # enhanced_print("[DEBUG] Attempting to input 'Advance' on GAME div...")
            # try:
            #     game_div.clear()
            #     game_div.send_keys("Advance")
            #     time.sleep(.5)
            #     game_div.send_keys(Keys.ENTER)
            #     enhanced_print("[DEBUG] Input set to 'Advance' on GAME div.")
            #     time.sleep(.5)
            # except Exception as e:
            #     enhanced_print(f"[DEBUG] Failed to input on GAME div: {e}")
            #     # Try using JavaScript to set value
            #     enhanced_print("[DEBUG] Trying JavaScript approach...")
            #     driver.execute_script("""
            #         arguments[0].textContent = 'Advance';
            #         arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            #     """, game_div)
            #     enhanced_print("[DEBUG] Set 'Advance' using JavaScript.")


            # ============= Select 'Advance' on dropdown list ============= 
            enhanced_print("[DEBUG] Looking for dropdown and Advance option...")
            try:
                dropdown = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[@class='ts-dropdown single' and contains(@style,'display: block')]"))
                )
                enhanced_print(f"[DEBUG] Found dropdown: {dropdown}")
                enhanced_print(f"[DEBUG] Dropdown style: {dropdown.get_attribute('style')}")
                
                advance_option = dropdown.find_element(By.XPATH, ".//div[@data-value='Advance']")
                enhanced_print(f"[DEBUG] Found Advance option: {advance_option}")
                enhanced_print(f"[DEBUG] Advance option text: {advance_option.text}")
                enhanced_print(f"[DEBUG] Advance option data-value: {advance_option.get_attribute('data-value')}")
                
                advance_option.click()
                enhanced_print("[DEBUG] Successfully clicked Advance option")
            except Exception as dropdown_error:
                enhanced_print(f"[DEBUG] Failed to find/click Advance option: {dropdown_error}")
                # Try alternative approach
                enhanced_print("[DEBUG] Trying alternative selector...")
                try:
                    advance_alt = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@data-value='Advance']"))
                    )
                    advance_alt.click()
                    enhanced_print("[DEBUG] Successfully clicked Advance with alternative selector")
                except Exception as alt_error:
                    enhanced_print(f"[DEBUG] Alternative approach also failed: {alt_error}")
                    raise dropdown_error

        except Exception as e:
            enhanced_print("Error:", e)

        time.sleep(.5)
        # ======================= Click on 'Sub Category' combobox and select 'Internal Transfer' =======================

        try:
            click_external_transfer = lambda driver: WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-value='3' and text()='External Transfer']"))
            ).click()

            # usage
            click_external_transfer(driver)

        except Exception as e:
            enhanced_print("Error:", e)


        try:
            # Inline function to wait for dropdown and click "Internal Transfer"
            click_internal_transfer = lambda driver: WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='ts-dropdown single' and contains(@style,'display: block')]"))
            ).find_element(By.XPATH, ".//div[@data-value='4' and text()='Internal Transfer']").click()

            # usage
            click_internal_transfer(driver)

        except Exception as e:
            enhanced_print("Error:", e)

        time.sleep(.5)
    else:
        enhanced_print(f"[INFO] Transaction type '{transaction_type}' - skipping ADJUSTMENTADD/CASH_IN category/subcategory selection")

    # Check transaction type and execute category/subcategory selection only for ADJUSTMENTDEDUCT
    if transaction_type.upper() in ("ADJUSTMENTDEDUCT", "CASH_OUT"):
        enhanced_print("[INFO] ADJUSTMENTDEDUCT detected - executing category selection")
        
        # ======================= Click on 'category' combobox and select 'Advance' =======================

        wait = WebDriverWait(driver, 15)
        out_radio = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="radio"][value="out"]'))
        )
        
        smart_click(out_radio)
        enhanced_print("[INFO] Successfully clicked 'out' radio button for withdrawal transaction")

        try:
            # 1. Wait for and click the GAME div
            game_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.item[data-value="GAME"]'))
            )
            game_div.click()
            enhanced_print("Clicked the GAME element.")

            enhanced_print("[DEBUG] Looking for dropdown and Advance option...")
            try:
                dropdown = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[@class='ts-dropdown single' and contains(@style,'display: block')]"))
                )
                enhanced_print(f"[DEBUG] Found dropdown: {dropdown}")
                enhanced_print(f"[DEBUG] Dropdown style: {dropdown.get_attribute('style')}")
                
                advance_option = dropdown.find_element(By.XPATH, ".//div[@data-value='Advance']")
                enhanced_print(f"[DEBUG] Found Advance option: {advance_option}")
                enhanced_print(f"[DEBUG] Advance option text: {advance_option.text}")
                enhanced_print(f"[DEBUG] Advance option data-value: {advance_option.get_attribute('data-value')}")
                
                advance_option.click()
                enhanced_print("[DEBUG] Successfully clicked Advance option")
            except Exception as dropdown_error:
                enhanced_print(f"[DEBUG] Failed to find/click Advance option: {dropdown_error}")
                # Try alternative approach
                enhanced_print("[DEBUG] Trying alternative selector...")
                try:
                    advance_alt = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@data-value='Advance']"))
                    )
                    advance_alt.click()
                    enhanced_print("[DEBUG] Successfully clicked Advance with alternative selector")
                except Exception as alt_error:
                    enhanced_print(f"[DEBUG] Alternative approach also failed: {alt_error}")
                    raise dropdown_error


        except Exception as e:
            enhanced_print("Error:", e)

        time.sleep(2)


        # try:
        #     # Wait until the input element is visible
        #     input_element = WebDriverWait(driver, 10).until(
        #         EC.visibility_of_element_located(
        #             (By.CSS_SELECTOR, 'input#tomselect-4-ts-control[role="combobox"]')
        #         )
        #     )
        #     
        #     # Send multiple BACKSPACE keys to "clear"
        #     for _ in range(30):  # adjust 30 based on max expected length
        #         input_element.send_keys(Keys.BACKSPACE)
        #         time.sleep(0.05)  # small delay to ensure JS catches it

        #     time.sleep(0.5)
        #     input_element.send_keys("External Transfer")
        #     time.sleep(1)
        #     input_element.send_keys(Keys.ENTER)
        #     time.sleep(1)
        #     enhanced_print("Text sent successfully!")

        # except Exception as e:
        #     enhanced_print(f"Failed to send keys: {e}")

        # time.sleep(.5)

    else:
        enhanced_print(f"[INFO] Transaction type '{transaction_type}' - skipping ADJUSTMENTDEDUCT/CASH_OUT category selection")

    # Click 'out' radio button only for withdrawal transactions
    # enhanced_print(f"[DEBUG] Record transaction type: '{transaction_type}' (upper: '{transaction_type.upper()}')")
    # enhanced_print(f"[DEBUG] Is withdrawal check: {transaction_type.upper() == 'WITHDRAWAL'}")
    
    if transaction_type.upper() in ("WITHDRAWAL", "MANUAL_WITHDRAWAL", "ADJUSTMENTDEDUCT", "CASH_OUT"):
        enhanced_print(f"[INFO] {transaction_type} detected - clicking 'out' radio button")
        wait = WebDriverWait(driver, 15)
        out_radio = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="radio"][value="out"]'))
        )
        
        smart_click(out_radio)
        enhanced_print(f"[INFO] Successfully clicked 'out' radio button for {transaction_type} transaction")
    else:
        enhanced_print(f"[INFO] Not a withdrawal type (type: '{transaction_type}') - skipping 'out' radio button")

    # ===== Order ID =====
    order_id_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Bank Reference']"))
    )

    # Force scroll into view before clear and type
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", order_id_input)
    time.sleep(0.3)

    order_id_input.clear()
    order_id_input.send_keys(record["Order ID"])
    enhanced_print(f"[INFO] Order ID entered: {record['Order ID']}")


    # ===== Phone Number ===== (Only for DEPOSIT, MANUAL_DEPOSIT, WITHDRAWAL, MANUAL_WITHDRAWAL)

    if transaction_type.upper() in ("DEPOSIT", "MANUAL_DEPOSIT", "WITHDRAWAL", "MANUAL_WITHDRAWAL"):
        enhanced_print(f"[INFO] {transaction_type} transaction - filling phone number field")
        
        phone_number_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Player ID']"))
        )
        
        # Multiple scrolling approaches to ensure element is interactable
        try:
            # Approach 1: Scroll to top first
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            # Approach 2: Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", phone_number_input)
            time.sleep(0.5)
            
            # Approach 3: Additional scrolling to ensure visibility
            driver.execute_script("""
                arguments[0].focus();
                arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                window.scrollBy(0, -100);
            """, phone_number_input)
            time.sleep(1)
            
            # Try to clear the field
            phone_number_input.clear()
            enhanced_print("[DEBUG] Phone number input cleared successfully")
            
        except Exception as clear_error:
            enhanced_print(f"[DEBUG] Clear failed: {clear_error}, trying JavaScript approach...")
            # JavaScript fallback for clearing
            driver.execute_script("arguments[0].value = '';", phone_number_input)
            enhanced_print("[DEBUG] Phone number input cleared with JavaScript")
        
        # Enter the phone number
        try:
            phone_number_input.send_keys(record["Phone Number"])
            enhanced_print(f"[INFO] Phone Number entered: {record['Phone Number']}")
        except Exception as send_error:
            enhanced_print(f"[DEBUG] Send keys failed: {send_error}, trying JavaScript...")
            driver.execute_script("arguments[0].value = arguments[1];", phone_number_input, record["Phone Number"])
            enhanced_print(f"[INFO] Phone Number entered with JavaScript: {record['Phone Number']}")
    else:
        enhanced_print(f"[INFO] {transaction_type} transaction - skipping phone number field")



    # ===== Amount =====

    amount_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='amount']"))
    )
    amount_input.clear()
    amount_input.send_keys(str(record["Amount"]).replace(",", ""))
    enhanced_print(f"[INFO] Order ID entered: {record['Amount']}")



    # ===== Bank Charges =====
    if record["Bank Tax"] != "-":
        bank_charge_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Bank Charge']"))
        )
        bank_charge_input.clear()
        bank_charge_input.send_keys(str(record["Bank Tax"]).replace(",", ""))
        enhanced_print(f"[INFO] Bank Charge entered: {record['Bank Tax']}")
    else:
        enhanced_print("[INFO] Skipped Bank Charge input (value was '-')")



    # ===== Datepicker =====

    calendar_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Choose datetime...']"))
    )
    
    # Use smart click with calendar verification
    smart_click(calendar_input, verify_callback=lambda: verify_calendar_opened(driver))
    enhanced_print(f"[INFO] Calendar input clicked...")

    calendar_popup = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "flatpickr-calendar"))
    )

    if "open" in calendar_popup.get_attribute("class"):
        enhanced_print("[INFO] Calendar popup is OPEN")

        # Use platform-specific date format
        if platform.system() == "Windows":
            target_date = record["Datetime"].strftime("%B %#d, %Y")  # Windows: %#d removes leading zero
        else:
            target_date = record["Datetime"].strftime("%B %-d, %Y")  # Unix/Mac: %-d removes leading zero
        all_days = driver.find_elements(By.CSS_SELECTOR, ".flatpickr-day")

        for day in all_days:
            if day.get_attribute("aria-label") == target_date:
                driver.execute_script("arguments[0].scrollIntoView(true);", day)
                # Use smart click for date selection
                smart_click(day)
                enhanced_print(f"[INFO] Clicked date: {target_date}")
                break
        else:
            enhanced_print(f"[ERROR] Date '{target_date}' not found in picker.")

    else:
        enhanced_print("[WARN] Calendar popup did NOT open")


    # ===== Hour =====
    wait = WebDriverWait(driver, 40)
    merchant_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.flatpickr-hour")))
    merchant_input.clear()
    merchant_input.send_keys(record["Hour"])

    time.sleep(.5)


    # ===== Minutes =====
    wait = WebDriverWait(driver, 40)
    merchant_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.flatpickr-minute")))
    merchant_input.clear()
    merchant_input.send_keys(record["Minute"])

    time.sleep(.5)


    # ===== Decide AM or PM from the record =====

    ampm_target = "AM" if int(record.get("Hour", 0)) < 12 else "PM"
    ampm_toggle = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "flatpickr-am-pm"))
    )

    # Check and click if needed
    current_ampm = ampm_toggle.text.strip().upper()
    if current_ampm != ampm_target:
        # Use smart click for AM/PM toggle
        smart_click(ampm_toggle)
        enhanced_print(f"[INFO] AM/PM toggled to {ampm_target}")
    else:
        enhanced_print(f"[INFO] AM/PM already set to {ampm_target}")

    time.sleep(1)
    
    # Select Player ID field (only for transactions that have phone number field)
    if transaction_type.upper() in ("DEPOSIT", "MANUAL_DEPOSIT", "WITHDRAWAL", "MANUAL_WITHDRAWAL"):
        try:
            player_id_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Player ID']"))
            )
            
            # Add scrolling for Player ID field as well
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", player_id_input)
            time.sleep(0.3)
            
            player_id_input.click()
            enhanced_print(f"[INFO] Player ID field clicked for {transaction_type}")
        except Exception as player_click_error:
            enhanced_print(f"[DEBUG] Player ID click failed: {player_click_error}, continuing...")
    else:
        enhanced_print(f"[INFO] {transaction_type} transaction - skipping Player ID field click")

    time.sleep(1)
    
    # Confirm calendar selection by pressing Enter on the calendar input or body
    try:
        # First try to press Enter on the calendar input to confirm the datetime selection
        calendar_input = driver.find_element(By.XPATH, "//input[@placeholder='Choose datetime...']")
        calendar_input.send_keys(Keys.ENTER)
        enhanced_print("[INFO] Calendar selection confirmed via Enter on calendar input")
    except Exception as e:
        enhanced_print(f"[WARN] Could not confirm calendar via input: {e}")
        # Fallback: press Enter on body to confirm calendar
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
            enhanced_print("[INFO] Calendar selection confirmed via Enter on body")
        except Exception as e2:
            enhanced_print(f"[WARN] Could not confirm calendar: {e2}")
    
    time.sleep(0.5)
    
    # Check for player ID toast after form submission
    if check_player_id_toast(driver):
        enhanced_print("\033[91m[WARN]\033[0m Player ID field validation failed - form not submitted")
        
        # Try pressing Enter up to 3 times with 2s interval
        for attempt in range(5):
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ENTER)
                enhanced_print(f"[INFO] Sent ENTER key to dismiss toast (attempt {attempt+1}/3)")
                time.sleep(3)
            except Exception as e:
                enhanced_print(f"[ERROR] Could not send ENTER key: {e}")
    else:
        enhanced_print("[INFO] No player ID toast detected - form submission successful")
    
    time.sleep(.5)










def parse_and_execute(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_gateway = None
    current_records = []
    performed_gateways = set()
    current_transaction_type = "DEPOSIT"  # Default to DEPOSIT

    supported_gateways = {
        "Laxmi_bank_Baijianath_20250407", "Esewa_bank_Shankar Yadav_20250612", "Laxmi_bank_Subash Sunar_20250806"
    }

    # Temporary variables for one record
    order_id = phone = amount = time_str = transaction_type = bank_tax = None
    dt = hour_str = minute_str = None

    for raw_line in lines:
        line = remove_bom(raw_line.strip())

        if not line:
            continue

        # Detect WITHDRAWALS section banner
        if "WITHDRAWALS" in line and "=" in line:
            current_transaction_type = "WITHDRAWAL"
            enhanced_print(f"[INFO] Detected WITHDRAWALS section - switching to withdrawal mode: '{line}'")
            continue

        # Detect DEPOSITS section banner  
        if "DEPOSITS" in line and "=" in line:
            current_transaction_type = "DEPOSIT"
            enhanced_print(f"[INFO] Detected DEPOSITS section - switching to deposit mode: '{line}'")
            continue

        # Stop condition — flush records first
        if line.startswith("==== GRAND TOTAL for All Gateways:"):
            enhanced_print("[INFO] Reached GRAND TOTAL line. Stopping processing.")
            break

        # Detect gateway header line
        if line.startswith("====") and "Total Amount" in line:
            if current_records:
                enhanced_print(f"[DEBUG] Flushing {len(current_records)} records under gateway '{current_gateway}'")
                for record in current_records:
                    add_transaction_details(record)
            current_records = []

            match = re.match(r"==== (.*?) \(", line)
            if match:
                detected_gateway = match.group(1)
                if detected_gateway in supported_gateways:
                    current_gateway = detected_gateway
                    # Always call gateway_setup_movement for each gateway section (deposits/withdrawals)
                    gateway_setup_movement(current_gateway)
                    performed_gateways.add(current_gateway)
                else:
                    enhanced_print(f"[WARNING] Unsupported gateway '{detected_gateway}', skipping records.")
                    current_gateway = None
            continue

        # Skip if gateway not set
        if not current_gateway:
            continue

        # Parse record fields
        if line.startswith("Order ID:"):
            order_id = line.split(":", 1)[1].strip()
        elif line.startswith("Transaction Type:"):
            transaction_type = line.split(":", 1)[1].strip()
        elif line.startswith("Phone Number:"):
            phone = line.split(":", 1)[1].strip()
        elif line.startswith("Amount:"):
            amount = line.split(":", 1)[1].strip()
        elif line.startswith("Bank Charges:"):
            bank_tax = line.split(":", 1)[1].strip()
        elif line.startswith("Time:"):
            time_str = line.split(":", 1)[1].strip()
            try:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                hour_str = f"{dt.hour:02d}"
                minute_str = f"{dt.minute:02d}"

                # ✅ Only append once all fields are known (bank_tax can be None/missing)
                if all([order_id, phone, amount, time_str, transaction_type]):
                    enhanced_print(f"[DEBUG] Creating record with Transaction Type: {transaction_type}")
                    current_records.append({
                        "Order ID": order_id,
                        "Phone Number": phone,
                        "Amount": amount,
                        "Time": time_str,
                        "Hour": hour_str,
                        "Minute": minute_str,
                        "Datetime": dt,
                        "Transaction Type": transaction_type,
                        "Bank Tax": bank_tax if bank_tax is not None else "-"
                    })
                    # Reset vars for next record
                    order_id = phone = amount = time_str = transaction_type = bank_tax = None
                    dt = hour_str = minute_str = None
            except ValueError:
                enhanced_print(f"[ERROR] Invalid datetime: {time_str}")
                continue

    # ✅ Final flush at EOF
    if current_records:
        enhanced_print(f"[DEBUG] Final flush: {len(current_records)} records under gateway '{current_gateway}'")
        for record in current_records:
            add_transaction_details(record)



# ===== Function call HERE =====
enhanced_print("📋 Starting transaction processing from file...")
parse_and_execute("selenium_project/selenium-transaction_history.txt")
enhanced_print("All transactions processed successfully!")
enhanced_print("Automation completed. Closing browser...")
time.sleep(2)
driver.quit()

# Cleanup
try:
    if os.path.exists('status_terminal.bat'):
        os.remove('status_terminal.bat')
    enhanced_print("Cleanup completed")
except:
    pass

cleanup_terminal()

