import serial, threading, time
from getpass import getpass
from math import atan2, degrees, sqrt

ser = serial.Serial ("/dev/ttyACM1", 115200)
old_data = []
threshold = 150

def read_data ():
    try:
        data = tuple ((int (i.strip ()) for i in ser.readline ().decode ('utf-8').strip () [1 : -1].split (",")))
        data [2] # Length check
    except Exception as e:
        return
    return data

sampling = True
def sample_idle ():
    global old_data, sampling
    while sampling:
        data = read_data ()
        if data:
            old_data.append (data)

sample = threading.Thread (target = sample_idle)

input ("Start sampling idle condition? ")
sample.start ()

input ("Stop sampling idle condition? ")
sampling = False
sample.join ()

print ("Sampling idle condition done.")
avg_x = sum (i [0] for i in old_data) / len (old_data)
avg_y = sum (i [2] for i in old_data) / len (old_data)
print ("Average values:", avg_x, avg_y)

points = []
input ("Start recording acceleration? ")
try:
    while True:
        data = read_data ()
        ts = time.time_ns ()
        if data:
            heading = round (degrees (atan2 (data [0] - avg_x, data [2] - avg_y)))
            magnitude = round (sqrt ((data [0] - avg_x) ** 2 + (data [2] - avg_y) ** 2))
            if magnitude > threshold:
                points.extend ((heading, magnitude, ts // 1000000))
                print ("+", end = "", flush = True)
except KeyboardInterrupt:
    pass

print (f"\nRecording done, {len (points)} points recorded.")
pos_points = getpass ("Please paste the list of position points: ").strip ().split (",")
