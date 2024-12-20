import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
CONTROL_PIN = 18  # Replace with your pin
GPIO.setup(CONTROL_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(CONTROL_PIN, GPIO.HIGH)
        print("Pin HIGH")
        time.sleep(5)
        GPIO.output(CONTROL_PIN, GPIO.LOW)
        print("Pin LOW")
        time.sleep(5)
except KeyboardInterrupt:
    print("Test interrupted.")
finally:
    GPIO.cleanup()