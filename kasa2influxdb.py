import time
from datetime import datetime
import influxdb.exceptions as inexc
import socket
from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions, SYNCHRONOUS
import logging
import sys



# Import the entire configuration dictionary from config.py
from config import sensor_data, influxdb_config, other_config

# Unpack the configuration variables from the dictionaries
token = influxdb_config['token']
org = influxdb_config['org']
bucket = influxdb_config['bucket']
dburl = influxdb_config['dburl']

port = other_config['port']
sample_time = other_config['sample_time']
timeout_time = other_config['timeout_time']


#write to DB options
client = InfluxDBClient(url=dburl, token=token)
write_api = client.write_api(write_options=WriteOptions(batch_size=100, flush_interval=5000))

# Configure logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


#Main loop
def main():
    global querymsg
    querymsg = getquery('{"emeter":{"get_realtime":{}}}')

    while True:
        try:
            sensor_data_list = []
            all_data_points = []
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            for sensor in sensor_data:
                raw_data = []
                raw_data = read_sensor(sensor)
                sensor_data_list.append((sensor['name'], raw_data))

            all_data_points = format_influx(sensor_data_list)
            write_database(client, all_data_points,write_api)

            # Print the timestamp and sensor data after writing to the database
            print(f"Timestamp: {timestamp}")
            print('-' * 40)
            for sensor_name, data in sensor_data_list:
                if data is not None:
                    power_value = f"{data['power']} W"
                    print(f"{sensor_name:15} | {power_value:<10}")
                else:
                    print(f"{sensor_name:15} | {'offline':<10}")

            # Add a blank line after each interval
            print()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            
        # Clear printout memory and wait for sample time before the next iteration
        sys.stdout.flush()
        time.sleep(sample_time - time.monotonic() % sample_time)
        return


         
#Generates query for to send to devices - credit https://github.com/softScheck/tplink-smartplug
def getquery(string):
    from struct import pack
    key = 171
    result = pack('>I', len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += bytes([a])
    return result



#Sends query to devices
def read_sensor(sensor):
    data = poll_sensor(sensor['ip'], port, querymsg, sensor['name'])
    if data is None:
        return
    return decrypt_json(data)



#Open socket with tp link deivce and gets data
def poll_sensor(ip, port, querymsg, device_name):
    try:
        with socket.create_connection((ip, port), timeout=timeout_time) as sock_tcp:
            sock_tcp.send(querymsg)
            data = sock_tcp.recv(2048)
            return data
    except (ConnectionError, socket.timeout) as e:
        error_message = f"Error for {device_name}: {e}"
        logging.error(error_message)
        return None



#Decrypts the tplink data- credit https://github.com/softScheck/tplink-smartplug
def decrypt(string):
    key = 171
    result = ""
    for i in string:
        a = key ^ i
        key = i
        result += chr(a)
    return result



#Extracts the relevent json infomation
def decrypt_json(data):
    import json
    try:
        decrypted = decrypt(data[4:])
        decrypt_dict = json.loads(decrypted)
        return {'voltage':      decrypt_dict['emeter']['get_realtime']['voltage_mv']/1000,    # V
                'current':      decrypt_dict['emeter']['get_realtime']['current_ma']/1000,    # A
                'power':        decrypt_dict['emeter']['get_realtime']['power_mw']/1000,      # W
                'energy_total': decrypt_dict['emeter']['get_realtime']['total_wh']/1000,      # kWh
               }
    except:
        raise TypeError("Could not decrypt returned data.")




#Formats data so it can be pushed to the influxDB intance
def format_influx(sensor_data_list):
    all_data_points = []
    for sensor, data in sensor_data_list:
        if data is None:
            continue

        data_points = [
            Point.measurement(sensor).field('Power', data['power']).time(datetime.utcnow(), WritePrecision.NS),
            Point.measurement(sensor).field('Current', data['current']).time(datetime.utcnow(), WritePrecision.NS),
            Point.measurement(sensor).field('Voltage', data['voltage']).time(datetime.utcnow(), WritePrecision.NS),
            Point.measurement(sensor).field('Total_Energy', data['energy_total']).time(datetime.utcnow(), WritePrecision.NS)
        ]
        all_data_points.extend(data_points)
    return(all_data_points)
      


#Writes data to influxDB (2.0+)
def write_database(client, all_data_points, write_api):
    try:        
        write_api.write(bucket=bucket, org=org, record=all_data_points)
        return
    except Exception as e:
        logging.error(f"Error writing data to InfluxDB: {e}")
        return
    return
#Initilize code + exeption handling
if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Program stopped by keyboard interrupt [CTRL_C] by user.")
            break  # Exit the outer loop on keyboard interrupt
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(sample_time)  # Add a sleep to prevent constant looping in case of errors

        
