# BeeGhost

A social media automation toolkit providing a simple way to automate removing all likes, comments, reposts, etc. associated with a social media account. Useful for resetting your algorithm and "muddying" your online data. 

## Getting Started

### Dependencies

* Python
* selenium=4.23.1
* undetected-chromedriver=3.5.5

### Installing

1. **Clone the repository:**
```bash
git clone https://github.com/AndrewKelton/BeeGhost
```

2. **Install the required packages:**
```bash
pip install -r requirements.txt
pip install -e
```

### Executing program

```bash
# Run BeeGhost to delete sepcific content on a specified platform 
beeghost <platform> <content> <username> <password>
```

**Example:** Delete all youtube comments
```bash
beeghost youtube comments 
```
_Username and password can be left out of command line input, if you use a .env file._

## Help

### Cookies

Cookies currently works only for Instagram. **To save Instagram cookies:**

```py
# example saving Instagram cookies
from BeeGhost.models.instagram import Instagram

instagram = Instagram(
    username="user", # <your username here> 
    password="pass123", # <your password here> 
    cookies=None,
    headless=False
)

instagram.login() # logs in to instagram account 
instagram.save_cookies() # saves cookies in project directory
```

*<small>Headless mode will not work unless you have cookies saved for Instagram.</small>*

### 2-Factor Authentication
Some platforms may require 2FA when you login for the first time with this script. Make sure to approve the login request, otherwise you will not be able to use this script. Youtube requires you to enter a passkey or confirm 2FA on every login, unless you have 2FA turned off for Google (don't do this).

## Authors

Contributors names and contact info

Andrew Kelton
[@andrew-kelton](https://www.linkedin.com/in/andrew-kelton)

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

* [Instagram Like Activity Deleter](https://gist.github.com/braunglasrakete/8a7cad3ecb135470c4b93d7223b0927e)
