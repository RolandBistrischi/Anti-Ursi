import time
import fake_rpi
from RPi import GPIO
# Configurare GPIO
pump_pin = 17  # Pin GPIO pentru pompă
speaker_pin = 27  # Pin GPIO pentru difuzor

GPIO.setmode(GPIO.BCM)
GPIO.setup(pump_pin, GPIO.OUT)
GPIO.setup(speaker_pin, GPIO.OUT)

def activate_pump_and_speaker():
    """Activează pompa și difuzorul."""
    GPIO.output(pump_pin, GPIO.HIGH)  # Activează pompa
    GPIO.output(speaker_pin, GPIO.HIGH)  # Activează difuzorul
    print("Pompa și difuzorul sunt activate")

def deactivate_pump_and_speaker():
    """Dezactivează pompa și difuzorul."""
    GPIO.output(pump_pin, GPIO.LOW)  # Dezactivează pompa
    GPIO.output(speaker_pin, GPIO.LOW)  # Dezactivează difuzorul
    print("Pompa și difuzorul sunt dezactivate")

def cleanup_gpio():
    """Curăță configurarea GPIO."""
    GPIO.cleanup()
