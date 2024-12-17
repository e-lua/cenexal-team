from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models.models import Response,Error,SummarizeQuery,ChatQuery,DataframeQuery
from repositories.excel.hta import ExcelHTARepository
from repositories.azure_openai import AzureOpenAIRepository
from repositories.memory_chat import MemoryChatRepository
from repositories.ms_sql_server.hta import MsSQLServerHTARepository
from services.hta import  HTAService
from services.llm import LlmService
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

# ApiKey
API_KEY=os.getenv("API_KEY")

# Initialize ExcelHTARepository
sqlserver_hta_repository = MsSQLServerHTARepository(os.getenv("AZURE_SQL_USER"),os.getenv("AZURE_SQL_PASS"),os.getenv("AZURE_SQL_SERVER"),os.getenv("AZURE_SQL_DATABASE"))

# Initialize ExcelHTARepository
excel_hta_repository = ExcelHTARepository(source_path="data",destination_path="data")

# Initialize AzureOpenAIRepository
azure_open_ai_repository = AzureOpenAIRepository(azure_openai_url=os.getenv("AZURE_OPENAI_URL"),azure_deployment=os.getenv("AZURE_DEPLOYMENT"),azure_openai_api_key=os.getenv("AZURE_OPENAI_KEY"),azure_endpoint=os.getenv("AZURE_ENDPOINT"),azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION"))

# Initialize ExcelHTARepository
memory_chat_repository = MemoryChatRepository()

# Initialize  HTAService
file_service =  HTAService(excelHTARepository=excel_hta_repository,sqlServerHTARepository=sqlserver_hta_repository)

# Initialize LlmService
llm_service = LlmService(os.getenv("AZURE_DEPLOYMENT"),azureopenaiRepository=azure_open_ai_repository,excelHTARepository=excel_hta_repository,memoryChatRepository=memory_chat_repository,sqlServerHTARepository=sqlserver_hta_repository)

# Initialize FastAPI
app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Unauthorized access"}

@app.get(
    "/cenexal-team/v1/file",
    name="Get files",
    operation_id="get_cenexal_team_file",
    description="Gets all the original and prepared files associated with cenexal team.",
)
async def get_all_file(request: Request):
    
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    archivos = []
    for nombre_archivo in os.listdir("data"):
        ruta_archivo = os.path.join("data", nombre_archivo)
        if os.path.isfile(ruta_archivo):
            archivos.append(nombre_archivo)

    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=archivos)
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )

@app.post(
    "/cenexal-team/v1/hta/file/prepare",
    name="Prepare file",
    operation_id="post_cenexal_team_file_prepare",
    description="Prepare the uploaded file, convert it to csv and save the original and converted file.",
)
async def hta_prepare_file(request: Request,file: UploadFile = File(...)):
    
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    filename_splitted = file.filename.split(".")  
    file_name = filename_splitted[0]
    file_extension =  filename_splitted[1]
        
    # Delete source file
    reponse_delete_source =  HTAService.delete_files(file_service,file_name,file_extension)
    if reponse_delete_source.error.code != 0:
        return JSONResponse(
            status_code=500,
            content=reponse_delete_source.model_dump()
        )

    # Storage file
    file_location = os.path.join('data', file.filename)
    with open(file_location, "wb") as file_object:
        file_object.write(file.file.read())
        
    # Prepare file
    reponse_service =  HTAService.prepare_clean_excel(file_service,file_name,file_extension)
    if reponse_service.error.code != 0:
        return JSONResponse(
            status_code=500,
            content=reponse_service.model_dump()
        )

    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=reponse_service.data)
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )

@app.get(
    "/cenexal-team/v1/hta/file/filters",
    name="Get filters",
    operation_id="get_cenexal_team_filters",
    description="Get the filters ready to incorporate the chatbot form for Teams into Adaptive Card.",
)
async def hta_get_filters_from_file(request: Request,file_name: str):
    
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    # Get filters
    reponse_service =  HTAService.get_filters_from_excel(file_service,file_name)
    if reponse_service.error.code != 0:
        return JSONResponse(
            status_code=500,
            content=reponse_service.model_dump()
        )

    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=reponse_service.data)
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )

@app.get(
    "/cenexal-team/v1/hta/file/column",
    name="Get data from column",
    operation_id="get_cenexal_team_column_data",
    description="Gets the column data from cenexal file, row by row, in a concatenated manner.",
)
async def hta_get_column(request: Request,file_name: str, file_extension: str, column_name: str, HTA_AGENCY_NAME: str, COUNTRY: str, HTA_DECISION_DT: str, BIOMARKERS: str, PRIMARY_DISEASE: str, DRUG_NAME: str, GENERIC_DRUG_NAME: str, DRUG_COMBINATIONS: str, TREATMENT_MODALITY: str, ASMR_REQUESTED: str, ASMR_RECIEVED: str, HTA_STATUS:str):

    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    # Get column info
    reponse_service =  HTAService.get_columns_from_excel(file_service,file_name,file_extension,column_name, HTA_AGENCY_NAME, COUNTRY, HTA_DECISION_DT, BIOMARKERS, PRIMARY_DISEASE, DRUG_NAME, GENERIC_DRUG_NAME, DRUG_COMBINATIONS, TREATMENT_MODALITY, ASMR_REQUESTED, ASMR_RECIEVED,HTA_STATUS)
    if reponse_service.error.code != 0:
        return JSONResponse(
            status_code=500,
            content=reponse_service.model_dump()
        )

    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=reponse_service.data)
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )

