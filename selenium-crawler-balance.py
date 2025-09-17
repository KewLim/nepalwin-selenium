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
        print("[WARNING] Browser was already closed or unavailable")
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
        "url": "https://bo.95np.com/user/login/",  # Update this with correct 95np URL
        "username": "tommy8888",     # Update this with correct 95np username
        "password": "tommy6666",     # Update this with correct 95np password
        "username_xpath": "//input[@placeholder='Username:']",  # Update if different
        "password_xpath": "//input[@placeholder='Password:']"   # Update if different
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
setup_automation_terminal("Balance Crawler")

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



# ======== Entered Main Page ========

# ======== Entered Balance Tracking =======

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


# ======= Balance Extraction Logic Here =======

def extract_balance_data_with_date_filter(driver, start_date, end_date, wait_timeout=20):
    """
    Extracts balance data with early-stopping date filtering.
    Returns (collected_records, should_stop_scraping)
    """
    print(f"[INFO] Filtering for dates: {start_date} to {end_date}")

    # Find the Bank Transaction Record table
    try:
        title_elem = driver.find_element(
            By.XPATH, "//div[@class='ant-pro-table-list-toolbar-title' and normalize-space()='Bank Transaction Record']"
        )
        table_elem = title_elem.find_element(
            By.XPATH, "./ancestor::div[contains(@class,'ant-pro-card')]//table"
        )
        rows = table_elem.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"[SUCCESS] Found {len(rows)} rows in Bank Transaction Record table")
    except Exception as e:
        print(f"[ERROR] Could not find Bank Transaction Record table: {e}")
        return [], True  # Stop if we can't find the table

    if not rows:
        print("[WARNING] No rows found in table")
        return [], False

    collected_records = []
    should_stop_scraping = False

    print(f"[INFO] Processing {len(rows)} rows with date filtering...")
    time.sleep(1)  # Stability delay

    for idx, row in enumerate(rows):
        try:
            cols = row.find_elements(By.TAG_NAME, 'td')

            if len(cols) < 6:  # Need at least 6 columns
                print(f"[WARNING] Row {idx + 1} has only {len(cols)} columns. Skipping.")
                continue

            # Skip summary rows
            first_col_text = cols[0].text.strip()
            if "Page Summary" in first_col_text or "Total Summary" in first_col_text:
                print(f"[INFO] Skipping summary row: '{first_col_text}'")
                continue

            # Extract date from column 2 (format: '2025-08-14 16:35:02')
            full_date_str = cols[1].text.strip()
            if not full_date_str:
                print(f"[WARNING] No date in row {idx + 1}, skipping")
                continue

            try:
                # Extract only the date part (ignore time)
                date_str = full_date_str.split(" ")[0]  # '2025-08-14'
                row_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                # Date filtering logic
                if row_date > end_date:
                    print(f"[DEBUG] Row {idx + 1} too new ({row_date}), skipping")
                    continue

                if row_date < start_date:
                    print(f"[INFO] Row {idx + 1} too old ({row_date}), stopping scraping")
                    should_stop_scraping = True
                    break

                # Row is within date range (start_date <= row_date <= end_date)
                # Extract balance information
                txn_type = cols[6].text.strip() if len(cols) > 6 else ""
                print(f"[DEBUG] Row {idx + 1}: Found transaction type '{txn_type}'")

                # Focus on all transaction types to track balance changes
                print(f"[INFO] Row {idx + 1}: Collecting balance data for '{txn_type}' transaction")

                # Parse amount - different column based on transaction type
                if txn_type.upper() in ("WITHDRAWAL", "ADJUSTMENTDEDUCT", "CASH_OUT"):
                    amount_text = cols[8].text.strip().replace("Rs", "").replace(",", "").strip()
                else:  # DEPOSIT, MANUAL_DEPOSIT, ADJUSTMENTADD, CASH_IN
                    amount_text = cols[7].text.strip().replace("Rs", "").replace(",", "").strip()
                try:
                    amount = float(amount_text) if amount_text else 0.0
                except ValueError:
                    print(f"[WARNING] Invalid amount '{amount_text}' in row {idx + 1}, setting to 0.0")
                    amount = 0.0

                # Extract balance from column 9
                balance_text = cols[9].text.strip().replace("Rs", "").replace(",", "").strip()
                try:
                    balance = float(balance_text) if balance_text else 0.0
                except ValueError:
                    print(f"[WARNING] Invalid balance '{balance_text}' in row {idx + 1}, setting to 0.0")
                    balance = 0.0

                # Create balance record
                record = {
                    "Gateway": cols[5].text.strip(),
                    "Order ID": cols[0].text.strip(),
                    "Phone Number": cols[4].text.strip(),
                    "Amount": amount,
                    "Balance": balance,
                    "Time": full_date_str,  # Keep full timestamp
                    "Transaction Type": txn_type,
                    "Bank Tax": cols[10].text.strip() if len(cols) > 10 else "",
                    "Date": row_date  # Add parsed date for easier processing
                }
                collected_records.append(record)

            except ValueError as e:
                print(f"[WARNING] Invalid date format '{full_date_str}' in row {idx + 1}: {e}")
                continue

        except Exception as e:
            print(f"[ERROR] Failed to process row {idx + 1}: {e}")
            continue

    print(f"[INFO] Collected {len(collected_records)} balance records from this page")
    print(f"[INFO] Should stop scraping: {should_stop_scraping}")

    return collected_records, should_stop_scraping



