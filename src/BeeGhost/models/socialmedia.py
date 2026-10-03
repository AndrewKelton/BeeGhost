
from selenium.webdriver import Chrome as ChromeSelenium
from undetected_chromedriver import Chrome as ChromeUndetected
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import traceback
from abc import ABC, abstractmethod
from typing import Any
import sys

WAIT_TIME = 15 # seconds

class SocialMedia(ABC):
    
    def __init__(self, username : str, password : str, cookies : dict[str, Any] | None, driver : ChromeSelenium | ChromeUndetected):
        self.username = username
        self.password = password
        self.cookies = cookies
        self.driver = driver
        
    def navigate_to_url(self, url : str):
        """Navigates to the url input by user"""
        
        try:    
            self.driver.get(url=url)
            print(f"Navigated to {self.driver.current_url}")
        
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    def click_button(self, ref : str) -> bool:
        """Clicks a button of ref : str"""
        
        try:    
            button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, ref))
            )
            button.click()
            
            return True

        except TimeoutException as e:
            traceback.print_exc()
            # print(f"Error: {e}", file=sys.stderr)
            return False
        
            
    def refresh(self):
        """Refreshes the driver"""
        self.driver.refresh()
    
    def close_browser(self):
        """Closes the browser window"""
        self.driver.quit()
    
    @abstractmethod
    def save_cookies(self):
        """Saves cookies into designated json file"""
        pass
    
    @abstractmethod
    def login(self) -> bool:
        """Logs into designated account"""
        pass
    