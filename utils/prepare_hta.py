import pandas as pd
import os
import json
import re

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
        df_new['HTA_AGENCY_NAME']=df['Agency'].apply(lambda x: x.strip() if isinstance(x, str) else x)
        df_new['COUNTRY']=df['Country'].apply(lambda x: x.strip() if isinstance(x, str) else x).fillna('na').replace('', 'na').astype(str)
        df_new['HTA_DECISION_DT'] = pd.to_datetime(df['Decision date'], format='%m/%d/%Y')
        df_new['HTA_DECISION_DT']= df_new['HTA_DECISION_DT'].dt.strftime('%Y%m%d')
        df_new['BIOMARKERS']=df['Primary_disease_subtype_3'].apply(lambda x: x.strip() if isinstance(x, str) else x).fillna('na').replace('', 'na').astype(str)
        df_new['PRIMARY_DISEASE']=df['Primary_disease_subtype_1(3)'].apply(lambda x: x.strip() if isinstance(x, str) else x).fillna('na').replace('', 'na').astype(str)
        df_new['DRUG_NAME']=df['Drug'].apply(lambda x: x.strip() if isinstance(x, str) else x).fillna('na').replace('', 'na').astype(str)
        df_new['GENERIC_DRUG_NAME']=df['Drug generic'].apply(lambda x: x.strip() if isinstance(x, str) else x).fillna('na').replace('', 'na').astype(str)
        df_new['DRUG_COMBINATIONS']=df['Drug combinations'].apply(lambda x: x.strip() if isinstance(x, str) else x).fillna('na').replace('', 'na').astype(str)        
        df_new['GENERAL_HTA_CONCLUSION']=df['General conclusion'].fillna('na').replace('', 'na').astype(str)
        df_new['DOSING']=df['Dosing'].fillna('na').replace('', 'na').astype(str)
        df_new['TREATMENT_DURATION']=df['Maximum treatment duration'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['INTERVENTION_ADD_DETAILS']=df['Additional details'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['TREATMENT_LINE']=df['Treatment line'].str.strip().fillna('na').replace('', 'na').str.lstrip('-')
        df_new['TREATMENT_MODALITY']=df['Treatment modality'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['COMPARATOR_DRUGS']=df['Comparator drug(s) used by manufacturer'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['COMPARATOR_COMBINATION_THERAPY']=df['Comparator drug(s) used by manufacturer'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['COMPARATOR_DRUGS_PAYERS']=df['Most relevant comparator drug(s) for payer'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['COMPARATOR_ADD_DETAILS']=df['Additional comparator details'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['TARGET_POPULATION']=df['Reviewed indication'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['ASMR_REQUESTED']=df['ASMR requested (France)'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['ASMR_RECIEVED']=df['ASMR rating (France)'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['CLINICAL_OUTCOMES']=df['Clinical outcomes'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['DATA_PACKAGES']=df['Clinical evidence included'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['STUDY_TYPE']=df['Type of evidence evaluated'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['EVENDENCE_SYNTHESIS']=df['Type of evidence synthesis'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['OUTCOMES_FROM_EVIDENCE']=df['Outcomes from evidence synthesis evaluated'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['COA_INSTRUMENTS']=df['COA instrument'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['COA_TYPE']=df['COA type'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['COA_DETAILS']=df['COA details'].fillna('na').replace('', 'na').str.strip().str.lstrip('-')
        df_new['RWE_USED']=df['RWE used as supporting evidence?'].fillna('na').replace('', 'na').astype(str)
        df_new['RWE_DATA_TYPE']=df['Area supported'].fillna('na').replace('', 'na').astype(str)
        df_new['RWE_PAYER_ACCEPTED']=df['Accepted by payer?'].fillna('na').replace('', 'na').astype(str)
        df_new['HTA_ANALYSIS_TYPE']=df['Type of analysis'].fillna('na').replace('', 'na').astype(str)
        df_new['CEA_EFFECTIVENESS_MEASURE']=df['If CEA, what is effectiveness measure?'].fillna('na').replace('', 'na').astype(str)
        df_new['ECON_MODEL']=df['Type of model'].fillna('na').replace('', 'na').astype(str)
        df_new['TIME_HORIZON']=df['Time horizon'].fillna('na').replace('', 'na').astype(str)
        df_new['ECON_MODEL_DESIGN']=df['Model design and key assumptions'].fillna('na').replace('', 'na').astype(str)
        df_new['PAYER_DECISION']=df['Payer details'].fillna('na').replace('', 'na').astype(str)
        df_new['KEY_DRIVE_CE']=df['Key drivers of cost-effectiveness'].fillna('na').replace('', 'na').astype(str)
        df_new['GENERAL_HTA_CONCLUSION']=df['General conclusion'].fillna('na').replace('', 'na').astype(str)
        df_new['GENERAL_HTA_CONCLUSION_SUMMARY']=''
        df_new['CLINICAL_POSITIVES']=df['Clinical positives'].fillna('na').replace('', 'na').astype(str)
        df_new['CLINICAL_NEGATIVES']=df['Clinical negatives'].fillna('na').replace('', 'na').astype(str)
        df_new['FINAL_RECOMMENDATION']=df['Recommendation'].fillna('na').replace('', 'na').astype(str)
        df_new['SUBGROUP_NAME'] = df['Subgroup name 1'].fillna('na').replace('', 'na').astype(str) + ' ' + df['Subgroup name 2'].fillna('na').replace('', 'na').astype(str) + ' ' + df['Subgroup name 3'].fillna('na').replace('', 'na').astype(str) + ' ' + df['Subgroup name 4'].fillna('na').replace('', 'na').astype(str) + ' ' + df['Subgroup name 5'].fillna('na').replace('', 'na').astype(str)
        df_new['HTA_STATUS']=df['HTA status'].fillna('na').replace('', 'na').astype(str)
        df_new['QUINTILES_LINK']=df['Direct link'].fillna('na').replace('', 'na').astype(str)
        df_new['WEB_URL']=df['Weblink'].fillna('na').replace('', 'na').astype(str)
    except:
        return "","Error prepare columns"
    
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

