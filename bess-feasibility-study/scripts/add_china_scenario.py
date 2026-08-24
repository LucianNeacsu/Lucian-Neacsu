#!/usr/bin/env python3
"""Adauga in model_financiar.xlsx o foaie noua "ScenariuChina": acelasi model
(buget, finantare, flux de numerar, VAN/RIR/payback), recalculat integral cu
un reper de cost turnkey din China in loc de reperul Europa din Ipoteze!C22.

Toate celelalte ipoteze (capacitate, putere, spread, cicluri, rata de
actualizare etc.) raman legate de foaia Ipoteze -- se modifica automat daca
utilizatorul le schimba acolo. Singura valoare noua, editabila, e reperul de
cost China (celula galbena C7).

Idempotent: daca foaia ScenariuChina exista deja, o sterge si o recreaza.
"""
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.workbook.properties import CalcProperties

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "model" / "model_financiar.xlsx"

NAVY = "FF1F3864"
YELLOW = "FFFFFF00"
BLUE = "FF0000FF"
GREEN = "FF008000"
GRAY = "FF808080"
RED = "FFC00000"
WHITE = "FFFFFFFF"

F_TITLE = Font(name="Arial", bold=True, size=13, color=NAVY)
F_SECTION = Font(name="Arial", bold=True, size=10, color=WHITE)
FILL_SECTION = PatternFill(fgColor=NAVY, fill_type="solid")
F_LABEL = Font(name="Arial", size=10)
F_LABEL_B = Font(name="Arial", bold=True, size=10)
F_INPUT = Font(name="Arial", size=10, color=BLUE)
FILL_INPUT = PatternFill(fgColor=YELLOW, fill_type="solid")
F_LINK = Font(name="Arial", size=10, color=GREEN)
F_NOTE = Font(name="Arial", italic=True, size=8, color=GRAY)
F_WARN = Font(name="Arial", bold=True, size=10, color=RED)
FILL_YEARROW = PatternFill(fgColor=NAVY, fill_type="solid")
F_YEAR = Font(name="Arial", bold=True, size=10, color=WHITE)

NUM_EUR = r"#,##0;\(#,##0\);\-"
NUM_1DEC = r"#,##0.0;\(#,##0.0\);\-"
NUM_PCT = "0.0%"
NUM_INT = "0"
NUM_FX = "0.000"

YEAR_COLS = list("DEFGHIJKLMNOPQR")  # An 1 .. An 15 (15 columns)


def sect(ws, row, text):
    ws.cell(row=row, column=2, value=text)
    for col in range(2, 6):
        c = ws.cell(row=row, column=col)
        c.font = F_SECTION
        c.fill = FILL_SECTION


def label(ws, row, text, bold=False):
    c = ws.cell(row=row, column=2, value=text)
    c.font = F_LABEL_B if bold else F_LABEL


def val(ws, row, col, value, font=F_LABEL, numfmt=NUM_EUR, fill=None):
    c = ws.cell(row=row, column=col, value=value)
    c.font = font
    c.number_format = numfmt
    if fill:
        c.fill = fill
    return c


def note(ws, row, text, col=5):
    c = ws.cell(row=row, column=col, value=text)
    c.font = F_NOTE


