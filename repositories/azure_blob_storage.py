from azure.data.tables import TableServiceClient, TableEntity
import os

class BlobStorageRepository:
    
    def __init__(self,azure_storage_account_name: str,azure_storage_account_key: str,azure_storage_table_name: str):
            
        # Azure data
        self.account_name=azure_storage_account_name
        self.account_key=azure_storage_account_key
        self.table_name=azure_storage_table_name

    def insert_data_into_table_storage(self,data):
        try:
            # Conexión al Table Service Client
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
            table_service = TableServiceClient.from_connection_string(conn_str=connection_string)

            # Get the table reference
            table_client = table_service.get_table_client(table_name=self.table_name)

            # Insertar registros
            for idx, row in enumerate(data):
                entity = TableEntity()
                entity["PartitionKey"] = "partition_test"
                entity["RowKey"] = str(idx)
                entity.update(row)

                table_client.upsert_entity(entity=entity)
            
            return len(data),""

        except Exception as e:
            return 0,str(e)
