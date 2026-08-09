"""
Detector simplu de miscare pentru camere de supraveghere.

Cum functioneaza pe scurt:
1. Deschidem un flux video (camera IP prin RTSP, sau webcam pentru test).
2. Comparam fiecare cadru cu cadrul anterior.
3. Daca diferenta dintre cadre e suficient de mare, inseamna ca ceva s-a miscat.
4. Cand detectam miscare, salvam o poza si afisam un mesaj de alerta.

Acesta e un punct de plecare simplu, gandit pentru cineva care abia incepe
sa programeze. Poate fi extins mai tarziu (ex: trimitere email/SMS,
pastrarea inregistrarilor o perioada, mai multe camere in paralel).
"""

import os
import time
from datetime import datetime

import cv2

# ---------------------------------------------------------------------------
# Configurare - aici schimbi sursa video, fara sa atingi restul codului
# ---------------------------------------------------------------------------

# Pentru camera ta IP/NVR: pune adresa RTSP, de exemplu:
#   rtsp://utilizator:parola@192.168.1.50:554/stream1
# O poti seta ca variabila de mediu (fara sa o scrii direct in cod):
#   export CAMERA_SOURCE="rtsp://..."
# Daca nu setezi nimic, foloseste webcam-ul calculatorului (0) - bun pentru test.
VIDEO_SOURCE = os.environ.get("CAMERA_SOURCE", 0)

# Cat de mare trebuie sa fie diferenta intre doua cadre ca sa consideram ca e miscare.
# Valoare mai mica = mai sensibil (detecteaza si schimbari mici de lumina).
MOTION_THRESHOLD = 25

# Suprafata minima (in pixeli) a unei zone in miscare, ca sa ignoram zgomotul
# normal din imagine (frunze care se misca, variatii mici de lumina etc.).
MIN_MOTION_AREA = 500

# Cate secunde asteptam intre doua alerte succesive, ca sa nu ne bombardeze
# cu zeci de poze pentru aceeasi miscare continua.
ALERT_COOLDOWN_SECONDS = 10

SNAPSHOTS_DIR = "snapshots"


def send_alert(frame, timestamp):
    """Ce se intampla cand detectam miscare.

    Momentan doar salveaza o poza si afiseaza un mesaj in consola.
    Aici e locul unde, mai tarziu, poti adauga trimitere de email/SMS.
    """
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    filename = os.path.join(SNAPSHOTS_DIR, f"miscare_{timestamp}.jpg")
    cv2.imwrite(filename, frame)
    print(f"[ALERTA] Miscare detectata la {timestamp}! Poza salvata: {filename}")


def main():
    capture = cv2.VideoCapture(VIDEO_SOURCE)
    if not capture.isOpened():
        raise SystemExit(f"Nu pot deschide sursa video: {VIDEO_SOURCE}")

    print(f"Pornit, citesc de la: {VIDEO_SOURCE}. Apasa Ctrl+C pentru oprire.")

    previous_frame = None
    last_alert_time = 0.0

    while True:
        ok, frame = capture.read()
        if not ok:
            print("Nu mai primesc imagine de la camera. Ma opresc.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if previous_frame is None:
            previous_frame = gray
            continue

        frame_diff = cv2.absdiff(previous_frame, gray)
        thresh = cv2.threshold(frame_diff, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = any(cv2.contourArea(c) >= MIN_MOTION_AREA for c in contours)

        if motion_detected and (time.time() - last_alert_time) >= ALERT_COOLDOWN_SECONDS:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            send_alert(frame, timestamp)
            last_alert_time = time.time()

        previous_frame = gray


if __name__ == "__main__":
    main()
