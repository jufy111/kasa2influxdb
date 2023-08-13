# Smart Plug Data Collection and InfluxDB Integration

This Python script collects real-time data from TP-Link smart plugs and pushes it to an InfluxDB instance for storage and analysis. It interfaces with TP-Link devices using a custom query mechanism, decrypts the returned data, and formats it to be compatible with InfluxDB's write protocol. This project is particularly useful for monitoring power consumption and energy usage of various devices.

## Key Features

- Collects voltage, current, power, and total energy consumption data from TP-Link smart plugs.
- Sends custom queries to TP-Link devices for data retrieval.
- Decrypts and parses returned JSON data.
- Utilizes InfluxDB 2.0+ API for efficient data storage.
- Offers error logging for troubleshooting and debugging.

## Technologies Used

- Python
- InfluxDB
- TP-Link Smart Plug API

## Usage

1. Clone the repository.
2. Modify the configuration variables in the `config.py` file to match your setup.
3. Run the `kasa2influxdb.py` script to start data collection and InfluxDB integration.
4. Collected data will be stored in your InfluxDB instance for further analysis.

**Note:** This repository provides a foundational structure for integrating TP-Link smart plug data with InfluxDB. Feel free to customize and expand the project according to your requirements.

```
# config.py

# Sensor Definition
sensor_data = [
    {'ip': '10.10.10.101', 'name': 'devicename1'},
    {'ip': '10.10.10.102', 'name': 'devicename2'},
    {'ip': '10.10.10.103', 'name': 'devicename3'}
    # ... add other sensors ...
]

# InfluxDB Configuration
influxdb_config = {
    'token': "yourtokenhere",
    'org': "yourorg",
    'bucket': "bucketnamehere",
    'dburl': "http://10.10.10.10:8086"  #IP and port of you influxdb instance
}

# Other Configuration
other_config = {
    'port': 9999,  #this is the port the kasa devices use, leave as is.
    'sample_time': 10,
    'timeout_time': 1 #timeout for query in seconds
}```
