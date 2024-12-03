from models.models import Response,Error
from repositories.excel.hta import ExcelHTARepository
import os

class FileService:
    
    def __init__(self,excelHTARepository : ExcelHTARepository):

        self.excelHTARepository = excelHTARepository
        
    def delete(self,file_name: str, file_extension: str):
        
        file_path = f'data/{file_name}.{file_extension}'
                       
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                return Response(error=Error(code=5001, detail="Error read sheet, details: "+e), data="")
              
        # Ok
        return Response(error=Error(code=0, detail=""), data="OK")
    
    def prepare(self,file: str, file_name: str, file_extension: str):
        
        if file=="HTA":
            json_data,error_details = self.excelHTARepository.prepare(file_name,file_extension)
            if error_details != "":
                return Response(error=Error(code=5001, detail="error prepare hta, details: "+error_details), data="")
                
        # Ok
        return Response(error=Error(code=0, detail=""), data=json_data)
    
    def get_column(self, file: str, file_name: str, file_extension: str,column_name: str, HTA_AGENCY_NAME: str, COUNTRY: str, HTA_DECISION_DT: str, BIOMARKERS: str, PRIMARY_DISEASE: str, DRUG_NAME: str, GENERIC_DRUG_NAME: str, DRUG_COMBINATIONS: str, TREATMENT_MODALITY: str, ASMR_REQUESTED: str, ASMR_RECIEVED: str, HTA_STATUS:str):
        
        if file=="HTA":
            result,error_details = self.excelHTARepository.get_columns(file_name,file_extension,column_name, HTA_AGENCY_NAME, COUNTRY, HTA_DECISION_DT, BIOMARKERS, PRIMARY_DISEASE, DRUG_NAME, GENERIC_DRUG_NAME, DRUG_COMBINATIONS, TREATMENT_MODALITY, ASMR_REQUESTED, ASMR_RECIEVED,HTA_STATUS)
            if error_details != "":
                return Response(error=Error(code=5001, detail=f"error get column {column_name} from hta: details: "+error_details), data={"rows":0,"column_data": ""})
                
                
        # Ok
        return Response(error=Error(code=0, detail=""), data=result)  
    
    def get_filters(self,file: str, file_name: str):
        
        if file=="HTA":
            json_data,error_details =  self.excelHTARepository.get_filters(file_name)
            if error_details != "":
                return Response(error=Error(code=5001, detail="error get filters from hta, details: "+error_details), data="")
                
        # Ok
        return Response(error=Error(code=0, detail=""), data=json_data)
        