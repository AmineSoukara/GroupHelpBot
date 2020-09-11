# Create a new config.py file in same dir and import, then extend this class.
class Config(object):
    LOGGER = True

    # REQUIRED
    API_KEY = ""
    OWNER_ID = ""
    OWNER_USERNAME = "sushantgirdhar"
    TELETHON_HASH = "" # for purge stuffs
    TELETHON_ID = ""

    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = ""
    MESSAGE_DUMP = ""  # needed to make sure 'save from' messages persist
    LOAD = []
    NO_LOAD = []
    WEBHOOK = False
    URL = None

    # OPTIONAL
    SUDO_USERS = [871552081, 1103210216, 1128699250, 777000] # List of id's (not usernames) for users which have sudo access to the bot.
    SUPPORT_USERS = [871552081, 1103210216, 1128699250]  # List of id's (not usernames) for users which are allowed to gban, but can also be banned.
    WHITELIST_USERS = [871552081, 1103210216, 687327662, 559624559, 621763309, 746809172, 732770918]  # List of id's (not usernames) for users which WONT be banned/kicked by the bot.
    WHITELIST_CHATS = []
    BLACKLIST_CHATS = []
    DONATION_LINK = None  # EG, paypal
    CERT_PATH = None
    PORT = 8440
    DEL_CMDS = 'False'  # Whether or not you should delete "blue text must click" commands
    STRICT_GBAN = 'True'
    WORKERS = 8  # Number of subthreads to use. This is the recommended amount - see for yourself what works best!
    BAN_STICKER = 'CAACAgUAAx0CV16c6gACAwleqo1o4IwxMoFvUoAKepdkk-Id0QACfAEAAlHU8jNUYCseRVdVpxkE' # banhammer marie sticker
    ALLOW_EXCL = True  # DEPRECATED, USE BELOW INSTEAD! Allow ! commands as well as /
    CUSTOM_CMD = '/', '?', '.' # Set to ('/', '!') or whatever to enable it, like ALLOW_EXCL but with more custom handler!
    API_OPENWEATHER = '' # OpenWeather API
    SPAMWATCH_API = '' # Your SpamWatch token
    WALL_API = ''
    CHROME_DRIVER = '/app/.chromedriver/bin/chromedriver'
    GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google-chrome'
    LYDIA_API_KEY = ''
    YOUTUBE_API_KEY = ''
    REM_BG_API_KEY = ''
    
class Production(Config):
    LOGGER = False


class Development(Config):
    LOGGER = True
