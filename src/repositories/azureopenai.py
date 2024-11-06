from langchain_openai import AzureOpenAI
import openai
import requests
import json

class AzureOpenAIRepository:
    
    def __init__(self,azure_openai_url: str,azure_deployment: str,azure_openai_api_key: str, azure_endpoint: str,azure_api_version: str):

        # Initialize model embedding and model language
        #self.client =  openai.AzureOpenAI(
        #    api_key=azure_openai_api_key,
        #    api_version=azure_api_version,
        #    azure_endpoint=azure_endpoint
        #)
            
        # Azure data
        self.azure_openai_url=azure_openai_url
        self.azure_endpoint=azure_endpoint
        self.azure_api_version=azure_api_version
        self.azure_api_key=azure_openai_api_key
        self.azure_deployment=azure_deployment

    def Embedding(self,text_to_embed: str):
        
        # Setup OpenAI with Azure
        openai.api_type = "azure"
        openai.azure_endpoint = self.azure_endpoint
        openai.api_version = self.azure_api_version
        openai.api_key = self.azure_api_key
        
        try:     
            embedded_text = openai.embeddings.create(
                input=text_to_embed,
                model="text-embedding-ada-002"
            )
        except Exception as e:
            print("---> Exception embedding text: ",e)
        
        # Ok
        return embedded_text.data[0].embedding

    def Summarize(self,azure_api_key:str,user_prompt: str,text_to_summary: str,max_token_output: int):
        
        # Given the user prompt and the text to be summarized, write a summary in markdown table format and separate it into 20 kilobyte fragments if necessary, taking into account that if you do separate, the symbol to identify the separation is _END_.
        
        #       Given the text to be summarized, write a summary in markdown table format and separate it into 20 kilobyte fragments if necessary, taking into account that if you do separate, the symbol to identify the separation is _END_.
        
        print(user_prompt)
        
        # Build query
        system_message = f"""
        Given the text to be summarized, write a summary in markdown table format.
        """
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "api-key": azure_api_key
        }

        # Body de la solicitud
        body = {
            "messages": [
                {
                    "role": "system",
                    "content": f"""
                            ${system_message} 
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                            <text_to_be_summarized>
                            ${text_to_summary} 
                            </text_to_be_summarized>
                    """
                }
            ],
            "temperature": 0.7,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "max_tokens": max_token_output,
            "stop": None
        }

        try:
                       
            # Request
            response = requests.post(url=self.azure_openai_url, headers=headers, data=json.dumps(body))
    
            # Verify status request
            if response.status_code != 200:
                return "",f"Error requests {response.text}"
                
            # Convert response
            response_json = response.json()
            
            # Extraer el contenido del campo "content" del "message"
            content = response_json['choices'][0]['message']['content']
        except Exception as e:
            return "",f"Error post request, details: {e}"
                     
        # Ok 
        return content,""