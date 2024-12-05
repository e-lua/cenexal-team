from utils.token_counter import token_counter
from utils.split_text_by_bytes import split_text_by_bytes
from utils.verify_limit_tpm import verify_limit_token_per_minute
from models.models import Response,Error
from repositories.azureopenai import AzureOpenAIRepository
from repositories.excel.hta import ExcelHTARepository
from repositories.memory_chat import MemoryChatRepository
from repositories.ms_sql_server.hta import MsSQLServerHTARepository
from typing import Any
import pandas as pd
import json
import io

class LlmService:
        
    def __init__(self,model: str,azureopenaiRepository : AzureOpenAIRepository,excelHTARepository : ExcelHTARepository,memoryChatRepository: MemoryChatRepository,sqlServerHTARepository: MsSQLServerHTARepository):
        
        self.model = model
        self.azureopenaiRepository = azureopenaiRepository
        self.excelHTARepository = excelHTARepository
        self.memoryChatRepository=memoryChatRepository
        self.sqlServerHTARepository = sqlServerHTARepository

    def get_summary(self,max_token_input: int,max_token_output: int,text_to_summarize: str,system_prompt: str,user_prompt: str):
        
        # Verify token limit per minute
        is_exceeded = verify_limit_token_per_minute(max_token_output)
        if is_exceeded:
           return Response(error=Error(code=4001, detail="Token rate limit have been exceeded"), data=[]) 
        
        # Count words
        if len(text_to_summarize) < 20:
            return Response(error=Error(code=4002, detail="The information to be summarized is very little so it will not be processed."), data=[])
        
        # Count tokensz
        tokens,error_details = token_counter(text_to_summarize,self.model)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
        
        if tokens > max_token_input:
            return Response(error=Error(code=4003, detail="The text to be summarized is very large"), data=[])
        
        # Summarize text
        summary,error_details = self.azureopenaiRepository.summarize(system_prompt,text_to_summarize,max_token_output)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])

        # Split summary
        fragments_to_msteams = split_text_by_bytes(summary,20000)
        
        # Ok
        return Response(error=Error(code=0, detail=""), data=fragments_to_msteams)

    def chat_file(self, file:str,file_name: str,user_prompt: str,max_token_output: int):
                
        if file=="HTA":
            dataframe_hta,error_details = self.excelHTARepository.get_data(file_name)
            if error_details != "":
                return Response(error=Error(code=5001, detail="error get the hta as a dataframe, details: "+error_details), data="")
        
        if dataframe_hta.empty:
            return Response(error=Error(code=5001, detail=error_details), data=[])
        
        df_cleaned = dataframe_hta.dropna(how='all')
        df_head = df_cleaned.head(3)
        df_as_text = df_head.to_string(index=False)
        json_data = df_head.to_json(orient='records')
        
        if len(df_as_text)>200000:
            return Response(error=Error(code=4004, detail="you are trying to send a long text"), data=[])
                    
        # Count tokens
        tokens,error_details = token_counter(df_as_text,self.model)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
                
        if tokens > 100000:
            return Response(error=Error(code=4003, detail="The text to be summarized is very large"), data=[])

        system_prompt= f"You are an expert in data analysis and will receive the user's dataframe and his query. You must respond in Markdown format and in English.."
        
        user_prompt=f"Estos son los datos del DataFrame:\n{json_data}\n{user_prompt}"
        
        messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
        
        
        # Verify token limit per minute
        is_exceeded = verify_limit_token_per_minute(max_token_output)
        if is_exceeded:
           return Response(error=Error(code=4001, detail="Token rate limit have been exceeded"), data=[]) 
        
        # Chat
        response_chat,error_details = self.azureopenaiRepository.completion(messages,max_token_output)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
                
        # Split summary
        fragments_to_msteams = split_text_by_bytes(response_chat,20000)
        
        # Ok
        return Response(error=Error(code=0, detail=""), data=fragments_to_msteams) 

    def chat_completion_with_memory(self,chat_id: str,user_prompt: str,max_token_output: int):
        
        # Verify token limit per minute
        is_exceeded = verify_limit_token_per_minute(max_token_output)
        if is_exceeded:
           return Response(error=Error(code=4001, detail="Token rate limit have been exceeded"), data=[]) 
        
        # Create an objcet for chat_id y messages 
        data_object = { "chat_id": chat_id,
        "messages": []}
                
        # Update memory
        _ = self.memoryChatRepository.update_memory(chat_id,"user",user_prompt,120000,self.model)
        
        # Get memory
        messages = self.memoryChatRepository.get_memory(chat_id)

        # Chat
        response_chat,error_details = self.azureopenaiRepository.completion(messages,max_token_output)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
 
        # Split summary
        fragments_to_msteams = split_text_by_bytes(response_chat,20000)
        
        # Create an objcet for chat_id y messages 
        data_object = { "chat_id": chat_id,
        "messages": fragments_to_msteams}
        
        # Ok
        return Response(error=Error(code=0, detail=""), data=data_object) 

    def query_dataframe(self, file:str,file_name: str,user_prompt: str,max_token_output: int):
        
        if file=="HTA":
            dataframe_hta,error_details = self.excelHTARepository.get_data(file_name)
            if error_details != "":
                return Response(error=Error(code=5001, detail="error get the hta as a dataframe, details: "+error_details), data="")
        
        if dataframe_hta.empty:
            return Response(error=Error(code=5001, detail=error_details), data=[])
        
        buffer = io.StringIO()
        dataframe_hta.info(buf=buffer)
        dataframe_info = buffer.getvalue()
        
        # System prompt
        system_prompt = f"""
        Given the following dataframe information, write a python code to query the dataframe that retrieves the requested information. 
        Return the python code inside a JSON structure with the key "python_code".
        <example>{{
            "sql_query": "# Filtrar el DataFrame para COUNTRY = 'France'
                            df_filtrado = df[df['COUNTRY'] == 'France']

                            # Seleccionar solo la columna COA_DETAILS
                            resultado = df_filtrado[['COA_DETAILS']]

                            # Mostrar el resultado
                            print(resultado)"
            "original_query": "Give the COA_DETAILS where COUNTRY is France."
        }}
        </example>
        <dataframe_info>
        {dataframe_info}
        </dataframe_info>
        """
                
        # Count tokens
        tokens,error_details = token_counter(dataframe_info,self.model)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
                
        if tokens > 110000:
            return Response(error=Error(code=4003, detail="The text to be summarized is very large"), data=[])

        # Get the python code
        python_code,error_details = self.azureopenaiRepository.completion_with_json_object(system_prompt,user_prompt,max_token_output)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
                           
        # Verify format SQL query
        if not python_code:
            return {"error":"SQL query generation failed"}
        result_dict = json.loads(python_code)
        
        # Pass the dataframe to the python code
        context_dataframe = {'df': dataframe_hta}
        exec(result_dict["python_code"], context_dataframe)
                
        # Recuperar el resultado
        result = context_dataframe.get("resultado")

        # Ok
        return Response(error=Error(code=0, detail=""), data=result) 

    def build_answer(self,result: list[dict[str, Any]], human_query: str,max_token_output:int):

        # Verify token limit per minute
        is_exceeded = verify_limit_token_per_minute(max_token_output)
        if is_exceeded:
           return Response(error=Error(code=4001, detail="Token rate limit have been exceeded"), data=[]) 
        
        system_message = f"""
        Given a users question and the SQL rows response from the database from which the user wants to get the answer,
        write a response to the user's question in Markdown format.
        <user_question> 
        {human_query}
        </user_question>
        <sql_response>
        ${result} 
        </sql_response>
        """

        messages=[
            {"role": "system", "content": system_message}
        ]
                
        # Get the python code
        answer,error_details = self.azureopenaiRepository.completion(messages,max_token_output)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
                
        # Ok
        return Response(error=Error(code=0, detail=""), data=answer)

    def human_query_to_sql(self,human_query: str,max_token_output: int):
                
        # Verify token limit per minute
        is_exceeded = verify_limit_token_per_minute(max_token_output)
        if is_exceeded:
           return Response(error=Error(code=4001, detail="Token rate limit have been exceeded"), data=[]) 
        
        # Count tokens
        tokens,error_details = token_counter(human_query,self.model)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
             
        if tokens > 110000:
            return Response(error=Error(code=4003, detail="The text to be summarized is very large"), data=[])
        
        # Get the database schema
        database_schema = self.sqlServerHTARepository.get_schema()
        
        system_prompt = f"""
        Given the following schema, write a SQL query that retrieves the requested information. 
        Return the SQL query inside a JSON structure with the key "sql_query".
        <example>{{
            "sql_query": "SELECT * FROM users WHERE age > 18;"
            "original_query": "Show me all users older than 18 years old."
        }}
        </example>
        <schema>
        {database_schema}
        </schema>
        """
        user_prompt = human_query
  
        # Get the python code
        sql_query,error_details = self.azureopenaiRepository.completion_with_json_object(system_prompt,user_prompt,max_token_output)
        if error_details != "":
            return Response(error=Error(code=5001, detail=error_details), data=[])
            
        # Verify format SQL query
        if not sql_query:
            return Response(error=Error(code=5002, detail="SQL query generation failed"), data=[])
        result_dict = json.loads(sql_query)
        
        # Query sql
        result_query = self.sqlServerHTARepository.query(result_dict["sql_query"])
    
        # Ok
        return Response(error=Error(code=0, detail=""), data=result_query) 