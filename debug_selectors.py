from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def debug_page_elements():
    """Debug script to find the correct selectors"""
    
    # Setup Firefox
    options = Options()
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.maximize_window()
    
    try:
        print("[INFO] Navigating to login page...")
        driver.get("https://bo.nepalwin.com/user/login")
        
        # Login
        wait = WebDriverWait(driver, 40)
        print("[INFO] Logging in...")
        
        username_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username:']")))
        username_field.send_keys("kewlim888")
        
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password:']")))
        password_field.send_keys("aaaa1111")
        password_field.send_keys(Keys.ENTER)
        
        time.sleep(3)
        print("[SUCCESS] Logged in successfully")
        
        # Wait for page to load
        try:
            transaction_header = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//span[@class='ant-page-header-heading-title' and text()='Transaction']"))
            )
            print("[SUCCESS] Transaction header found")
        except:
            print("[WARNING] Transaction header not found, continuing...")
        
        # Debug: Find all possible sidebar elements
        print("\n[DEBUG] Searching for sidebar elements...")
        
        # Look for various sidebar patterns
        sidebar_patterns = [
            "//div[contains(@class, 'sidebar')]",
            "//div[contains(@class, 'menu')]",
            "//nav",
            "//aside",
            "//div[contains(@class, 'nav')]"
        ]
        
        for pattern in sidebar_patterns:
            try:
                elements = driver.find_elements(By.XPATH, pattern)
                if elements:
                    print(f"[FOUND] {len(elements)} elements matching: {pattern}")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            print(f"  Element {i+1}: class='{elem.get_attribute('class')}', text='{elem.text[:100]}'")
                        except:
                            print(f"  Element {i+1}: Unable to read attributes")
            except:
                continue
        
        # Look for buttons with "Member" text
        print("\n[DEBUG] Searching for Member buttons...")
        member_patterns = [
            "//button[contains(text(), 'Member')]",
            "//div[contains(text(), 'Member')]",
            "//span[contains(text(), 'Member')]",
            "//a[contains(text(), 'Member')]",
            "//*[contains(text(), 'Member')]"
        ]
        
        for pattern in member_patterns:
            try:
                elements = driver.find_elements(By.XPATH, pattern)
                if elements:
                    print(f"[FOUND] {len(elements)} elements matching: {pattern}")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            print(f"  Element {i+1}: tag='{elem.tag_name}', class='{elem.get_attribute('class')}', text='{elem.text}'")
                        except:
                            print(f"  Element {i+1}: Unable to read attributes")
            except:
                continue
        
        # Look for the current failing selector
        print(f"\n[DEBUG] Testing current selector...")
        try:
            current_selector = "//div[@class='sidebar-item-container']//button[.//div[text()='Member']]"
            elements = driver.find_elements(By.XPATH, current_selector)
            if elements:
                print(f"[FOUND] Current selector found {len(elements)} elements")
                for elem in elements:
                    print(f"  Element: visible={elem.is_displayed()}, enabled={elem.is_enabled()}")
            else:
                print("[NOT FOUND] Current selector found 0 elements")
        except Exception as e:
            print(f"[ERROR] Current selector failed: {e}")
        
        print("\n[INFO] Debug complete. Closing browser...")

        
    except Exception as e:
        print(f"[ERROR] Debug failed: {e}")
        print("\n[INFO] Closing browser...")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page_elements()