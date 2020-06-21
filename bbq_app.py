import pygatt
import csv
import datetime

# Connect to the device
connect_key = bytearray.fromhex("2101020304000000000000") # Update this with correct connection key you obtained in part 2
enable_notifications = bytearray.fromhex("0b0100000000") # This value is correct, no need to update
bbq_mac = "ff:ff:ff:ff:ff:ff" # Update this with your BBQ device's MAC address

adapter = pygatt.GATTToolBackend()

def fahrenheit(celcius):
    return int(round(celcius * (9/5.0) + 32))

# Process and save the realtime data
def handle_notification(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    temps = {"timestamp": str(datetime.datetime.now())}
    for i in range(0,8,2):
        celcius = int(int.from_bytes(value[i:i+2], "little") / 10)
        f_degrees = fahrenheit(celcius)
        temps[f"Probe-{int(i/2)+1}"] = f_degrees
    with open("temperature_log.csv", "a") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([temps[field] for field in temps])
    
        
try:
    adapter.start()

    try:
        device = adapter.connect(bbq_mac,timeout=20)
    except:
        print("Couldn't connect to the device, retrying...")
        device = adapter.connect(bbq_mac,timeout=20)

    # Send the connection key to the 0x29
    print("Pairing with the device...")
    device.char_write_handle(0x0029, connect_key)
    # Enable notifications by writing to 0x34
    device.char_write_handle(0x0034, enable_notifications)
    print("Connected with the device.")
    
    with open('temperature_log.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Timestamp", "Probe 1", "Probe 2", "Probe 3", "Probe 4"])
    # Subscribe and listen for notifications of the realtime data
    try:
        device.subscribe("0000fff4-0000-1000-8000-00805f9b34fb", callback=handle_notification)
    except Exception as e:
        try:
            device.subscribe("0000fff4-0000-1000-8000-00805f9b34fb", callback=handle_notification)
        except:
            pass
    
    input("Enter any key to quit....")
    

finally:
    adapter.stop()



