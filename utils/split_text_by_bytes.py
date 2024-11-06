import tiktoken

# This function count the number of tokens
def split_text_by_bytes(text:str, max_size: int):
    
    fragments = []
    start = 0
    while start < len(text):
        finish = start + max_size

        # Adjustment to not count table rows
        if finish < len(text):
            # Find the end of the last complete row before the limit
            finish = text.rfind("\n", start, finish) + 1  # +1 for including the line break

            # Make sure not to cut off the header
            if finish <= start:
                finish = start + max_size  #Fallback if there is no clean break

        fragments.append(text[start:finish])
        start = finish

    return fragments

