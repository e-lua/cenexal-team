from utils.create_filter_mask import create_filter_mask
from utils.prepare_hta import prepare_hta
import pandas as pd
import os


class ExcelHTARepository:
    
    def __init__(self,source_path: str,destination_path: str):
        
        self.source_path = source_path
        self.destination_path = destination_path
    
    # This function gets the data from the requested column and the record id from the cleaned file
    def get_columns(self,file_name: str, file_extension: str,column_name:str, HTA_AGENCY_NAME: str, COUNTRY: str, HTA_DECISION_DT: str, BIOMARKERS: str, PRIMARY_DISEASE: str, DRUG_NAME: str, GENERIC_DRUG_NAME: str, DRUG_COMBINATIONS: str, TREATMENT_MODALITY: str, ASMR_REQUESTED: str, ASMR_RECIEVED: str, HTA_STATUS:str):
                    
        try:
            csv_output = os.path.join( f'{self.destination_path}/{file_name}.{file_extension}')
        except Exception as e:
            return {"rows":0,"column_data": ""},str(e)

        # Read CSV
        try:
            df_cleaned = pd.read_csv(csv_output)
        except pd.errors.EmptyDataError:
            return {"rows":0,"column_data": ""},"No data to process"
        except Exception as e:
            return {"rows":0,"column_data": ""},str(e)
        
        # Filter 'df_cleaned'    
        mask_HTA_AGENCY_NAME = create_filter_mask(df_cleaned, 'HTA_AGENCY_NAME', HTA_AGENCY_NAME)      
        mask_COUNTRY = create_filter_mask(df_cleaned, 'COUNTRY', COUNTRY)  
        mask_HTA_DECISION_DT = create_filter_mask(df_cleaned, 'HTA_DECISION_DT', HTA_DECISION_DT)
        mask_BIOMARKERS = create_filter_mask(df_cleaned, 'BIOMARKERS', BIOMARKERS)
        mask_PRIMARY_DISEASE = create_filter_mask(df_cleaned, 'PRIMARY_DISEASE', PRIMARY_DISEASE)
        mask_DRUG_NAME = create_filter_mask(df_cleaned, 'DRUG_NAME', DRUG_NAME)
        mask_GENERIC_DRUG_NAME = create_filter_mask(df_cleaned, 'GENERIC_DRUG_NAME', GENERIC_DRUG_NAME)
        mask_DRUG_COMBINATIONS = create_filter_mask(df_cleaned, 'DRUG_COMBINATIONS', DRUG_COMBINATIONS)
        mask_TREATMENT_MODALITY = create_filter_mask(df_cleaned, 'TREATMENT_MODALITY', TREATMENT_MODALITY)
        mask_ASMR_REQUESTED = create_filter_mask(df_cleaned, 'ASMR_REQUESTED', ASMR_REQUESTED)
        mask_ASMR_RECIEVED = create_filter_mask(df_cleaned, 'ASMR_RECIEVED', ASMR_RECIEVED)
        mask_HTA_STATUS = create_filter_mask(df_cleaned, 'HTA_STATUS', HTA_STATUS)     
            
        filtered_df = df_cleaned[mask_HTA_AGENCY_NAME & mask_COUNTRY & mask_HTA_DECISION_DT & mask_BIOMARKERS & mask_PRIMARY_DISEASE & mask_DRUG_NAME & mask_GENERIC_DRUG_NAME & mask_DRUG_COMBINATIONS & mask_TREATMENT_MODALITY & mask_ASMR_REQUESTED & mask_ASMR_RECIEVED & mask_HTA_STATUS]
        
        
        # Return specified column if it exists 
        if column_name in filtered_df.columns:
            
            try:
                all_data_from_column = filtered_df[column_name].tolist()
            except Exception as e:
                return "",e

            result =  ". ".join(all_data_from_column)
            result += "."
        
        else: 
            return {"rows":0,"column_data": ""},"Column does not exist"

        # Print
        return {"rows":len(all_data_from_column),"column_data": result},""

    # This function gets all the filters and returns as json
    def get_filters(self, file_name: str):
    
        try:
            csv_output = os.path.join(f'{self.destination_path}/{file_name}.csv')
            
        except Exception as e:
            return "",f"Error get files, details: {e}"
            
        
        # Read CSV
        try:
            df_cleaned = pd.read_csv(csv_output)
        except Exception as e:
            return "",f"Error read csv, details: {e}"
        
        # Prepare filters
        filters= df_cleaned[["HTA_AGENCY_NAME","COUNTRY","BIOMARKERS","PRIMARY_DISEASE","DRUG_NAME","GENERIC_DRUG_NAME","DRUG_COMBINATIONS","TREATMENT_MODALITY","ASMR_REQUESTED","ASMR_RECIEVED","HTA_STATUS"]]
        
        # Get unique values for each column 
        unique_values = {}
        for col in filters.columns: 
            unique_values[col] = list(set(filters[col].str.split(r'[,+]', expand=True).stack()))
        
        # Create JSON
        output = []
        for col, values in unique_values.items():
                
            # Remove duplicates and sort values
            unique_sorted_values = sorted({val.strip() for val in values if val.strip().lower() != "na"})
            
            # Create the choices sorted and with unique values
            choices = [{"title": val, "value": val} for val in unique_sorted_values]
            
            output.append({"id":col,"label": f"Select one or many {col}", "choices": choices, "placeholder": "", "isMultiSelect": True})          
            
        # Print
        return output,""

    # This function takes the new rows from the "HTA Record Search" table and updates it into the cleaned and prepared CSV
    def prepare(self, file_name: str, file_extension: str):
        
        json_data,error_details = prepare_hta(self.source_path,self.destination_path,file_name,file_extension)
        
        return json_data,error_details