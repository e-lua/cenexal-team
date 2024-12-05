import pandas as pd

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
        # On error, return a mask that does not filter anything
        return pd.Series([True] * len(df))
