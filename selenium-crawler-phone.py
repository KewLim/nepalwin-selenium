from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time
import signal
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from selenium.webdriver.support.ui import Select
from datetime import datetime
from collections import defaultdict
from terminal_utils import setup_automation_terminal, cleanup_terminal, print_status

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n[WARNING] Shutdown signal received. Cleaning up...")
    try:
        driver.quit()
        print("[INFO] Browser closed successfully")
    except:
        print("⚠️ Browser was already closed or unavailable")
    sys.exit(0)




# Windows Firefox profile path (comment out if you want a fresh profile)
# profile_path = "C:\\Users\\BDC Computer ll\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\your-profile-name"
# firefox_profile = webdriver.FirefoxProfile(profile_path)

options = Options()
# options.set_preference("profile", profile_path)  # Commented out for fresh profile
# Optional: Use a specific Firefox profile for Windows
# To find your Firefox profiles, navigate to: %APPDATA%\Mozilla\Firefox\Profiles\
# Example Windows profile path:
# options.profile = "C:\\Users\\YourUsername\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\xxxxxxxx.selenium-profile"

# Headless mode if needed
# options.add_argument('--headless')

# Setup the driver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)
driver.maximize_window()



# ======== Website Configuration ========
website_configs = {
    "1": {
        "name": "NepalWin",
        "url": "https://bo.nepalwin.com/user/login",
        "username": "kewlim888",
        "password": "aaaa1111",
        "username_xpath": "//input[@placeholder='Username:']",
        "password_xpath": "//input[@placeholder='Password:']"
    },
    "2": {
        "name": "95np",
        "url": "https://bo.95np.com/user/login/",
        "username": "tommy8888",
        "password": "tommy6666",
        "username_xpath": "//input[@placeholder='Username:']",
        "password_xpath": "//input[@placeholder='Password:']"
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
                print(f"\n✅ Selected: {selected_config['name']}")
                print(f"🌐 URL: {selected_config['url']}")
                print(f"👤 Username: {selected_config['username']}")
                print("-"*50)
                return selected_config
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
            exit(0)

# Setup terminal with custom settings
setup_automation_terminal("Phone Number Crawler")

# Select website configuration
config = select_website()

# Login with selected configuration
print(f"\n🚀 Connecting to {config['name']}...")
driver.get(config['url'])

wait = WebDriverWait(driver, 40)
username_input = wait.until(EC.presence_of_element_located((By.XPATH, config['username_xpath'])))
username_input.send_keys(config['username'])

wait = WebDriverWait(driver, 40)
password_input = wait.until(EC.presence_of_element_located((By.XPATH, config['password_xpath'])))
password_input.send_keys(config['password'])
password_input.send_keys(Keys.ENTER)

print(f"✅ Login attempted for {config['name']}")

time.sleep(2)

# ======== Entered Main Page ========

# Wait until the Transaction header is present and visible
transaction_header = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, "//span[@class='ant-page-header-heading-title' and text()='Transaction']"))
)

print("✅ 'Transaction' header found, proceeding...")

# Wait until the 'Report' menu item is visible and clickable
report_item = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//span[text()='Report']"))
)

# Click it
report_item.click()
time.sleep(2)


# ======== Entered Player Page ========

# Wait until the link is visible and clickable
link = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.LINK_TEXT, "Member Information & Referral Link"))
)

# Click the link
link.click()
print("Clicked 'Member Information & Referral Link' successfully.")


# Select date section
from date_selector import get_date_selection, DateSelector

# Use date selection modal
start_date, end_date = get_date_selection()

if start_date and end_date:
    print(f"\033[1;32m[APPROVED]\033[0m Date range selected: {start_date} to {end_date}")
    print(f"\033[1;33m[INFO]\033[0m Using optimized extraction with early stopping")
else:
    print("\033[1;31m[ERROR] No dates selected, exiting...\033[0m")
    driver.quit()
    exit(1)

# ======== Entered Main Page ========

# Wait for sidebar to appear





# ======== Entered 2.1 Deposit =======


# Wait for panel loading
WebDriverWait(driver, 20).until(
    EC.invisibility_of_element_located((By.CLASS_NAME, "box box-info"))
)
print("[INFO] Panel load complete")


time.sleep(2)

# Wait for ajax loader loading
WebDriverWait(driver, 20).until(
    EC.invisibility_of_element_located((By.CLASS_NAME, "ajaxLoader"))
)
print("\033[94m[INFO] ajaxLoader complete\033[0m")

time.sleep(2)






# ======= Print Logic Here =======

phone_groups = defaultdict(list)


