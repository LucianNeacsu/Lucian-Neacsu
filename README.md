# Detector de miscare pentru camere de supraveghere

Un proiect simplu, de inceput, care citeste imagini de la o camera si te
anunta cand detecteaza miscare (potentiala efractie). E gandit ca prima ta
tema de lucru cu Claude Code.

## Ce face

`motion_alert.py`:

1. Deschide un flux video (webcam pentru test, sau camera ta IP prin RTSP).
2. Compara fiecare imagine noua cu cea anterioara.
3. Daca diferenta e destul de mare, considera ca e miscare.
4. Salveaza o poza in folderul `snapshots/` si afiseaza un mesaj de alerta.

## Cum il rulezi

```bash
pip install -r requirements.txt
python motion_alert.py
```

Implicit foloseste webcam-ul calculatorului (util ca sa testezi ca merge).
Opreste-l cu `Ctrl+C`.

## Cum il conectezi la camera ta reala

Sistemul tau de camere are probabil un stream RTSP (verifica in setarile
NVR-ului/routerului adresa camerei - de obicei ceva de forma
`rtsp://utilizator:parola@IP:554/...`). Seteaza-l ca variabila de mediu,
fara sa il scrii in cod:

```bash
export CAMERA_SOURCE="rtsp://utilizator:parola@192.168.1.50:554/stream1"
python motion_alert.py
```

## Concepte de programare folosite (pe scurt)

- **Variabile** (`MOTION_THRESHOLD`, `VIDEO_SOURCE`) - valori pe care le poti
  schimba usor fara sa cauti prin tot codul.
- **Functii** (`send_alert`, `main`) - bucati de cod cu un nume, pe care le
  poti apela ori de cate ori ai nevoie.
- **Bucla `while True`** - repeta acelasi lucru (citeste o imagine, verifica
  daca e miscare) la infinit, pana il opresti tu.
- **Conditii `if`** - codul ia decizii ("daca e miscare SI a trecut destul
  timp de la ultima alerta, atunci trimite alerta").

## Pasi urmatori (idei, cand esti gata)

- Trimitere alerta pe **email** cand se detecteaza miscare.
- Rulare in fundal / ca serviciu, ca sa mearga continuu.
- Pastrarea/curatarea automata a pozelor mai vechi de o anumita perioada.
- Detectie mai inteligenta (persoane vs. animale/masini) cu un model AI.

Cand vrei sa treci la oricare dintre astea, spune-i lui Claude Code ce vrei
si il extindem impreuna, pas cu pas.
