import time
from datetime import datetime
import influxdb.exceptions as inexc
import socket
from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import WriteOptions, SYNCHRONOUS
import logging


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

client = InfluxDBClient(url=dburl, token=token)

# Configure logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Create an empty list to accumulate data points for all sensors
all_data_points = []

def main():
    global querymsg
    querymsg = getquery('{"emeter":{"get_realtime":{}}}')
    
    while True:
        try:
            sensor_data_list = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            for sensor in sensor_data:
                data = read_sensor(sensor)
                sensor_data_list.append((sensor['name'], data))

            # Call the modified write_database function to write all accumulated data
            write_database(client, sensor_data_list)

            # Print the timestamp and sensor data after writing to the database
            print(f"Timestamp: {timestamp}")
            print('-' * 30)
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

        # Wait for sample time before the next iteration
        time.sleep(sample_time - time.monotonic() % sample_time)


                
#generates query for to send to devices
def getquery(string):
    from struct import pack
    key = 171
    result = pack('>I', len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += bytes([a])
    return result

#sends query to devices
def read_sensor(sensor):
    data = poll_sensor(sensor['ip'], port, querymsg, sensor['name'])
    if data is None:
        return None
    return decrypt_power(data)



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



def decrypt(string):
    """
    Decrypt the TP-Link Smart Home Protocoll: XOR Autokey Cipher with starting key = 171
    This follows: https://github.com/softScheck/tplink-smartplug
    """
    key = 171
    result = ""
    for i in string:
        a = key ^ i
        key = i
        result += chr(a)
    return result



def decrypt_power(data):
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

      

def write_database(client, sensor_data_list):
    all_data_points = []

    for sensor, data in sensor_data_list:
        if data is None:
            continue

        data_points = [
            Point.measurement(sensor).tag('Measurement', 'Power').field('Reading', data['power']).time(datetime.utcnow(), WritePrecision.NS),
            Point.measurement(sensor).tag('Measurement', 'Current').field('Reading', data['current']).time(datetime.utcnow(), WritePrecision.NS),
            Point.measurement(sensor).tag('Measurement', 'Voltage').field('Reading', data['voltage']).time(datetime.utcnow(), WritePrecision.NS),
            Point.measurement(sensor).tag('Measurement', 'Total_Energy').field('Reading', data['energy_total']).time(datetime.utcnow(), WritePrecision.NS)
        ]
        all_data_points.extend(data_points)

    try:
        write_api = client.write_api(write_options=WriteOptions(batch_size=1000, flush_interval=5000))
        write_api.write(bucket=bucket, org=org, record=all_data_points)
    except Exception as e:
        logging.error(f"Error writing data to InfluxDB: {e}")



#initilize code + so,e exeption handling
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
