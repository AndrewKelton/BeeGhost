import threading
import time
import random
import logging 

logging.basicConfig(
    level=logging.INFO,
    style="{",
    format="\n[{asctime}] {message}",
    datefmt="%H:%M:%S"
)

TIME_MIN = 900
TIME_MAX = 1260

BEE_GHOST_BANNER = """
\033[93m ██████╗ ███████╗███████╗\033[95m ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
\033[93m ██╔══██╗██╔════╝██╔════╝\033[95m██╔════╝ ██║  ██║ ██╔═══██╗██╔════╝╚══██╔══╝
\033[93m ██████╔╝█████╗  █████╗  \033[95m██║  ███╗███████║ ██║   ██║███████╗   ██║
\033[93m ██╔══██╗██╔══╝  ██╔══╝  \033[95m██║   ██║██╔══██║ ██║   ██║╚════██║   ██║
\033[93m ██████╔╝███████╗███████╗\033[95m╚██████╔╝██║  ██║ ╚██████╔╝███████║   ██║
\033[93m ╚═════╝ ╚══════╝╚══════╝\033[95m ╚═════╝ ╚═╝  ╚═╝  ╚═════╝ ╚══════╝   ╚═╝
\033[0m
+==============================================================================+

Created by: Andrew Kelton, a wannabe systems software engineer.

+==============================================================================+
"""

def start_quit_listener(stop_event : threading.Event):
    """
    Starts listener thread for user input while program is running. 
    If the user types and enters 'quit' into the terminal during a 
    run, the program can exit gracefully, closing selenium and 
    performing cleanup.
    """
    def listen():
        while True:
            command = input()
            
            if command.strip().lower() == "quit":
                stop_event.set()
                print("\n...Quitting")
                break
    
    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
    
def sleep_randomly(
        stop_event : threading.Event, 
        min_time : int = TIME_MIN, 
        max_time : int = TIME_MAX
    ) -> bool:
    """
    Sleeps for a random amount of time, while also listening for a
    stop event. For example, if the user enters 'quit' in this implementation
    the program will not wait for the sleep to finish.
    """
    random_time = random.randint(min_time, max_time)
    logging.info(f"Sleeping for {random_time:.2f}s")
    return not stop_event.wait(random_time)

def print_no_username_error():
    print("""\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        No username and/or password input. You must provide a
        username and a password via command line input, or in a .env
        file in the root directory. Naming convention for environment
        variables for this program are as follows:
        YOUTUBE_EMAIL=""
        YOUTUBE_PASSWORD=""
        INSTAGRAM_USERNAME=""
        INSTAGRAM_PASSWORD=""
        X_USERNAME=""
        X_PASSWORD=""
        """
    )
    
# def print_startup_screen():
#     print(BEE_GHOST_BANNER)