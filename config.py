from os import getenv


API_ID = int(getenv("API_ID", "27900743"))
API_HASH = getenv("API_HASH", "ebb06ea8d41420e60b29140dcee902fc")
BOT_TOKEN = getenv("BOT_TOKEN", "8003649544:AAGoiThVN8KLJyKGsGf1BcfTsjDTrSmjFR8")
OWNER_ID = int(getenv("OWNER_ID", "7804396225"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "7804396225").split()))
MONGO_URL = getenv("MONGO_DB", "mongodb+srv://rsrasasingh:FS2G9YbI28KbPHLC@cluster0.yljr3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

CHANNEL_ID = int(getenv("CHANNEL_ID", "-1002566364060"))
PREMIUM_LOGS = int(getenv("PREMIUM_LOGS", "-1002566364060"))
