from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import json
import threading

from BeeGhost.models.socialmedia import SocialMedia
from BeeGhost.models.ratelimitchecker import RateLimitChecker
from BeeGhost.utils import start_quit_listener, sleep_randomly

class Instagram(SocialMedia):
    
    BASE_LINK = "https://www.instagram.com/"
    LIKES_LINK = "https://www.instagram.com/your_activity/interactions/likes/"
    COMMENTS_LINK = "https://www.instagram.com/your_activity/interactions/comments/"
    REPOSTS_LINK = "https://www.instagram.com/your_activity/interactions/reposts/"
    STORY_REPLIES_LINK = "https://www.instagram.com/your_activity/interactions/story_replies/"
    SAVED_LINK = "https://www.instagram.com/saved/all-posts/"
    LOGIN_LINK = "https://www.instagram.com/accounts/login/"
    # REVIEWS_LINK = "your_activity/interactions/reviews"
    
    MAX_REQUESTS = 10
    
    def __init__(self, username : str, password : str, cookies=None, headless=False):
        
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
            
            self.click_button(ref='//button[text()="Not Now"]')
            
            print(f"Logged in as {self.username}")
            
            return True
        else:
            # login with username + password
            
            username = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.NAME, "email"))
            )
            username.send_keys(self.username)
            username.send_keys(Keys.RETURN)
            
            password = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.NAME, "pass"))
            )
            password.send_keys(self.password)
            password.send_keys(Keys.RETURN)
            
            input("press enter when you enter 2 step")
            
            print(f"Logged in as {self.username}")
            time.sleep(2.5)
            
            return True
        
    def scroll(self):
        """This will not work with scrolling Instagram interactions pages.
        Instagram interactions pages have a scroll bar within a div.
        """
        # TODO: get the div id for the scroll bar from instagram 
        
        # last_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(2)
    
    def select_content(self) -> int:
        """Selects all content on an Instagram page by clicking each
        button called "Toggle checkbox".
        
        Returns:
            int: total number of content selected
        """
        
        try:
            content = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((
                    By.XPATH,
                    '//div[@role="button"][.//div[@aria-label="Toggle checkbox"]]'
                ))
            )
            
            for cont in content:
                self.driver.execute_script("arguments[0].click();", cont)
            return len(content)
            
        except TimeoutException:
            return 0
        
        except Exception:
            return -1
    
    def save_cookies(self):
        "saves cookies to instagram_cookies.json"
        
        cookies = self.driver.get_cookies()

        with open("instagram_cookies.json", "w") as f:
            json.dump(cookies, f, indent=4)

        print("Cookies saved.")
    
    def remove_comments(self) -> bool:
        """Removes comments from associated Instagram account.
        
        Returns:
            bool: True if the removal was successful, False otherwise.
        """
        
        self.navigate_to_url(self.COMMENTS_LINK)
        
        stop_event = threading.Event() # event flag
        start_quit_listener(stop_event=stop_event) # listen for 'quit' early termination
        
        rateLimitChecker = RateLimitChecker(max_requests=self.MAX_REQUESTS)
        
        total_comment_counter = 0 # counter for total content removed overall
        success = True
        
        try:
            while True:
                # loops until all posts gone
                
                if not rateLimitChecker.is_allowed():
                    stop_event.wait(rateLimitChecker.get_sleep_time())
                
                if stop_event.is_set():
                    break

                if not self.click_button("//div[span[normalize-space()='Select']]"):
                    self.refresh()
                    continue
                
                if stop_event.is_set():
                    break
                        
                num_comments = self.select_content() # toggles checkbox of posts
                
                if num_comments > 0:
                    
                    try:
                        # click removal confirmation
                        self.click_button(ref=
                            f"//span[text()='Delete']"
                        )
                        successful_deletion = self.click_button(ref=
                            f"//button[.//div[text()='Delete']]"
                        )
                        
                        if successful_deletion:
                            rateLimitChecker.record_request()
                            print(f"successfully removed {num_comments} comments(s)")
                            total_comment_counter = total_comment_counter + num_comments
                            success = True
                            
                        if not sleep_randomly(stop_event=stop_event, min_time=80):
                            break
                        
                    except Exception as e:
                        print(f"error: {e}")
                        success = False
                
                elif num_comments == 0:
                    success = True
                    break # uncommented from all posts
                
                elif num_comments == -1:
                    print("Error: instagram.select_content() returned -1")
                
        finally:
            print(f"removed {total_comment_counter} post(s)")
            return success
            
    def remove_likes(self) -> bool:
        """Removes likes from associated Instagram account.
                
        Returns:
            bool: True if the removal was successful, False otherwise.
        """
                
        self.navigate_to_url(self.LIKES_LINK)
        
        stop_event = threading.Event() # event flag
        start_quit_listener(stop_event=stop_event) # listen for 'quit' early termination
        
        rateLimitChecker = RateLimitChecker(max_requests=self.MAX_REQUESTS)
        
        total_likes_counter = 0 # counter for total content removed overall
        success = True
        
        try:
            while True:
                # loops until all posts gone
                
                if not rateLimitChecker.is_allowed():
                    stop_event.wait(rateLimitChecker.get_sleep_time())
                
                if stop_event.is_set():
                    break
                
                if not self.click_button("//div[span[normalize-space()='Select']]"):
                    self.refresh()
                    continue
                
                if stop_event.is_set():
                    break
                        
                num_likes = self.select_content() # toggles checkbox of posts
                
                if num_likes > 0:
                    
                    try:
                        # click removal confirmation
                        self.click_button(ref=
                            f"//span[text()='Unlike']"
                        )
                        success = self.click_button(ref=
                            f"//button[.//div[text()='Unlike']]"
                        )
                        
                        if success:
                            rateLimitChecker.record_request()
                            print(f"successfully removed {num_likes} like(s)")
                            total_likes_counter = total_likes_counter + num_likes
                            success = False
                            
                        if not sleep_randomly(stop_event=stop_event, min_time=80):
                            break
                        
                    except Exception as e:
                        print(f"error: {e}")
                        success = False
                
                elif num_likes == 0:
                    success = True
                    break # uncommented from all posts
                
                elif num_likes == -1:
                    print("Error: instagram.select_content() returned -1")
                
        finally:
            print(f"removed {total_likes_counter} post(s)")
            return success
            
    def remove_story_replies(self) -> bool:
        """Removes story replies from associated Instagram account.
                
        Returns:
            bool: True if the removal was successful, False otherwise.
        """
        
        self.navigate_to_url(self.STORY_REPLIES_LINK)
        
        stop_event = threading.Event() # event flag
        start_quit_listener(stop_event=stop_event) # listen for 'quit' early termination
        
        rateLimitChecker = RateLimitChecker(max_requests=self.MAX_REQUESTS)
        
        total_story_replies_counter = 0 # counter for total content removed overall
        success = True
        
        try:
            while True:
                # loops until all posts gone
                
                if not rateLimitChecker.is_allowed():
                    stop_event.wait(rateLimitChecker.get_sleep_time())
                
                if stop_event.is_set():
                    break

                if not self.click_button("//div[span[normalize-space()='Select']]"):
                    self.refresh()
                    continue
                
                if stop_event.is_set():
                    break
                        
                num_story_replies = self.select_content() # toggles checkbox of posts
                
                if num_story_replies > 0:
                    
                    try:
                        # click removal confirmation
                        self.click_button(ref=
                            f"//span[text()='Delete']"
                        )
                        success = self.click_button(ref=
                            f"//button[.//div[text()='Delete']]"
                        )
                        
                        if success:
                            rateLimitChecker.record_request()
                            print(f"successfully removed {num_story_replies} story replies")
                            total_story_replies_counter = total_story_replies_counter + num_story_replies
                            success = False
                            
                        if not sleep_randomly(stop_event=stop_event, min_time=80):
                            break
                        
                    except Exception as e:
                        print(f"error: {e}")
                        success = False
                
                elif num_story_replies == 0:
                    success = True
                    break # removed story replies from all posts
                
                elif num_story_replies == -1:
                    print("Error: instagram.select_content() returned -1")
                
        finally:
            print(f"removed {total_story_replies_counter} post(s)")
            return success
            
    def remove_reposts(self) -> bool:
        """Removes reposts from associated Instagram account.
                
        Returns:
            bool: True if the removal was successful, False otherwise.
        """
        
        self.navigate_to_url(self.REPOSTS_LINK)
        
        stop_event = threading.Event() # event flag
        start_quit_listener(stop_event=stop_event) # listen for 'quit' early termination
        
        rateLimitChecker = RateLimitChecker(max_requests=self.MAX_REQUESTS)
        
        total_story_replies_counter = 0 # counter for total content removed overall
        success = True
        
        try:
            while True:
                # loops until all posts gone
                
                if not rateLimitChecker.is_allowed():
                    stop_event.wait(rateLimitChecker.get_sleep_time())
                
                if stop_event.is_set():
                    break

                self.click_button(
                    "//div[span[normalize-space()='Select']]"
                ) # click 'Select' button 
                
                if stop_event.is_set():
                    break
                        
                num_story_replies = self.select_content() # toggles checkbox of posts
                
                if num_story_replies > 0:
                    
                    try:
                        # click removal confirmation
                        self.click_button(ref=
                            f"//span[text()='Delete']"
                        )
                        success = self.click_button(ref=
                            f"//button[.//div[text()='Delete']]"
                        )
                        
                        if success:
                            rateLimitChecker.record_request()
                            print(f"successfully removed {num_story_replies} reposts")
                            total_story_replies_counter = total_story_replies_counter + num_story_replies
                            success = False
                            
                        if not sleep_randomly(stop_event=stop_event, min_time=80):
                            break
                        
                    except Exception as e:
                        print(f"error: {e}")
                        success = False
                
                elif num_story_replies == 0:
                    success = True
                    break # removed reposts from all posts
                
                elif num_story_replies == -1:
                    print("Error: instagram.select_content() returned -1")
                
        finally:
            print(f"removed {total_story_replies_counter} post(s)")
            return success