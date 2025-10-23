import cv2
import face_recognition
import os
import numpy as np

# Caminho para a pasta de rostos conhecidos
KNOWN_FACES_DIR = "data/known_faces"
TOLERANCE = 0.55  # Limiar de similaridade (quanto menor, mais rígido)
MODEL = "hog"  # Modelo de detecção (hog ou cnn)

# Carregar rostos conhecidos
known_faces = []
known_names = []

for name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    if not os.path.isdir(person_dir):
        continue
    for filename in os.listdir(person_dir):
        filepath = os.path.join(person_dir, filename)
        if filename.startswith('.'):
            continue
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_faces.append(encodings[0])
            known_names.append(name)

print(f"{len(set(known_names))} alunos carregados: {list(set(known_names))}")

# Inicializar webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        continue

    # Reduzir tamanho para acelerar processamento
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detectar rostos
    face_locations = face_recognition.face_locations(rgb_small_frame, model=MODEL)
    face_encodings = []
    if face_locations:
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Comparar com rostos conhecidos
        distances = face_recognition.face_distance(known_faces, face_encoding)
        if len(distances) > 0:
            best_match_index = np.argmin(distances)
            name = known_names[best_match_index]
            similarity = 1 - distances[best_match_index]  # Quanto maior, mais parecido
            similarity_percent = int(similarity * 100)

            if distances[best_match_index] > TOLERANCE:
                name = "Desconhecido"
        else:
            name = "Desconhecido"
            similarity_percent = 0

        # Ajustar coordenadas para frame original
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Desenhar quadrado e texto
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 4)
        cv2.putText(frame, f"{name} ({similarity_percent}%)", (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 4)

    cv2.imshow("Reconhecimento Facial", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
