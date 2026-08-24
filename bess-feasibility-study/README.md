# Studiu de Fezabilitate — instalație BESS, Cramele Odobești SA

Workflow Claude Code care leagă un model financiar parametric (`.xlsx`) de
ciorna structurată a Studiului de Fezabilitate (`.docx`, conform H.G.
907/2016, Anexa 4), pentru proiectul de instalație autonomă de stocare a
energiei electrice în baterii (BESS) propus de Cramele Odobești SA în zona
Movilița, județul Vrancea, în cadrul apelului Fondul pentru modernizare.

## Ce face

De fiecare dată când modelul financiar se schimbă (oferte reale de la
furnizori, cost de racordare din studiul de soluție, spread de piață dintr-o
analiză reală etc.), workflow-ul regenerează automat draftul `.docx` cu
indicatorii tehnico-economici actualizați — fără să atingă secțiunile care
sunt legal în sarcina proiectantului atestat.

```
bess-feasibility-study/
├── model/model_financiar.xlsx          model financiar parametric (intrare)
├── templates/SF_ciorna_template.docx   ciorna SF originală (intrare, sursă de adevăr pentru structură)
├── scripts/
│   ├── extract_model.py                xlsx → data/model_values.json
│   ├── fill_docx.py                    json + template → output/*.docx
│   ├── generate.sh                     rulează cei doi pași de mai sus
│   └── add_china_scenario.py           adaugă/actualizează foaia ScenariuChina în xlsx
├── data/model_values.json              (generat)
└── output/SF_Cramele_Odobesti_BESS.docx  (generat — livrabilul)
```

## Scenariul alternativ: reper de cost China

`model/model_financiar.xlsx` conține și o foaie `ScenariuChina`, adăugată cu
`scripts/add_china_scenario.py`, care recalculează integral bugetul,
finanțarea și fluxul de numerar folosind un reper de cost turnkey din China
(implicit 73.000 USD/MWh, BNEF/Ember 2025-2026) în loc de reperul Europa din
`Ipoteze!C22` (177.000 USD/MWh) — toate celelalte ipoteze rămân legate de
foaia `Ipoteze`. Foaia include și un tabel de comparație Europa vs. China.

Cu reperele de test actuale, diferența e mare: investiția totală scade de la
~43,3 mil. EUR la ~19,4 mil. EUR, contribuția proprie de la ~32,3 la ~8,4 mil.
EUR, iar VAN trece din negativ (~‑11 mil. EUR) în pozitiv (~+14,2 mil. EUR),
cu RIR de ~31% și termen de recuperare de ~4 ani (față de 13 ani). Este o
ilustrare a sensibilității proiectului la costul unitar de echipamente, **nu
o ofertă și nu o recomandare de furnizor** — vezi avertismentul din foaie
despre taxe vamale UE, certificare CE și costul de service local pe termen
lung, care nu sunt incluse în acest reper.

Pentru a rula `python3 scripts/extract_model.py` din nou fetch cu valori
proaspete după orice editare manuală a modelului, deschide întâi
`model_financiar.xlsx` în Excel sau LibreOffice și salvează-l o dată — fișierul
are `fullCalcOnLoad` activat, deci recalculează automat tot la deschidere.

## Cum îl rulezi

```bash
bash scripts/generate.sh
```

Sau, invocat din Claude Code, skill-ul `genereaza-studiu-fezabilitate`
(`.claude/skills/genereaza-studiu-fezabilitate/SKILL.md`) rulează același
workflow ori de câte ori modelul financiar e actualizat.

Dependențe: `python3` cu `openpyxl` și `python-docx`; opțional `soffice`
(LibreOffice) pentru recalcularea automată a formulelor — dacă lipsește sau
eșuează, scriptul continuă cu valorile deja salvate în fișier și avertizează.

## Ce completează automat, și ce nu

Documentul original are trei tipuri de marcaje:

| Marcaj | Cine îl completează | Ce face workflow-ul |
|---|---|---|
| `[DE COMPLETAT ...]` cu sursă în model (CAPEX, VAN, RIR, termen de recuperare, energie descărcată anual) | calculabil din model | **completează automat**, cu mențiunea explicită "valoare de test, model parametric" |
| `[DE COMPLETAT]` fără sursă în model (locuri de muncă, date cadastrale, structura contribuției proprii etc.) | beneficiar / consultant | lăsat neatins |
| `[DE COMPLETAT DE PROIECTANT]` / `[ÎN SARCINA PROIECTANTULUI]` | proiectant atestat | **niciodată atins** — devizul general, studiile de teren, scenariul de securitate la incendiu, piesele desenate rămân exclusiv în sarcina lui |

`fill_docx.py` verifică textul fiecărui placeholder înainte de a-l scrie:
dacă nu începe cu `[DE COMPLETAT` sau conține `DE PROIECTANT`, nu îl atinge.

## Avertisment — valabil pentru orice document generat de acest workflow

Modelul financiar conține în prezent **valori de test** (spread de piață,
cost de racordare, ofertă de echipamente) declarate ca atare chiar în foaia
`Ipoteze` a modelului. Cu aceste valori, modelul arată un **VAN negativ**
(~‑11 mil. EUR) și o RIR de sub 2% — proiectul nu e demonstrat viabil, doar
"testabil" ca structură de calcul. Documentul generat păstrează mențiunea
"valoare de test — a se recalcula cu date reale" lângă fiecare cifră derivată
din model, exact ca și restul ciornei originale (care avertizează în mai
multe locuri: rezultatele cu valori de test "nu au valoare de prognoză și nu
se transcriu în studiul de fezabilitate" final).

Documentul generat de acest workflow **nu este un studiu de fezabilitate
valabil** și nu poate deveni unul fără:

- deviz general și devize pe obiecte (H.G. 907/2016), pe bază de oferte ferme;
- studiu geotehnic și studiu topografic;
- scenariu de securitate la incendiu;
- studiu de soluție de racordare, de la operatorul de rețea;
- analiză de piață reală pentru spread și venituri din servicii de sistem;
- verificarea tehnică de specialitate și semnătura unui proiectant atestat.

Toate acestea sunt marcate explicit în document și rămân integral în sarcina
proiectantului/consultanților de specialitate.
