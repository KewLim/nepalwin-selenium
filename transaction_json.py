from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
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

# Setup the driver with error handling
try:
    print("🔧 Setting up Firefox driver...")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.maximize_window()
    print("✅ Firefox driver started successfully")
except Exception as e:
    print(f"❌ Firefox driver failed to start: {e}")
    print("\n🔧 Trying alternative Firefox setup...")
    try:
        # Try without GeckoDriverManager
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service()  # Use system geckodriver
        driver = webdriver.Firefox(service=service, options=options)
        driver.maximize_window()
        print("✅ Firefox driver started with alternative setup")
    except Exception as e2:
        print(f"❌ Alternative Firefox setup also failed: {e2}")
        print("\n🔧 Trying Chrome as fallback...")
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
            driver.maximize_window()
            print("✅ Chrome driver started successfully as fallback")
        except Exception as e3:
            print(f"❌ Chrome fallback also failed: {e3}")
            print("\n💡 Troubleshooting suggestions:")
            print("1. Make sure Firefox or Chrome is installed and updated")
            print("2. Try restarting your computer")
            print("3. Check if any antivirus is blocking webdrivers")
            print("4. Run as administrator")
            print("5. Try running: pip install --upgrade selenium webdriver-manager")
            sys.exit(1)



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
setup_automation_terminal("Deposit Crawler")

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

# ======== Entered Transaction =======

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


# ======= Print Logic Here =======

