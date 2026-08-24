#!/usr/bin/env python3
"""Genereaza draftul de Studiu de Fezabilitate cu indicatorii din modelul financiar.

Citeste data/model_values.json (produs de extract_model.py) si completeaza,
in templates/SF_ciorna_template.docx, DOAR celulele din tabelul "Principalii
indicatori tehnico-economici" (capitolul V.4) marcate cu "[DE COMPLETAT ...]".

Nu atinge niciodata:
  - placeholderele "[DE COMPLETAT DE PROIECTANT]" sau "[ÎN SARCINA PROIECTANTULUI]"
    (rezervate legal proiectantului atestat);
  - placeholderele "[DE VERIFICAT ...]" (verificari normative, nu valori de calcul);
  - orice alta celula/paragraf din document.

Fiecare valoare inserata este marcata explicit ca provizorie ("valoare de test,
model parametric"), in aceeasi logica de avertizare pe care o foloseste deja
documentul original -- vezi cap. IV.6 din ciorna: rezultatele cu valori de test
nu au valoare de prognoza si nu se depun ca atare.

Iesire: output/SF_Cramele_Odobesti_BESS.docx
"""
import json
import sys
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "templates" / "SF_ciorna_template.docx"
VALUES_PATH = ROOT / "data" / "model_values.json"
OUT_PATH = ROOT / "output" / "SF_Cramele_Odobesti_BESS.docx"

TEST_NOTE = "valoare de test, model parametric — a se recalcula cu date reale"


def fmt_eur(x):
    return f"{round(x):,}".replace(",", ".") + " EUR"


def fmt_mwh(x):
    return f"{round(x):,}".replace(",", ".") + " MWh"


def fmt_pct(x):
    return f"{x * 100:.2f}".replace(".", ",") + " %"


def fmt_years(x):
    return f"{x:.1f}".replace(".", ",") + " ani"


def build_replacements(v):
    capex_cm_aprox = (
        v["capex_linie_racord_eur"]
        + v["capex_statie_conexiune_eur"]
        + v["capex_constructii_civile_eur"]
        + v["capex_sisteme_siguranta_eur"]
    )
    return {
        "Valoarea totală a investiției, inclusiv TVA": (
            f"{fmt_eur(v['capex_total_eur'])}, fără TVA (modelul nu calculează TVA) — "
            f"estimare parametrică din modelul financiar, NU deviz general ({TEST_NOTE})"
        ),
        "din care construcții-montaj": (
            f"{fmt_eur(capex_cm_aprox)} — aproximare parametrică "
            "(linie de racord + stație de conexiune + construcții civile + sisteme de siguranță); "
            "necesită devizul pe obiecte pentru valoarea exactă"
        ),
        "Energie descărcată anual": (
            f"{fmt_mwh(v['energie_descarcata_an1_mwh'])} (anul 1 de exploatare) — {TEST_NOTE}"
        ),
        "Valoarea actualizată netă": f"{fmt_eur(v['van_eur'])} — {TEST_NOTE}",
        "Rata internă de rentabilitate": f"{fmt_pct(v['rir'])} — {TEST_NOTE}",
        "Termen de recuperare": f"{fmt_years(v['payback_ani'])} — {TEST_NOTE}",
    }


def is_fillable_placeholder(text):
    t = text.strip()
    if not t.startswith("[DE COMPLETAT"):
        return False
    if "DE PROIECTANT" in t:
        return False
    return True


def main():
    if not VALUES_PATH.exists():
        sys.exit(f"Nu gasesc {VALUES_PATH}. Ruleaza intai extract_model.py.")
    values = json.loads(VALUES_PATH.read_text(encoding="utf-8"))
    replacements = build_replacements(values)

    d = docx.Document(TEMPLATE_PATH)

    target_table = None
    for t in d.tables:
        header = [c.text.strip() for c in t.rows[0].cells]
        if header[:2] == ["Indicator", "Valoare"]:
            target_table = t
            break
    if target_table is None:
        sys.exit("Nu gasesc tabelul 'Indicator / Valoare' (cap. V.4) in template.")

    filled, skipped = [], []
    for row in target_table.rows[1:]:
        label = row.cells[0].text.strip()
        value_cell = row.cells[1]
        current_text = value_cell.text.strip()

        if label in replacements:
            if not is_fillable_placeholder(current_text):
                skipped.append((label, "nu mai e placeholder needitabil, nu suprascriu"))
                continue
            new_text = replacements[label]
            para = value_cell.paragraphs[0]
            if para.runs:
                para.runs[0].text = new_text
                for extra in para.runs[1:]:
                    extra.text = ""
            else:
                para.add_run(new_text)
            filled.append(label)
        elif is_fillable_placeholder(current_text):
            skipped.append((label, "placeholder rezervat proiectantului sau fara sursa in model"))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    d.save(OUT_PATH)

    print(f"Salvat {OUT_PATH}")
    print(f"Completate {len(filled)} celule: {filled}")
    print(f"Lasate neatinse {len(skipped)} celule:")
    for label, reason in skipped:
        print(f"  - {label}: {reason}")


if __name__ == "__main__":
    main()
