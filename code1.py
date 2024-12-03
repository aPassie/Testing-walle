import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# Initialize I2C interface
i2c = busio.I2C(SCL, SDA)

# Initialize PCA9685
pca = PCA9685(i2c)
pca.frequency = 50  # Set PWM frequency for servos

# Control a specific channel (e.g., Channel 0)
servo_channel = pca.channels[0]

# Function to set duty cycle (0-100%)
def set_servo_angle(channel, angle):
    pulse_length = 650 + (angle / 180) * 1850  # Convert angle to pulse length
    channel.duty_cycle = int(pulse_length / 20000 * 0xFFFF)

# Example: Move servo to angles
while True:
    for angle in range(0, 181, 10):  # 0° to 180°
        set_servo_angle(servo_channel, angle)
        time.sleep(0.5)

    for angle in range(180, -1, -10):  # 180° to 0°
        set_servo_angle(servo_channel, angle)
        time.sleep(0.5)
