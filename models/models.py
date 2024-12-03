from pydantic import BaseModel
from typing import Any

class Error(BaseModel):
    code: int
    detail: str

class Response(BaseModel):
    error: Error
    data: Any

class SummarizeQuery(BaseModel):
    text_to_summary: str
    system_prompt: str
    user_prompt: str
    max_token_input: int
    max_token_output: int

class ChatQuery(BaseModel):
    user_prompt: str
    max_token_input: int
    max_token_output: int

class DataframeQuery(BaseModel):
    user_prompt: str
    max_token_output: int
