# CLAUDE.md

Acest fișier oferă indicații pentru Claude Code (claude.ai/code) atunci când lucrează cu codul din acest repository.

## Prezentare generală a proiectului

Acesta este un proiect Python mic, gândit pentru începători, care urmărește un
flux video (o webcam sau o cameră IP/NVR prin RTSP) și alertează la detectarea
mișcării, salvând o poză. Este prezentat explicit (în `README.md`) ca o primă
temă practică pentru cineva care abia începe să programeze, cu idei de "pași
următori" (alerte pe email, rulare ca serviciu de fundal, curățarea automată a
pozelor vechi, detecție bazată pe AI pentru persoane/animale) lăsate pentru
sesiuni viitoare.

Toată documentația vizibilă utilizatorului și comentariile din cod sunt scrise
în română — păstrează această limbă când editezi `README.md` sau comentariile
din scripturile existente și menține explicațiile pe înțelesul unui începător
(README-ul chiar enumeră ce concepte de programare — variabile, funcții,
bucle `while`, condiții `if` — demonstrează fiecare parte a codului).

## Comenzi

```bash
# Instalează singura dependență (opencv-python)
pip install -r requirements.txt

# Test rapid de conexiune: se conectează o singură dată, salvează test_poza.jpg, apoi iese
python test_camera.py

# Bucla continuă de detecție a mișcării (Ctrl+C pentru oprire)
python motion_alert.py
```

Nu există pas de build, linter sau suite de teste configurate în acest repo.

Ambele scripturi citesc sursa video din variabila de mediu `CAMERA_SOURCE` (un
URL RTSP de forma `rtsp://user:parola@192.168.1.50:554/stream1`); dacă nu e
setată, folosesc implicit `0`, webcam-ul local. Nu scrie niciodată credențiale
de cameră direct în cod — transmite-le mereu prin `CAMERA_SOURCE`.

## Arhitectură

- `test_camera.py` — verificare minimă de sănătate. Deschide `VIDEO_SOURCE` o
  singură dată, citește un cadru, îl salvează în `test_poza.jpg` și iese cu un
  mesaj clar OK/EROARE. Menit să fie rulat înainte de `motion_alert.py` pentru
  a confirma că adresa RTSP/credențialele sunt corecte.
- `motion_alert.py` — detectorul propriu-zis, structurat astfel:
  1. Constantele la nivel de modul `VIDEO_SOURCE` / `MOTION_THRESHOLD` /
     `MIN_MOTION_AREA` / `ALERT_COOLDOWN_SECONDS` — locul intenționat pentru a
     ajusta comportamentul fără a atinge logica buclei.
  2. `send_alert(frame, timestamp)` — salvează o poză în `snapshots/` (creat
     la nevoie, exclus din git) și afișează un mesaj de alertă; acesta este
     punctul de extensie desemnat pentru viitoare canale de notificare (ex.
     email/SMS) menționate la "pași următori" din README.
  3. `main()` — deschide captura, apoi repetă în buclă: citește un cadru,
     convertește la grayscale + blur, calculează diferența față de cadrul
     anterior, aplică threshold + dilate, găsește contururi și tratează orice
     contur mai mare decât `MIN_MOTION_AREA` ca mișcare. `ALERT_COOLDOWN_SECONDS`
     limitează alertele repetate pentru mișcare susținută.

Nu există alte module — ambele fișiere sunt scripturi de sine stătătoare care
folosesc aceeași convenție a variabilei de mediu `CAMERA_SOURCE`.
