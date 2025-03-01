This repository provides a dockerized service for producing sample MQTT data, published every 2 seconds.

### Containers

#### mqtt_simulator
- The data is produced with a Python script.
- People are spawned in random locations at intervals and their location is updated every 2 seconds.
- If the location is changed, it is published to the topic.

#### mongodb_container
- The data is saved in a MongoDB database.
- People come and leave. As long as they are in the simulation and their location is updated, their data is stored in a collection called `active_people`.
- As soon as they leave, their data is transferred.
  ** To view the data with UI MongoDB Compass would help **

#### mqtt_container
- This serves as the MQTT broker.

### How to use:
- Clone the repository.
- Your docker daemon must be running obviously.
- Run `docker compose up --build` in terminal.
- Your data must be published through port 1883 and saved into MongoDB.
