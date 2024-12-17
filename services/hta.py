from models.models import Response,Error
from repositories.excel.hta import ExcelHTARepository
from repositories.ms_sql_server.hta import MsSQLServerHTARepository
from repositories.azure_blob_storage import BlobStorageRepository
import os

class HTAService:
    
    def __init__(self,excelHTARepository : ExcelHTARepository,sqlServerHTARepository: MsSQLServerHTARepository,blobStorageRepository: BlobStorageRepository):

        self.excelHTARepository = excelHTARepository
        self.sqlServerHTARepository = sqlServerHTARepository
        self.blobStorageRepository = blobStorageRepository
        
    def delete_files(self,file_name: str, file_extension: str):
        
        file_path = f'data/{file_name}.{file_extension}'
                       
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                return Response(error=Error(code=5001, detail="Error read sheet, details: "+e), data="")
              
        # Ok
        return Response(error=Error(code=0, detail=""), data="OK")
    
    def prepare_clean_excel(self,file_name: str, file_extension: str):
    
        json_data,error_details = self.excelHTARepository.prepare(file_name,file_extension)
        if error_details != "":
            return Response(error=Error(code=5001, detail="error prepare hta, details: "+error_details), data="")
                
        # Ok
        return Response(error=Error(code=0, detail=""), data=json_data)
    
    def get_columns_from_excel(self, file_name: str, file_extension: str,column_name: str, HTA_AGENCY_NAME: str, COUNTRY: str, HTA_DECISION_DT: str, BIOMARKERS: str, PRIMARY_DISEASE: str, DRUG_NAME: str, GENERIC_DRUG_NAME: str, DRUG_COMBINATIONS: str, TREATMENT_MODALITY: str, ASMR_REQUESTED: str, ASMR_RECIEVED: str, HTA_STATUS:str):
    
        result,error_details = self.excelHTARepository.get_columns(file_name,file_extension,column_name, HTA_AGENCY_NAME, COUNTRY, HTA_DECISION_DT, BIOMARKERS, PRIMARY_DISEASE, DRUG_NAME, GENERIC_DRUG_NAME, DRUG_COMBINATIONS, TREATMENT_MODALITY, ASMR_REQUESTED, ASMR_RECIEVED,HTA_STATUS)
        if error_details != "":
            return Response(error=Error(code=5001, detail=f"error get column {column_name} from hta: details: "+error_details), data={"rows":0,"column_data": ""})
                    
        # Ok
        return Response(error=Error(code=0, detail=""), data=result)  
    
    def get_filters_from_excel(self,file_name: str):
        
        json_data,error_details =  self.excelHTARepository.get_filters(file_name)
        if error_details != "":
            return Response(error=Error(code=5001, detail="error get filters from hta, details: "+error_details), data="")
            
        # Ok
        return Response(error=Error(code=0, detail=""), data=json_data)
    
    def move_from_excel_to_database(self,file_name: str):
    
        dataframe_hta,error_details = self.excelHTARepository.get_data(file_name)
        if error_details != "":
            return Response(error=Error(code=5001, detail="error get the hta as a dataframe, details: "+error_details), data="")
        
        if dataframe_hta.empty:
            return Response(error=Error(code=5001, detail=error_details), data=[])
    
        error_update = self.sqlServerHTARepository.udpate(dataframe_hta)
        if error_update != "":
                return Response(error=Error(code=5001, detail="error update in database, details: "+error_update), data="")
            
        # Ok
        return Response(error=Error(code=0, detail=""), data="OK")
        
    def move_from_database_to_blob(self):
        
        # Query sql
        query = "SELECT ID,HTA_AGENCY_NAME,COUNTRY,HTA_DECISION_DT,HTA_DECISION_DT,HTA_DECISION_DT,BIOMARKERS,PRIMARY_DISEASE,DRUG_NAME,GENERIC_DRUG_NAME,DRUG_COMBINATIONS,GENERAL_HTA_CONCLUSION,DOSING,TREATMENT_DURATION,INTERVENTION_ADD_DETAILS ,TREATMENT_LINE,TREATMENT_MODALITY,COMPARATOR_DRUGS,COMPARATOR_COMBINATION_THERAPY,COMPARATOR_DRUGS_PAYERS,COMPARATOR_ADD_DETAILS,TARGET_POPULATION,ASMR_REQUESTED,ASMR_RECIEVED ,CLINICAL_OUTCOMES,DATA_PACKAGES,STUDY_TYPE,EVENDENCE_SYNTHESIS,OUTCOMES_FROM_EVIDENCE,COA_INSTRUMENTS,COA_TYPE,COA_DETAILS,RWE_USED,RWE_DATA_TYPE,RWE_PAYER_ACCEPTED,HTA_ANALYSIS_TYPE,CEA_EFFECTIVENESS_MEASURE,ECON_MODEL,TIME_HORIZON,ECON_MODEL_DESIGN,PAYER_DECISION,KEY_DRIVE_CE,GENERAL_HTA_CONCLUSION,CLINICAL_POSITIVES,CLINICAL_NEGATIVES,FINAL_RECOMMENDATION,SUBGROUP_NAME,HTA_STATUS,QUINTILES_LINK,WEB_URL,REIMBURSED_INDICATION,CONCAT('ID:',ID,',HTA_AGENCY_NAME:',HTA_AGENCY_NAME,',COUNTRY:',COUNTRY,',HTA_DECISION_DT:',HTA_DECISION_DT,',HTA_DECISION_DT:',HTA_DECISION_DT,',HTA_DECISION_DT:',HTA_DECISION_DT,',BIOMARKERS:',BIOMARKERS,',PRIMARY_DISEASE:',PRIMARY_DISEASE,',DRUG_NAME:',DRUG_NAME,',GENERIC_DRUG_NAME:',GENERIC_DRUG_NAME,',DRUG_COMBINATIONS:',DRUG_COMBINATIONS,',TREATMENT_MODALITY:',TREATMENT_MODALITY,',ASMR_REQUESTED:',ASMR_REQUESTED,',ASMR_RECIEVED:',ASMR_RECIEVED,',HTA_STATUS:',HTA_STATUS) AS COLUMN_TO_VECTORIZE FROM HTA"
        result_query = self.sqlServerHTARepository.query(query)
        if not result_query:
            return Response(error=Error(code=4002, detail="No data found"), data=[])
        
        number_rows,error_insert = self.blobStorageRepository.insert_data_into_table_storage(result_query)
        if error_insert != "":
                return Response(error=Error(code=5003, detail="error insert in blob, details: "+error_insert), data="")
            
        
        # Ok
        return Response(error=Error(code=0, detail=""), data=number_rows)