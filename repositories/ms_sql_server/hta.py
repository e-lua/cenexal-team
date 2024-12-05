from sqlalchemy import create_engine, text,inspect,QueuePool
from sqlalchemy.orm import sessionmaker
from typing import Any
import pandas as pd


class MsSQLServerHTARepository:
    
    def __init__(self,username: str,password: str,server: str,database: str):
        
        self.connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
        self.engine = create_engine(self.connection_string,poolclass=QueuePool,pool_size=50,max_overflow=100)
        
    def udpate(self,dataframe: pd.DataFrame):
        
        table_name="HTA"
        
        try:
                
            # Replace all empty/null values ​​with empty string since all columns are non-null
            dataframe = dataframe.fillna('')
            
            # Convert float64 columns to string
            float_cols = dataframe.select_dtypes(include=['float64']).columns
            for col in float_cols:
                dataframe[col] = dataframe[col].astype(str, errors='ignore')
                dataframe[col] = dataframe[col].replace('nan', '')
            
            # Convert DataFrame to list of dictionaries (equivalent to JSON)
            data_as_json = dataframe.to_dict(orient="records")

            with self.engine.connect() as connection:
                # Start transaction
                with connection.begin() as transaction:
                    # Step 1: Delete data from the table
                    delete_query = text(f"DELETE FROM {table_name}")
                    connection.execute(delete_query)
                    print(f"Data deleted from table '{table_name}'.")

                    # Step 2: Insert data into the table
                    # Create a dynamic insert query
                    columns = dataframe.columns.tolist()
                    placeholders = ", ".join([f":{col}" for col in columns])
                    insert_query = text(
                        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                    )

                    # Run batch insert
                    connection.execute(insert_query, data_as_json)
                    print(f"{len(dataframe)} were inserted in '{table_name}'.")
                    
            return ""
                    
        except Exception as e:
            return str(e)

    def get_schema(self):
        
        # Create and inspector to inspect the DB
        inspector = inspect(self.engine)
        
        # Get table names
        table_names = inspector.get_table_names()

        # Get the name of all tables in DB
        def get_column_details(table_name):
            columns = inspector.get_columns(table_name)
            return [f"{col['name']} ({col['type']})" for col in columns]
        
        schema_info = []
        for table_name in table_names:
            table_info = [f"Table: {table_name}"]
            table_info.append("Columns:")
            table_info.extend(f" -{column}" for column in get_column_details(table_name))
            schema_info.append("\n".join(table_info))
            
        self.engine.dispose()
        return "\n\n".join(schema_info)
    
    def query(self,sql_query: str) -> list[dict[str,Any]]:
        with self.engine.connect() as connection:
            statement = text(sql_query)
            result = connection.execute(statement)
            return [dict(row._mapping) for row in result]   