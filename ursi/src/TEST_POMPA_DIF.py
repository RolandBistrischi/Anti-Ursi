import RPi.GPIO as GPIO
import time

# Pin de control pentru pompa și buzzer
CONTROL_PIN = 18  

def setup_gpio():
    """Configurează GPIO și setează pinul de control ca OUTPUT."""
    try:
        GPIO.setmode(GPIO.BCM)  # Se folosește numerotarea BCM
        GPIO.setup(CONTROL_PIN, GPIO.OUT)  # Configurează pinul ca OUTPUT
        GPIO.output(CONTROL_PIN, GPIO.LOW)
        print("GPIO configurat cu succes.")
    except Exception as e:
        print(f"Eroare la configurarea GPIO: {e}")
        raise  # Ridică din nou excepția pentru a opri scriptul

def activate_pump_and_buzzer():
    """Activează pompa și buzzer-ul."""
    try:
        GPIO.output(CONTROL_PIN, GPIO.HIGH)  # Trimite HIGH
        print("Pompa și buzzer-ul sunt ACTIVE.")
    except RuntimeError as e:
        print(f"Eroare la activarea pompei și buzzer-ului: {e}")
        raise

def deactivate_pump_and_buzzer():
    """Dezactivează pompa și buzzer-ul."""
    try:
        GPIO.output(CONTROL_PIN, GPIO.LOW)  # Trimite LOW (0V)
        print("Pompa și buzzer-ul sunt OPRITE.")
    except RuntimeError as e:
        print(f"Eroare la dezactivarea pompei și buzzer-ului: {e}")
        raise

def main():
    """Funcția principală."""
    setup_gpio()  # Asigură-te că GPIO este configurat corect
    try:
        print("Aștept 5 secunde înainte de a porni pompa și buzzer-ul...")
        time.sleep(5)  # Așteaptă 5 secunde
        activate_pump_and_buzzer()  # Activează pompa și buzzer-ul

        print("Pompa și buzzer-ul sunt active. Apasă Ctrl + C pentru a opri.")
        while True:
            time.sleep(1)  # Menține programul activ pentru a nu opri execuția
    except KeyboardInterrupt:
        print("\nOprire manuală (Ctrl+C).")
    except Exception as e:
        print(f"A apărut o eroare: {e}")
    finally:
        deactivate_pump_and_buzzer()
        GPIO.cleanup()  # Resetare GPIO
        print("GPIO a fost resetat.")

if __name__ == "__main__":
    main()
