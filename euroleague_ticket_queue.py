"""
EuroLeague Final 4 Ticket Queue Auto-Joiner
This script automatically opens the ticketing platform and helps you join the queue
when it opens, while maintaining your logged-in session.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timedelta
import sys

# Configuration
TICKET_URL = "https://euroleaguef4tickets.com/en/"

# Set the exact time when ticket sales open (adjust as needed)
# IMPORTANT: This time is in YOUR LOCAL TIMEZONE (your computer's time)
# If the queue opens at 10:00 CET and you're in Zagreb (CET), set it to "10:00:00"
# If it opens in a different timezone, convert to YOUR timezone first
# QUEUE_OPEN_TIME = "10:00:00"  # Format: HH:MM:SS in 24-hour format
QUEUE_OPEN_TIME = "21:13:00"  # Format: HH:MM:SS in 24-hour format in Greek timezone

class TicketQueueBot:
    def __init__(self):
        self.driver = None
        
    def setup_browser(self):
        """Initialize the browser with options to avoid detection"""
        print("Setting up browser...")
        print("Installing/updating ChromeDriver automatically...")
        
        options = webdriver.ChromeOptions()
        
        # Uncomment the next line if you want to see the browser (recommended for first run)
        # options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent to look like a real browser
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Use webdriver-manager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Browser ready!")
        
    def manual_login(self):
        """Navigate to login page and wait for user to log in manually"""
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("Opening the ticket website...")
        print("Please log in with your EuroLeague ID in the browser window.")
        print("After you've successfully logged in, return here and press ENTER.")
        print("="*60 + "\n")
        
        self.driver.get(TICKET_URL)
        time.sleep(3)
        
        # Wait for user to confirm they've logged in
        input("Press ENTER after you have logged in successfully...")
        
        # Verify we're still on the right domain
        current_url = self.driver.current_url
        print(f"\nCurrent URL: {current_url}")
        print("Login session saved!")
        
    def wait_until_queue_opens(self, target_time_str):
        """Wait until the specified time to join the queue"""
        # Parse target time
        target_time = datetime.strptime(target_time_str, "%H:%M:%S").time()
        today = datetime.now().date()
        target_datetime = datetime.combine(today, target_time)
        
        # If target time has already passed today, assume it's tomorrow
        if datetime.now() > target_datetime:
            target_datetime += timedelta(days=1)
        
        print(f"\nTarget queue opening time: {target_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        while True:
            now = datetime.now()
            time_remaining = (target_datetime - now).total_seconds()
            
            if time_remaining <= 0:
                print("\n🎯 TIME TO JOIN THE QUEUE!")
                break
            
            # Show countdown
            hours, remainder = divmod(int(time_remaining), 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"\rTime until queue opens: {hours:02d}:{minutes:02d}:{seconds:02d}", end='', flush=True)
            
            # Refresh page periodically to keep session alive (every 2 minutes)
            if time_remaining > 120 and int(time_remaining) % 120 == 0:
                print("\n🔄 Refreshing page to keep session alive...")
                self.driver.refresh()
                time.sleep(2)
            
            time.sleep(1)
    
    def join_queue(self):
        """Continuously refresh and try to join the queue"""
        print("\n" + "="*60)
        print("ATTEMPTING TO JOIN QUEUE")
        print("="*60)

        attempt = 0
        
        while True:
            attempt += 1
            print(f"\nAttempt {attempt}")
            
            try:
                # Refresh the page
                self.driver.refresh()
                time.sleep(3)
                
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                # Check if we're in the Queue-it system
                if "queue-it.net" in current_url:
                    print("✅ You're in the Queue-it system!")
                    print(f"Queue URL: {current_url}")
                    
                    # Check for specific queue indicators
                    if "you are now in line" in page_source or "in line" in page_source:
                        print("🎉 Successfully joined the queue!")
                        return True
                    elif "expected service time" in page_source:
                        print("🎉 You're waiting in the queue!")
                        return True
                    elif "your turn" in page_source:
                        print("🎉 Found queue confirmation!")
                        return True
                    else:
                        print("⏳ Queue-it detected, checking status...")
                
                # Check if we're being redirected to queue
                elif "platiniumgroup" in current_url.lower():
                    print("✅ Detected queue redirect!")
                    time.sleep(3)  # Wait for queue page to load
                    return True
                
                # Look for queue elements on the main page
                try:
                    # Queue-it specific elements
                    queue_indicators = [
                        "//div[contains(@class, 'queue')]",
                        "//div[contains(text(), 'queue')]",
                        "//div[contains(text(), 'waiting')]",
                        "//div[contains(text(), 'in line')]",
                        "//*[contains(@id, 'queue')]",
                    ]
                    
                    for selector in queue_indicators:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            print(f"✅ Found queue indicator: {selector}")
                            time.sleep(2)
                            return True
                            
                except Exception as e:
                    pass
                
                print(f"Queue not yet available, will retry in 10 seconds...")
                time.sleep(10)  # Wait between attempts
                
            except Exception as e:
                print(f"⚠️ Error on attempt {attempt}: {str(e)}")
                time.sleep(10)
        
        print("\n⚠️ Max attempts reached. Please check the browser manually.")
        return False
    
    def monitor_queue_status(self):
        """Monitor queue status after joining"""
        print("\n" + "="*60)
        print("MONITORING QUEUE STATUS")
        print("="*60)
        print("Keep this window open. You'll be notified of any changes.")
        print("The browser window will stay open for you to complete the purchase.")
        print("="*60 + "\n")
        
        try:
            last_progress = None
            check_count = 0
            
            while True:
                check_count += 1
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                # Check if we've exited the queue (back to main ticket site)
                if "queue-it.net" not in current_url and "euroleaguef4tickets.com" in current_url:
                    print("\n\n🎉 YOU'RE THROUGH THE QUEUE!")
                    print("🎟️ You can now purchase your tickets!")
                    print("Complete your purchase in the browser window.")
                    break
                
                # Try to extract queue position/progress info
                try:
                    # Look for expected service time
                    if "expected service time" in page_source or "expectedservicetime" in page_source:
                        # Try to find the time element
                        time_elements = self.driver.find_elements(By.XPATH, 
                            "//*[contains(text(), 'AM') or contains(text(), 'PM') or contains(text(), 'minutes')]")
                        if time_elements:
                            time_text = time_elements[0].text
                            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] ⏰ Expected service time: {time_text}   ", 
                                  end='', flush=True)
                    
                    # Look for progress indicator
                    progress_elements = self.driver.find_elements(By.XPATH, 
                        "//*[contains(@class, 'progress') or contains(@id, 'progress')]")
                    if progress_elements:
                        for elem in progress_elements:
                            style = elem.get_attribute("style")
                            if style and "width" in style:
                                # Extract progress percentage
                                import re
                                match = re.search(r'width:\s*(\d+)', style)
                                if match:
                                    progress = match.group(1)
                                    if progress != last_progress:
                                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📊 Progress: {progress}%")
                                        last_progress = progress
                    
                    # Check for "your turn" or similar messages
                    if "your turn" in page_source or "you will now be redirected" in page_source:
                        print("\n\n🎉 IT'S YOUR TURN!")
                        print("The page should redirect automatically...")
                        time.sleep(5)
                        continue
                    
                except Exception as e:
                    pass
                
                # Generic status update every 10 checks
                if check_count % 10 == 0:
                    if "queue-it.net" in current_url:
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ Still in queue, monitoring... (check #{check_count})")
                    else:
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📍 Current URL: {current_url[:60]}...")
                
                time.sleep(6)  # Check every 6 seconds (Queue-it updates every 40s typically)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")
        except Exception as e:
            print(f"\n\n⚠️ Error during monitoring: {str(e)}")
            print("Check the browser manually.")
    
    def run(self, wait_for_time=True):
        """Main execution flow"""
        try:
            self.setup_browser()
            self.manual_login()
            
            if wait_for_time:
                # Wait until queue opens
                self.wait_until_queue_opens(QUEUE_OPEN_TIME)
            else:
                print("\nSkipping wait time (queue should be open now)")
            
            # Try to join the queue
            success = self.join_queue()
            
            if success:
                # Monitor the queue
                self.monitor_queue_status()
            
            # Keep browser open for manual completion
            print("\n✅ Script complete! Browser window will remain open.")
            print("Press Ctrl+C to close the browser and exit.\n")
            
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\nClosing browser...")
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                try:
                    input("\nPress ENTER to close the browser and exit...")
                except:
                    pass
                self.driver.quit()

if __name__ == "__main__":
    print("="*60)
    print("EuroLeague Final 4 Ticket Queue Auto-Joiner")
    print("="*60)
    print("\nIMPORTANT SETUP INSTRUCTIONS:")
    print("1. Make sure Chrome browser is installed")
    print("2. Install required packages: pip install -r requirements.txt")
    print("   (ChromeDriver will be downloaded automatically)")
    print("3. Update QUEUE_OPEN_TIME variable if needed")
    print("\nOptions:")
    print("  [1] Wait until queue opens (recommended)")
    print("  [2] Join queue immediately (for testing or if queue is open)")
    print("="*60)
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    bot = TicketQueueBot()
    
    if choice == "1":
        bot.run(wait_for_time=True)
    elif choice == "2":
        bot.run(wait_for_time=False)
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)
