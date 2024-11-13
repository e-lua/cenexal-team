from datetime import datetime
import pandas as pd
import os

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
    if HTA_AGENCY_NAME: 
        HTA_AGENCY_NAME = [f.strip() for f in HTA_AGENCY_NAME.split(',')] 
        mask_HTA_AGENCY_NAME = df_cleaned['HTA_AGENCY_NAME'].apply(lambda x: any([f in x for f in HTA_AGENCY_NAME])) 
    else: 
        mask_HTA_AGENCY_NAME = pd.Series([True] * len(df_cleaned)) 
        
    if COUNTRY: 
        COUNTRY = [f.strip() for f in COUNTRY.split(',')] 
        mask_COUNTRY= df_cleaned['COUNTRY'].apply(lambda x: any([f in x for f in COUNTRY])) 
    else: 
        mask_COUNTRY = pd.Series([True] * len(df_cleaned)) 
    
    if HTA_DECISION_DT: 
        HTA_DECISION_DT = [f.strip() for f in HTA_DECISION_DT.split(',')] 
        mask_HTA_DECISION_DT = df_cleaned['HTA_DECISION_DT'].apply(lambda x: any([f in x for f in HTA_DECISION_DT])) 
    else: 
        mask_HTA_DECISION_DT = pd.Series([True] * len(df_cleaned)) 
     
    if BIOMARKERS: 
        BIOMARKERS = [f.strip() for f in BIOMARKERS.split(',')] 
        mask_BIOMARKERS = df_cleaned['BIOMARKERS'].apply(lambda x: any([f in x for f in BIOMARKERS])) 
    else: 
        mask_BIOMARKERS = pd.Series([True] * len(df_cleaned)) 
       
    if PRIMARY_DISEASE: 
        PRIMARY_DISEASE = [f.strip() for f in PRIMARY_DISEASE.split(',')] 
        mask_PRIMARY_DISEASE = df_cleaned['PRIMARY_DISEASE'].apply(lambda x: any([f in x for f in PRIMARY_DISEASE])) 
    else: 
        mask_PRIMARY_DISEASE = pd.Series([True] * len(df_cleaned)) 
     
    if DRUG_NAME: 
        DRUG_NAME = [f.strip() for f in DRUG_NAME.split(',')] 
        mask_DRUG_NAME = df_cleaned['DRUG_NAME'].apply(lambda x: any([f in x for f in DRUG_NAME])) 
    else: 
        mask_DRUG_NAME = pd.Series([True] * len(df_cleaned)) 
     
    if GENERIC_DRUG_NAME: 
        GENERIC_DRUG_NAME = [f.strip() for f in GENERIC_DRUG_NAME.split(',')] 
        mask_GENERIC_DRUG_NAME = df_cleaned['GENERIC_DRUG_NAME'].apply(lambda x: any([f in x for f in GENERIC_DRUG_NAME])) 
    else: 
        mask_GENERIC_DRUG_NAME = pd.Series([True] * len(df_cleaned)) 
     
    if DRUG_COMBINATIONS: 
        DRUG_COMBINATIONS = [f.strip() for f in DRUG_COMBINATIONS.split(',')] 
        mask_DRUG_COMBINATIONS = df_cleaned['DRUG_COMBINATIONS'].apply(lambda x: any([f in x for f in DRUG_COMBINATIONS])) 
    else: 
        mask_DRUG_COMBINATIONS = pd.Series([True] * len(df_cleaned)) 
     
    if TREATMENT_MODALITY: 
        TREATMENT_MODALITY = [f.strip() for f in TREATMENT_MODALITY.split(',')] 
        mask_TREATMENT_MODALITY = df_cleaned['TREATMENT_MODALITY'].apply(lambda x: any([f in x for f in TREATMENT_MODALITY])) 
    else: 
        mask_TREATMENT_MODALITY = pd.Series([True] * len(df_cleaned)) 
     
    if ASMR_REQUESTED: 
        ASMR_REQUESTED = [f.strip() for f in ASMR_REQUESTED.split(',')] 
        mask_ASMR_REQUESTED = df_cleaned['ASMR_REQUESTED'].apply(lambda x: any([f in x for f in ASMR_REQUESTED])) 
    else: 
        mask_ASMR_REQUESTED = pd.Series([True] * len(df_cleaned)) 
     
    if ASMR_RECIEVED: 
        ASMR_RECIEVED = [f.strip() for f in ASMR_RECIEVED.split(',')] 
        mask_ASMR_RECIEVED = df_cleaned['ASMR_RECIEVED'].apply(lambda x: any([f in x for f in ASMR_RECIEVED])) 
    else: 
        mask_ASMR_RECIEVED = pd.Series([True] * len(df_cleaned)) 
    
    if HTA_STATUS: 
        HTA_STATUS = [f.strip() for f in HTA_STATUS.split(',')] 
        mask_HTA_STATUS = df_cleaned['HTA_STATUS'].apply(lambda x: any([f in x for f in HTA_STATUS])) 
    else: 
        mask_HTA_STATUS = pd.Series([True] * len(df_cleaned)) 
     
        
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

