import requests
from typing import Any

class AISearchRepository:
    
    def __init__(self,endpoint: str,index_name: str,api_key: str,api_key_admin: str):
            
        # Azure data
        self.endpoint=endpoint
        self.index_name=index_name
        self.api_key=api_key
        self.api_key_admin=api_key_admin
    
    def update_index(self,json_data):
        
        url = f"{self.endpoint}/indexes/{self.index_name}/docs/index?api-version=2024-07-01"
        headers = {
            "Content-Type": "application/json",
            "api-key": f"{self.api_key_admin}"
        }
        try:
            response = requests.post(url, json=json_data, headers=headers)
            return response.json(), ""
            
        except Exception as e:
            return "",f"Error update AzureAISearch, details: {str(e)}"
            
    def search_by_vector(self,query_vector):
        
        url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version=2024-07-01"
        headers = {
            "Content-Type": "application/json",
            "api-key": f"{self.api_key}"
        }
        payload = {
            "count": True,
            "select": "COUNTRY,DRUG_NAME",
            "vectorFilterMode": "preFilter",
            "vectorQueries": [
                {
                    "kind": "vector",
                    "vector": query_vector,
                    "exhaustive": True,
                    "fields": "vectors_from_column_to_vectorize",
                    "k": 10
                }
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json(), ""
            
        except Exception as e:
            return [],f"Error search in AzureAISearch, details: {str(e)}"
        