def extract_transaction_data_with_date_filter(driver, start_date, end_date, wait_timeout=20):
    """
    Extracts transaction data with early-stopping date filtering.
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
                
                # print(f"[DEBUG] Row {idx + 1}: Date {row_date}, Range {start_date} to {end_date}")
                
                # Date filtering logic
                if row_date > end_date:
                    print(f"[DEBUG] Row {idx + 1} too new ({row_date}), skipping")
                    continue
                
                if row_date < start_date:
                    print(f"[INFO] Row {idx + 1} too old ({row_date}), stopping scraping")
                    should_stop_scraping = True
                    break
                
                # Row is within date range (start_date <= row_date <= end_date)
                # Filter transaction type first
                txn_type = cols[6].text.strip() if len(cols) > 6 else ""
                print(f"[DEBUG] Row {idx + 1}: Found transaction type '{txn_type}'")

                if txn_type.upper() not in ("DEPOSIT", "WITHDRAWAL", "MANUAL_DEPOSIT", "MANUAL_WITHDRAWAL"):
                    print(f"[DEBUG] Row {idx + 1}: Skipping '{txn_type}' - not in allowed list")
                    continue

                print(f"[INFO] Row {idx + 1}: Collecting '{txn_type}' transaction")
                


                # Parse amount - different column based on transaction type
                if txn_type.upper() in ("WITHDRAWAL", "MANUAL_WITHDRAWAL"):
                    amount_text = cols[8].text.strip().replace("Rs", "").replace(",", "").strip()
                else:  # DEPOSIT, MANUAL_DEPOSIT
                    amount_text = cols[7].text.strip().replace("Rs", "").replace(",", "").strip()
                try:
                    amount = float(amount_text) if amount_text else 0.0
                except ValueError:
                    print(f"[WARNING] Invalid amount '{amount_text}' in row {idx + 1}, setting to 0.0")
                    amount = 0.0

                # Create record
                record = {
                    "Gateway": cols[5].text.strip(),
                    "Order ID": cols[0].text.strip(),   
                    "Phone Number": cols[4].text.strip(),  
                    "Amount": amount,  
                    "Time": full_date_str,  # Keep full timestamp
                    "Transaction Type": txn_type,
                    "Bank Tax": cols[10].text.strip() if len(cols) > 10 else "",
                    "Balance": cols[9].text.strip(),
                    "Date": row_date  # Add parsed date for easier processing
                }
                collected_records.append(record)
                
            except ValueError as e:
                print(f"[WARNING] Invalid date format '{full_date_str}' in row {idx + 1}: {e}")
                continue
                
        except Exception as e:
            print(f"[ERROR] Failed to process row {idx + 1}: {e}")
            continue
    
    print(f"[INFO] Collected {len(collected_records)} records from this page")
    print(f"[INFO] Should stop scraping: {should_stop_scraping}")
    
    return collected_records, should_stop_scraping



def print_grouped_results(gateway_groups):
    import json

    print(f"[DEBUG] print_grouped_results called with {len(gateway_groups)} gateway groups")
    for gateway, records in gateway_groups.items():
        print(f"[DEBUG] Gateway '{gateway}' has {len(records)} records")

    # Collect all records from all gateways
    all_records = []
    for gateway, records in gateway_groups.items():
        all_records.extend(records)

    # Group all transactions by Login ID (player)
    player_groups = defaultdict(list)

    for record in all_records:
        login_id = record["Phone Number"]
        player_groups[login_id].append(record)

    # Helper function to parse time safely
    def safe_parse_time(record):
        try:
            if record["Time"] and record["Time"].strip():
                return datetime.strptime(record["Time"], "%Y-%m-%d %H:%M:%S")
            else:
                return datetime.min
        except ValueError:
            return datetime.min

    # Analyze each player's transaction pattern
    json_output = []
    for login_id, transactions in player_groups.items():
        # Sort transactions by time (oldest first for pattern analysis)
        sorted_transactions = sorted(transactions, key=safe_parse_time)

        # Calculate totals and counts
        total_in = 0
        total_out = 0
        deposit_count = 0
        withdrawal_count = 0

        for txn in sorted_transactions:
            txn_type = txn.get("Transaction Type", "").upper()
            if txn_type in ("DEPOSIT", "MANUAL_DEPOSIT"):
                total_in += float(txn["Amount"])
                deposit_count += 1
            elif txn_type in ("WITHDRAWAL", "MANUAL_WITHDRAWAL"):
                total_out += float(txn["Amount"])
                withdrawal_count += 1

        winloss = total_in - total_out
        total_amount = total_in + total_out

        # Calculate bonus based on deposit count (cumulative)
        bonus_amount = 0
        if deposit_count >= 5:
            bonus_amount += 50
        if deposit_count >= 10:
            bonus_amount += 100
        if deposit_count >= 15:
            bonus_amount += 150
        if deposit_count >= 20:
            bonus_amount += 200
        if deposit_count >= 30:
            bonus_amount += 500

        # Calculate bonus based on total deposit amount (Total In) (cumulative)
        depo_amount_bonus = 0
        if total_in >= 500:
            depo_amount_bonus += 18
        if total_in >= 1000:
            depo_amount_bonus += 28
        if total_in >= 3000:
            depo_amount_bonus += 38
        if total_in >= 5000:
            depo_amount_bonus += 58
        if total_in >= 10000:
            depo_amount_bonus += 108

        # Check eligibility: deposit followed by withdrawal > threshold before next deposit
        eligible = False
        i = 0
        while i < len(sorted_transactions):
            txn = sorted_transactions[i]
            txn_type = txn.get("Transaction Type", "").upper()

            # Look for a deposit
            if txn_type in ("DEPOSIT", "MANUAL_DEPOSIT"):
                deposit_amount = float(txn["Amount"])

                # Look ahead for withdrawals before next deposit
                withdrawals_sum = 0
                j = i + 1

                while j < len(sorted_transactions):
                    next_txn = sorted_transactions[j]
                    next_type = next_txn.get("Transaction Type", "").upper()

                    if next_type in ("DEPOSIT", "MANUAL_DEPOSIT"):
                        # Found next deposit, stop looking
                        break
                    elif next_type in ("WITHDRAWAL", "MANUAL_WITHDRAWAL"):
                        withdrawals_sum += float(next_txn["Amount"])

                    j += 1

                # Check if withdrawal sum > 1000 (and deposit >= 500 as example)
                if deposit_amount >= 500 and withdrawals_sum > 1000:
                    eligible = True
                    break

            i += 1

        # Calculate total bonus and turnover
        depo_wd_bonus = 68 if eligible else 0
        total_bonus = depo_wd_bonus + depo_amount_bonus + bonus_amount
        turnover = total_bonus * 2  # Turnover is always 2x of Total Bonus

        player_record = {
            "Login ID": login_id,
            "Amount": f"{total_amount:.2f}",
            "Total In": f"{total_in:.2f}",
            "Deposit Count": deposit_count,
            "Total Out": f"{total_out:.2f}",
            "Withdrawal Count": withdrawal_count,
            "winloss": f"{winloss:.2f}",
            "Depo/WD Bonus": depo_wd_bonus,
            "Depo Amount Bonus": depo_amount_bonus,
            "Depo Count Bonus": bonus_amount,
            "Total Bonus": total_bonus,
            "Turnover": turnover,
            "_total_bonus_numeric": total_bonus  # Temporary field for sorting
        }
        json_output.append(player_record)

    # Sort by Total Bonus (descending - big to small)
    json_output.sort(key=lambda x: x["_total_bonus_numeric"], reverse=True)

    # Remove temporary sorting field
    for record in json_output:
        del record["_total_bonus_numeric"]

    # Write JSON to file
    with open("selenium_project/json_transaction_output.json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)

    # Print summary to console
    total_deposits = sum(1 for record in all_records if record.get("Transaction Type", "").upper() in ("DEPOSIT", "MANUAL_DEPOSIT"))
    total_withdrawals = sum(1 for record in all_records if record.get("Transaction Type", "").upper() in ("WITHDRAWAL", "MANUAL_WITHDRAWAL"))
    eligible_count = sum(1 for player in json_output if player["Total Bonus"] > 0)
    total_bonus_sum = sum(player["Total Bonus"] for player in json_output)

    print(f"\033[92m{'='*80}\033[0m")
    print(f"\033[92m                    JSON OUTPUT GENERATED (PLAYER-BASED)\033[0m")
    print(f"\033[92m{'='*80}\033[0m")
    print(f"\033[95m  Unique Players: \033[92m{len(player_groups)}\033[0m")
    print(f"\033[95m  Eligible Players: \033[92m{eligible_count}\033[0m")
    print(f"\033[95m  Eligible Bonus: \033[92m{total_bonus_sum} (Total)\033[0m")
    print(f"\033[95m  Total Deposit Transactions: \033[92m{total_deposits}\033[0m")
    print(f"\033[95m  Total Withdrawal Transactions: \033[92m{total_withdrawals}\033[0m")
    print(f"\033[95m  Output File: \033[92mselenium_project/json_transaction_output.json\033[0m")
    print(f"\033[92m{'='*80}\033[0m")



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


def run_optimized_transaction_extraction(driver, start_date, end_date):
    """
    Optimized extraction with early stopping based on date range.
    Stops scraping when encountering dates older than start_date.
    """
    page_counter = 1
    all_collected_records = []
    duplicate_count = 0
    stop_scraping = False
    
    print(f"\033[92m[INFO] Starting optimized extraction for date range: {start_date} to {end_date}\033[0m")
    
    while not stop_scraping:
        print(f"\033[92m[INFO] Scraping page {page_counter}...\033[0m")
        
        # Extract data from current page with date filtering
        page_records, should_stop = extract_transaction_data_with_date_filter(
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
    
    # Group records by gateway for output
    gateway_groups = defaultdict(list)
    for record in all_collected_records:
        gateway_groups[record["Gateway"]].append(record)
    
    # Print summary
    total_records = len(all_collected_records)
    print(f"\033[92m[SUMMARY] Extraction completed:\033[0m")
    print(f"  - Pages scraped: {page_counter}")
    print(f"  - Total records collected: {total_records}")
    print(f"  - Unique gateways: {len(gateway_groups)}")
    print(f"  - Duplicates skipped: {duplicate_count}")
    
    if total_records > 0:
        print_grouped_results(gateway_groups)
    else:
        print("\033[93m[WARNING] No records found in the specified date range.\033[0m")
    
def show_post_crawl_menu():
    """Show menu after crawling is complete"""
    print("\n" + "="*70)
    print("           CRAWLING COMPLETED - SELECT NEXT ACTION")
    print("="*70)
    print("1. Run Phone Number Crawler Script")
    print("2. Run Add Deposit Script (with start Order ID configuration)")
    print("3. Run Add Player Script")
    print("4. Exit")
    print("="*70)

    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            if choice == "1":
                print("\n🚀 Starting Phone Number Crawler Script...")
                print("="*70)
                import subprocess
                subprocess.run(["python", "selenium-crawler-phone.py"], check=False)
                return
            elif choice == "2":
                print("\n🚀 Starting Add Deposit Script...")
                print("="*70)
                import subprocess
                subprocess.run(["python", "selenium-add-deposit.py"], check=False)
                return
            elif choice == "3":
                print("\n🚀 Starting Add Player Script...")
                print("="*70)
                import subprocess
                subprocess.run(["python", "selenium-add-player.py"], check=False)
                return
            elif choice == "4":
                print("\n✅ Exiting...")
                return
            else:
                print("❌ Invalid choice. Please enter 1-4.")
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
            return

def main():
    run_optimized_transaction_extraction(driver, start_date, end_date)
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