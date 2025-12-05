import json
import logging
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData
import os
from datetime import datetime
import uuid

EVENTHUB_CONN_STR = os.environ["EVENTHUB_CONN_STR"]
EVENTHUB_NAME = ""

producer = EventHubProducerClient.from_connection_string(
    conn_str=EVENTHUB_CONN_STR,
    eventhub_name=EVENTHUB_NAME
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a REST request.')
    
    try:
        req_body = req.get_json()
        logging.info(f"Received data: {json.dumps(req_body)}")
        
        if not isinstance(req_body, list):
            req_body = [req_body]
        
        successful_messages = 0
        
        event_data_batch = producer.create_batch()
        
        for sensor_data in req_body:
            if 'id' not in sensor_data:
                sensor_data['id'] = str(uuid.uuid4())
            
            if 'sensorId' in sensor_data:
                sensor_data['sensor_id'] = sensor_data.pop('sensorId')
            if 'sensorType' in sensor_data:
                sensor_data['sensor_type'] = sensor_data.pop('sensorType')
            
            required_fields = ['sensor_id', 'sensor_type', 'value', 'unit']
            missing_fields = [f for f in required_fields if f not in sensor_data]
            
            if missing_fields:
                logging.warning(f"Missing fields: {missing_fields}")
                continue
            
            if 'timestamp' not in sensor_data:
                sensor_data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            
            event_data = EventData(json.dumps(sensor_data))
            
            try:
                event_data_batch.add(event_data)
                successful_messages += 1
            except ValueError:
                producer.send_batch(event_data_batch)
                event_data_batch = producer.create_batch()
                event_data_batch.add(event_data)
                successful_messages += 1
        
        if len(event_data_batch) > 0:
            producer.send_batch(event_data_batch)
        
        response_data = {
            "status": "success",
            "message": f"Processed {successful_messages} sensor readings",
            "processed_count": successful_messages
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json",
            headers={'Content-Type': 'application/json'}
        )
        
    except ValueError as e:
        error_data = {"status": "error", "message": "Invalid JSON format"}
        return func.HttpResponse(
            json.dumps(error_data),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        error_data = {"status": "error", "message": "Internal server error"}
        return func.HttpResponse(
            json.dumps(error_data),
            status_code=500,
            mimetype="application/json"
        )