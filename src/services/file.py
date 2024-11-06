from repositories.azureopenai import AzureOpenAIRepository
from utils.get_column_hta import get_columns_hta
from utils.prepare_hta import prepare_hta
from models.models import Response,Error
import os

class FileService:
    
    def __init__(self,source_path: str,destination_path: str):
        
        self.source_path = source_path
        self.destination_path = destination_path

    def delete(self,file_name: str, file_extension: str):
        
        file_path = f'../data/{file_name}.{file_extension}'
        
        print(file_path)
               
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                return Response(error=Error(code=5001, detail="Error read sheet, details: "+e), data="")
                
                
        # Ok
        return Response(error=Error(code=0, detail=""), data="OK")
    
    def prepare(self,file: str, file_name: str, file_extension: str):
        
        if file=="HTA":
            json_data,error_details = prepare_hta(self.source_path,self.destination_path,file_name,file_extension)
            if error_details != "":
                return Response(error=Error(code=5001, detail="error prepare hta"), data="")
                
        # Ok
        return Response(error=Error(code=0, detail=""), data=json_data)
    
    def get_column(self, file: str, file_name: str, file_extension: str,column_name: str, HTA_AGENCY_NAME: str, COUNTRY: str, HTA_DECISION_DT: str, BIOMARKERS: str, PRIMARY_DISEASE: str, DRUG_NAME: str, GENERIC_DRUG_NAME: str, DRUG_COMBINATIONS: str, TREATMENT_MODALITY: str, ASMR_REQUESTED: str, ASMR_RECIEVED: str):
        
        if file=="HTA":
            result,error_details = get_columns_hta(self.destination_path,file_name,file_extension,column_name, HTA_AGENCY_NAME, COUNTRY, HTA_DECISION_DT, BIOMARKERS, PRIMARY_DISEASE, DRUG_NAME, GENERIC_DRUG_NAME, DRUG_COMBINATIONS, TREATMENT_MODALITY, ASMR_REQUESTED, ASMR_RECIEVED)
            if error_details != "":
                return Response(error=Error(code=5001, detail=f"error get column {column_name} from hta: details: "+error_details), data="")
                
                
        # Ok
        return Response(error=Error(code=0, detail=""), data=result)   