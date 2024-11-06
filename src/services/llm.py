from utils.token_counter import token_counter
from utils.split_text_by_bytes import split_text_by_bytes
from utils.verify_limit_tpm import verify_limit_token_per_minute
from models.models import Response,Error
from repositories.azureopenai import AzureOpenAIRepository
import os

class LlmService:
    
    azureopenaiRepository: AzureOpenAIRepository
    
    def __init__(self,model: str,azure_openai_key: str,azureopenaiRepository : AzureOpenAIRepository):
        
        self.model = model
        self.azureopenaiRepository = azureopenaiRepository
        self.azure_openai_key=azure_openai_key

    def get_summary(self,max_token_input: int,max_token_output: int,text_to_summarize: str,user_prompt: str):
        
        # Verify token limit per minute
        is_exceeded = verify_limit_token_per_minute(max_token_output)
        if is_exceeded:
           return Response(error=Error(code=4001, detail="Token rate limit have been exceeded"), data="") 
        
        # Count words
        if len(text_to_summarize) < 20:
            return Response(error=Error(code=4002, detail="The information to be summarized is very little so it will not be processed."), data="")
        
        # Count tokens
        tokens,error_details = token_counter(text_to_summarize,self.model)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data="")
        
        if tokens > max_token_input:
            return Response(error=Error(code=4003, detail="The text to be summarized is very large"), data="")
        
        # Summarize text
        summary,error_details = self.azureopenaiRepository.Summarize(self.azure_openai_key,user_prompt,text_to_summarize,max_token_output)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data="")

        # Split summary
        fragments_to_msteams = split_text_by_bytes(summary,20000)
        
        # Ok
        return Response(error=Error(code=0, detail=""), data=fragments_to_msteams)
    