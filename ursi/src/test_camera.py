import cv2
import os
import subprocess
import ultralytics
import numpy as np
from RPi import GPIO
import sys
sys.path.append('/usr/bin/python3/ultralytics')
import ultralytics
import pigpio
import time


pi = pigpio.pi()
LED_EROARE = 27
CONTROL_PIN = 18  # Pin pentru buzzer și pompă (GPIO 18)

pi.set_mode(LED_EROARE, pigpio.OUTPUT)
pi.set_mode(CONTROL_PIN, pigpio.OUTPUT)

pi.write(LED_EROARE, 0)
pi.write(CONTROL_PIN, 0)

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
        print(stdout)  # Optional: Debugging output
        if "bearface" in stdout:
            return True
    except subprocess.CalledProcessError as e:
        print(f"Eroare la rularea scriptului: {e.stderr}")
    return False

def process_video_stream():
    """Procesează fluxul video în timp real folosind libcamera și FFmpeg."""
    prediction_save_path = "/home/echipa1/Downloads/albear-main/data/07_model_output/beardetection"
    os.makedirs(prediction_save_path, exist_ok=True)

    libcamera_command = [
        "libcamera-vid", "--inline", "--framerate", "5", "--width", "640", "--height", "480",
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
                pi.write(LED_EROARE, 1)
                pi.write(CONTROL_PIN, 1)
                time.sleep(7)
                pi.write(CONTROL_PIN, 0)
                pi.write(LED_EROARE, 0)

                #GPIO.output(LED_EROARE, GPIO.HIGH)
            else:
                print("Niciun urs detectat.")
                pi.write(LED_EROARE, 0)
                pi.write(CONTROL_PIN, 0)

                #GPIO.output(LED_EROARE, GPIO.LOW)

            # Afișează cadrul video
            cv2.imshow("Video Stream", frame)

            # Oprește cu tasta 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        process_camera.terminate()
        process_ffmpeg.terminate()
        pi.write(CONTROL_PIN, 0)
        pi.stop()        
        cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video_stream()