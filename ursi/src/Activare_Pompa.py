import RPi.GPIO as GPIO
import time

# Configurarea pinurilor GPIO
pump_pin = 17  # Pinul GPIO conectat la baza tranzistorului pentru pompă
speaker_pin = 27  # Pinul GPIO conectat la baza tranzistorului pentru difuzor

GPIO.setmode(GPIO.BCM)
GPIO.setup(pump_pin, GPIO.OUT)
GPIO.setup(speaker_pin, GPIO.OUT)

def activate_pump_and_speaker():
    GPIO.output(pump_pin, GPIO.HIGH)  # Activează pompa
    GPIO.output(speaker_pin, GPIO.HIGH)  # Activează difuzorul
    print("Pompa și difuzorul sunt activate")
    time.sleep(10)  # Păstrează activat 10 secunde
    deactivate_pump_and_speaker()

def deactivate_pump_and_speaker():
    GPIO.output(pump_pin, GPIO.LOW)  # Dezactivează pompa
    GPIO.output(speaker_pin, GPIO.LOW)  # Dezactivează difuzorul
    print("Pompa și difuzorul sunt dezactivate")

# Curățarea GPIO după terminarea scriptului
GPIO.cleanup()
