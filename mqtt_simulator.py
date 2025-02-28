import paho.mqtt.client as mqtt
import json
import time
import random
import datetime
from pymongo import MongoClient
import numpy as np  # For normal distribution
import os
import data_archiver

# MQTT Configuration
#MQTT_BROKER = os.getenv('MQTT_BROKER', 'mqtt-broker') #os.getenv('VARIABLE_NAME', 'default_value')
#MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_BROKER = 'mqtt-broker'
MQTT_PORT = 1883
TOPIC = "location/update"
MQTT_QOS = 1  # Ensure at least once delivery


#load evironment variables from .env
mongodb_active_collection= os.getenv("MONGODB_ACTIVE_COLLECTION_NAME")
mongodb_archive_collection= os.getenv("MONGODB_ARCHIVE_COLLECTION_NAME")
mongodb_container_name = os.getenv("MONGODB_CONTAINER_NAME")
#mongodb_container_name = "localhost"

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('MONGODB_DBNAME')
MONGODB_ACTIVE_COLLECTION_NAME="active_people"
MONGODB_ARCHIVE_COLLECTION_NAME="archived_people"



# Connect to MongoDB
client_mongo = MongoClient(MONGO_URI)
db = client_mongo[DB_NAME]


##### CREATE COLLECTIONS
#########################

# List existing collections in mqtt_db
existing_collections = db.list_collection_names()

# Check if the collections 'archived_people' and 'active_people' exist, and create them if not
if 'archived_people' not in existing_collections:
    db.create_collection('archived_people')
    print("Created 'archived_people' collection.")

if 'active_people' not in existing_collections:
    db.create_collection('active_people')
    print("Created 'active_people' collection.")


collection = db[MONGODB_ACTIVE_COLLECTION_NAME]




# Train Station Boundaries
STATION_BOUNDARIES = {"x": (0, 100), "y": (0, 100), "z": (0, 10)}

def generate_random_entry_time():
    """Random entry time (now or soon)."""
    return datetime.datetime.now() + datetime.timedelta(seconds=random.randint(0, 60))  # Enter within 1 min

def generate_exit_time(entry_time):
    """Exit time based on N(5,10), clamped to 1 min min."""
    stay_duration = max(60, int(np.random.normal(5 * 60, 10 * 60)))  # Convert minutes to seconds
    return entry_time + datetime.timedelta(seconds=stay_duration)

def random_location():
    """Generate a random location inside the station."""
    return {
        "x": random.randint(*STATION_BOUNDARIES["x"]),
        "y": random.randint(*STATION_BOUNDARIES["y"]),
        "z": random.randint(*STATION_BOUNDARIES["z"]),
    }

def update_location(last_location):
    """Move within [-1, 0, +1] range."""
    return {
        "x": last_location["x"] + random.choice([-1, 0, 1]),
        "y": last_location["y"] + random.choice([-1, 0, 1]),
        "z": last_location["z"] + random.choice([-1, 0, 1]),
    }

def add_new_people():
    """Continuously add new people to the station."""
    num_new_people = random.randint(5, 10)  # Add 5-10 new people every 10 sec
    now = datetime.datetime.now()
    
    new_users = []
    for _ in range(num_new_people):
        entry_time = generate_random_entry_time()
        exit_time = generate_exit_time(entry_time)
        user_id = f"user_{random.randint(1000, 9999)}"

        new_users.append({
            "user_id": user_id,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "current_location": random_location(),
            "history": []
        })

    if new_users:
        collection.insert_many(new_users)
        print(f"Added {len(new_users)} new people.")

def get_active_people():
    """Fetch people currently inside the station."""
    now = datetime.datetime.now()
    return list(collection.find({"entry_time": {"$lte": now}, "exit_time": {"$gt": now}}))

def remove_exited_people():
    """Delete people who have left the station."""
    now = datetime.datetime.now()
    result = collection.delete_many({"exit_time": {"$lt": now}})
    if result.deleted_count > 0:
        print(f"Removed {result.deleted_count} exited people.")

def update_location_in_db(user_id, new_location):
    """Update a person's location and add to history."""
    collection.update_one(
        {"user_id": user_id},
        {"$set": {"current_location": new_location}, "$push": {"history": new_location}}
    )

def publish_location(client):
    """Continuously publish active users' locations."""






    while True:
        now = datetime.datetime.now()

        # Add new people every 10 sec
        if int(now.timestamp()) % 10 == 0:
            add_new_people()

        # Remove old users every 30 sec
        if int(now.timestamp()) % 30 == 0:
            remove_exited_people()

        # Update locations of active people
        active_people = get_active_people()
        updates = {}

        for person in active_people:
            user_id = person["user_id"]
            last_location = person["current_location"]
            new_location = update_location(last_location)

            if new_location != last_location:
                updates[user_id] = new_location
                update_location_in_db(user_id, new_location)

        if updates:
            message = json.dumps(updates)
            client.publish(TOPIC, message, qos=MQTT_QOS)
            print(f"Published: {message}")

        time.sleep(2)

        data_archiver.move_exited_users_to_archive()


# MQTT Client Setup
client = mqtt.Client()
#client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.connect('mqtt_container', 1883, 60)

try:
    publish_location(client)
except KeyboardInterrupt:
    print("Stopping Publisher")
finally:
    client.disconnect()
    client_mongo.close()
