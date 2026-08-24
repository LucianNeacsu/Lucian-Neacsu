---
name: genereaza-studiu-fezabilitate
description: Regenereaza draftul de Studiu de Fezabilitate (BESS, Cramele Odobesti SA) din modelul financiar parametric dupa fiecare actualizare a bess-feasibility-study/model/model_financiar.xlsx. Foloseste cand utilizatorul modifica ipotezele modelului financiar (oferte reale, cost de racordare, spread de piata etc.) si vrea ca documentul .docx sa reflecte noile cifre, sau cand cere explicit "regenereaza studiul de fezabilitate" / "actualizeaza SF cu modelul nou".
---

# Genereaza Studiu de Fezabilitate (BESS Cramele Odobesti)

Acest skill leaga doua documente din `bess-feasibility-study/`:

- `model/model_financiar.xlsx` — modelul financiar parametric (Ipoteze, CAPEX,
  Finantare, CashFlow, Rezultate, Scenarii).
- `templates/SF_ciorna_template.docx` — ciorna structurata a Studiului de
  Fezabilitate conform H.G. 907/2016, Anexa 4.

Rularea workflow-ului produce `output/SF_Cramele_Odobesti_BESS.docx`: aceeasi
ciorna, cu indicatorii tehnico-economici din capitolul V.4 completati automat
din model (CAPEX total, energie descarcata anual, VAN, RIR, termen de
recuperare).

## Cand se foloseste

Dupa orice editare a `model/model_financiar.xlsx` (de exemplu inlocuirea
valorilor de test din foaia `Ipoteze` cu oferte ferme de la furnizori, cost de
racordare din studiul de solutie, sau spread din analiza de piata reala).

## Pasi

1. Ruleaza workflow-ul complet:
   ```bash
   bash bess-feasibility-study/scripts/generate.sh
   ```
   Acesta recalculeaza modelul (best-effort, LibreOffice), extrage
   indicatorii in `data/model_values.json`, si scrie documentul completat in
   `output/SF_Cramele_Odobesti_BESS.docx`.

2. Verifica in output-ul scriptului lista "Completate" (celulele scrise) si
   "Lasate neatinse" (placeholderele sarite). Orice placeholder marcat
   `[ÎN SARCINA PROIECTANTULUI]` sau `[DE COMPLETAT DE PROIECTANT]` trebuie sa
   ramana neatins — sunt rezervate legal proiectantului atestat.

3. Daca modelul a fost editat manual si scriptul raporteaza valori lipsa
   (`None`), deschide `model_financiar.xlsx` in Excel sau LibreOffice si
   salveaza-l o data (fortand recalcularea formulelor), apoi ruleaza din nou
   pasul 1.

4. Fiecare valoare inserata in document e marcata explicit
   `valoare de test, model parametric — a se recalcula cu date reale`. Nu
   sterge aceasta mentiune si nu prezenta documentul generat ca studiu de
   fezabilitate final — ramane o ciorna de lucru (vezi avertismentele din
   capul documentului si din README-ul proiectului).

## Detalii implementare

- `scripts/extract_model.py` — citeste celulele cheie din xlsx (valori
  cached, `data_only=True`) intr-un JSON intermediar.
- `scripts/fill_docx.py` — gaseste in docx tabelul cu antetul
  `Indicator / Valoare` (capitolul V.4) si inlocuieste, rand cu rand, doar
  celulele al caror text incepe cu `[DE COMPLETAT` si nu contine
  `DE PROIECTANT`. Pastreaza formatarea originala a fiecarui run.
- Mapping-ul foaie!celula → indicator este in `CELLS` din
  `extract_model.py`; daca modelul financiar capata randuri noi, actualizeaza
  acolo, nu in `fill_docx.py`.

Detalii complete despre proiect, limitele lui si ce nu poate inlocui
(deviz general, studii de teren, aviz ISU etc.): `bess-feasibility-study/README.md`.
