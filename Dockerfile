# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 1883 (MQTT) available to the world outside this container
EXPOSE 1883

# Define environment variables if necessary (like MongoDB URI, MQTT broker URI)
# ENV MQTT_BROKER=mqtt-broker

# Run the Python script
CMD ["python", "mqtt_simulator.py"]