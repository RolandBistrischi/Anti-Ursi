import time
from RPi import GPIO  # For actual Raspberry Pi GPIO control

# GPIO Configuration
control_pin = 18  # Pin GPIO for controlling the pump and buzzer
PWM_FREQUENCY = 1000  # Default frequency in Hz for the buzzer (you can adjust this)

# Set up GPIO in BCM mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(control_pin, GPIO.OUT)  # Configure control pin as output

# Set up PWM for tone control
pwm = GPIO.PWM(control_pin, PWM_FREQUENCY)  # Initialize PWM on the control pin
pwm.start(0)  # Start with 0% duty cycle (OFF)

def set_buzzer_tone(frequency, duty_cycle=50):
    """
    Sets the buzzer tone by adjusting the PWM frequency and duty cycle.
    - frequency: Tone frequency in Hz (e.g., 440 for A4 note).
    - duty_cycle: Percentage of time the signal is HIGH (default 50% for balanced tone).
    """
    pwm.ChangeFrequency(frequency)
    pwm.ChangeDutyCycle(duty_cycle)
    print(f"Buzzer tone set to {frequency} Hz with {duty_cycle}% duty cycle.")

def activate_pump_and_buzzer(tone_frequency=1000):
    """
    Activates the pump and buzzer by switching on the relay/transistor.
    Optionally sets a specific tone for the buzzer.
    """
    set_buzzer_tone(tone_frequency)  # Set the desired tone for the buzzer
    GPIO.output(control_pin, GPIO.HIGH)  # Ensure the pin is HIGH
    print(f"Pump and buzzer are activated with tone {tone_frequency} Hz.")

def deactivate_pump_and_buzzer():
    """
    Deactivates the pump and buzzer by switching off the relay/transistor.
    Stops the PWM signal to the buzzer.
    """
    pwm.ChangeDutyCycle(0)  # Turn off the buzzer tone
    GPIO.output(control_pin, GPIO.LOW)  # Deactivate the relay/transistor
    print("Pump and buzzer are deactivated.")

def cleanup_gpio():
    """
    Cleans up the GPIO configuration when exiting the program.
    """
    pwm.stop()  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO
    print("GPIO cleaned up.")

