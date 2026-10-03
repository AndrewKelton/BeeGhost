from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
import time 
import json
import threading

from BeeGhost.models.socialmedia import SocialMedia
from BeeGhost.models.ratelimitchecker import RateLimitChecker
from BeeGhost.utils import start_quit_listener, sleep_randomly

class X(SocialMedia):
    
    BASE_LINK = "https://x.com/"
    LIKES_LINK = "https://x.com/i/history/likes"
    LOGIN_LINK = "https://x.com/i/jf/onboarding/web?mode=login"
    
    def __init__(self, username : str, password : str, cookies=None, headless=False):
    
        # PROFILE_LINK = f"https://x.com/{self.username}"
              
        options = uc.ChromeOptions()
        
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
                    
        driver = uc.Chrome(options=options)

        super().__init__(
            username=username,
            password=password,
            cookies=cookies,
            driver=driver,
        )
    
    def login(self) -> bool:
        
        self.driver.get(self.LOGIN_LINK)
        
        if self.cookies != None:
            # login with cookies
            
            for cookie in self.cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            
            return True
        
        else:
            # login with username + password
            
            username = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.NAME, "username_or_email"))
            )
            username.send_keys(self.username)
            username.send_keys(Keys.RETURN)
            
            try:
                password = WebDriverWait(self.driver, 15).until(
                    EC.visibility_of_element_located((By.NAME, "password"))
                )
                password.send_keys(self.password)
                password.send_keys(Keys.RETURN)
                
                print(f"logged in as {self.username}")
                
                return True
            
            except TimeoutException:
                # this will happen if we login too much
                
                self.driver.save_screenshot("x_login_error.png")
                raise RuntimeError(
                    "Password field did not appear. "
                    "X may have presented a login restriction or verification page."
                )
            
    def save_cookies(self):
        "saves cookies to x.json"
        
        cookies = self.driver.get_cookies()

        with open("x_cookies.json", "w") as f:
            json.dump(cookies, f, indent=4)

        print("Cookies saved.")
        
    def remove_likes(self):
        """Removes comments from associated X account.
        
        Returns:
            bool: True if the removal was successful, False otherwise.
        """
        
        self.navigate_to_url(self.LIKES_LINK)
    
        stop_event = threading.Event() # event flag
        start_quit_listener(stop_event) # listen for 'quit' early termination

        rateLimitChecker = RateLimitChecker(max_requests=15)
        
        total_likes_counter = 0
        success = True

        try:
            while True:
                
                if not rateLimitChecker.is_allowed():
                    stop_event.wait(rateLimitChecker.get_sleep_time())
                
                if stop_event.is_set():
                    break
                
                if self.click_button("//button[@data-testid='unlike']"): # remove liked
                    rateLimitChecker.record_request()
                    print(f"successfully removed a like")
                    total_likes_counter = total_likes_counter + 1
                    success = True # lowk can never fail
                
                self.refresh()
                
                if not sleep_randomly(stop_event=stop_event, min_time=80, max_time=480):
                    break
            
        finally:
            print(f"removed {total_likes_counter} like(s)")
            return success