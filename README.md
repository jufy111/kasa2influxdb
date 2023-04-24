Code Pulls data from TP-link smart plugs KP115 and pushes data to an influxdb (2.0+) instance

## Required Dependices  
pip install influxdb  
pip install influxdb_client  




## Modify the below variables as relevent to you  
You can moniter any number of plugs, just add more or less to both 'ip' and 'plug'  
ip   = ['192.168.1.21', '192.168.1.22', '192.168.1.23' ]        #Set static IP to your smart plug  
plug = ['name1', 'name2', 'name3'] #device name in influxdb  
sample_time = 10        #in seconds  

InfluxDB Database Details   
token = "1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz==" # token generator from influxDB  
org = "your_org_here"  
bucket = "Energy Monitering"  
dburl = "http://192.168.1.20:8086" #IP of yourr influxDB  