def extract_phone_data_with_date_filter(driver, start_date, end_date, wait_timeout=20):
    """
    Extracts phone data with early-stopping date filtering.
    Returns (collected_records, should_stop_scraping)
    """
    print(f"[INFO] Filtering for dates: {start_date} to {end_date}")
    
    # Wait until at least one row exists
    WebDriverWait(driver, wait_timeout).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr")) > 0
    )

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"[SUCCESS] Found {len(rows)} rows in Member Information table")

    collected_records = []
    should_stop_scraping = False
    
    print(f"[INFO] Processing {len(rows)} rows with date filtering...")
    time.sleep(1)  # Stability delay

    for idx in range(len(rows)):
        try:
            # Re-find rows to avoid stale element reference
            current_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            if idx >= len(current_rows):
                print(f"[WARNING] Row {idx + 1} no longer exists. Skipping.")
                continue
                
            row = current_rows[idx]
            cols = row.find_elements(By.TAG_NAME, 'td')
            
            if len(cols) < 5:  # Reduce minimum column requirement
                print(f"[WARNING] Row {idx + 1} has only {len(cols)} columns. Skipping.")
                continue
            
            # Filter out summary rows
            first_col_text = cols[0].text.strip() if len(cols) > 0 else ""
            if "Page Summary" in first_col_text or "Total Summary" in first_col_text:
                print(f"[INFO] Skipping summary row: '{first_col_text}'")
                continue

            # DEBUG: Print all column data to identify the date column
            print(f"\n[DEBUG] Row {idx + 1} - Total columns: {len(cols)}")
            for col_idx, col in enumerate(cols):
                col_text = col.text.strip()
                print(f"[DEBUG] Column {col_idx}: '{col_text}'")
                
            # Extract date from appropriate column (you need to identify which column has dates)
            registration_date_str = cols[0].text.strip() if len(cols) > 0 else ""
            print(f"[DEBUG] Trying to parse date from column 0: '{registration_date_str}'")
            
            if not registration_date_str:
                print(f"[WARNING] No registration date in row {idx + 1}, skipping")
                continue
            
            try:
                # Parse registration date - support multiple formats for Windows compatibility
                date_formats = [
                    "%Y-%m-%d",          # 2025-08-27
                    "%m/%d/%Y",          # 08/27/2025 (US format)
                    "%d/%m/%Y",          # 27/08/2025 (European format)
                    "%Y/%m/%d",          # 2025/08/27
                    "%d-%m-%Y",          # 27-08-2025
                    "%m-%d-%Y",          # 08-27-2025
                    "%d.%m.%Y",          # 27.08.2025 (German format)
                    "%Y%m%d"             # 20250827 (compact format)
                ]
                
                # Extract date part if datetime string
                if ' ' in registration_date_str:
                    date_str = registration_date_str.split(" ")[0]  # Extract date part
                else:
                    date_str = registration_date_str
                
                row_date = None
                for date_format in date_formats:
                    try:
                        row_date = datetime.strptime(date_str, date_format).date()
                        print(f"[DEBUG] Successfully parsed '{date_str}' using format '{date_format}'")
                        break
                    except ValueError:
                        continue
                
                if row_date is None:
                    raise ValueError(f"Unable to parse date '{date_str}' with any known format")
                
                print(f"[DEBUG] Row {idx + 1}: Date {row_date}, Range {start_date} to {end_date}")
                
                # Date filtering logic
                if row_date > end_date:
                    print(f"[DEBUG] Row {idx + 1} too new ({row_date}), skipping")
                    continue
                
                if row_date < start_date:
                    print(f"[INFO] Row {idx + 1} too old ({row_date}), stopping scraping")
                    should_stop_scraping = True
                    break
                
                # Row is within date range (start_date <= row_date <= end_date)
                print(f"[INFO] Row {idx + 1} within range ({row_date}), collecting")
                
                phone_number = cols[3].text.strip() if len(cols) > 3 else ""
                email = cols[4].text.strip() if len(cols) > 4 else ""
                login_id = cols[2].text.strip() if len(cols) > 2 else ""
                full_name = cols[1].text.strip() if len(cols) > 1 else ""
                
                print(f"[DEBUG] Row {idx + 1}: full_name = '{full_name}', login_id = '{login_id}', phone_number = '{phone_number}'")
                

                if phone_number:
                    record = {
                        "Login ID": login_id,
                        "Full Name": full_name,
                        "Phone Number": phone_number,
                        "Email": email,
                        "Registration Date": registration_date_str,
                        "Date": row_date  # Add parsed date for easier processing
                    }
                    collected_records.append(record)

            except ValueError as e:
                print(f"[WARNING] Invalid date format '{registration_date_str}' in row {idx + 1}: {e}")
                continue
                
        except Exception as e:
            print(f"[ERROR] Failed to process row {idx + 1}: {e}")
            continue

    print(f"[INFO] Collected {len(collected_records)} records from this page")
    print(f"[INFO] Should stop scraping: {should_stop_scraping}")
    
    return collected_records, should_stop_scraping



