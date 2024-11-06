import tiktoken

# This function count the number of tokens
def token_counter(text:str, model: str):
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception as e:
        return "","Error get encoding, details: "+str(e)
    
    try:
        num_tokens = len(encoding.encode(text))
    except Exception as e:
        return "","Error encode, details: "+str(e)
    
    # Count tokens
    return num_tokens,""

