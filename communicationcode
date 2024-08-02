import serial

# port açılımı
ser = serial.Serial('COM8', baudrate=115200, timeout=1)

# porttan okuma
def read_data():
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            print(f"Received data: {data}")

try:
    read_data()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
