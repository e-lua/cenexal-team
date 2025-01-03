import pandas as pd
import os
import numpy as np
import unicodedata

def clean_and_preserve(x):
    if isinstance(x, str):
        return x.strip()
    if pd.isna(x):
        return np.nan
    return str(x)

def clean_text_column(text):

    # Convert to string if not
    cleaned = str(text).strip()
    
    # Normalize text to remove invisible or unusual characters
    cleaned = unicodedata.normalize("NFKC", cleaned)
    
    # Clean
    cleaned = cleaned.lstrip('-').replace("- ","")

    # Convert to string and clean special characters
    cleaned = str(text).encode('ascii', 'ignore').decode('ascii')
    # Replace special quotes with single quotes
    cleaned = cleaned.replace('"', "'").replace('"', "'").replace('"', "'")
    
    return np.nan if not cleaned or cleaned.isspace() else cleaned

def format_coa_details(row):
    # Clean strings and manage non-existent columns
    def clean_str(value):
        if pd.isna(value):
            return ''
    
        # Convert to string if not
        cleaned = str(value).strip()
        
        # Final cleaning
        cleaned = cleaned.strip()
        if cleaned.startswith("+") or cleaned.startswith("-") or cleaned.startswith("="):
            cleaned = cleaned[1:]
        
        # Convert to string and clean special characters
        cleaned = str(value).encode('ascii', 'ignore').decode('ascii')
        # Replace special quotes with single quotes
        cleaned = cleaned.replace('"', "'").replace('"', "'").replace('"', "'")
        
        return str(value).strip().lstrip('-')
    
    def get_column_value(row, column_name):
        if column_name in row.index:
            return clean_str(row[column_name])
        return ''
    
    # First add the data from COA details column
    result = clean_str(row['COA details']) + "\n\n"
    
    for i in range(1, 6):
        # Only add info if the column exists and has data
        instrument_name = get_column_value(row, f'Instrument {i}')
        significance = get_column_value(row, f'Significance {i}')
        hta_discussion = get_column_value(row, f'Discussion by HTA body {i}')
        hta_details = get_column_value(row, f'HTA Discussion details {i}')
        
        if instrument_name:
            result += f"COA Instrument {i} Name: {instrument_name}\n"
            
        if significance:
            result += f"Instrument {i} Clinical Significance: {significance}\n"
            
        # Only add HTA Discussion line if either discussion or details exist
        if hta_discussion or hta_details:
            result += f"Instrument {i} HTA Discussion: {hta_discussion} & {hta_details}\n"
        
        # Only add new line if any data was added for this instrument
        if any([instrument_name, significance, hta_discussion, hta_details]):
            result += "\n"
    
    return result

def format_rwe_details(row):
    # Clean strings and manage non-existent columns
    def clean_str(value):
        if pd.isna(value):
            return ''
    
        # Convert to string if not
        cleaned = str(value).strip()
        
        # Final cleaning
        cleaned = cleaned.strip()
        if cleaned.startswith("+") or cleaned.startswith("-") or cleaned.startswith("="):
            cleaned = cleaned[1:]
        
        # Convert to string and clean special characters
        cleaned = str(value).encode('ascii', 'ignore').decode('ascii')
        # Replace special quotes with single quotes
        cleaned = cleaned.replace('"', "'").replace('"', "'").replace('"', "'")
        
        return str(value).strip().lstrip('-')
    
    def get_column_value(row, column_name):
        if column_name in row.index:
            return clean_str(row[column_name])
        return ''
    
    # First add the data from 'RWE used as supporting evidence?' column
    first_value = clean_str(row['RWE used as supporting evidence?'])
    result = first_value + "\n\n"
    
    if str(first_value)=="True":
        for i in range(1, 6):
            # Only add info if the column exists and has data
            rwe_source = get_column_value(row, f'RWE source {i}')
            tpye_of_source = get_column_value(row, f'Type of source {i}')
            rwe_area_supported = get_column_value(row, f'RWE Area Supported {i}')
            payer_acceptance = get_column_value(row, f'Payer Acceptance {i}')
            rwe_rationale = get_column_value(row, f'RWE Rationale {i}')
            additional_rwe_details = get_column_value(row, f'Additional RWE Details {i}')
            
            if rwe_source:
                result += f"RWE source {i}: {rwe_source}\n"
                
            if tpye_of_source:
                result += f"Type of source {i}: {tpye_of_source}\n"
                
            if rwe_area_supported:
                result += f"RWE Area Supported {i}: {rwe_area_supported}\n"
                
            if payer_acceptance:
                result += f"Payer Acceptance {i}: {payer_acceptance}\n"
                
            if rwe_rationale:
                result += f"RWE Rationale {i}: {rwe_rationale}\n"
                
            if additional_rwe_details:
                result += f"Additional RWE Details {i}: {additional_rwe_details}\n"
                
            # Only add new line if any data was added for this instrument
            if any([rwe_source, tpye_of_source, rwe_area_supported, payer_acceptance,rwe_rationale,additional_rwe_details]):
                result += "\n"
        
    return result

