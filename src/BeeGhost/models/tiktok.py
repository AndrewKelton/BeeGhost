# 

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import json

from BeeGhost.models.socialmedia import SocialMedia

class TikTok(SocialMedia):
    """This class is broken"""
    
    BASE_LINK = "https://www.tiktok.com/"
    LOGIN_LINK = "https://www.tiktok.com/login/phone-or-email/email/"
    PROFILE_LINK = "https://www.tiktok.com/@andrew.kelton4/"
    
    def __init__(self, username : str, password : str, cookies=None, headless=False):
        
        options = uc.ChromOptions()
        
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        
        driver = uc.Chrome(options=options)
        
        super().__init__(
            username=username,
            password=password,
            cookies=cookies,
            driver=driver
        )
    
    def login(self):
        
        self.driver.get(self.LOGIN_LINK)
        
        if self.cookies != None:
            
            for cookie in self.cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
        
            time.sleep(0.5)
        
        else:
            
            username = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.NAME, "username"))
            )
            username.send_keys(self.username)
            username.send_keys(Keys.RETURN)
            
            password = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.NAME, "password"))
            )
            password.send_keys(self.password)
            password.send_keys(Keys.RETURN)
            
        print(f"logged in as {self.username}")
        time.sleep(2.5)
    
    def save_cookies(self):
        "saves cookies to tiktok_cookies.json"
        
        cookies = self.driver.get_cookies()

        with open("tiktok_cookies.json", "w") as f:
            json.dump(cookies, f, indent=4)

        print("Cookies saved.")