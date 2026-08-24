#!/usr/bin/env python3
"""Extrage indicatorii cheie din modelul financiar (.xlsx) intr-un JSON intermediar.

Ruleaza dupa fiecare modificare a model/model_financiar.xlsx, inainte de fill_docx.py.
Foloseste valorile CACHED din fisier (data_only=True) -- daca modelul a fost editat
manual si nu a fost recalculat de Excel/LibreOffice, ruleaza intai:
    python3 scripts/office/soffice.py --headless --convert-to xlsx --outdir model model/model_financiar.xlsx
sau orice alta metoda de recalculare, altfel valorile citite pot fi vechi (None).
"""
import json
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "model" / "model_financiar.xlsx"
OUT_PATH = ROOT / "data" / "model_values.json"

# Harta valorilor de interes pentru studiul de fezabilitate: cheie -> (foaie, celula)
CELLS = {
    "capacitate_mwh": ("Ipoteze", "C12"),
    "putere_mw": ("Ipoteze", "C14"),
    "durata_stocare_ore": ("Ipoteze", "C13"),
    "capex_total_eur": ("Rezultate", "C5"),
    "capex_unitar_eur_mwh": ("Rezultate", "C6"),
    "capex_eligibil_eur": ("CAPEX", "C17"),
    "capex_linie_racord_eur": ("CAPEX", "C7"),
    "capex_statie_conexiune_eur": ("CAPEX", "C8"),
    "capex_constructii_civile_eur": ("CAPEX", "C10"),
    "capex_sisteme_siguranta_eur": ("CAPEX", "C11"),
    "energie_descarcata_an1_mwh": ("CashFlow", "D7"),
    "grant_eur": ("Rezultate", "C7"),
    "contributie_proprie_eur": ("Rezultate", "C8"),
    "pondere_grant": ("Rezultate", "C9"),
    "ebitda_an1_eur": ("Rezultate", "C11"),
    "van_eur": ("Rezultate", "C12"),
    "rir": ("Rezultate", "C13"),
    "payback_ani": ("Rezultate", "C14"),
}


def main():
    if not MODEL_PATH.exists():
        sys.exit(f"Nu gasesc modelul financiar la {MODEL_PATH}")

    wb = openpyxl.load_workbook(MODEL_PATH, data_only=True)

    values = {}
    missing = []
    for key, (sheet, coord) in CELLS.items():
        if sheet not in wb.sheetnames:
            missing.append(f"{key}: foaia {sheet} nu exista")
            continue
        v = wb[sheet][coord].value
        if v is None:
            missing.append(f"{key}: {sheet}!{coord} este gol (recalculeaza fisierul .xlsx)")
        values[key] = v

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(values, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Scris {OUT_PATH} cu {len(values)} valori.")
    if missing:
        print("ATENTIE, valori lipsa sau negasite:")
        for m in missing:
            print(f"  - {m}")


if __name__ == "__main__":
    main()