@app.post(
    "/cenexal-team/v1/hta/summarize",
    name="Get data summarized",
    operation_id="get_summarized_data",
    description="Gets a text and respond with the summary in Markdown table format validated for MS Teams",
)
async def hta_summarize(request: Request,payload: SummarizeQuery):
    
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    # Get column info
    reponse_service = LlmService.get_summary(llm_service,payload.max_token_input,payload.max_token_output,payload.text_to_summary,payload.system_prompt,payload.user_prompt)
    if reponse_service.error.code != 0:
        
        code_error= str(reponse_service.error.code)
        status=0

        if code_error[:3]=="500":
            status=500
            
        if code_error[:3]=="400":
            status=400
        
        return JSONResponse(
            status_code=status,
            content=reponse_service.model_dump()
        )
    
    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=reponse_service.data)
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )

@app.post(
    "/cenexal-team/v1/chat-with-file",
    name="Chat with the database",
    operation_id="chat_with_database",
    description="Chat with the database and respond with the system response in Markdown table format validated for MS Teams",
)
async def chat_with_file(request: Request,payload: ChatQuery):
    
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    # Get column info
    reponse_service_sql_query = LlmService.human_query_to_sql(llm_service,payload.user_prompt,payload.max_token_output)
    if reponse_service_sql_query.error.code != 0:
        
        code_error= str(reponse_service_sql_query.error.code)
        status=0

        if code_error[:3]=="500":
            status=500
            
        if code_error[:3]=="400":
            status=400
        
        return JSONResponse(
            status_code=status,
            content=reponse_service_sql_query.model_dump()
        )
    
    # Get response
    reponse_service_build_answer = LlmService.build_answer(llm_service,reponse_service_sql_query,payload.user_prompt,payload.max_token_output)
    if reponse_service_build_answer.error.code != 0:
        
        code_error= str(reponse_service_build_answer.error.code)
        status=0

        if code_error[:3]=="500":
            status=500
            
        if code_error[:3]=="400":
            status=400
        
        return JSONResponse(
            status_code=status,
            content=reponse_service_build_answer.model_dump()
        )
    
    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=reponse_service_build_answer.data)
    
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )
   
@app.post(
    "/cenexal-team/v1/chat-with-memory",
    name="Chat with memory ",
    operation_id="chat_with_memory",
    description="Chat with memory and respond with the system response in Markdown format validated for MS Teams",
)
async def chat_with_memory(request: Request,payload: ChatQuery):
    
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    # Get column info
    reponse_service = LlmService.chat_completion_with_memory(llm_service,payload.chat_id,payload.user_prompt,payload.max_token_output)
    if reponse_service.error.code != 0:
        
        code_error= str(reponse_service.error.code)
        status=0

        if code_error[:3]=="500":
            status=500
            
        if code_error[:3]=="400":
            status=400
        
        return JSONResponse(
            status_code=status,
            content=reponse_service.model_dump()
        )
    
    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=reponse_service.data)
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )

@app.put(
    "/cenexal-team/v1/hta/file/update-in-database",
    name="Update HTA data in database",
    operation_id="udpate_hta_in_database",
    description="Update HTA data in the database.",
)
async def hta_update_in_database(request: Request):
    
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    # Get column info
    reponse_service =  HTAService.move_from_excel_to_database(file_service,"HTA_mBC_Export_Adnan_PREPARED")
    if reponse_service.error.code != 0:
        
        code_error= str(reponse_service.error.code)
        status=0

        if code_error[:3]=="500":
            status=500
            
        if code_error[:3]=="400":
            status=400
        
        return JSONResponse(
            status_code=status,
            content=reponse_service.model_dump()
        )
    
    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=reponse_service.data)
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )

@app.post(
    "/cenexal-team/v2/hta/file/column",
    name="Get data from column with llm",
    operation_id="get_cenexal_team_column_data_with_llm",
    description="Gets the column data with llm from cenexal file, row by row, in a concatenated manner.",
)
async def hta_chat(request: Request,payload: DataframeQuery):
    
    api_key = request.headers.get("api-key")
    if not api_key:
        raise HTTPException(status_code=400, detail="api-key not provided")
    if request.headers.get("api-key")!=API_KEY:
        raise HTTPException(status_code=400, detail="Invalid api-key")        

    # Get column info
    reponse_service = LlmService.query_dataframe(llm_service,"HTA","HTA_mBC_Export_Adnan_PREPARED",payload.user_prompt,payload.max_token_output)
    if reponse_service.error.code != 0:
        
        code_error= str(reponse_service.error.code)
        status=0

        if code_error[:3]=="500":
            status=500
            
        if code_error[:3]=="400":
            status=400
        
        return JSONResponse(
            status_code=status,
            content=reponse_service.model_dump()
        )
    
    # OK
    response_obj = Response(error=Error(code=0, detail=""), data=reponse_service.data)
    return JSONResponse(
        status_code=200,
        content=response_obj.model_dump()
    )