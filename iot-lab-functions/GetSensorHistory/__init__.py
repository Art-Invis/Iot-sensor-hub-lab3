import json
import logging
import azure.functions as func
from azure.cosmos import CosmosClient
import os
from datetime import datetime, timedelta

# Cosmos DB settings
COSMOS_URI = os.environ["COSMOS_URI"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
COSMOS_DB = os.environ["COSMOS_DB"]
COSMOS_CONTAINER = os.environ["COSMOS_CONTAINER"]

client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
database = client.get_database_client(COSMOS_DB)
container = database.get_container_client(COSMOS_CONTAINER)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('GetSensorHistory function processed a request.')
    
    try:
        # Параметри запиту
        sensor_type = req.params.get('sensorType')
        sensor_id = req.params.get('sensorId')
        hours = int(req.params.get('hours', 24))  
        limit = int(req.params.get('limit', 100))
        
        query_parts = []
        parameters = []
        
        # Фільтр по типу сенсора
        if sensor_type:
            query_parts.append("c.sensorType = @sensor_type")
            parameters.append({"name": "@sensor_type", "value": sensor_type})
        
        # Фільтр по конкретному сенсору
        if sensor_id:
            query_parts.append("c.sensorId = @sensor_id")
            parameters.append({"name": "@sensor_id", "value": sensor_id})
        
        # Фільтр по часу (останні N годин)
        time_filter = datetime.utcnow() - timedelta(hours=hours)
        query_parts.append("c.timestamp >= @time_filter")
        parameters.append({
            "name": "@time_filter", 
            "value": time_filter.isoformat() + "Z"
        })
        
        where_clause = " AND ".join(query_parts) if query_parts else "1=1"
        
        # Використовуємо TOP замість OFFSET/LIMIT
        query = f"""
            SELECT TOP {limit} * FROM c 
            WHERE {where_clause}
            ORDER BY c.timestamp DESC
        """
        
        logging.info(f"Executing query: {query}")
        
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        # Додаткове сортування у Python (на випадок якщо Cosmos DB віддає не так)
        items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        response_data = {
            "status": "success",
            "count": len(items),
            "filters": {
                "sensorType": sensor_type,
                "sensorId": sensor_id, 
                "hours": hours,
                "limit": limit
            },
            "data": items
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json",
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


