from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models.models import Response,Error,SummarizeQuery
from repositories.azureopenai import AzureOpenAIRepository
from services.file import FileService
from services.llm import LlmService
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

# Initialize AzureOpenAIRepository
azure_open_ai_repository = AzureOpenAIRepository(azure_openai_url=os.getenv("AZURE_OPENAI_URL"),azure_deployment=os.getenv("AZURE_DEPLOYMENT"),azure_openai_api_key=os.getenv("AZURE_OPENAI_KEY"),azure_endpoint=os.getenv("AZURE_ENDPOINT"),azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION"))

# Initialize FileService
file_service = FileService(source_path="data",destination_path="data")

# Initialize LlmService
llm_service = LlmService(os.getenv("AZURE_DEPLOYMENT"),os.getenv("AZURE_OPENAI_KEY"),azure_open_ai_repository)

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

@app.get("/cenexal-team/v1/file")
async def get_all_file():
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

@app.post("/cenexal-team/v1/hta/file/prepare")
async def prepare_file(file: UploadFile = File(...)):
    
    filename_splitted = file.filename.split(".")  
    file_name = filename_splitted[0]
    file_extension =  filename_splitted[1]
        
    # Delete source file
    reponse_delete_source = FileService.delete(file_service,file_name,file_extension)
    if reponse_delete_source.error.code != 0:
        return JSONResponse(
            status_code=500,
            content=reponse_delete_source.model_dump()
        )
    
    # Delete destination file - CSV Prepared
    reponse_delete_destination = FileService.delete(file_service,file_name+"_PREPARED","csv")
    if reponse_delete_destination.error.code != 0:
        return JSONResponse(
            status_code=500,
            content=reponse_delete_destination.model_dump()
        )
    
    # Delete destination file - JSON Prepared
    reponse_delete_destination = FileService.delete(file_service,"hta","json")
    if reponse_delete_destination.error.code != 0:
        return JSONResponse(
            status_code=500,
            content=reponse_delete_destination.model_dump()
        )
    
    # Storage file
    file_location = os.path.join('data', file.filename)
    with open(file_location, "wb") as file_object:
        file_object.write(file.file.read())
        
    # Prepare file
    reponse_service = FileService.prepare(file_service,"HTA",file_name,file_extension)
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

@app.get("/cenexal-team/v1/hta/file/column")
async def get_column(file_name: str, file_extension: str, column_name: str, HTA_AGENCY_NAME: str, COUNTRY: str, HTA_DECISION_DT: str, BIOMARKERS: str, PRIMARY_DISEASE: str, DRUG_NAME: str, GENERIC_DRUG_NAME: str, DRUG_COMBINATIONS: str, TREATMENT_MODALITY: str, ASMR_REQUESTED: str, ASMR_RECIEVED: str):
    
    # Get column info
    reponse_service = FileService.get_column(file_service,"HTA",file_name,file_extension,column_name, HTA_AGENCY_NAME, COUNTRY, HTA_DECISION_DT, BIOMARKERS, PRIMARY_DISEASE, DRUG_NAME, GENERIC_DRUG_NAME, DRUG_COMBINATIONS, TREATMENT_MODALITY, ASMR_REQUESTED, ASMR_RECIEVED)
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

@app.post("/cenexal-team/v1/hta/summarize")
async def summarize(payload: SummarizeQuery):
    
    # Get column info
    reponse_service = LlmService.get_summary(llm_service,payload.max_token_input,payload.max_token_output,payload.text_to_summary,payload.user_prompt)
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
