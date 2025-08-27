import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from config import CHROME_OPTIONS, TIMEOUT, DELAY_BETWEEN_REQUESTS

class WebDriverManager:
    """Manage Chrome WebDriver with proper error handling"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with proper configuration"""
        try:
            self.logger.info("====== WebDriver manager ======")
            
            # Setup Chrome options
            chrome_options = Options()
            for option in CHROME_OPTIONS:
                chrome_options.add_argument(option)
            
            # Try different approaches to get ChromeDriver
            service = None
            
            # Method 1: Use WebDriverManager
            try:
                self.logger.info("Attempting to download ChromeDriver...")
                driver_path = ChromeDriverManager().install()
                self.logger.info(f"ChromeDriver downloaded to: {driver_path}")
                service = Service(driver_path)
            except Exception as e:
                self.logger.warning(f"WebDriverManager failed: {e}")
            
            # Method 2: Try with default service if WebDriverManager failed
            if not service:
                self.logger.info("Trying with default service...")
                service = Service()
            
            # Create WebDriver instance
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(TIMEOUT)
            
            # Test the driver with a simple navigation
            self.logger.info("Testing WebDriver with Google...")
            self.driver.get("https://www.google.com")
            self.logger.info(f"WebDriver test successful: {self.driver.title}")
            
            self.logger.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            
            # Additional error information
            if "193" in str(e):
                self.logger.error("This appears to be a ChromeDriver binary issue.")
                self.logger.error("Try manually installing Chrome browser or updating it.")
            
            return False
    
    def get_driver(self):
        """Get the WebDriver instance"""
        if not self.driver:
            if not self.setup_driver():
                raise Exception("Failed to setup WebDriver")
        return self.driver
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def navigate_to_url(self, url):
        """Navigate to a URL with error handling"""
        try:
            driver = self.get_driver()
            driver.get(url)
            time.sleep(DELAY_BETWEEN_REQUESTS)
            return True
        except TimeoutException:
            self.logger.error(f"Timeout loading URL: {url}")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to URL {url}: {e}")
            return False
    
    def wait_for_element(self, by, value, timeout=TIMEOUT):
        """Wait for an element to be present"""
        try:
            driver = self.get_driver()
            wait = WebDriverWait(driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            self.logger.error(f"Element not found: {by}={value}")
            return None
    
    def wait_for_elements(self, by, value, timeout=TIMEOUT):
        """Wait for elements to be present"""
        try:
            driver = self.get_driver()
            wait = WebDriverWait(driver, timeout)
            return wait.until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            self.logger.error(f"Elements not found: {by}={value}")
            return []
    
    def find_element_safe(self, by, value):
        """Find element with error handling"""
        try:
            driver = self.get_driver()
            return driver.find_element(by, value)
        except NoSuchElementException:
            self.logger.warning(f"Element not found: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {by}={value}: {e}")
            return None
    
    def find_elements_safe(self, by, value):
        """Find elements with error handling"""
        try:
            driver = self.get_driver()
            return driver.find_elements(by, value)
        except Exception as e:
            self.logger.error(f"Error finding elements {by}={value}: {e}")
            return []
    
    def get_page_source(self):
        """Get page source safely"""
        try:
            driver = self.get_driver()
            return driver.page_source
        except Exception as e:
            self.logger.error(f"Error getting page source: {e}")
            return ""
    
    def get_current_url(self):
        """Get current URL safely"""
        try:
            driver = self.get_driver()
            return driver.current_url
        except Exception as e:
            self.logger.error(f"Error getting current URL: {e}")
            return ""

    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_driver()
