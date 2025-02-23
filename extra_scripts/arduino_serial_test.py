import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.flush()

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Received: {line}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Программа завершена.")
finally:
    ser.close()