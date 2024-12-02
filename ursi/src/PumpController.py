import threading
import time
from RPi import GPIO

# varianta cu clasa

# Configurarea pinilor
PUMP_PIN = 17
SPEAKER_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.setup(SPEAKER_PIN, GPIO.OUT)


class PumpController:
    """Controler pentru gestionarea pompei și difuzorului."""

    def __init__(self, min_run_time=300):  # Timp minim (în secunde) pentru funcționare
        self.min_run_time = min_run_time
        self.is_active = False
        self.last_activation_time = None
        self.lock = threading.Lock()  # Asigură acces sincronizat

    def cleanup_gpio(self):
        """Curăță configurarea GPIO."""
        GPIO.cleanup()

    def activate(self):
       # """Activează pompa și difuzorul într-un thread separat."""
        with self.lock:
            if not self.is_active:
                self.is_active = True
                self.last_activation_time = time.time()
                GPIO.output(PUMP_PIN, GPIO.HIGH)
                GPIO.output(SPEAKER_PIN, GPIO.HIGH)
                print("Pompa și difuzorul sunt activate.")

        # Creează și pornește un thread pentru a verifica durata minimă de rulare
        threading.Thread(target=self._ensure_minimum_runtime, daemon=True).start()

    def deactivate(self):
        """Dezactivează pompa și difuzorul după timpul minim."""
        with self.lock:
            if self.is_active and (time.time() - self.last_activation_time >= self.min_run_time):
                self.is_active = False
                GPIO.output(PUMP_PIN, GPIO.LOW)
                GPIO.output(SPEAKER_PIN, GPIO.LOW)
                print("Pompa și difuzorul sunt dezactivate.")

    def _ensure_minimum_runtime(self):
        """Asigură că pompa rămâne activă cel puțin timpul minim setat."""
        while True:
            time.sleep(1)  # Verifică periodic
            with self.lock:
                if self.is_active and (time.time() - self.last_activation_time >= self.min_run_time):
                    # Deactivate only if no new activation signal came in
                    self.is_active = False
                    GPIO.output(PUMP_PIN, GPIO.LOW)
                    GPIO.output(SPEAKER_PIN, GPIO.LOW)
                    print("Pompa și difuzorul au fost oprite după timpul minim.")
                    break


""""
# Exemplu de utilizare

if __name__ == "__main__":
    try:
        pump_controller = PumpController(min_run_time=300)  # Setăm timpul minim la 5 minute (300 secunde)

        # Simulează detectarea unui urs
        print("Detectare urs!")
        pump_controller.activate()

        # Așteaptă pentru demonstrație
        time.sleep(10)  # După 10 secunde, încearcă să oprești pompa
        print("Nu mai este detectat ursul.")
        pump_controller.deactivate()

        # Continuă rularea pentru a observa comportamentul thread-ului
        time.sleep(320)  # Așteaptă 5 minute și 20 secunde pentru demonstrație
    finally:
        GPIO.cleanup()
"""""
