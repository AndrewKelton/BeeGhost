import argparse
import json
from selenium.common.exceptions import InvalidSessionIdException
import os
from dotenv import load_dotenv
from collections.abc import Sequence

from BeeGhost.utils import BEE_GHOST_BANNER, print_no_username_error
from BeeGhost.models.instagram import Instagram
from BeeGhost.models.youtube import YouTube
from BeeGhost.models.x import X

MAX_SESSION_CRASHES=10

def parse_args(argv : Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete likes, comments, reposts, etc. from social media accounts.")
    parser.add_argument(
        "platform",
        choices=["youtube", "instagram", "x"],
        help="Social media platform to remove data from"
    )
    parser.add_argument(
        "removal_type",
        choices=["likes", "comments", "reposts", "story_replies"],
        help="Type of interaction to remove"
    )
    parser.add_argument(
        "username",
        type=str,
        nargs='?',
        default=None,
        help="Username/email for account you are logging in with"
    )
    parser.add_argument(
        "password",
        type=str,
        nargs='?',
        default=None,
        help="Password of associated username you are logging in with"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser without displaying it"
    )
    
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None):
    
    print(BEE_GHOST_BANNER)
    
    load_dotenv()
    args = parse_args(argv)
    
    print(f"Booting removal sequence for: {args.platform} {args.removal_type}")
    
    username = None
    password =  None
    
    # check if username and password given
    if args.username is not None:
        username = args.username
        if args.password is not None:
            password = args.password
        else:
            username = None # reset username 
            print("No password given, using account in .env file...")
    
    session_crashes = 0 # session crashed counter

    # loop max times if session crashes
    while session_crashes < MAX_SESSION_CRASHES:
        try:
            
            # YouTube
            if args.platform == 'youtube':
                
                if username is None:
                    username = os.getenv("YOUTUBE_EMAIL")
                    password = os.getenv("YOUTUBE_PASSWORD")
                    
                    if username is None or password is None:
                        print_no_username_error()
                        return
                
                youtube = YouTube(
                    email=username, 
                    password=password, 
                    headless=False # headless doesn't work on youtube
                )
                youtube.navigate_to_url(youtube.BASE_LINK)
                
                # check removal type first, since youtube module only supports deleting comments
                if args.removal_type == 'comments': 
                    
                    if youtube.login(): # 
                        youtube.remove_comments()
                    
                else:
                    print("\nThe YouTube module currently only supports deleting comments.")
                    
                youtube.close_browser()
                session_crashes = MAX_SESSION_CRASHES # set session crashes to max if success
            
            # Instagram
            elif args.platform == 'instagram':
                
                if username is None:
                    username = os.getenv("INSTAGRAM_USERNAME")
                    password = os.getenv("INSTAGRAM_PASSWORD")
                    
                    if username is None or password is None:
                        print_no_username_error()
                        return
                
                try:
                    with open("instagram_cookies.json", "r") as f:
                        cookies = json.load(f)
                except FileNotFoundError:
                    cookies = None
                
                instagram = Instagram(
                    username=username, 
                    password=password, 
                    cookies=cookies, 
                    headless=args.headless
                )
                
                if instagram.login():
                    
                    if args.removal_type == 'likes':
                        instagram.remove_likes()
                    if args.removal_type == 'comments':
                        instagram.remove_comments()
                    # if args.removal_type == 'reposts':
                    #     instagram.remove_reposts() # wip
                    if args.removal_type == 'story_replies':
                        instagram.remove_story_replies()
                    
                instagram.close_browser()
                session_crashes = 10 # set session crashes to max if success
            
            # X
            elif args.platform == 'x':
                
                if username is None:
                    username = os.getenv("X_USERNAME")
                    password = os.getenv("X_PASSWORD")
                    
                    if username is None or password is None:
                        print_no_username_error()
                        return
                
                x = X(
                    username=username, 
                    password=password, 
                    cookies=None, # cookies doesn't do much in X
                    headless=args.headless
                )
                
                if x.login():
                    
                    if args.removal_type == 'likes':
                        x.remove_likes()
                        
                x.close_browser()
                session_crashes = 10 # set session crashes to max if success
                
        except InvalidSessionIdException:
            session_crashes = session_crashes + 1 # session crashed with invalid id, so restart
        
        finally:
            print("Goodbye...")