def main():
    wb = openpyxl.load_workbook(MODEL_PATH)
    if "ScenariuChina" in wb.sheetnames:
        del wb["ScenariuChina"]
    ws = wb.create_sheet("ScenariuChina")
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 44
    ws.column_dimensions["C"].width = 16
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 60
    for col in "FGHIJKLMNOPQR":
        ws.column_dimensions[col].width = 12

    ws["B2"] = "SCENARIU ALTERNATIV: REPER DE COST DIN CHINA"
    ws["B2"].font = F_TITLE
    ws["B3"] = (
        "Recalculează bugetul, finanțarea și fluxul de numerar cu un reper de cost "
        "turnkey din China, păstrând toate celelalte ipoteze din foaia Ipoteze "
        "neschimbate (capacitate, putere, spread, cicluri, rata de actualizare etc.)."
    )
    ws["B3"].font = F_LABEL
    ws["B4"] = "CIORNĂ DE LUCRU. Celula galbenă de mai jos se completează de utilizator. Restul se calculează automat."
    ws["B4"].font = F_NOTE

    # 1. Ipoteza de cost alternativa
    sect(ws, 6, "1. IPOTEZĂ DE COST ALTERNATIVĂ")
    label(ws, 7, "Cost turnkey referință China")
    val(ws, 7, 3, 73000, F_INPUT, NUM_EUR, FILL_INPUT)
    ws.cell(row=7, column=4, value="USD/MWh").font = F_LABEL
    note(ws, 7, "Reper BNEF/Ember 2025-2026 pentru sisteme turnkey China. NU este ofertă. "
                "Comparație: Ipoteze!C22 = reper Europa (177.000 USD/MWh).")

    label(ws, 8, "Cost turnkey referință China")
    c = val(ws, 8, 3, "=C7*Ipoteze!C21", F_LABEL, NUM_EUR)
    ws.cell(row=8, column=4, value="EUR/MWh").font = F_LABEL
    note(ws, 8, "Convertit la cursul din Ipoteze!C21")

    # 2. Buget de investitie recalculat
    sect(ws, 10, "2. BUGET DE INVESTIȚIE RECALCULAT")
    label(ws, 11, "Cost unitar de putere")
    val(ws, 11, 3, "=C8*Ipoteze!C12*Ipoteze!C25/(Ipoteze!C12/Ipoteze!C13)", numfmt=NUM_EUR)
    ws.cell(row=11, column=4, value="EUR/MW").font = F_LABEL

    label(ws, 12, "Cost unitar energetic")
    val(ws, 12, 3, "=C8*(1-Ipoteze!C25)", numfmt=NUM_EUR)
    ws.cell(row=12, column=4, value="EUR/MWh").font = F_LABEL

    label(ws, 13, "Cost echipamente BESS")
    val(ws, 13, 3, "=C12*Ipoteze!C12+C11*Ipoteze!C14", numfmt=NUM_EUR)
    ws.cell(row=13, column=4, value="EUR").font = F_LABEL

    label(ws, 14, "Linie de racord 110 kV")
    val(ws, 14, 3, "=Ipoteze!C32", F_LINK, NUM_EUR)
    ws.cell(row=14, column=4, value="EUR").font = F_LABEL
    note(ws, 14, "Neschimbat față de scenariul de referință")

    label(ws, 15, "Stație de conexiune")
    val(ws, 15, 3, "=Ipoteze!C34", F_LINK, NUM_EUR)
    ws.cell(row=15, column=4, value="EUR").font = F_LABEL

    label(ws, 16, "Tarif de racordare")
    val(ws, 16, 3, "=Ipoteze!C35", F_LINK, NUM_EUR)
    ws.cell(row=16, column=4, value="EUR").font = F_LABEL

    label(ws, 17, "Construcții civile")
    val(ws, 17, 3, "=Ipoteze!C37*C13", numfmt=NUM_EUR)
    ws.cell(row=17, column=4, value="EUR").font = F_LABEL

    label(ws, 18, "Sisteme de siguranță și incendiu")
    val(ws, 18, 3, "=Ipoteze!C39*C13", numfmt=NUM_EUR)
    ws.cell(row=18, column=4, value="EUR").font = F_LABEL

    label(ws, 19, "Proiectare, avize, consultanță")
    val(ws, 19, 3, "=Ipoteze!C41*C13", numfmt=NUM_EUR)
    ws.cell(row=19, column=4, value="EUR").font = F_LABEL

    label(ws, 20, "Subtotal", bold=True)
    val(ws, 20, 3, "=SUM(C13:C19)", F_LABEL_B, NUM_EUR)

    label(ws, 21, "Neprevăzute")
    val(ws, 21, 3, "=C20*Ipoteze!C43", numfmt=NUM_EUR)

    label(ws, 22, "TOTAL INVESTIȚIE", bold=True)
    val(ws, 22, 3, "=C20+C21", F_LABEL_B, NUM_EUR)

    label(ws, 23, "Cost unitar al investiției")
    val(ws, 23, 3, "=IFERROR(C22/Ipoteze!C12,0)", numfmt=NUM_EUR)
    ws.cell(row=23, column=4, value="EUR/MWh instalat").font = F_LABEL

    label(ws, 24, "Total cheltuieli eligibile (estimat)")
    val(ws, 24, 3, "=C13+C15+C17+C18", numfmt=NUM_EUR)
    note(ws, 24, "Exclude proiectarea și, prudent, linia și tariful de racordare, ca în foaia CAPEX")

    # 3. Finantare
    sect(ws, 26, "3. FINANȚARE")
    label(ws, 27, "Ajutor cerut = ofertă x capacitate")
    val(ws, 27, 3, "=Ipoteze!C46*Ipoteze!C12", numfmt=NUM_EUR)

    label(ws, 28, "Test 1: plafon unitar (Ipoteze!C47)")
    val(ws, 28, 3, "=Ipoteze!C47*Ipoteze!C12", numfmt=NUM_EUR)

    label(ws, 29, "Test 2: plafon per întreprindere")
    val(ws, 29, 3, "=Ipoteze!C48", numfmt=NUM_EUR)

    label(ws, 30, "Test 3: 100% din cheltuielile eligibile")
    val(ws, 30, 3, "=C24", numfmt=NUM_EUR)

    label(ws, 31, "AJUTOR ACORDABIL", bold=True)
    val(ws, 31, 3, "=MIN(C27,C28,C29,C30)", F_LABEL_B, NUM_EUR)

    label(ws, 32, "Contribuție proprie")
    val(ws, 32, 3, "=C22-C31", numfmt=NUM_EUR)

    # 4. Flux de numerar
    sect(ws, 34, "4. FLUX DE NUMERAR (ani 0-15)")
    ws.cell(row=35, column=3, value="An 0").font = F_YEAR
    ws.cell(row=35, column=3).fill = FILL_YEARROW
    for i, col in enumerate(YEAR_COLS, start=1):
        cell = ws[f"{col}35"]
        cell.value = f"An {i}"
        cell.font = F_YEAR
        cell.fill = FILL_YEARROW

    label(ws, 36, "Energie descărcată (MWh/an)")
    val(ws, 36, 3, 0, F_LINK, NUM_1DEC)
    for col in YEAR_COLS:
        val(ws, 36, ord(col) - 64, f"=CashFlow!{col}7", F_LINK, NUM_1DEC)

    label(ws, 37, "Venit din arbitraj")
    val(ws, 37, 3, 0, F_LINK, NUM_EUR)
    for col in YEAR_COLS:
        val(ws, 37, ord(col) - 64, f"=CashFlow!{col}8", F_LINK, NUM_EUR)

    label(ws, 38, "Venit din servicii de sistem")
    val(ws, 38, 3, 0, F_LINK, NUM_EUR)
    for col in YEAR_COLS:
        val(ws, 38, ord(col) - 64, f"=CashFlow!{col}9", F_LINK, NUM_EUR)

    label(ws, 39, "Costuri de rețea și consum tehnologic")
    val(ws, 39, 3, 0, F_LINK, NUM_EUR)
    for col in YEAR_COLS:
        val(ws, 39, ord(col) - 64, f"=CashFlow!{col}10", F_LINK, NUM_EUR)

    label(ws, 40, "Costuri O&M (recalculate cu noul TOTAL)")
    val(ws, 40, 3, 0, F_LABEL, NUM_EUR)
    for i, col in enumerate(YEAR_COLS, start=1):
        val(ws, 40, ord(col) - 64, f"=-$C$22*Ipoteze!C54*(1+Ipoteze!C55)^{i}", numfmt=NUM_EUR)

    label(ws, 41, "EBITDA", bold=True)
    val(ws, 41, 3, 0, F_LABEL_B, NUM_EUR)
    for col in YEAR_COLS:
        val(ws, 41, ord(col) - 64, f"=SUM({col}37:{col}40)", F_LABEL_B, NUM_EUR)

    label(ws, 42, "Amortizare")
    val(ws, 42, 3, 0, F_LABEL, NUM_EUR)
    for i, col in enumerate(YEAR_COLS, start=1):
        val(ws, 42, ord(col) - 64, f"=IF({i}<=Ipoteze!C61,-$C$22/Ipoteze!C61,0)", numfmt=NUM_EUR)

    label(ws, 43, "Profit brut")
    val(ws, 43, 3, 0, F_LABEL, NUM_EUR)
    for col in YEAR_COLS:
        val(ws, 43, ord(col) - 64, f"={col}41+{col}42", numfmt=NUM_EUR)

    label(ws, 44, "Impozit pe profit")
    val(ws, 44, 3, 0, F_LABEL, NUM_EUR)
    for col in YEAR_COLS:
        val(ws, 44, ord(col) - 64, f"=-MAX(0,{col}43)*Ipoteze!C60", numfmt=NUM_EUR)

    label(ws, 45, "Profit net")
    val(ws, 45, 3, 0, F_LABEL, NUM_EUR)
    for col in YEAR_COLS:
        val(ws, 45, ord(col) - 64, f"={col}43+{col}44", numfmt=NUM_EUR)

    label(ws, 46, "Investiție")
    val(ws, 46, 3, "=-C22", numfmt=NUM_EUR)

    label(ws, 47, "Grant încasat")
    val(ws, 47, 3, "=C31", numfmt=NUM_EUR)

    label(ws, 48, "FLUX DE NUMERAR NET", bold=True)
    val(ws, 48, 3, "=C46+C47", F_LABEL_B, NUM_EUR)
    for col in YEAR_COLS:
        val(ws, 48, ord(col) - 64, f"={col}41+{col}44", F_LABEL_B, NUM_EUR)

    label(ws, 49, "Flux cumulat")
    val(ws, 49, 3, "=C48", numfmt=NUM_EUR)
    prev = "C"
    for col in YEAR_COLS:
        val(ws, 49, ord(col) - 64, f"={prev}49+{col}48", numfmt=NUM_EUR)
        prev = col

    # 5. Indicatori
    sect(ws, 51, "5. INDICATORI DE PERFORMANȚĂ (SCENARIU CHINA)")
    label(ws, 52, "Investiție totală")
    val(ws, 52, 3, "=C22", numfmt=NUM_EUR)
    label(ws, 53, "Grant obținut")
    val(ws, 53, 3, "=C31", numfmt=NUM_EUR)
    label(ws, 54, "Contribuție proprie necesară")
    val(ws, 54, 3, "=C32", numfmt=NUM_EUR)
    label(ws, 55, "Ponderea grantului")
    val(ws, 55, 3, "=IFERROR(C31/C22,0)", numfmt=NUM_PCT)
    label(ws, 56, "EBITDA an 1")
    val(ws, 56, 3, "=D41", numfmt=NUM_EUR)
    label(ws, 57, "VAN al proiectului")
    val(ws, 57, 3, "=NPV(Ipoteze!C59,D48:R48)+C48", numfmt=NUM_EUR)
    label(ws, 58, "RIR al proiectului")
    val(ws, 58, 3, "=IFERROR(IRR(C48:R48),0)", numfmt=NUM_PCT)
    label(ws, 59, "Termen de recuperare simplu")
    val(ws, 59, 3, "=IFERROR(MATCH(0,C49:R49,1),0)", numfmt=NUM_INT)

    # 6. Comparatie
    sect(ws, 61, "6. COMPARAȚIE EUROPA (Ipoteze) vs CHINA (acest scenariu)")
    for col, text in [(2, "Indicator"), (3, "Europa (reper Ipoteze!C22)"), (4, "China (acest scenariu)"), (5, "Diferență")]:
        c = ws.cell(row=62, column=col, value=text)
        c.font = F_LABEL_B

    rows = [
        ("Cost turnkey referință (USD/MWh)", "=Ipoteze!C22", "=C7", NUM_EUR),
        ("Total investiție (EUR)", "=Rezultate!C5", "=C22", NUM_EUR),
        ("Contribuție proprie (EUR)", "=Rezultate!C8", "=C32", NUM_EUR),
        ("VAN (EUR)", "=Rezultate!C12", "=C57", NUM_EUR),
        ("RIR", "=Rezultate!C13", "=C58", NUM_PCT),
        ("Termen de recuperare (ani)", "=Rezultate!C14", "=C59", NUM_INT),
    ]
    r = 63
    for name, eur_formula, china_formula, fmt in rows:
        label(ws, r, name)
        val(ws, r, 3, eur_formula, numfmt=fmt)
        val(ws, r, 4, china_formula, numfmt=fmt)
        val(ws, r, 5, f"=D{r}-C{r}", numfmt=fmt)
        r += 1

    # Avertisment
    ws.cell(row=r + 1, column=2, value="AVERTISMENT").font = F_WARN
    ws.cell(row=r + 2, column=2, value=(
        "Reperul de cost China e o valoare de piață generală (BNEF/Ember 2025-2026), NU o ofertă pentru acest "
        "proiect -- exact ca reperul Europa din Ipoteze. Diferența rezultată arată cât de sensibil e proiectul "
        "la costul unitar de echipamente, nu o recomandare de furnizor."
    )).font = F_LABEL
    ws.cell(row=r + 3, column=2, value=(
        "Taxe vamale/antidumping UE la celule și module LFP din China, certificarea CE, transportul și costul "
        "de service local pe durata de 15 ani a analizei NU sunt incluse în acest reper și pot reduce semnificativ "
        "avantajul de cost aparent. Verifică și eventuale cerințe de origine a echipamentelor din ghidul apelului."
    )).font = F_LABEL

    # openpyxl nu poate scrie valori cache langa formule -- fara acest flag,
    # fisierul ar afisa celule goale in orice program care citeste valori
    # cache fara sa recalculeze (ex: pandas, preview-uri). Cu flagul setat,
    # Excel/LibreOffice recalculeaza automat tot fisierul la prima deschidere.
    wb.calculation = CalcProperties(fullCalcOnLoad=True)

    wb.save(MODEL_PATH)
    print(f"Foaie 'ScenariuChina' scrisa in {MODEL_PATH}")
    print("Recalculare fortata la deschidere (fullCalcOnLoad) activata pentru tot fisierul.")


if __name__ == "__main__":
    main()