def print_grouped_phone_results(grouped_data):
    total_records = sum(len(records) for records in grouped_data.values())
    print(f"\n[INFO] Writing {total_records} total records to file.")

    with open("selenium_project/selenium-phone-number.txt", "w", encoding="utf-8") as f:
        for group, records in grouped_data.items():
            header = f"\n==== {group} ({len(records)} records) ====\n"
            print(f"\033[92m{header}\033[0m")
            f.write(header)

            for i, record in enumerate(records, 1):
                line = (
                    f"#{i} - Full Name: {record.get('Full Name', 'Unknown')}, "
                    f"Login ID: {record.get('Login ID', 'Unknown')}, "
                    f"Phone: {record['Phone Number']}, "
                    f"Email: {record['Email']}, "
                    f"Registration: {record.get('Registration Date', 'Unknown')}\n"
                )
                print(line.strip())
                f.write(line)

        footer = f"\n==== TOTAL: {total_records} phone numbers collected ====\n"
        print(f"\033[95m{footer}\033[0m")
        f.write(footer)


def click_next_page(driver, wait_timeout=10):
    try:
        # Search for next button specifically outside the sidebar area (in main content)
        next_button = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ant-pagination-item-link:has(span[aria-label="right"])'))
        )
        next_button.click()
        time.sleep(2)
        print("[INFO] Clicked on the Next button.")
        return True
    except Exception as e:
        print(f"[WARNING] Could not click Next button: {e}")
        return False


seen_phone_numbers = set()  # Track seen phone numbers to prevent duplicates

def run_optimized_phone_extraction(driver, start_date, end_date):
    """
    Optimized extraction with early stopping based on date range.
    Stops scraping when encountering dates older than start_date.
    """
    page_counter = 1
    all_collected_records = []
    duplicate_count = 0
    stop_scraping = False
    
    print(f"\033[92m[INFO] Starting optimized phone extraction for date range: {start_date} to {end_date}\033[0m")
    
    while not stop_scraping:
        print(f"\033[92m[INFO] Scraping page {page_counter}...\033[0m")
        
        # Extract data from current page with date filtering
        page_records, should_stop = extract_phone_data_with_date_filter(
            driver, start_date, end_date
        )
        
        # Check for duplicates and add to collection
        for record in page_records:
            phone_number = record["Phone Number"]
            if phone_number not in seen_phone_numbers:
                all_collected_records.append(record)
                seen_phone_numbers.add(phone_number)
            else:
                duplicate_count += 1
                print(f"\033[93m[WARNING] Duplicate phone number '{phone_number}' found on page {page_counter}. Skipping.\033[0m")
        
        print(f"[INFO] Page {page_counter}: Collected {len(page_records)} new records")
        
        # Check if we should stop scraping
        if should_stop:
            print(f"\033[93m[INFO] Reached date boundary. Stopping extraction at page {page_counter}.\033[0m")
            stop_scraping = True
            break
        
        # Try to go to next page
        print(f"[DEBUG] Attempting to navigate to next page...")
        time.sleep(1)
        has_next = click_next_page(driver)
        if not has_next:
            print("[INFO] No more pages found. Finishing extraction.")
            break
        else:
            print(f"[SUCCESS] Successfully navigated to page {page_counter + 1}")
            
        page_counter += 1
        time.sleep(1)
    
    # Group records for output
    phone_groups = defaultdict(list)
    for record in all_collected_records:
        phone_groups["All"].append(record)
    
    # Print summary
    total_records = len(all_collected_records)
    print(f"\033[92m[SUMMARY] Extraction completed:\033[0m")
    print(f"  - Pages scraped: {page_counter}")
    print(f"  - Total phone numbers collected: {total_records}")
    print(f"  - Duplicates skipped: {duplicate_count}")
    
    if total_records > 0:
        print_grouped_phone_results(phone_groups)
    else:
        print("\033[93m[WARNING] No phone numbers found in the specified date range.\033[0m")

def main():
    run_optimized_phone_extraction(driver, start_date, end_date)
    time.sleep(5)
    driver.quit()
    cleanup_terminal()

if __name__ == "__main__":
    # Set up signal handlers for stopping
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Kill command
    print("🚦 Press Ctrl+C to stop the automation at any time")
    print("   (Note: On macOS terminal, use Ctrl+C, not Cmd+C)")
    main()