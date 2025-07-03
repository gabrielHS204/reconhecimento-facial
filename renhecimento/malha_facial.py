import cv2
from deepface import DeepFace
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Iniciar webcam
cap = cv2.VideoCapture(0)

# Iniciar o FaceMesh
with mp_face_mesh.FaceMesh(
    max_num_faces=2,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    frame_count = 0
    ultima_emocao_detectada = ""  # <- Correto: declarar fora do loop

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        # A cada 30 frames, atualiza a emoção
        if frame_count % 15 == 0:
            try:
                small_frame = cv2.resize(frame, (320, 240))
                analysis = DeepFace.analyze(
                    small_frame,
                    actions=['emotion'],
                    enforce_detection=False
                )

                # Compatível com diferentes versões
                if isinstance(analysis, list):
                    dominant_emotion = analysis[0]['dominant_emotion']
                else:
                    dominant_emotion = analysis['dominant_emotion']

                ultima_emocao_detectada = f'Emocao: {dominant_emotion}'

            except Exception as e:
                print("Erro na detecção:", e)

        # Desenhar malha facial
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
                )

        if ultima_emocao_detectada:
            cv2.putText(frame, ultima_emocao_detectada, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Exibir o frame
        cv2.imshow("FaceMesh", frame)
        frame_count += 1

        # Sair com 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Encerrar recursos
cap.release()
cv2.destroyAllWindows()