# This function takes the new rows from the "HTA Record Search" table and updates it into the cleaned and prepared CSV
def prepare_hta(path_source: str, path_destination: str, file_name: str, file_extension: str):
   
    try:
        excel_file = os.path.join(f'{path_source}/{file_name}.{file_extension}')
        csv_output = os.path.join(f'{path_destination}/{file_name}_PREPARED.csv')
        
        # Verify HTARecordSearch_Clean.csv
        if not os.path.exists(csv_output):
            # Create csv file
            with open(csv_output, 'w') as file:
                file.write("")
                
    except Exception as e:
        return "",f"Error get files, details: {e}"
        
    # Read sheet as DataFrame
    try:
        df = pd.read_excel(excel_file, sheet_name="HTA Record Search", header=1)
    except Exception as e:
        return "",f"Error read sheet, details: {e}"
    
    # Create new DataFrame
    df_new = pd.DataFrame()

    try:
        df_new['ID']=df['Direct link'].apply(lambda x: x.split("https://hta.quintiles.com/HTA/View/")[1] if "https://hta.quintiles.com/HTA/View/" in x else None)
        df_new['HTA_AGENCY_NAME']=df['Agency'].apply(clean_and_preserve) 
        df_new['COUNTRY']=df['Country'].apply(clean_and_preserve) 
        df_new['HTA_DECISION_DT'] = pd.to_datetime(df['Decision date'], format='%m/%d/%Y', errors='coerce')
        df_new['HTA_DECISION_DT']= df_new['HTA_DECISION_DT'].dt.strftime('%Y%m%d')
        df_new['HTA_DECISION_DT']= df_new['HTA_DECISION_DT'].astype(str)
        df_new['BIOMARKERS']=df['Primary_disease_subtype_3'].apply(clean_and_preserve) 
        df_new['PRIMARY_DISEASE']=df['Primary_disease_subtype_1(3)'].apply(clean_and_preserve) 
        df_new['DRUG_NAME']=df['Drug'].apply(clean_and_preserve) 
        df_new['GENERIC_DRUG_NAME']=df['Drug generic'].apply(clean_and_preserve)
        df_new['DRUG_COMBINATIONS']=df['Drug combinations'].apply(clean_and_preserve)    
        df_new['GENERAL_HTA_CONCLUSION']=df['General conclusion'].apply(clean_text_column).replace('nan', np.nan)
        df_new['DOSING']=df['Dosing'].apply(clean_text_column).replace('nan', np.nan)
        df_new['TREATMENT_DURATION']=df['Maximum treatment duration'].apply(clean_text_column).replace('nan', np.nan)
        df_new['INTERVENTION_ADD_DETAILS']=df['Additional details'].apply(clean_text_column).replace('nan', np.nan)
        df_new['TREATMENT_LINE']=df['Treatment line'].apply(clean_text_column).replace('nan', np.nan)
        df_new['TREATMENT_MODALITY']=df['Treatment modality'].apply(clean_text_column).replace('nan', np.nan)
        df_new['COMPARATOR_DRUGS']=df['Comparator drug(s) used by manufacturer'].apply(clean_text_column).replace('nan', np.nan)
        df_new['COMPARATOR_COMBINATION_THERAPY']=df['Comparator drug(s) used by manufacturer'].apply(clean_text_column).replace('nan', np.nan)
        df_new['COMPARATOR_DRUGS_PAYERS']=df['Most relevant comparator drug(s) for payer'].apply(clean_text_column).replace('nan', np.nan)
        df_new['COMPARATOR_ADD_DETAILS']=df['Additional comparator details'].apply(clean_text_column).replace('nan', np.nan)
        df_new['TARGET_POPULATION']=df['Reviewed indication'].apply(clean_text_column).replace('nan', np.nan)
        df_new['ASMR_REQUESTED']=df['ASMR requested (France)'].apply(clean_text_column).replace('nan', np.nan)
        df_new['ASMR_RECIEVED']=df['ASMR rating (France)'].apply(clean_text_column).replace('nan', np.nan)
        df_new['CLINICAL_OUTCOMES']=df['Clinical outcomes'].apply(clean_text_column).replace('nan', np.nan)
        df_new['DATA_PACKAGES']=df['Clinical evidence included'].apply(clean_text_column).replace('nan', np.nan)
        df_new['STUDY_TYPE']=df['Type of evidence evaluated'].apply(clean_text_column).replace('nan', np.nan)
        df_new['EVENDENCE_SYNTHESIS']=df['Type of evidence synthesis'].apply(clean_text_column).replace('nan', np.nan)
        df_new['OUTCOMES_FROM_EVIDENCE']=df['Outcomes from evidence synthesis evaluated'].apply(clean_text_column).replace('nan', np.nan)
        df_new['COA_INSTRUMENTS']=df['COA instrument'].apply(clean_text_column).replace('nan', np.nan)
        df_new['COA_TYPE']=df['COA type'].apply(clean_text_column).replace('nan', np.nan)
        df_new['COA_DETAILS']=df.apply(format_coa_details, axis=1)
        df_new['RWE_USED']=df['RWE used as supporting evidence?'].apply(clean_text_column).replace('nan', np.nan)
        df_new['RWE_DATA_TYPE']=df['Area supported'].apply(clean_text_column).replace('nan', np.nan)
        df_new['RWE_PAYER_ACCEPTED']=df['Accepted by payer?'].apply(clean_text_column).replace('nan', np.nan)
        df_new['HTA_ANALYSIS_TYPE']=df['Type of analysis'].apply(clean_text_column).replace('nan', np.nan)
        df_new['CEA_EFFECTIVENESS_MEASURE']=df['If CEA, what is effectiveness measure?'].apply(clean_text_column).replace('nan', np.nan)
        df_new['ECON_MODEL']=df['Type of model'].apply(clean_text_column).replace('nan', np.nan)
        df_new['TIME_HORIZON']=df['Time horizon'].apply(clean_text_column).replace('nan', np.nan)
        df_new['ECON_MODEL_DESIGN']=df['Model design and key assumptions'].apply(clean_text_column).replace('nan', np.nan)
        df_new['PAYER_DECISION']=df['Payer details'].apply(clean_text_column).replace('nan', np.nan)
        df_new['KEY_DRIVE_CE']=df['Key drivers of cost-effectiveness'].apply(clean_text_column).replace('nan', np.nan)
        df_new['GENERAL_HTA_CONCLUSION']=df['General conclusion'].apply(clean_text_column).replace('nan', np.nan)
        df_new['CLINICAL_POSITIVES']=df['Clinical positives'].apply(clean_text_column).replace('nan', np.nan)
        df_new['CLINICAL_NEGATIVES']=df['Clinical negatives'].apply(clean_text_column).replace('nan', np.nan)
        df_new['FINAL_RECOMMENDATION']=df['Recommendation'].apply(clean_text_column).replace('nan', np.nan)
        df_new['SUBGROUP_NAME'] = df['Subgroup name 1'].apply(clean_text_column).replace('nan', np.nan)+ ' ' + df['Subgroup name 2'].apply(clean_text_column).replace('nan', np.nan) + ' ' + df['Subgroup name 3'].apply(clean_text_column).replace('nan', np.nan)  + ' ' + df['Subgroup name 4'].apply(clean_text_column).replace('nan', np.nan) + ' ' + df['Subgroup name 5'].apply(clean_text_column).replace('nan', np.nan)
        df_new['HTA_STATUS']=df['HTA status'].apply(clean_text_column).replace('nan', np.nan)
        df_new['QUINTILES_LINK']=df['Direct link'].apply(clean_text_column).replace('nan', np.nan)
        df_new['WEB_URL']=df['Weblink'].apply(clean_text_column).replace('nan', np.nan)
        df_new['REIMBURSED_INDICATION']=df['Specify reimbursed indication (final)'].apply(clean_text_column).replace('nan', np.nan) + ' ' + df['Reimbursed indication'].apply(clean_text_column).replace('nan', np.nan)
        df_new['RWE_DETAILS']=df.apply(format_rwe_details, axis=1)
    except  Exception as e:
        return "",f"error prepare columns, details: {e}"
    
    # Read CSV
    try:
        df_cleaned = pd.read_csv(csv_output)
        process_data = True
    except pd.errors.EmptyDataError:
        df_final = df_new
        process_data = False

    if process_data:
        # Set as same type
        df_cleaned['ID']=df_cleaned['ID'].astype(str)
        df_new['ID']=df_new['ID'].astype(str)
        
        # Make sure 'ID' in the index in both dataframes
        df_alfa = df_cleaned.set_index('ID')
        df_beta = df_new.set_index('ID')
        
        # Get all IDs from both dataframes
        all_ids = set(df_alfa.index).union(set(df_beta.index))

        # List to storage results
        results = []

        # Iterar sobre todos los IDs
        for id_actual in all_ids:
            if id_actual in df_alfa.index:
                # If ID is in df_alfa
                results.append(df_alfa.loc[id_actual])
            else:
                # If ID is only in df_beta
                results.append(df_beta.loc[id_actual])

        # Create df_final
        df_final = pd.DataFrame(results)

        # Reset index to get 'ID' as column
        df_final = df_final.reset_index()
        df_final = df_final.rename(columns={'index': 'ID'})
        
    # Save new csv
    df_final.to_csv(csv_output, index=False)
    
    # Prepare filters
    filters= df_new[["HTA_AGENCY_NAME","COUNTRY","BIOMARKERS","PRIMARY_DISEASE","DRUG_NAME","GENERIC_DRUG_NAME","DRUG_COMBINATIONS","TREATMENT_MODALITY","ASMR_REQUESTED","ASMR_RECIEVED","HTA_STATUS"]]
    
    # Get unique values for each column 
    unique_values = {}
    for col in filters.columns: 
        unique_values[col] = list(set(filters[col].replace(np.nan,'nan').str.split(r'[,+]', expand=True).stack()))
    
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

