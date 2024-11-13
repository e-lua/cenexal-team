import pandas as pd
import os
import json
import re

# This function gets all the filters
def get_filters(path_source: str, path_destination: str, file_name: str):
   
    try:
        csv_output = os.path.join(f'{path_destination}/{file_name}.csv')
        
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

