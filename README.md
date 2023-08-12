# kasa2influxDB  
The script pulls data from TP-link smart plugs (KP115) and pushes data to an influxdb (2.0+) instance


#### Required Dependices  
pip install influxdb  
pip install influxdb_client  

Modify the config.py file with your relevent device IP address and names.

Define your sensors here, IP and a name, add as many as you want
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