def print_balance_results(gateway_groups):
    print(f"[DEBUG] print_balance_results called with {len(gateway_groups)} gateway groups")
    for gateway, records in gateway_groups.items():
        print(f"[DEBUG] Gateway '{gateway}' has {len(records)} balance records")

    with open("selenium_project/selenium-balance_history.txt", "w", encoding="utf-8") as f:

        f.write("="*80 + "\n")
        f.write("                         BALANCE TRACKING REPORT\n")
        f.write("="*80 + "\n")
        print(f"\033[92m{'='*80}\033[0m")
        print(f"\033[92m                         BALANCE TRACKING REPORT\033[0m")
        print(f"\033[92m{'='*80}\033[0m")

        for gateway, records in gateway_groups.items():
            # Sort records by time (latest first) with error handling
            def safe_parse_time(record):
                try:
                    if record["Time"] and record["Time"].strip():
                        return datetime.strptime(record["Time"], "%Y-%m-%d %H:%M:%S")
                    else:
                        return datetime.min  # Put records with no time at the end
                except ValueError:
                    print(f"[WARNING] Invalid time format: '{record['Time']}'")
                    return datetime.min

            sorted_records = sorted(records, key=safe_parse_time, reverse=True)

            # Get latest and earliest balance for this gateway
            latest_balance = sorted_records[0]["Balance"] if sorted_records else 0.0
            earliest_balance = sorted_records[-1]["Balance"] if sorted_records else 0.0
            balance_change = latest_balance - earliest_balance

            header = f"\n==== {gateway} Balance History ({len(records)} record{'s' if len(records) != 1 else ''}) ====\n"
            header += f"Latest Balance: Rs {latest_balance:,.2f} | Earliest Balance: Rs {earliest_balance:,.2f} | Change: Rs {balance_change:+,.2f}\n"
            print(f"\033[92m{header}\033[0m")
            f.write(header)

            for i, record in enumerate(sorted_records, 1):
                entry = (
                    f"\nRecord #{i}\n"
                    f"Order ID: {record['Order ID']}\n"
                    f"Transaction Type: {record.get('Transaction Type', 'Unknown')}\n"
                    f"Phone Number: {record['Phone Number']}\n"
                    f"Amount: Rs {record['Amount']:,.2f}\n"
                    f"Balance After Transaction: Rs {record['Balance']:,.2f}\n"
                    f"Bank Charges: {record.get('Bank Tax', 'N/A')}\n"
                    f"Time: {record['Time']}\n"
                )
                print(f"\033[94m{entry}\033[0m")
                f.write(entry)

        total_records = sum(len(records) for records in gateway_groups.values())

        # Create grand summary
        f.write("\n")
        grand_summary_header = f"=========================== BALANCE SUMMARY ===========================\n\n"
        print(f"\033[92m{grand_summary_header}\033[0m", end="")
        f.write(grand_summary_header)

        print(f"\033[95m  Total Records Tracked: \033[92m{total_records}\033[95m\n\033[0m", end="")
        print(f"\033[95m  Gateways Monitored: \033[92m{len(gateway_groups)}\033[95m\n\n\033[0m", end="")
        f.write(f"  Total Records Tracked: {total_records}\n")
        f.write(f"  Gateways Monitored: {len(gateway_groups)}\n\n")

        # Summary for each gateway
        for gateway, records in gateway_groups.items():
            # Sort to get latest balance
            sorted_records = sorted(records, key=safe_parse_time, reverse=True)
            latest_balance = sorted_records[0]["Balance"] if sorted_records else 0.0

            # Extract date from the first record's time
            try:
                if records[0]["Time"] and records[0]["Time"].strip():
                    transaction_date = datetime.strptime(records[0]["Time"], "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y")
                else:
                    transaction_date = "Unknown"
            except (ValueError, IndexError):
                transaction_date = "Unknown"

            # Create gateway summary
            gateway_header = f"==== {gateway}_{transaction_date} ====\n\n"
            print(f"\033[92m{gateway_header}\033[0m", end="")
            f.write(gateway_header)

            print(f"\033[95m  Records Tracked: \033[92m{len(records)}\033[95m\n\033[0m", end="")
            print(f"\033[95m  Current Balance: \033[92mRs {latest_balance:,.2f}\033[95m\n\n\033[0m", end="")

            f.write(f"  Records Tracked: {len(records)}\n")
            f.write(f"  Current Balance: Rs {latest_balance:,.2f}\n\n")


