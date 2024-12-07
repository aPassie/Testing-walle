#!/usr/bin/python3
"""
WALL-E CALIBRATION CODE

@file      calibrate_servos.py
@brief     Script to calibrate the servo motor min/max positions
@author    Original: Simon Bluett, Modified for RPi: [Assistant]
@copyright MIT license
@version   2.0
@date      2024

HOW TO USE:
1. Make sure you have the required libraries:
   pip3 install adafruit-circuitpython-pca9685

2. Run this script: python3 calibrate_servos.py

3. The script will let you control each servo motor individually. The
   aim is to find the maximum and minimum PWM pulse widths for each servo's
   LOW and HIGH positions. Diagrams showing these positions can be found at:
   https://wired.chillibasket.com/3d-printed-wall-e/

   Controls:
   - 'a' or 'd': Move servo by -10/+10 pulse width
   - 'z' or 'c': Move servo by -1/+1 pulse width
   - 'n': Confirm position and move to next step
   - 'q': Quit calibration
"""

import board
import busio
from adafruit_pca9685 import PCA9685
import time
import sys
import tty
import termios

# Number of servo motors
SERVOS = 7

# Servo names and descriptions
SERVO_INFO = [
    ("Head Rotation", "LOW (head facing left)", "HIGH (head facing right)"),
    ("Neck Top Joint", "LOW (neck tilted down)", "HIGH (neck tilted up)"),
    ("Neck Bottom Joint", "LOW (neck retracted)", "HIGH (neck extended)"),
    ("Eye Right", "LOW (eye lowered)", "HIGH (eye raised)"),
    ("Eye Left", "LOW (eye lowered)", "HIGH (eye raised)"),
    ("Arm Left", "LOW (arm lowered)", "HIGH (arm raised)"),
    ("Arm Right", "LOW (arm lowered)", "HIGH (arm raised)")
]

class ServoCalibrator:
    def __init__(self):
        # Initialize I2C and PCA9685
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(i2c)
        self.pca.frequency = 50
        
        # Initialize calibration values
        self.preset = [[300, 500] for _ in range(SERVOS)]  # Default ranges
        self.current_servo = 0
        self.current_position = 400  # Starting position
        self.is_low_position = True
        
    def set_servo_pulse(self, position):
        """Set servo position using pulse width"""
        try:
            self.pca.channels[self.current_servo].duty_cycle = position << 4
            self.current_position = position
            print(f"Position: {position}", end='\r')
        except ValueError as e:
            print(f"Invalid position: {e}")
            
    def get_char(self):
        """Get a single character from stdin"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
        
    def calibrate(self):
        """Main calibration routine"""
        print("\nWALL-E Servo Calibration")
        print("------------------------")
        print("Controls:")
        print("  a/d - Move by -10/+10")
        print("  z/c - Move by -1/+1")
        print("  n   - Next position")
        print("  q   - Quit\n")
        
        while self.current_servo < SERVOS:
            servo_name, low_desc, high_desc = SERVO_INFO[self.current_servo]
            position_type = "LOW" if self.is_low_position else "HIGH"
            position_desc = low_desc if self.is_low_position else high_desc
            
            print(f"\nCalibrating {servo_name}")
            print(f"Set {position_type} position ({position_desc})")
            
            # Enable servo
            self.set_servo_pulse(self.current_position)
            
            while True:
                char = self.get_char()
                
                if char == 'q':
                    print("\nCalibration aborted")
                    self.cleanup()
                    return
                    
                elif char == 'n':
                    # Save position and move to next
                    if self.is_low_position:
                        self.preset[self.current_servo][0] = self.current_position
                        self.is_low_position = False
                    else:
                        self.preset[self.current_servo][1] = self.current_position
                        self.current_servo += 1
                        self.is_low_position = True
                    break
                    
                elif char == 'a':
                    self.set_servo_pulse(max(150, self.current_position - 10))
                elif char == 'd':
                    self.set_servo_pulse(min(600, self.current_position + 10))
                elif char == 'z':
                    self.set_servo_pulse(max(150, self.current_position - 1))
                elif char == 'c':
                    self.set_servo_pulse(min(600, self.current_position + 1))
        
        self.output_results()
        self.cleanup()
        
    def output_results(self):
        """Output the calibration results"""
        print("\nCalibration complete! Copy these values into config.py:\n")
        print("SERVO_LIMITS = {")
        for i in range(SERVOS):
            name = SERVO_INFO[i][0].replace(" ", "_").lower()
            print(f"    '{name}': ({self.preset[i][0]}, {self.preset[i][1]}),")
        print("}")
        
    def cleanup(self):
        """Clean up and disable servos"""
        for i in range(16):
            self.pca.channels[i].duty_cycle = 0
        self.pca.deinit()

if __name__ == "__main__":
    calibrator = ServoCalibrator()
    try:
        calibrator.calibrate()
    except KeyboardInterrupt:
        print("\nCalibration aborted")
        calibrator.cleanup() 