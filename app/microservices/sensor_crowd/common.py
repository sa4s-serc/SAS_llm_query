from pymongo import MongoClient
from datetime import datetime

def store_to_mongodb(sensor_name, timestamp, sensor1_data, sensor1_location, sensor2_data, sensor2_location):
    """This function stores the given sensor data, along with location information, into the MongoDB database."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['sensordatabaseversion2']
    collection = db['sensordata']

    # Data structure now includes both sensor data and location
    sensor_data = {
        'sensor1': {
            'data': sensor1_data,
            'location': sensor1_location
        },
        'sensor2': {
            'data': sensor2_data,
            'location': sensor2_location
        }
    }
    
    update_data = {sensor_name: sensor_data}

    # Store or update sensor data in MongoDB, using the timestamp as the unique identifier
    collection.update_one(
        {'_id': timestamp},
        {'$set': update_data},
        upsert=True  # If document doesn't exist, create a new one
    )
    
    print(f"Data stored successfully for {sensor_name} at {timestamp}.")
def store_to_mongodb_sensor(db_name, collection_name, sensor_name, timestamp, sensor1_data, sensor1_location, sensor2_data, sensor2_location):
    """This function stores the given data, along with location information, into the specified MongoDB collection."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db[collection_name]

        # Data structure includes sensor data and location information
        sensor_data = {
            'sensor1': {
                'data': sensor1_data,
                'location': sensor1_location
            },
            'sensor2': {
                'data': sensor2_data,
                'location': sensor2_location
            }
        }
        
        update_data = {sensor_name: sensor_data}

        # Update the document in MongoDB, creating a new one if it doesn't exist
        collection.update_one(
            {'_id': timestamp},
            {'$set': update_data},
            upsert=True
        )
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Data stored successfully for {sensor_name} at {timestamp}. Current time: {current_time}")
    except Exception as e:
        print(f"Error storing data to MongoDB: {e}")
