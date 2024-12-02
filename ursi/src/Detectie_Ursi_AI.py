import os
import threading
import time

import fake_rpi
from RPi import GPIO  # Acum funcționează datorită fake-rpi
# import RPi.GPIO as GPIO  # Asigură-te că folosești biblioteca corectă
import cv2
import tensorflow as tf

from src.Activare_Pompa import activate_pump_and_speaker, deactivate_pump_and_speaker, cleanup_gpio

# Configurarea pinului pentru buton
BUTTON_PIN = 18  # Pinul GPIO conectat la buton
LED_EROARE = 21


def setup_gpio():
    """Configurează GPIO pentru buton."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Rezistor pull-up pentru buton
    GPIO.setup(LED_EROARE, GPIO.OUT)  # LED-ul de eroare


def shutdown(channel):
    """Funcția de oprire a sistemului."""
    print("Buton apăsat! Oprire sistem.")
    os.system("sudo shutdown -h now")


def button_listener():
    """Thread pentru ascultarea butonului."""
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=shutdown, bouncetime=300)
    while True:
        time.sleep(1)  # Idle thread-ul pentru economisire CPU


def load_model(model_path):
    """Încarcă modelul AI."""
    print(f"Încărcare model din {model_path}...")
    return tf.keras.models.load_model(model_path)


def preprocess_frame(frame):
    """Preprocesează imaginea pentru model."""
    input_image = cv2.resize(frame, (224, 224))  # Ajustează la dimensiunea modelului
    input_image = input_image / 255.0  # Normalizare
    return input_image.reshape(1, 224, 224, 3)


def detect_bear(model, frame):
    """Determină dacă este detectat un urs în cadru."""
    input_image = preprocess_frame(frame)
    prediction = model.predict(input_image)
    return prediction[0] > 0.5  # Prag de detectare


def main():
    """Funcția principală."""
    try:
        # Configurare GPIO
        setup_gpio()
        GPIO.output(LED_EROARE, GPIO.LOW)

        # Pornire thread pentru ascultarea butonului
        threading.Thread(target=button_listener, daemon=True).start()

        # Încarcă modelul pre-antrenat
        model = load_model('/calea/catre/modelul_tau.h5')

        # Deschide camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Camera nu poate fi accesată.")
            GPIO.output(LED_EROARE, GPIO.HIGH)  # Activează LED-ul de eroare
            return

        is_active = False
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Camera nu returnează cadre. Ieșire.")
                GPIO.output(LED_EROARE, GPIO.HIGH)
                break

            # Verifică dacă un urs este detectat
            if detect_bear(model, frame):
                if not is_active:
                    activate_pump_and_speaker()
                    is_active = True
                else:
                    if is_active:
                        deactivate_pump_and_speaker()
                        is_active = False

            # Afișează imaginea
            cv2.imshow("Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Ieșire prin comanda utilizatorului.")
                break

        cap.release()
    finally:
        # Curățare
        cv2.destroyAllWindows()
        cleanup_gpio()
        print("GPIO curățat. Ieșire în siguranță.")


if __name__ == "__main__":
    main()
