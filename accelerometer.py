import serial, subprocess, threading, time
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
avg_y = sum (i [1] for i in old_data) / len (old_data)
print ("Average values:", avg_x, avg_y)

points = []
headings = []
max_headings = 10
old_ts = 0
input ("Start recording acceleration? ")
try:
    while True:
        data = read_data ()
        ts = time.time_ns ()
        if ts - old_ts < 1000000:
            continue
        elif data:
            heading = degrees (atan2 (data [1] - avg_y, data [0] - avg_x))
            magnitude = round (sqrt ((data [0] - avg_x) ** 2 + (data [1] - avg_y) ** 2))
            if magnitude > threshold:
                points.extend ((round (heading), magnitude, ts // 1000000))
                old_ts = ts
                print ("+", end = "", flush = True)
except KeyboardInterrupt:
    pass

print (f"\nRecording done, {len (points)} points recorded.")
subprocess.run (["wl-copy", "--", ",".join (map (str, points))])
print ("Data copied to clipboard.")