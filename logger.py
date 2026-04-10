import os
import requests
from datetime import datetime
from util import load_user_json

DEBUG = False

# log.info()
# log.debug()
# log.warn()
# --> telegram 


def info(user, msg):
    msg = f"{datetime.now()} - {msg}\n"
    with open(f"./data/{user}/info.log", "a") as f:
        f.write(msg)
    print(f"INFO: {msg}")

def debug(user, msg):
    if DEBUG:
        msg = f"{datetime.now()} - {msg}\n"
        with open(f"./data/{user}/debug.log", "a") as f:
            f.write(msg)
        print(f"DEBUG: {msg}")

def warn(user, msg):
    msg = f"{datetime.now()} - {msg}\n"
    with open(f"./data/{user}/warn.log", "a") as f:
        f.write(msg)
    print(f"WARN: {msg}")

#     telegram_log(user, msg)

## untested
# def telegram_log(user, msg):
#     TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
#     if not TOKEN:
#         return
    
#     user_config = load_user_json(user)
#     try:
#         CHAT_ID = user_config["telegram_chat_id"]
#     except:
#         return
    
#     url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
#     requests.get(url).json()
