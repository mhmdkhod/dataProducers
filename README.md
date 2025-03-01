This repository provides a dockerized service for producing sample MQTT data, published every 2 seconds. 

Container: mqtt_simulator
The data is produced with a python script: 
on intervlas people are spawned in random locations and their location is updated every 2 seconds. If the location is changed, it is published to the topic.

Container: mongodb_container
The data is saved in MongoDB database:
people come and leave. As long as they are in the simulation and their locationis updated, their data is stores in a collection called active_people. As soons as they leave, their data is transferred to archived_people.

Container: mqtt_container
This serves as the MQTT broker.


