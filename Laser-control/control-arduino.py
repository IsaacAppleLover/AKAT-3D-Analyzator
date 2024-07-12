#pip install pyserial

import serial
from time import sleep

# Replace 'COM3' with the correct port name for your Arduino
ser = serial.Serial('COM3', 9600)
#1ser.open()
ser.flushInput()

try:
    while True:
        command = input("Enter '1' to turn on or '0' to turn off: ").strip()
        if command:
            command += "\n"  # Ensure we're sending a newline character
            ser.write(command.encode())
            print("Command sent.")
            sleep(1)  # Short pause to allow Arduino to process the command
except KeyboardInterrupt:
    ser.close()
    print("Exiting...")

