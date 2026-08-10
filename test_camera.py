"""
Test rapid de conexiune la camera.

Se conecteaza o singura data, ia o poza si o salveaza local, ca sa
verifici rapid ca adresa/portul/user/parola sunt corecte, inainte
sa pornesti supravegherea continua din motion_alert.py.

Rulare:
    export CAMERA_SOURCE="rtsp://admin:PAROLA@IP:554/Streaming/Channels/101"
    python test_camera.py
"""

import os
import sys

import cv2

VIDEO_SOURCE = os.environ.get("CAMERA_SOURCE", 0)


def main():
    print(f"Incerc sa ma conectez la: {VIDEO_SOURCE}")
    capture = cv2.VideoCapture(VIDEO_SOURCE)

    if not capture.isOpened():
        print("EROARE: nu m-am putut conecta. Verifica adresa, portul si user/parola.")
        sys.exit(1)

    ok, frame = capture.read()
    capture.release()

    if not ok:
        print("EROARE: conexiunea s-a deschis, dar nu am primit nicio imagine.")
        sys.exit(1)

    cv2.imwrite("test_poza.jpg", frame)
    print("OK! Poza salvata ca test_poza.jpg - deschide-o sa vezi ce vede camera.")


if __name__ == "__main__":
    main()
