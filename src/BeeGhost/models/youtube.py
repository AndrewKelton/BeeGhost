from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
import time 
import sys
import threading

from BeeGhost.models.socialmedia import SocialMedia
from BeeGhost.models.ratelimitchecker import RateLimitChecker
from BeeGhost.utils import start_quit_listener, sleep_randomly

# TODO: Fix bug where if you reach rate limit by user input
# (not actually the program running), then program will say a 
# comment is successfully deleted, when it is still on the screen.
# Need to create a function that checks if the comment still 
# appears on the screen after "deletion"

class YouTube(SocialMedia):
    
    BASE_LINK = "https://www.youtube.com/"
    COMMENTS_LINK = "https://myactivity.google.com/page?hl=en&utm_medium=web&utm_source=youtube&page=youtube_comments"
    
    def __init__(self, email : str, password : str, headless=False):
        
        options = uc.ChromeOptions()
        # options.add_argument(f"--user-data-dir={google_data_path}")
        # options.add_argument("--profile-directory=Default")
        
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            
        driver = uc.Chrome(options=options)
        
        super().__init__(
            username=email,
            password=password,
            cookies=None,
            driver=driver
        )
        
    def login(self) -> bool:
        
        self.click_button(ref='//a[@aria-label="Sign in"]')
        
        email_box = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.ID, "identifierId"))
        )
        email_box.send_keys(self.username)
        email_box.send_keys(Keys.RETURN)
        
        input("\npress enter when you enter your passkey")
        # TODO: Automatically enter the passkey
        # Maybe there is a file or something i can automate my fingerprint with?
        print("\n")
        
        try:
            account = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "button#avatar-btn"))
            )
            print("Successfully logged in to YouTube!")
            return True
        
        except Exception as e:
            print(f"Error: Could not login to YouTube. \n{e}")
            return False

    def click_button(self, ref : str, description : str = "button") -> str | None:
        """
        Clicks a YouTube button of ref : str and returns
        the related comment tied to that button if it exists.
        
        Returns:
            str: comment deleted
        """
        for attempt in range(3):
            try:
                button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, ref))
                )
                
                comment = button.get_attribute("aria-label")
                
                if comment and comment.startswith("Delete activity item "):
                    comment = comment.replace("Delete activity item ", "", 1)
                button.click()
                
                return comment 
                    
            except TimeoutException as e:
                if attempt < 2:
                    print("Delete button not found. Refreshing page...")
                    self.driver.refresh()
                    time.sleep(2)
                else:
                    print(f"Error clicking {description} after refresh: {type(e).__name__}: {e}", file=sys.stderr)
                    return None
            
    def save_cookies(self) -> bool:
        """Cookies won't work correctly with a Google profile."""
        return False 
    
    def xpath_exists(self, xpath : str) -> bool:
        """Checks if some xpath exists
        
        Returns:
            bool: True if xpath exists, False otherwise.
        """
        try:   
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((
                    By.XPATH,
                    xpath
                ))
            )
            return False
        except TimeoutException:
            return True
    
    def remove_comments(self) -> bool:
        """Removes comments from associated YouTube account.
        
        Returns:
            bool: True if the removal(s) were successful, False otherwise.
        """
        
        # TODO: We can actually remove all the comments for a single day
        # within a farirly quick timespan. Rather than waiting x time 
        # after deleting one comment, we should delete all comments within
        # f'//div[data-date="{first_date_on_screen}""]'
        # maybe can also delete the next item when `<div class="Mh0NNb Mp2Z0b misTTe" jslog="121710; track:impression" jsaction="click:.CLIENT" style="visibility: visible;"><div class="M6tHv"><div class="aGJE1b" id="J9Hpafc77">Deleting now</div><div class="dnmu6e" tabindex="0" jsaction="focus:.CLIENT"></div><div class="x95qze" role="button" tabindex="0" aria-describedby="J9Hpafc77" jslog="121709; track:impression,click" jsaction="click:.CLIENT;blur:.CLIENT">Cancel</div><div class="dnmu6e" tabindex="0" jsaction="focus:.CLIENT"></div></div></div>`
        # appears as hidden, and wait while it is visible
        
        self.navigate_to_url(self.COMMENTS_LINK)

        stop_event = threading.Event() # event flag
        start_quit_listener(stop_event=stop_event) # listen for 'quit' early termination
        
        rateLimitChecker = RateLimitChecker(max_requests=10) # rate limit checker works great!
        
        total_comment_counter = 0 # counter for total content removed overall
        success = True
        
        try:
            while True:
                # loops until all comments are gone
                
                if not self.xpath_exists(xpath='//p[text()="No activity."]'):
                    print("All comments deleted...")
                    break
                
                if not rateLimitChecker.is_allowed():
                    stop_event.wait(rateLimitChecker.get_sleep_time())
 
                if stop_event.is_set():
                    break
                
                # click delete on a comment
                comment = self.click_button(
                    '//button[contains(@aria-label, "Delete activity item")]'
                )
                
                # something failed
                if comment is None:
                    success = False
                    continue
                
                if stop_event.is_set():
                    break
                
                time.sleep(1.5)

                # confirmation button may or may not pop up, it's fine either way
                self.click_button('//div[@role="button"][.//span[normalize-space()="Delete"]]')
                
                # this will tell us that the comment was actually deleted
                if self.xpath_exists(xpath='//div[text()="1 item deleted"]'):
                    rateLimitChecker.record_request()
                    success = True
                    total_comment_counter = total_comment_counter + 1
                    
                    print(f"successfully deleted {comment}")
                
                # comment was not actually deleted
                else:
                    success = False
                    
                if not sleep_randomly(stop_event=stop_event, min_time=80):
                    break
    
        except Exception as e:
            print(f"Error deleting comments: {type(e).__name__}: {e}", file=sys.stderr)
            success = False

            import traceback
            traceback.print_exc()
            
        finally:
            print(f"removed {total_comment_counter} post(s)")
            return success