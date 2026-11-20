"""Schreibt Objekte sicher in das Blatt Pipeline, ohne Formeln zu zerstoeren.

Beispiele:
  python3 tools/pipeline.py liste
  python3 tools/pipeline.py neu '{"quelle":"https://...","stadt":"Passau","typ":"ETW","nutzung":"Vermietung","baujahr":1995,"wfl":68,"kaufpreis":219000,"miete":780,"hg_nu":95}'
  python3 tools/pipeline.py setze 4 '{"standortnote":4,"status":"In Prüfung","begruendung":"..."}'

Agenten duerfen NUR ueber dieses Skript in die Pipeline schreiben.
Berechnete Spalten (gruen) werden beim Oeffnen in Excel/LibreOffice aktualisiert.
"""

import datetime
import json
import sys

from openpyxl import load_workbook

DATEI = "Immobilien-Investor.xlsx"
ERSTE, LETZTE = 3, 202
# nur Eingabespalten – berechnete Spalten werden nie beschrieben
SPALTEN = {
    "id": 1, "datum": 2, "quelle": 3, "stadt": 4, "stadtteil": 5, "typ": 6, "nutzung": 7,
    "baujahr": 8, "wfl": 9, "kaufpreis": 10, "miete": 11, "hg_nu": 12,
    "standortnote": 19, "status": 21, "begruendung": 23, "doppelt": 24,
}


def laden():
    return load_workbook(DATEI)


def zeilen(ws):
    for r in range(ERSTE, LETZTE + 1):
        if ws.cell(r, 3).value or ws.cell(r, 10).value:
            yield r


def duplikat(ws, neu):
    """Gleiche Stadt, Wohnflaeche +-2 m², Kaufpreis +-5 % oder gleicher Link."""
    for r in zeilen(ws):
        if neu.get("quelle") and ws.cell(r, 3).value == neu["quelle"]:
            return ws.cell(r, 1).value
        try:
            if (ws.cell(r, 4).value == neu.get("stadt")
                    and abs(float(ws.cell(r, 9).value) - float(neu["wfl"])) <= 2
                    and abs(float(ws.cell(r, 10).value) - float(neu["kaufpreis"])) <= 0.05 * float(neu["kaufpreis"])):
                return ws.cell(r, 1).value
        except (TypeError, ValueError, KeyError):
            continue
    return None


def neu(daten):
    wb = laden()
    ws = wb["Pipeline"]
    belegt = list(zeilen(ws))
    frei = next((r for r in range(ERSTE, LETZTE + 1) if r not in belegt), None)
    if frei is None:
        sys.exit("Pipeline voll – erledigte Objekte archivieren.")
    dup = duplikat(ws, daten)
    daten.setdefault("id", f"O{frei - 2:03d}")
    daten.setdefault("datum", datetime.date.today())
    daten.setdefault("status", "Neu")
    if dup:
        daten["doppelt"] = dup
    for k, v in daten.items():
        if k not in SPALTEN:
            sys.exit(f"Unbekanntes Feld: {k}. Erlaubt: {', '.join(SPALTEN)}")
        ws.cell(frei, SPALTEN[k], v)
    wb.save(DATEI)
    print(f"Zeile {frei}, ID {daten['id']}" + (f" – MÖGLICHES DUPLIKAT von {dup}" if dup else ""))


def setze(zeile, daten):
    wb = laden()
    ws = wb["Pipeline"]
    for k, v in daten.items():
        if k not in SPALTEN or k == "id":
            sys.exit(f"Feld nicht änderbar: {k}")
        ws.cell(int(zeile), SPALTEN[k], v)
    wb.save(DATEI)
    print("aktualisiert:", zeile)


def liste():
    ws = laden()["Pipeline"]
    for r in zeilen(ws):
        werte = {k: ws.cell(r, c).value for k, c in SPALTEN.items()}
        print(r, json.dumps(werte, default=str, ensure_ascii=False))


if __name__ == "__main__":
    befehl = sys.argv[1] if len(sys.argv) > 1 else "liste"
    if befehl == "liste":
        liste()
    elif befehl == "neu":
        neu(json.loads(sys.argv[2]))
    elif befehl == "setze":
        setze(sys.argv[2], json.loads(sys.argv[3]))
    else:
        sys.exit(__doc__)
