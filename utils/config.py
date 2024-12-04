import time

# Max. tokens per minute
MAX_TOKENS = 29000
MAX_REQUEST = 160
CURRENT_STATUS = "FREE"
WINDOW = 60  # 60 seconds
TOKEN_CONSUMED = 0
START_TIME = time.time()
