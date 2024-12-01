from datetime import datetime
import pandas as pd
import os

def create_filter_mask(df, column_name, filter_values):
    try:
        # If there are no filter values, return all True
        if not filter_values:
            return pd.Series([True] * len(df))
            
        # Clean and split the values
        if ',' in str(filter_values):
            # Multiple values
            values_list = [str(f.strip()) for f in filter_values.split(',')]
        else:
            # Unique value
            values_list = [str(filter_values).strip()]
        
        values_list = [str(f.strip()) for f in filter_values.split(',') if f.strip()]
        
        def safe_compare(x):
            if pd.isna(x):
                return False
            x_str = str(x)
            return any(str(f) in x_str for f in values_list)
            
        # Create the mask by applying the verification function
        return df[column_name].apply(safe_compare)
        
    except Exception as e:
        print(f"Error process values {column_name}: {str(e)}")
        # On error, return a mask that does not filter anything
        return pd.Series([True] * len(df))
    
# This function gets the data from the requested column and the record id from the cleaned file
def get_columns_hta(path: str,file_name: str, file_extension: str,column_name:str, HTA_AGENCY_NAME: str, COUNTRY: str, HTA_DECISION_DT: str, BIOMARKERS: str, PRIMARY_DISEASE: str, DRUG_NAME: str, GENERIC_DRUG_NAME: str, DRUG_COMBINATIONS: str, TREATMENT_MODALITY: str, ASMR_REQUESTED: str, ASMR_RECIEVED: str, HTA_STATUS:str):
    
    try:
        csv_output = os.path.join( f'{path}/{file_name}.{file_extension}')
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

