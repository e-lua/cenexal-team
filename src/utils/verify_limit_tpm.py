import time
import utils.config

# This function verify if the limite of 30K tokens per minute has been exceeded
def verify_limit_token_per_minute(token_increment: int):
    
    # Current time
    current_time = time.time()
    elapsed_time = current_time - utils.config.START_TIME

    # Restart the time window if the limit has passed (60 seconds)
    if elapsed_time > utils.config.WINDOW:
        utils.config.START_TIME = current_time
        utils.config.TOKEN_CONSUMED = 0
        utils.config.CURRENT_STATUS="FREE"
    
    if utils.config.CURRENT_STATUS=="FULL":
        return True
    
    # Check if you can proceed to consume tokens
    if utils.config.TOKEN_CONSUMED + token_increment > utils.config.MAX_TOKENS:
        utils.config.CURRENT_STATUS="FULL"
        utils.config.START_TIME=time.time()
        return True
    else:
        # Consume tokens and allow request
        utils.config.TOKEN_CONSUMED += token_increment

    return False

