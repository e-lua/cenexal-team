from models.models import Response,Error
from repositories.excel.hta import ExcelHTARepository
from repositories.ms_sql_server.hta import MsSQLServerHTARepository
from repositories.azure_blob_storage import BlobStorageRepository
from repositories.azure_openai import AzureOpenAIRepository
from repositories.azure_ai_search import AISearchRepository
import numpy as np
import os
import json

class HTAService:
    
    def __init__(self,excelHTARepository : ExcelHTARepository,sqlServerHTARepository: MsSQLServerHTARepository,blobStorageRepository: BlobStorageRepository,azureopenaiRepository:AzureOpenAIRepository,aisearchRepository:AISearchRepository):

        self.excelHTARepository = excelHTARepository
        self.sqlServerHTARepository = sqlServerHTARepository
        self.blobStorageRepository = blobStorageRepository
        self.azureopenaiRepository=azureopenaiRepository
        self.aisearchRepository=aisearchRepository
        
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
    
    def generate_json(self):
        
        # Query sql
        query = "SELECT ID,HTA_AGENCY_NAME,COUNTRY,HTA_DECISION_DT,HTA_DECISION_DT,HTA_DECISION_DT,BIOMARKERS,PRIMARY_DISEASE,DRUG_NAME,GENERIC_DRUG_NAME,DRUG_COMBINATIONS,GENERAL_HTA_CONCLUSION,DOSING,TREATMENT_DURATION,INTERVENTION_ADD_DETAILS ,TREATMENT_LINE,TREATMENT_MODALITY,COMPARATOR_DRUGS,COMPARATOR_COMBINATION_THERAPY,COMPARATOR_DRUGS_PAYERS,COMPARATOR_ADD_DETAILS,TARGET_POPULATION,ASMR_REQUESTED,ASMR_RECIEVED ,CLINICAL_OUTCOMES,DATA_PACKAGES,STUDY_TYPE,EVENDENCE_SYNTHESIS,OUTCOMES_FROM_EVIDENCE,COA_INSTRUMENTS,COA_TYPE,COA_DETAILS,RWE_USED,RWE_DATA_TYPE,RWE_PAYER_ACCEPTED,HTA_ANALYSIS_TYPE,CEA_EFFECTIVENESS_MEASURE,ECON_MODEL,TIME_HORIZON,ECON_MODEL_DESIGN,PAYER_DECISION,KEY_DRIVE_CE,GENERAL_HTA_CONCLUSION,CLINICAL_POSITIVES,CLINICAL_NEGATIVES,FINAL_RECOMMENDATION,SUBGROUP_NAME,HTA_STATUS,QUINTILES_LINK,WEB_URL,REIMBURSED_INDICATION,COLUMN_TO_VECTORIZE FROM VIEW_HTA_V2"
        result_query = self.sqlServerHTARepository.query(query)
        if not result_query:
            return Response(error=Error(code=4002, detail="No data found"), data=[])
        
        vectors_from_column_to_vectorize = []
        
        # Add the new column to each object in the array
        for obj in result_query:
            obj["vectors_from_column_to_vectorize"] = vectors_from_column_to_vectorize
            
        # File name
        nombre_archivo = "data/hta.json"

        # Save data to file
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(result_query, archivo, indent=4)
        
        # Ok
        return Response(error=Error(code=0, detail=""), data=len(result_query))
    
    def convert_json_to_vector(self):
                            
        # File name
        nombre_archivo = "data/hta.json"

        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        # Make sure it is an array and not empty
        if isinstance(datos, list) and len(datos) > 0:
            
            num_chunks=2
            num_fin=393
            for i in range(380,num_fin):
                
                objeto = datos[i]
                
                # Get the value of the COLUMN_TO_VECTORIZE field
                valor_column_to_vectorize = objeto.get("COLUMN_TO_VECTORIZE")
                                    
                words = valor_column_to_vectorize.split()
                chunk_size = len(words) // num_chunks
                chunks = [' '.join(words[i * chunk_size:(i + 1) * chunk_size]) for i in range(num_chunks)]
                
                # Add remaining words to the last chunk
                if len(words) % num_chunks != 0:
                    chunks[-1] += ' ' + ' '.join(words[num_chunks * chunk_size:])

                # Get the embeddings of each chunk
                embeddings = []
                for chunk in chunks:
                    vector, error =  self.azureopenaiRepository.embedding(chunk)
                    if error:
                        print(f"Error generating embedding: {error}")
                        continue
                    embeddings.append(vector)
                    
                if not embeddings:
                    return Response(error=Error(code=2, detail="No embeddings were generated."), data="")
            
                # Convert embeddings to numpy arrays
                embeddings_np = [np.array(embedding) for embedding in embeddings]
                
                # Calculate the average
                averaged_embedding = np.mean(embeddings_np, axis=0)
                
                # Update the value of the column_vector field
                objeto["vectors_from_column_to_vectorize"] = averaged_embedding.tolist()
                
            # Save changes to JSON file
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
                                   
        else:
            print("The JSON file does not contain an array or is empty.")
            
        # Ok
        return Response(error=Error(code=0, detail=""), data=num_fin)
    
    def get_dimensions_from_json(self):
                            
        # Nombre del archivo
        nombre_archivo = "data/hta.json"

        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        # Make sure it is an array and not empty
        if isinstance(datos, list) and len(datos) > 0:
            
            dimensions = []
            
            for i in range(0,393):
                
                objeto = datos[i]
                
                # Get the value of the vectors_from_column_to_vectorize field
                vectors = objeto.get("vectors_from_column_to_vectorize")
                                    
                dimensions.append(len(vectors))
                       
        else:
            print("El archivo JSON no contiene un array o está vacío.")
            
        # Ok
        return Response(error=Error(code=0, detail=""), data=max(dimensions))
    
    def update_json_in_aisearch(self):
                            
        # Nombre del archivo
        file_name = "data/hta_to_aisearch.json"

        with open(file_name, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
        
        # Update Index in AzureAISearch
        response_aisearch,error_search = self.aisearchRepository.update_index(json_data)
        if error_search != "":
            return Response(error=Error(code=5005, detail=error_search), data="")
         
        # Ok
        return Response(error=Error(code=0, detail=""), data=response_aisearch)