def click_next_page(driver, wait_timeout=10):
    try:
        selectors_to_try = [
            "//li[@title='Next Page' and @aria-disabled='false']//button[@class='ant-pagination-item-link']",
            # Fallback: by class only (less strict)
            "//button[@class='ant-pagination-item-link']",
        ]

        next_button = None
        working_selector = None

        print("[DEBUG] Searching for Next button...")

        for selector in selectors_to_try:
            try:
                print(f"[DEBUG] Trying: {selector}")
                next_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                working_selector = selector
                print(f"[SUCCESS] Found next button using: {selector}")
                break
            except Exception as e:
                print(f"[DEBUG] Failed: {e}")
                continue

        if not next_button:
            print("[ERROR] Could not find Next button with any selector")
            return False

        # Try multiple click strategies
        print(f"[DEBUG] Found button, attempting to click using: {working_selector}")

        # Strategy 1: Regular click
        try:
            next_button.click()
            time.sleep(4)
            print(f"[INFO] Successfully clicked Next button with regular click")
            return True
        except Exception as e:
            print(f"[DEBUG] Regular click failed: {e}")

        # Strategy 2: JavaScript click
        try:
            print("[DEBUG] Trying JavaScript click...")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
            print(f"[INFO] Successfully clicked Next button with JavaScript")
            return True
        except Exception as e:
            print(f"[DEBUG] JavaScript click failed: {e}")

        # Strategy 3: Action chains click
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            print("[DEBUG] Trying ActionChains click...")
            ActionChains(driver).move_to_element(next_button).click().perform()
            time.sleep(2)
            print(f"[INFO] Successfully clicked Next button with ActionChains")
            return True
        except Exception as e:
            print(f"[DEBUG] ActionChains click failed: {e}")

        # Strategy 4: Scroll into view then click
        try:
            print("[DEBUG] Trying scroll into view then click...")
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            next_button.click()
            time.sleep(2)
            print(f"[INFO] Successfully clicked Next button after scrolling into view")
            return True
        except Exception as e:
            print(f"[DEBUG] Scroll + click failed: {e}")

        print("[ERROR] All click strategies failed")
        return False

    except Exception as e:
        print(f"[WARNING] Could not click Next button: {e}")
        return False




gateway_groups = defaultdict(list)  # Global collector
seen_order_ids = set()  # Track seen Order IDs to prevent duplicates


def run_optimized_balance_extraction(driver, start_date, end_date):
    """
    Optimized balance extraction with early stopping based on date range.
    Stops scraping when encountering dates older than start_date.
    """
    page_counter = 1
    all_collected_records = []
    duplicate_count = 0
    stop_scraping = False

    print(f"\033[92m[INFO] Starting optimized balance extraction for date range: {start_date} to {end_date}\033[0m")

    while not stop_scraping:
        print(f"\033[92m[INFO] Scraping page {page_counter}...\033[0m")

        # Extract balance data from current page with date filtering
        page_records, should_stop = extract_balance_data_with_date_filter(
            driver, start_date, end_date
        )

        # Check for duplicates and add to collection
        for record in page_records:
            order_id = record["Order ID"]
            if order_id not in seen_order_ids:
                all_collected_records.append(record)
                seen_order_ids.add(order_id)
            else:
                duplicate_count += 1
                print(f"\033[93m[WARNING] Duplicate Order ID '{order_id}' found on page {page_counter}. Skipping.\033[0m")

        print(f"[INFO] Page {page_counter}: Collected {len(page_records)} new balance records")

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

    # Group records by gateway for output
    gateway_groups = defaultdict(list)
    for record in all_collected_records:
        gateway_groups[record["Gateway"]].append(record)

    # Print summary
    total_records = len(all_collected_records)
    print(f"\033[92m[SUMMARY] Balance extraction completed:\033[0m")
    print(f"  - Pages scraped: {page_counter}")
    print(f"  - Total balance records collected: {total_records}")
    print(f"  - Unique gateways: {len(gateway_groups)}")
    print(f"  - Duplicates skipped: {duplicate_count}")

    if total_records > 0:
        print_balance_results(gateway_groups)
    else:
        print("\033[93m[WARNING] No balance records found in the specified date range.\033[0m")

def main():
    run_optimized_balance_extraction(driver, start_date, end_date)
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