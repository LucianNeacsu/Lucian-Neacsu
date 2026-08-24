#!/usr/bin/env bash
# Workflow complet: recalculeaza modelul financiar, extrage indicatorii,
# genereaza draftul de Studiu de Fezabilitate completat.
#
# Ruleaza de fiecare data cand model/model_financiar.xlsx se schimba
# (ipoteze noi, oferte reale, cost de racordare actualizat etc.).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "1/3 Recalculez modelul financiar (LibreOffice, best-effort)..."
TMP_OUT="$(mktemp -d)"
if timeout 90 soffice --headless --convert-to xlsx --outdir "$TMP_OUT" model/model_financiar.xlsx >/dev/null 2>&1 \
    && [ -f "$TMP_OUT/model_financiar.xlsx" ]; then
    cp "$TMP_OUT/model_financiar.xlsx" model/model_financiar.xlsx
else
    echo "ATENTIE: recalcularea automata a esuat sau LibreOffice e indisponibil." >&2
    echo "Continui cu valorile deja salvate (cached) in fisier." >&2
    echo "Daca ai editat manual celulele galbene din Ipoteze, deschide si salveaza" >&2
    echo "model_financiar.xlsx in Excel/LibreOffice inainte de a rula acest script," >&2
    echo "ca formulele sa aiba valori proaspete." >&2
fi
rm -rf "$TMP_OUT"

echo "2/3 Extrag indicatorii din model..."
python3 scripts/extract_model.py

echo "3/3 Generez draftul de Studiu de Fezabilitate completat..."
python3 scripts/fill_docx.py

echo "Gata. Document: output/SF_Cramele_Odobesti_BESS.docx"
