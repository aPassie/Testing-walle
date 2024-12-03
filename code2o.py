import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# Constants
SERVOS = 7
FREQUENCY = 60

# Servo Positions: Low, High
preset = [
    [398, 112],  # head rotation
    [565, 188],  # neck top
    [200, 400],  # neck bottom
    [475, 230],  # eye right
    [270, 440],  # eye left
    [350, 185],  # arm left
    [188, 360],  # arm right
]

# Rest position (percentage-based)
restpos = [50, 50, 40, 0, 0, 100, 100]

messages1 = [
    "Head Rotation - ",
    "Neck Top Joint - ",
    "Neck Bottom Joint - ",
    "Eye Right - ",
    "Eye Left - ",
    "Arm Left - ",
    "Arm Right - ",
]

messages2 = [
    ["LOW (head facing left)", "HIGH (head facing right)"],
    ["LOW (head looking up)", "HIGH (head looking down)"],
    ["LOW (head looking down)", "HIGH (head looking up)"],
    ["LOW (eye rotated down)", "HIGH (eye rotated up)"],
    ["LOW (eye rotated down)", "HIGH (eye rotated up)"],
    ["LOW (arm rotated down)", "HIGH (arm rotated up)"],
    ["LOW (arm rotated down)", "HIGH (arm rotated up)"],
]

# Initialize I²C bus and PCA9685
i2c_bus = busio.I2C(SCL, SDA)
pca = PCA9685(i2c_bus)
pca.frequency = FREQUENCY

# Function to move servo to a position
def change_servo_position(channel, position):
    pca.channels[channel].duty_cycle = int((position / 4096) * 65535)

# Function to soft-start the servo (smooth movement)
def soft_start(channel, position):
    for i in range(0, position, 10):
        change_servo_position(channel, i)
        time.sleep(0.01)

# Main calibration process
def calibration():
    current_servo = 0
    current_position = 0
    position = preset[current_servo][current_position]

    print("/////// Starting Wall-E Calibration Program ///////")
    while current_servo < SERVOS:
        print(f"{messages1[current_servo]} {messages2[current_servo][current_position]}")
        print("Commands: 'a'=-10, 'd'=+10, 'z'=-1, 'c'=+1, 'n'=confirm position")

        while True:
            command = input("Enter command: ").strip()
            if command == "a":
                position = max(0, position - 10)
                change_servo_position(current_servo, position)
            elif command == "d":
                position = min(4095, position + 10)
                change_servo_position(current_servo, position)
            elif command == "z":
                position = max(0, position - 1)
                change_servo_position(current_servo, position)
            elif command == "c":
                position = min(4095, position + 1)
                change_servo_position(current_servo, position)
            elif command == "n":
                preset[current_servo][current_position] = position
                print(f"[Confirmed Position: {position}]\n")
                current_position += 1
                if current_position > 1:
                    current_position = 0
                    current_servo += 1
                    if current_servo < SERVOS:
                        position = preset[current_servo][current_position]
                    else:
                        break
                else:
                    position = preset[current_servo][current_position]
                break

        if current_servo == SERVOS:
            break

    print("Calibrated values:")
    for idx, (low, high) in enumerate(preset):
        print(f"Servo {idx}: Low = {low}, High = {high}")

# Run the calibration
calibration()

# Turn off all servos
for i in range(SERVOS):
    pca.channels[i].duty_cycle = 0
pca.deinit()
