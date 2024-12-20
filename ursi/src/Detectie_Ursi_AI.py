import os
import subprocess
import numpy as np
import cv2
import platform
from RPi import GPIO  # GPIO pentru Raspberry Pi

# Configurare GPIO
BUTTON_PIN = 21  # Pin pentru buton
LED_EROARE = 27  # Pin pentru LED-ul de eroare
CONTROL_PIN = 18  # Pin pentru buzzer și pompă (GPIO 18)

# Configurare PWM pentru buzzer
PWM_FREQUENCY = 1000  # Frecvența default pentru tonul buzzer-ului
pwm = None  # PWM va fi inițializat mai târziu
gpio_initialized = False  # Flag pentru a verifica dacă GPIO a fost configurat corect

def setup_gpio():
    """Configurează GPIO pentru buton, LED și control pompă/buzzer."""
    global pwm, gpio_initialized
    try:
        if "arm" not in platform.uname().machine.lower():
            print("Not running on a Raspberry Pi! Skipping GPIO configuration.")
            return

        GPIO.setmode(GPIO.BCM)  # Utilizăm numerotarea BCM
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Rezistor pull-up pentru buton
        GPIO.setup(LED_EROARE, GPIO.OUT)  # LED de eroare
        GPIO.setup(CONTROL_PIN, GPIO.OUT)  # Pin de control pentru pompă și buzzer

        # Inițializează PWM pentru buzzer și pompă
        pwm = GPIO.PWM(CONTROL_PIN, PWM_FREQUENCY)
        pwm.start(0)  # Pornit cu ciclu de lucru 0% (OFF)

        gpio_initialized = True  # Marchează GPIO ca fiind configurat cu succes
        print("GPIO configurat cu succes.")
    except Exception as e:
        print(f"Eroare la configurarea GPIO: {e}")

def activate_pump_and_buzzer(frequency=1000):
    """Activează pompa și buzzer-ul cu un ton specific."""
    if pwm is None:
        print("Eroare: PWM nu este inițializat. Skipping buzzer activation.")
        return
    pwm.ChangeFrequency(frequency)  # Setează frecvența tonului buzzer-ului
    pwm.ChangeDutyCycle(50)  # Ciclu de lucru 50% pentru activare
    print(f"Pompa și buzzer-ul sunt active la frecvența {frequency} Hz.")

def deactivate_pump_and_buzzer():
    """Dezactivează pompa și buzzer-ul."""
    if pwm is None:
        print("Eroare: PWM nu este inițializat. Skipping buzzer deactivation.")
        return
    pwm.ChangeDutyCycle(0)  # Dezactivează PWM
    print("Pompa și buzzer-ul sunt dezactivate.")

def detect_bear_using_script(image_path, save_path):
    """Rulează scriptul pentru detectarea ursului."""
    try:
        command = [
            "python", "/home/echipa1/Downloads/albear-main/scripts/beardetection/model/predict.py",
            "--model-weights", "/home/echipa1/Downloads/albear-main/data/06_models/pipeline/metriclearning/bearfacesegmentation/model.pt",
            "--source-path", image_path,
            "--save-path", save_path,
            "--loglevel", "info"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        stdout = result.stdout.lower()
        print(stdout)  # Debugging output
        if "bearface" in stdout:
            return True
    except subprocess.CalledProcessError as e:
        print(f"Eroare la rularea scriptului: {e.stderr}")
    return False

def process_video_stream():
    """Procesează fluxul video în timp real și controlează pompa/buzzer-ul în funcție de detectare."""
    prediction_save_path = "/home/echipa1/Downloads/albear-main/data/07_model_output/beardetection"
    os.makedirs(prediction_save_path, exist_ok=True)

    libcamera_command = [
        "libcamera-vid", "--inline", "--framerate", "30", "--width", "640", "--height", "480",
        "--codec", "mjpeg", "--output", "-"
    ]

    ffmpeg_command = [
        "ffmpeg", "-i", "pipe:0", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"
    ]

    process_camera = subprocess.Popen(libcamera_command, stdout=subprocess.PIPE)
    process_ffmpeg = subprocess.Popen(
        ffmpeg_command, stdin=process_camera.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )

    try:
        frame_width = 640
        frame_height = 480
        frame_size = frame_width * frame_height * 3  # Dimensiunea bufferului (BGR)

        while True:
            buffer = process_ffmpeg.stdout.read(frame_size)
            if len(buffer) != frame_size:
                print("Buffer incomplet sau flux video încheiat.")
                break

            frame = np.frombuffer(buffer, dtype=np.uint8).reshape((frame_height, frame_width, 3))

            # Salvează cadrul curent ca imagine temporară
            temp_image_path = "temp_frame.jpg"
            cv2.imwrite(temp_image_path, frame)

            # Rulează detectarea ursului pe cadrul curent
            if detect_bear_using_script(temp_image_path, prediction_save_path):
                print("Urs detectat!")
                GPIO.output(LED_EROARE, GPIO.HIGH)  # Aprinde LED-ul de eroare
                activate_pump_and_buzzer()
            else:
                print("Niciun urs detectat.")
                GPIO.output(LED_EROARE, GPIO.LOW)  # Stinge LED-ul de eroare
                deactivate_pump_and_buzzer()

            # Afișează cadrul video
            cv2.imshow("Video Stream", frame)

            # Oprește cu tasta 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        process_camera.terminate()
        process_ffmpeg.terminate()
        deactivate_pump_and_buzzer()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        setup_gpio()
        process_video_stream()
    except KeyboardInterrupt:
        print("\nOprire manuală de la tastatură.")
    finally:
        if gpio_initialized:
            GPIO.cleanup()  # Resetare GPIO
