from pymongo import MongoClient, ASCENDING
import datetime
import os

#load evironment variables from .env
MONGO_URI = os.getenv('MONGO_URI')



# MongoDB Configuration
DB_NAME = os.getenv("MONGODB_DBNAME")
COLLECTION_ACTIVE = "active_people"
COLLECTION_ARCHIVE = "archived_people"

# Connect to MongoDB
client_mongo = MongoClient(MONGO_URI)
db = client_mongo[DB_NAME]
active_collection = db[COLLECTION_ACTIVE]
archive_collection = db[COLLECTION_ARCHIVE]

"""# Ensure Indexes for Fast Queries
active_collection.create_index([("entry_time", ASCENDING)])
active_collection.create_index([("exit_time", ASCENDING)])
active_collection.create_index([("user_id", ASCENDING)])

archive_collection.create_index([("entry_time", ASCENDING)])
archive_collection.create_index([("exit_time", ASCENDING)])
archive_collection.create_index([("user_id", ASCENDING)])
"""
def move_exited_users_to_archive():
    """Move users who have exited the station to an archive collection."""
    now = datetime.datetime.now()

    # Find users who have exited
    exited_users = list(active_collection.find({"exit_time": {"$lt": now}}))

    if exited_users:
        # Insert them into the archive
        archive_collection.insert_many(exited_users)

        # Remove from the active collection
        active_collection.delete_many({"exit_time": {"$lt": now}})

        print(f"Moved {len(exited_users)} users to archive.")




# Call this function every 30 seconds in  main loop



if __name__ == "__main__":
    move_exited_users_to_archive()
