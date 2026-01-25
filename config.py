import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "24754824"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "e24a9c7a6aa24e1c56fa349e104ec20e")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "968292174"))

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "idfinderpro")

# Force Subscription Channel
FORCE_SUB_CHANNEL = "idfinderpro"  # Channel username without @
FORCE_SUB_CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))

# Log Channel - All downloaded files will be forwarded here
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "0"))  # Set to 0 to disable logging

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))

# Crypto Pay API Token (from @CryptoBot)
CRYPTO_PAY_TOKEN = os.environ.get("CRYPTO_PAY_TOKEN", "")
