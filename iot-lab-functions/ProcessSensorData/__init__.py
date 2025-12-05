import json
import logging
import azure.functions as func
import os
from datetime import datetime
from typing import List
from azure.cosmos import CosmosClient
from azure.eventhub import EventHubProducerClient, EventData

COSMOS_URI = os.environ["COSMOS_URI"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
COSMOS_DB = os.environ["COSMOS_DB"]
COSMOS_CONTAINER = os.environ["COSMOS_CONTAINER"]

client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
database = client.get_database_client(COSMOS_DB)
container = database.get_container_client(COSMOS_CONTAINER)

# DLQ Event Hub settings
EVENTHUB_CONN_STR = os.environ["EVENTHUB_CONN_STR"]
DLQ_EVENTHUB_NAME = os.environ.get("DLQ_EVENTHUB_NAME", "iot-sensor-hub-dlq")

def send_to_dlq(original_data, error_message):
    """Відправляє повідомлення у Dead Letter Queue Event Hub"""
    try:
        producer = EventHubProducerClient.from_connection_string(
            conn_str=EVENTHUB_CONN_STR,
            eventhub_name=DLQ_EVENTHUB_NAME
        )
        dlq_message = {
            "error": error_message,
            "original_data": original_data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        batch = producer.create_batch()
        batch.add(EventData(json.dumps(dlq_message)))
        producer.send_batch(batch)
        producer.close()
        logging.warning(f"🚫 Sent to DLQ: {error_message}")
    except Exception as e:
        logging.error(f"❌ Failed to send to DLQ: {e}")

def main(events: List[func.EventHubEvent]):
    logging.info(f"Python EventHub trigger function processing {len(events)} events")

    for event in events:
        try:
            event_body = event.get_body().decode('utf-8')
            logging.info(f"Received event: {event_body}")

            data = json.loads(event_body)

            if 'sensor_type' in data and 'sensorType' not in data:
                data['sensorType'] = data.pop('sensor_type')
            if 'sensor_id' in data and 'sensorId' not in data:
                data['sensorId'] = data.pop('sensor_id')

            if 'id' not in data:
                import uuid
                data['id'] = str(uuid.uuid4())
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat() + 'Z'

            required_fields = ['sensorId', 'sensorType', 'value', 'unit']
            missing = [f for f in required_fields if f not in data]
            if missing:
                send_to_dlq(event_body, f"Missing required fields: {missing}")
                continue

            if not isinstance(data.get('value'), (int, float)):
                send_to_dlq(event_body, f"Invalid value type: {type(data.get('value'))}")
                continue

            if data.get('value', 0) < 0:
                send_to_dlq(event_body, f"Negative value: {data.get('value')}")
                continue

            container.create_item(body=data)
            logging.info(f"✅ Saved to Cosmos DB: {data['sensorId']}")

        except json.JSONDecodeError as e:
            send_to_dlq(event_body, f"JSON parse error: {str(e)}")
        except Exception as e:
            send_to_dlq(event_body, f"Processing error: {str(e)}")
            



