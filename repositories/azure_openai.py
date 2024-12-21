from langchain_openai import AzureOpenAI
from typing import List, Dict
import openai
import requests
import json

class AzureOpenAIRepository:
    
    def __init__(self,azure_openai_url: str,azure_deployment: str,azure_openai_api_key: str, azure_endpoint: str,azure_api_version: str):
            
        # Azure data
        self.azure_openai_url=azure_openai_url
        self.azure_endpoint=azure_endpoint
        self.azure_api_version=azure_api_version
        self.azure_api_key=azure_openai_api_key
        self.azure_deployment=azure_deployment

    def embedding(self,text_to_embed: str):
        
        # Setup OpenAI with Azure
        openai.api_type = "azure"
        openai.azure_endpoint = self.azure_endpoint
        openai.api_version = self.azure_api_version
        openai.api_key = self.azure_api_key
        
        try:     
            embedded_text = openai.embeddings.create(
                input=text_to_embed,
                model="text-embedding-3-large"
            )
        except Exception as e:
            return "",f"Error embed, details: {e}"
        
        # Ok
        return embedded_text.data[0].embedding,""

    def summarize(self,system_prompt: str,text_to_summary: str,max_token_output: int):
       
        if system_prompt=="":
            system_prompt="Given the text to be summarized, write a summary in markdown table format."
        
        # Setup OpenAI with Azure
        openai.api_type = "azure"
        openai.azure_endpoint = self.azure_endpoint
        openai.api_version = self.azure_api_version
        openai.api_key = self.azure_api_key

        try:
                       
            response = openai.chat.completions.create(
                model=self.azure_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_to_summary},
                ],
                max_tokens=max_token_output,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
        except Exception as e:
            return "",f"Error post request, details: {e}"
                     
        # Ok 
        return content,""

    def completion(self,input_messages: List[Dict[str, str]],max_token_output: int):
        
        # Setup OpenAI with Azure
        openai.api_type = "azure"
        openai.azure_endpoint = self.azure_endpoint
        openai.api_version = self.azure_api_version
        openai.api_key = self.azure_api_key

        try:
                       
            response = openai.chat.completions.create(
                model=self.azure_deployment,
                messages=input_messages,
                max_tokens=max_token_output,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
        except Exception as e:
            return "",f"Error post request, details: {e}"

        # Ok 
        return content,""

    def completion_with_json_object(self,system_prompt: str,user_prompt: str,max_token_output: int):
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "api-key": self.azure_api_key
        }
        
        # Body de la solicitud
        body = {
            "messages": [
                {
                    "role": "system",
                    "content": f"""
                            ${system_prompt} 
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                            ${user_prompt} 
                    """
                }
            ],
            "temperature": 0.7,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "max_tokens": 4096,
            "response_format": {
                "type": "json_object"
            }
        }
        
        try:
                       
            # Request
            response = requests.post(url=self.azure_openai_url, headers=headers, data=json.dumps(body))
    
            # Verify status request
            if response.status_code != 200:
                return "",f"Error requests {response.text}"
                
            # Convert response
            response_json = response.json()
            
            content = response_json['choices'][0]['message']['content']
            
        except Exception as e:
            return "",f"Error post request, details: {e}"
                    
                             
        # Ok 
        return content,""
    

    
    