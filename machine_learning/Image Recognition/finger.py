# finger_count_mediapipe.py
import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Inisialisasi - Ubah max_num_hands ke 2 untuk mendeteksi kedua tangan (hingga 10 jari)
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.5)

# Index landmark untuk ujung jari (tip) dan pip (second joint)
FINGER_TIPS = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
FINGER_PIPS = [2, 6, 10, 14, 18]  # untuk perbandingan (thumb use different axis)

cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks, handedness_label='Kanan'):
    lm = hand_landmarks.landmark
    img_h, img_w = 1, 1  # relatif, karena kita perbandingkan rasio

    fingers = []

    # Thumb: bandingkan x (karena thumb bergerak menyamping)
    # Untuk tangan kanan, thumb tip.x > thumb.ip.x ketika terangkat ke luar (bergantung orientasi)
    # Kita pakai trik umum: bandingkan tip (4) dan pip(2) pada axis x sesuai handedness
    if handedness_label == 'Kanan':
        fingers.append(1 if lm[FINGER_TIPS[0]].x < lm[FINGER_PIPS[0]].x else 0)
    else:
        fingers.append(1 if lm[FINGER_TIPS[0]].x > lm[FINGER_PIPS[0]].x else 0)

    # Other fingers: bandingkan y (tip lebih kecil y ketika jari terangkat ke atas pada koordinat gambar)
    for tip_idx, pip_idx in zip(FINGER_TIPS[1:], FINGER_PIPS[1:]):
        fingers.append(1 if lm[tip_idx].y < lm[pip_idx].y else 0)

    return sum(fingers), fingers

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Flip frame_rgb untuk memperbaiki deteksi handedness
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.flip(frame_rgb, 1)  # Flip horizontal sebelum process
    results = hands.process(frame_rgb)

    # Flip frame untuk display mirror
    frame = cv2.flip(frame, 1)

    display_text = "Tidak ada Jari terdeteksi"

    if results.multi_hand_landmarks:
        total_fingers = 0
        all_which = []
        hand_labels = []
        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = hand_handedness.classification[0].label  # Asli: Left atau Right
            # Ubah ke bahasa Indonesia
            if label == 'Left':
                label = 'Kiri'
            elif label == 'Right':
                label = 'Kanan'
            count, which = count_fingers(hand_landmarks, label)
            total_fingers += count
            all_which.append(which)
            hand_labels.append(label)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Tampilkan total jari dari kedua tangan, dan detail per tangan
        display_text = f"Total Jari: {total_fingers}   Tangan: {hand_labels}   Posisi: {all_which}"

    cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,0), 1)
    
    #ukuran frame
    frame = cv2.resize(frame, (0,0), fx=1.5, fy=1.5)
    cv2.imshow("Finger Counter (MediaPipe)", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Esc to quit
        break

cap.release()
cv2.destroyAllWindows()
