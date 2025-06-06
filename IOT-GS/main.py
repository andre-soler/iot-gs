import cv2
import mediapipe as mp
import threading
import numpy as np
import time
import pygame 

# Caminho do som de sirene
CAMINHO_SIRENE = r'c:\Users\andre\Downloads\sirene-boa-207574.mp3'

# Inicializa pygame mixer
pygame.mixer.init()

# Função para tocar a sirene
def tocar_sirene():
    if not pygame.mixer.music.get_busy():
        print("🚨 Sirene disparada!")
        pygame.mixer.music.load(CAMINHO_SIRENE)
        pygame.mixer.music.play()

# Inicialização do MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Inicializa a câmera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Não foi possível acessar a câmera.")
    exit()

print("🎥 Sistema iniciado. Pressione 'q' para sair.")

# Controle de tempo sem movimento
sem_movimento_inicio = None
sirenando = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("❌ Erro ao capturar imagem.")
        break

    # Análise de luminosidade
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brilho_medio = np.mean(gray)

    # Processamento de movimento
    imagem_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = pose.process(imagem_rgb)

    movimento_detectado = resultados.pose_landmarks is not None

    # Mostra imagem com marcações (se houver)
    imagem_bgr = cv2.cvtColor(imagem_rgb, cv2.COLOR_RGB2BGR)
    if movimento_detectado:
        mp_drawing.draw_landmarks(imagem_bgr, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("Monitoramento - Apagão", imagem_bgr)

    # Se estiver escuro e sem movimento por mais de 5 segundos → alerta
    if brilho_medio < 20:
        if not movimento_detectado:
            if sem_movimento_inicio is None:
                sem_movimento_inicio = time.time()
            elif time.time() - sem_movimento_inicio >= 5 and not sirenando:
                sirenando = True
                tocar_sirene()
        else:
            sem_movimento_inicio = None
            sirenando = False
    else:
        sem_movimento_inicio = None
        sirenando = False

    # Encerra ao pressionar 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        print("🛑 Encerrando sistema.")
        break

# Finaliza recursos
cap.release()
cv2.destroyAllWindows()
