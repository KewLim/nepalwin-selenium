from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time

def test_firefox_connection():
    """Test Firefox WebDriver connection"""
    try:
        print("[INFO] Setting up Firefox WebDriver...")
        
        # Configure Firefox options
        options = Options()
        # Uncomment the line below for headless mode
        # options.add_argument('--headless')
        
        # Use WebDriverManager to automatically download and manage GeckoDriver
        service = Service(GeckoDriverManager().install())
        
        print("[INFO] Starting Firefox browser...")
        driver = webdriver.Firefox(service=service, options=options)
        
        print("[SUCCESS] Firefox browser started successfully!")
        
        # Test navigation
        print("[INFO] Navigating to test page...")
        driver.get("https://www.google.com")
        
        print(f"[INFO] Page title: {driver.title}")
        print(f"[INFO] Current URL: {driver.current_url}")
        
        # Wait a few seconds to see the browser
        print("[INFO] Waiting 5 seconds...")
        time.sleep(5)
        
        print("[INFO] Closing browser...")
        driver.quit()
        
        print("[SUCCESS] Test completed successfully! Firefox WebDriver is working correctly.")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing Firefox WebDriver: {e}")
        print("\n[INFO] Troubleshooting tips:")
        print("1. Make sure Firefox is installed on your system")
        print("2. Check if Firefox is in your system PATH")
        print("3. Try running Firefox manually to ensure it works")
        return False

if __name__ == "__main__":
    test_firefox_connection()