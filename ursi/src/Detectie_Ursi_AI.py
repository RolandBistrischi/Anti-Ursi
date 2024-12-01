import cv2
import tensorflow as tf

from src.Activare_Pompa import activate_pump_and_speaker

# Încarcă modelul pre-antrenat
model = tf.keras.models.load_model('/calea/catre/modelul_tau.h5')

# Deschide camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Preprocesează imaginea (redimensionează la dimensiunea dorită)
    input_image = cv2.resize(frame, (224, 224))  # Exemplu pentru modelul ResNet
    input_image = input_image / 255.0  # Normalizare

    # Adaugă dimensiunea batch
    input_image = input_image.reshape(1, 224, 224, 3)

    # Realizează predicția
    prediction = model.predict(input_image)

    # Verifică dacă modelul a detectat ursul
    if prediction[0] > 0.5:  # Aceasta este o valoare de prag pe care o ajustezi
        print("Urs detectat!")
        # Activează semnalul pentru pompa și difuzor
        # Apel la funcția care activează tranzistorul
        activate_pump_and_speaker()

    # Afișează imaginea cu predicția
    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
