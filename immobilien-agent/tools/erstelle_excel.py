"""Erzeugt die Arbeitsmappe Immobilien-Investor.xlsx.

Die Mappe ist die gemeinsame Datenbasis fuer dich und die Agenten:
  Profil       - deine Strategie und Grenzwerte
  Marktdaten   - Kaufnebenkosten und Marktwerte je Stadt
  Objektanalyse- Detailrechner fuer EIN Objekt (Kauf / Nicht-Kauf)
  Pipeline     - alle gefundenen Objekte mit Schnellbewertung (Rangliste)
  Bestand      - deine Immobilien im Ueberblick
  Ausgaben     - jede Ausgabe je Objekt (fliesst in den Bestand)
  Kostenkatalog- alle Kostenpositionen mit Erklaerung und Steuerhinweis
  Kennzahlen   - Formeln, Bedeutung und Richtwerte

Aufruf:  python3 tools/erstelle_excel.py [Zieldatei]
"""

import sys
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ZIEL = sys.argv[1] if len(sys.argv) > 1 else "Immobilien-Investor.xlsx"

# ---------- Stil ----------
F_TITEL = Font(bold=True, size=14, color="FFFFFF")
F_KOPF = Font(bold=True, color="FFFFFF")
F_FETT = Font(bold=True)
F_HINWEIS = Font(italic=True, color="666666", size=9)
FILL_TITEL = PatternFill("solid", fgColor="1F3864")
FILL_KOPF = PatternFill("solid", fgColor="2F5496")
FILL_EINGABE = PatternFill("solid", fgColor="FFF2CC")  # gelb = Eingabe
FILL_ERGEBNIS = PatternFill("solid", fgColor="E2EFDA")  # gruen = Ergebnis
FILL_ABSCHNITT = PatternFill("solid", fgColor="D9E1F2")
ROT = PatternFill("solid", fgColor="F8CBAD")
GRUEN = PatternFill("solid", fgColor="C6EFCE")
GELB = PatternFill("solid", fgColor="FFEB9C")
DUENN = Side(style="thin", color="BFBFBF")
RAHMEN = Border(left=DUENN, right=DUENN, top=DUENN, bottom=DUENN)
WRAP = Alignment(wrap_text=True, vertical="top")

EUR = '#,##0 "€";[Red]-#,##0 "€"'
EUR2 = '#,##0.00 "€";[Red]-#,##0.00 "€"'
PROZ = "0.00%"
ZAHL1 = "0.0"
DATUM = "DD.MM.YYYY"


def titel(ws, text, breite):
    ws["A1"] = text
    ws["A1"].font = F_TITEL
    ws["A1"].fill = FILL_TITEL
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=breite)
    ws.row_dimensions[1].height = 24


def kopfzeile(ws, zeile, werte):
    for i, w in enumerate(werte, start=1):
        c = ws.cell(row=zeile, column=i, value=w)
        c.font = F_KOPF
        c.fill = FILL_KOPF
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = RAHMEN
    ws.row_dimensions[zeile].height = 32


def breiten(ws, liste):
    for i, b in enumerate(liste, start=1):
        ws.column_dimensions[get_column_letter(i)].width = b


wb = Workbook()

# =====================================================================
# 1. Anleitung
# =====================================================================
ws = wb.active
ws.title = "Anleitung"
titel(ws, "Immobilien-Investor – Arbeitsmappe", 2)
anleitung = [
    ("Farben", "Gelb = deine Eingabe. Grün = wird berechnet, nicht überschreiben."),
    ("1. Profil", "Einmal ausfüllen: Einkommen, Eigenkapital, Steuersatz, Zielwerte. Alle Blätter rechnen damit."),
    ("2. Marktdaten", "Kaufnebenkosten je Stadt sind vorbelegt. Marktpreise/Mieten füllt der Standort-Agent (mit Quelle und Datum)."),
    ("3. Pipeline", "Jedes gefundene Objekt = eine Zeile. Schnellbewertung und Rangliste. Der Objekt-Scout trägt hier ein."),
    ("4. Objektanalyse", "Für die besten Objekte aus der Pipeline: Detailrechnung mit Steuer, Stresstest und Empfehlung."),
    ("5. Bestand", "Deine gekauften Immobilien. Investitionen und laufende Kosten kommen automatisch aus dem Blatt Ausgaben."),
    ("6. Ausgaben", "Jede Rechnung/Ausgabe mit Objektname eintragen. Objektname muss exakt wie im Bestand geschrieben sein."),
    ("7. Kostenkatalog", "Alle Kostenpositionen eines Immobilieninvestors: wer zahlt, umlagefähig, steuerlich absetzbar."),
    ("8. Kennzahlen", "Was jede Kennzahl bedeutet und welcher Wert gut ist."),
    ("Wichtig", "Steuerliche Hinweise sind vereinfacht und ersetzen keine Steuerberatung. Richtwerte vor Entscheidungen prüfen."),
]
for i, (a, b) in enumerate(anleitung, start=3):
    ws.cell(row=i, column=1, value=a).font = F_FETT
    ws.cell(row=i, column=2, value=b).alignment = WRAP
breiten(ws, [18, 110])

# =====================================================================
# 2. Profil
# =====================================================================
pr = wb.create_sheet("Profil")
titel(pr, "Investorprofil und Grenzwerte", 3)
profil = [
    # key, label, wert, format, hinweis
    ("netto", "Haushaltsnettoeinkommen pro Monat", 0, EUR, "Für Belastungsquote bei Eigennutzung und Bankprüfung"),
    ("ek", "Verfügbares Eigenkapital (frei)", 0, EUR, "Nur Geld, das du wirklich einsetzen kannst; Notreserve abziehen"),
    ("reserve", "Notreserve, die nicht angetastet wird", 0, EUR, "Faustregel: 3–6 Monatsausgaben + Reserve je Objekt"),
    ("steuer", "Persönlicher Grenzsteuersatz (inkl. Soli/KiSt)", 0.42, PROZ, "Vom Steuerbescheid / Steuerberater"),
    ("zins", "Standard-Sollzins für Schnellrechnung", 0.04, PROZ, "Vollfinanzierung (100 % Kaufpreis) kostet meist einen Aufschlag – aktuell vom Finanzierungs-Agenten aktualisieren lassen"),
    ("tilg", "Standard-Anfangstilgung", 0.02, PROZ, "Höher = schneller schuldenfrei, aber höhere Rate"),
    ("instand", "Instandhaltung Sondereigentum (€/m²/Jahr)", 12, EUR2, "Faustregel 8–15 €/m²/Jahr, Altbau eher oben"),
    ("ausfall", "Mietausfallwagnis (% der Jahreskaltmiete)", 0.03, PROZ, "2–4 % üblich"),
    ("max_kpf", "Zielwert: max. Kaufpreisfaktor (Vermietung)", 25, ZAHL1, "Kaufpreis ÷ Jahreskaltmiete; je niedriger, desto besser"),
    ("min_rendite", "Zielwert: min. Bruttomietrendite", 0.04, PROZ, "Jahreskaltmiete ÷ Kaufpreis"),
    ("min_cf", "Zielwert: min. Cashflow nach Steuern pro Monat", 0, EUR, "0 = Objekt trägt sich selbst"),
    ("max_belastung", "Zielwert: max. Belastungsquote (Eigennutzung)", 0.35, PROZ, "Rate + Kosten ÷ Haushaltsnetto"),
    ("stress", "Stresstest: Zinsanstieg bei Anschlussfinanzierung", 0.02, PROZ, "Wie gut verträgt das Objekt +2 Prozentpunkte?"),
]
P = {}
kopfzeile(pr, 2, ["Eingabe", "Wert", "Hinweis"])
for i, (k, lab, wert, fmt, hin) in enumerate(profil, start=3):
    pr.cell(row=i, column=1, value=lab).border = RAHMEN
    c = pr.cell(row=i, column=2, value=wert)
    c.number_format = fmt
    c.fill = FILL_EINGABE
    c.border = RAHMEN
    h = pr.cell(row=i, column=3, value=hin)
    h.font = F_HINWEIS
    h.alignment = WRAP
    P[k] = f"Profil!$B${i}"
r = len(profil) + 4
pr.cell(row=r, column=1, value="Strategie").font = F_FETT
pr.cell(row=r, column=2, value="Kaufpreis zu 100 % finanziert, Kaufnebenkosten aus Eigenkapital. Mix aus Eigennutzung und Vermietung.").alignment = WRAP
pr.cell(row=r + 1, column=1, value="Zielregionen").font = F_FETT
pr.cell(row=r + 1, column=2, value="Passau, München, Münster (NRW)")
breiten(pr, [48, 22, 80])

# =====================================================================
# 3. Marktdaten
# =====================================================================
md = wb.create_sheet("Marktdaten")
titel(md, "Marktdaten je Stadt – Kaufnebenkosten und Marktwerte", 12)
kopfzeile(md, 2, [
    "Stadt", "Bundesland", "Grunderwerbsteuer", "Makler Käuferanteil (typ.)",
    "Notar + Grundbuch (typ.)", "Kaufpreis ETW €/m² (Bestand)", "Kaltmiete €/m² (Bestand)",
    "Mietpreisbremse?", "Bevölkerungstrend", "Leerstand", "Quelle", "Stand",
])
staedte = [
    ("Passau", "Bayern", 0.035),
    ("München", "Bayern", 0.035),
    ("Münster", "Nordrhein-Westfalen", 0.065),
]
for i, (s, bl, grest) in enumerate(staedte, start=3):
    werte = [s, bl, grest, 0.0357, 0.02, None, None, "prüfen", None, None,
             "GrESt: Landesrecht; Rest: Standort-Agent", None]
    for j, w in enumerate(werte, start=1):
        c = md.cell(row=i, column=j, value=w)
        c.border = RAHMEN
        if j in (3, 4, 5, 10):
            c.number_format = PROZ
        if j in (6, 7):
            c.number_format = EUR2
        if j >= 4:
            c.fill = FILL_EINGABE
    md.cell(row=i, column=12).number_format = DATUM
md.cell(row=7, column=1, value="Hinweise").font = F_FETT
for i, t in enumerate([
    "Grunderwerbsteuer Bayern 3,5 %, NRW 6,5 % (Stand Erstellung – bei Gesetzesänderung anpassen).",
    "Makler: 3,57 % inkl. MwSt. ist ein üblicher Käuferanteil, aber verhandelbar. Bei Wohnung/Einfamilienhaus an Privatkäufer gilt die Halbteilung (§ 656c BGB).",
    "Notar ca. 1,0–1,5 %, Grundbuch ca. 0,5 %. Zusammen meist ~2 %.",
    "Spalten F–J werden vom Standort-Agenten mit Quelle und Datum befüllt (Gutachterausschuss, Mietspiegel, Destatis, Zensus).",
], start=8):
    md.cell(row=i, column=1, value=t).font = F_HINWEIS
breiten(md, [12, 20, 14, 14, 14, 16, 16, 14, 18, 10, 34, 12])

MD_BEREICH = "Marktdaten!$A$3:$E$5"

# =====================================================================
# 4. Objektanalyse
# =====================================================================
oa = wb.create_sheet("Objektanalyse")
titel(oa, "Objektanalyse – Detailrechnung für ein Objekt", 3)
oa["A2"] = "Gelbe Felder ausfüllen. Bei Eigennutzung bei 'Kaltmiete' die Miete eintragen, die du sonst für eine vergleichbare Wohnung zahlen würdest."
oa["A2"].font = F_HINWEIS
oa.merge_cells("A2:C2")

O = {}
zeile = [3]


def abschnitt(text):
    zeile[0] += 1
    c = oa.cell(row=zeile[0], column=1, value=text)
    c.font = F_FETT
    for col in (1, 2, 3):
        oa.cell(row=zeile[0], column=col).fill = FILL_ABSCHNITT


def feld(key, label, wert, fmt=None, eingabe=False, hinweis=None):
    zeile[0] += 1
    r = zeile[0]
    oa.cell(row=r, column=1, value=label).border = RAHMEN
    c = oa.cell(row=r, column=2, value=wert)
    c.border = RAHMEN
    c.fill = FILL_EINGABE if eingabe else FILL_ERGEBNIS
    if fmt:
        c.number_format = fmt
    if hinweis:
        h = oa.cell(row=r, column=3, value=hinweis)
        h.font = F_HINWEIS
        h.alignment = WRAP
    O[key] = f"$B${r}"
    return O[key]


def f(text):
    """Ersetzt {key} durch Zellbezüge (Objektanalyse) bzw. {p:key} durch Profil."""
    out = text
    for k, v in P.items():
        out = out.replace("{p:" + k + "}", v)
    for k, v in O.items():
        out = out.replace("{" + k + "}", v)
    return "=" + out


abschnitt("Objekt")
feld("name", "Objektname / Link", "", eingabe=True)
feld("stadt", "Stadt", "Passau", eingabe=True, hinweis="Passau, München oder Münster (steuert Grunderwerbsteuer)")
feld("nutzung", "Nutzung", "Vermietung", eingabe=True, hinweis="Vermietung oder Eigennutzung")
feld("kp", "Kaufpreis", 0, EUR, True)
feld("wfl", "Wohnfläche (m²)", 0, ZAHL1, True)
feld("baujahr", "Baujahr", 1990, "0", True, "Steuert den AfA-Satz")
feld("boden", "Bodenanteil am Kaufpreis", 0.25, PROZ, True, "Boden wird nicht abgeschrieben. Großstadt oft 30–50 %, Wohnung in Passau eher 15–30 %. BMF-Arbeitshilfe nutzen")
feld("miete", "Kaltmiete pro Monat (Ist/Markt bzw. Vergleichsmiete)", 0, EUR, True)
feld("hg_ges", "Hausgeld gesamt pro Monat", 0, EUR, True, "Bei Haus: alle laufenden Bewirtschaftungskosten")
feld("hg_nu", "davon nicht umlagefähig pro Monat", 0, EUR, True, "Verwaltung, Erhaltungsrücklage, Kontogebühren – steht in der Hausgeldabrechnung")
feld("san", "Sanierung / Modernisierung direkt nach Kauf", 0, EUR, True)
feld("san_ek", "Sanierung aus Eigenkapital? (1 = ja, 0 = mitfinanzieren)", 1, "0", True)

abschnitt("Kaufnebenkosten (aus Eigenkapital)")
feld("q_grest", "Grunderwerbsteuer-Satz", f("IFERROR(VLOOKUP({stadt},%s,3,FALSE),0.065)" % MD_BEREICH), PROZ, hinweis="Aus Blatt Marktdaten")
feld("q_makler", "Maklerprovision-Satz", f("IFERROR(VLOOKUP({stadt},%s,4,FALSE),0.0357)" % MD_BEREICH), PROZ, True, "Formel überschreibbar, z. B. 0 bei provisionsfrei")
feld("q_notar", "Notar + Grundbuch-Satz", f("IFERROR(VLOOKUP({stadt},%s,5,FALSE),0.02)" % MD_BEREICH), PROZ, True)
feld("grest", "Grunderwerbsteuer", f("{kp}*{q_grest}"), EUR)
feld("makler", "Maklerprovision", f("{kp}*{q_makler}"), EUR)
feld("notar", "Notar + Grundbuch", f("{kp}*{q_notar}"), EUR)
feld("knk", "Kaufnebenkosten gesamt", f("{grest}+{makler}+{notar}"), EUR)
feld("knk_q", "Kaufnebenkosten in % vom Kaufpreis", f("IF({kp}>0,{knk}/{kp},0)"), PROZ)
feld("ek_bedarf", "Eigenkapitalbedarf", f("{knk}+IF({san_ek}=1,{san},0)"), EUR)
feld("ek_ok", "Eigenkapital reicht (nach Notreserve)?", f('IF({ek_bedarf}<={p:ek}-{p:reserve},"JA","NEIN")'))

abschnitt("Finanzierung (100 % Kaufpreis)")
feld("zins", "Sollzins", f("{p:zins}"), PROZ, True, "Formel aus Profil, mit echtem Angebot überschreiben")
feld("tilg", "Anfangstilgung", f("{p:tilg}"), PROZ, True)
feld("bindung", "Zinsbindung (Jahre)", 15, "0", True)
feld("darlehen", "Darlehensbetrag", f("{kp}+IF({san_ek}=1,0,{san})"), EUR)
feld("ltv", "Beleihungsauslauf (Darlehen ÷ Kaufpreis)", f("IF({kp}>0,{darlehen}/{kp},0)"), PROZ, hinweis="Über 100 %: Banken prüfen Einkommen sehr streng")
feld("rate", "Monatsrate (Zins + Tilgung)", f("{darlehen}*({zins}+{tilg})/12"), EUR2)
feld("zins_j1", "Zinsanteil im 1. Jahr (ca.)", f("{darlehen}*{zins}"), EUR)
feld("tilg_j1", "Tilgung im 1. Jahr (ca.)", f("{darlehen}*{tilg}"), EUR)
feld("rest", "Restschuld am Ende der Zinsbindung", f("IF({darlehen}>0,MAX(0,-FV({zins}/12,{bindung}*12,-{rate},{darlehen})),0)"), EUR)

abschnitt("Laufende Kosten und Kennzahlen")
feld("instand", "Instandhaltung Sondereigentum pro Monat", f("{wfl}*{p:instand}/12"), EUR2)
feld("ausfall", "Mietausfallwagnis pro Monat", f('IF({nutzung}="Vermietung",{miete}*{p:ausfall},0)'), EUR2)
feld("kosten", "Bewirtschaftungskosten, die du trägst, pro Monat", f('IF({nutzung}="Vermietung",{hg_nu},{hg_ges})+{instand}+{ausfall}'), EUR2, hinweis="Vermietung: nur nicht umlagefähige. Eigennutzung: alles")
feld("qm_preis", "Kaufpreis pro m²", f("IF({wfl}>0,{kp}/{wfl},0)"), EUR)
feld("kpf", "Kaufpreisfaktor", f("IF({miete}>0,{kp}/({miete}*12),0)"), ZAHL1, hinweis="Unter 20 sehr gut, 20–25 ok, über 30 teuer")
feld("brutto", "Bruttomietrendite", f("IF({kp}>0,{miete}*12/{kp},0)"), PROZ)
feld("netto_r", "Nettomietrendite (auf Gesamtinvest)", f("IF({kp}>0,({miete}*12-({hg_nu}+{instand}+{ausfall})*12)/({kp}+{knk}+{san}),0)"), PROZ)

abschnitt("Steuer (nur Vermietung, vereinfacht 1. Jahr)")
feld("afa_satz", "AfA-Satz", f("IF({baujahr}<1925,0.025,IF({baujahr}>=2023,0.03,0.02))"), PROZ, True, "Neubau mit Baubeginn ab 10/2023: evtl. 5 % degressiv – Steuerberater")
feld("afa", "Abschreibung (AfA) pro Jahr", f("({kp}+{knk})*(1-{boden})*{afa_satz}"), EUR)
feld("ergebnis", "Steuerliches Ergebnis pro Jahr", f('IF({nutzung}="Vermietung",{miete}*12-{zins_j1}-{hg_nu}*12-{afa},0)'), EUR, hinweis="Erhaltungsrücklage erst absetzbar, wenn die WEG sie ausgibt – hier vereinfacht")
feld("steuer", "Steuereffekt pro Jahr (+ = Erstattung)", f("-{ergebnis}*{p:steuer}"), EUR)

abschnitt("Ergebnis")
feld("cf_vor", "Saldo pro Monat vor Steuern", f("{miete}-{kosten}-{rate}"), EUR2, hinweis="Vermietung: Cashflow. Eigennutzung: gesparte Miete minus Kosten")
feld("cf_nach", "Cashflow pro Monat nach Steuern", f("{cf_vor}+{steuer}/12"), EUR2)
feld("belastung", "Monatliche Belastung (Eigennutzung)", f('IF({nutzung}="Eigennutzung",{rate}+{kosten},0)'), EUR2)
feld("quote", "Belastungsquote (Eigennutzung)", f('IF(AND({nutzung}="Eigennutzung",{p:netto}>0),{belastung}/{p:netto},0)'), PROZ)
feld("ek_rendite", "Eigenkapitalrendite 1. Jahr (Cashflow + Tilgung)", f("IF({ek_bedarf}>0,({cf_nach}*12+{tilg_j1})/{ek_bedarf},0)"), PROZ, hinweis="Ohne Wertsteigerung")
feld("stress_rate", "Stresstest: Rate nach Zinsbindung bei Zins + Aufschlag", f("{rest}*({zins}+{p:stress}+{tilg})/12"), EUR2)
feld("stress_cf", "Stresstest: Saldo vor Steuern danach", f("{miete}-{kosten}-{stress_rate}"), EUR2, hinweis="Miete heute angesetzt – Mietsteigerungen nicht eingerechnet")
feld("max_kp", "Verhandlungsziel: max. Kaufpreis für Ziel-Kaufpreisfaktor", f("{miete}*12*{p:max_kpf}"), EUR)

abschnitt("Empfehlung")
krit_v = f(
    '({kpf}>{p:max_kpf})+({brutto}<{p:min_rendite})+({cf_nach}<{p:min_cf})+({ek_ok}="NEIN")'
)
krit_e = f('({quote}>{p:max_belastung})+({ek_ok}="NEIN")+({stress_cf}<-{p:netto}*0.1)')
feld("fehler", "Anzahl verfehlter Kriterien",
     "=IF(" + O["kp"] + "=0,\"\",IF(" + O["nutzung"] + "=\"Vermietung\"," + krit_v[1:] + "," + krit_e[1:] + "))", "0")
feld("urteil", "Empfehlung", f('IF({fehler}="","– Daten fehlen –",IF({fehler}=0,"KAUF PRÜFEN – Besichtigung + Finanzierungsanfrage",IF({fehler}=1,"NACHVERHANDELN – Preis Richtung Verhandlungsziel","NICHT KAUFEN")))'))
oa.cell(row=zeile[0] + 2, column=1, value=(
    "Kriterien Vermietung: Kaufpreisfaktor ≤ Ziel, Bruttorendite ≥ Ziel, Cashflow nach Steuern ≥ Ziel, Eigenkapital reicht. "
    "Kriterien Eigennutzung: Belastungsquote ≤ Ziel, Eigenkapital reicht, Stresstest-Saldo nicht schlechter als −10 % des Nettoeinkommens. "
    "Das Ergebnis ist eine Rechenhilfe, keine Anlageberatung."
)).font = F_HINWEIS
oa.merge_cells(start_row=zeile[0] + 2, start_column=1, end_row=zeile[0] + 2, end_column=3)
oa.cell(row=zeile[0] + 2, column=1).alignment = WRAP
oa.row_dimensions[zeile[0] + 2].height = 45

dv_stadt = DataValidation(type="list", formula1="=Marktdaten!$A$3:$A$5", allow_blank=True)
dv_nutz = DataValidation(type="list", formula1='"Vermietung,Eigennutzung"', allow_blank=False)
oa.add_data_validation(dv_stadt)
oa.add_data_validation(dv_nutz)
dv_stadt.add(O["stadt"].replace("$", ""))
dv_nutz.add(O["nutzung"].replace("$", ""))

u = O["urteil"].replace("$", "")
oa.conditional_formatting.add(u, FormulaRule(formula=[f'LEFT({u},4)="KAUF"'], fill=GRUEN))
oa.conditional_formatting.add(u, FormulaRule(formula=[f'LEFT({u},4)="NACH"'], fill=GELB))
oa.conditional_formatting.add(u, FormulaRule(formula=[f'LEFT({u},5)="NICHT"'], fill=ROT))
for k in ("cf_vor", "cf_nach", "stress_cf"):
    oa.conditional_formatting.add(O[k].replace("$", ""), CellIsRule(operator="lessThan", formula=["0"], fill=ROT))
oa[O["urteil"].replace("$", "")].font = Font(bold=True, size=12)
breiten(oa, [55, 22, 70])

# =====================================================================
# 5. Pipeline
# =====================================================================
pl = wb.create_sheet("Pipeline")
titel(pl, "Pipeline – gefundene Objekte und Schnellbewertung (Rangliste nach Punkten sortieren)", 24)
pl_kopf = [
    "ID", "Gefunden am", "Quelle / Link", "Stadt", "Stadtteil", "Typ", "Nutzung geplant",
    "Baujahr", "Wohnfläche m²", "Kaufpreis", "Kaltmiete mtl. (Ist/Markt)", "Hausgeld nicht uml. mtl.",
    "€/m²", "Kaufpreisfaktor", "Bruttorendite", "Kaufnebenkosten (EK)", "Rate mtl. (100 %)",
    "Cashflow vor Steuern mtl.", "Standortnote 1–5", "Punkte (0–100)", "Status", "Schnellurteil",
    "Begründung (Berater)", "Doppelt? (ID)",
]
kopfzeile(pl, 2, pl_kopf)
for r in range(3, 203):
    md_lookup = lambda col: f"IFERROR(VLOOKUP(D{r},{MD_BEREICH},{col},FALSE),0)"
    formeln = {
        13: f'=IF(AND(I{r}>0,J{r}>0),J{r}/I{r},"")',
        14: f'=IF(AND(K{r}>0,J{r}>0),J{r}/(K{r}*12),"")',
        15: f'=IF(AND(K{r}>0,J{r}>0),K{r}*12/J{r},"")',
        16: f'=IF(J{r}>0,J{r}*({md_lookup(3)}+{md_lookup(4)}+{md_lookup(5)}),"")',
        17: f'=IF(J{r}>0,J{r}*({P["zins"]}+{P["tilg"]})/12,"")',
        18: f'=IF(J{r}>0,K{r}-L{r}-I{r}*{P["instand"]}/12-K{r}*{P["ausfall"]}-Q{r},"")',
        # Punkte: 40 Rendite (Kaufpreisfaktor), 30 Cashflow, 30 Standort
        20: (f'=IF(OR(J{r}="",J{r}=0,K{r}="",K{r}=0),"",ROUND('
             f'40*MAX(0,MIN(1,(35-N{r})/(35-{P["max_kpf"]}+5)))'
             f'+30*MAX(0,MIN(1,(R{r}+400)/600))'
             f'+IF(S{r}="",15,30*(S{r}-1)/4),0))'),
        22: (f'=IF(T{r}="","",IF(G{r}="Eigennutzung","→ Objektanalyse (Eigennutzung)",'
             f'IF(AND(N{r}<={P["max_kpf"]},R{r}>=-100),"Detailprüfung",IF(N{r}<={P["max_kpf"]}+5,"Nachverhandeln","Aussortieren"))))'),
    }
    for col in range(1, 25):
        c = pl.cell(row=r, column=col)
        c.border = RAHMEN
        if col in formeln:
            c.value = formeln[col]
            c.fill = FILL_ERGEBNIS
        else:
            c.fill = FILL_EINGABE
    pl.cell(row=r, column=2).number_format = DATUM
    for col in (10, 11, 12, 13, 16, 17, 18):
        pl.cell(row=r, column=col).number_format = EUR
    pl.cell(row=r, column=14).number_format = ZAHL1
    pl.cell(row=r, column=15).number_format = PROZ
    pl.cell(row=r, column=23).alignment = WRAP

dv_pl_stadt = DataValidation(type="list", formula1="=Marktdaten!$A$3:$A$5", allow_blank=True)
dv_pl_nutz = DataValidation(type="list", formula1='"Vermietung,Eigennutzung,offen"', allow_blank=True)
dv_pl_typ = DataValidation(type="list", formula1='"ETW,EFH,MFH,DHH,RH,Grundstück"', allow_blank=True)
dv_pl_status = DataValidation(type="list", formula1='"Neu,In Prüfung,Besichtigung,Finanzierungsanfrage,Angebot abgegeben,Abgelehnt,Gekauft"', allow_blank=True)
dv_pl_note = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
for dv, col in ((dv_pl_stadt, "D"), (dv_pl_nutz, "G"), (dv_pl_typ, "F"), (dv_pl_status, "U"), (dv_pl_note, "S")):
    pl.add_data_validation(dv)
    dv.add(f"{col}3:{col}202")
pl.conditional_formatting.add("R3:R202", CellIsRule(operator="lessThan", formula=["0"], fill=ROT))
pl.conditional_formatting.add("V3:V202", FormulaRule(formula=['V3="Detailprüfung"'], fill=GRUEN))
pl.conditional_formatting.add("V3:V202", FormulaRule(formula=['V3="Nachverhandeln"'], fill=GELB))
pl.conditional_formatting.add("V3:V202", FormulaRule(formula=['V3="Aussortieren"'], fill=ROT))
pl.freeze_panes = "D3"
pl.auto_filter.ref = "A2:X202"
breiten(pl, [8, 11, 30, 10, 14, 7, 13, 8, 9, 12, 12, 11, 9, 9, 9, 12, 11, 12, 9, 9, 16, 22, 45, 9])

# =====================================================================
# 6. Bestand
# =====================================================================
bs = wb.create_sheet("Bestand")
titel(bs, "Bestand – deine Immobilien und was du investiert hast", 26)
bs_kopf = [
    "Nr", "Objektname (eindeutig)", "Adresse", "Stadt", "Nutzung", "Kaufdatum", "Wohnfläche m²",
    "Kaufpreis", "Kaufnebenkosten", "Investitionen (aus Ausgaben)", "Gesamtinvestition",
    "Eigenkapital eingesetzt", "Darlehen ursprünglich", "Restschuld aktuell", "Sollzins",
    "Zinsbindung bis", "Rate mtl.", "Kaltmiete mtl.", "Nicht uml. Kosten mtl.", "Cashflow mtl. vor Steuern",
    "Marktwert geschätzt", "Nettovermögen (Wert − Schuld)", "Wertzuwachs (Wert − Invest)",
    "Bruttorendite auf Kaufpreis", "Laufende Kosten gesamt (aus Ausgaben)", "Spekulationsfrist endet",
]
kopfzeile(bs, 2, bs_kopf)
ERSTE, LETZTE = 3, 52
for r in range(ERSTE, LETZTE + 1):
    formeln = {
        1: f'=IF(B{r}="","",ROW()-2)',
        10: f'=IF(B{r}="","",SUMIFS(Ausgaben!$E:$E,Ausgaben!$B:$B,B{r},Ausgaben!$C:$C,"Investition*"))',
        11: f'=IF(B{r}="","",H{r}+I{r}+J{r})',
        20: f'=IF(B{r}="","",R{r}-S{r}-Q{r})',
        22: f'=IF(OR(B{r}="",U{r}=""),"",U{r}-N{r})',
        23: f'=IF(OR(B{r}="",U{r}=""),"",U{r}-K{r})',
        24: f'=IF(OR(B{r}="",H{r}=0,R{r}=0),"",R{r}*12/H{r})',
        25: f'=IF(B{r}="","",SUMIFS(Ausgaben!$E:$E,Ausgaben!$B:$B,B{r},Ausgaben!$C:$C,"Laufend*")+SUMIFS(Ausgaben!$E:$E,Ausgaben!$B:$B,B{r},Ausgaben!$C:$C,"Finanzierung*"))',
        26: f'=IF(OR(B{r}="",F{r}=""),"",EDATE(F{r},120))',
    }
    for col in range(1, 27):
        c = bs.cell(row=r, column=col)
        c.border = RAHMEN
        if col in formeln:
            c.value = formeln[col]
            c.fill = FILL_ERGEBNIS
        else:
            c.fill = FILL_EINGABE
    for col in (8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 25):
        bs.cell(row=r, column=col).number_format = EUR
    for col in (6, 16, 26):
        bs.cell(row=r, column=col).number_format = DATUM
    bs.cell(row=r, column=15).number_format = PROZ
    bs.cell(row=r, column=24).number_format = PROZ

# Beispielzeile
beispiel = {2: "BEISPIEL Passau ETW", 3: "Musterstraße 1, Passau", 4: "Passau", 5: "Vermietung",
            7: 60, 8: 200000, 9: 18000, 12: 18000, 13: 200000, 14: 196000, 15: 0.04,
            17: 1000, 18: 750, 19: 90, 21: 210000}
for col, w in beispiel.items():
    bs.cell(row=ERSTE, column=col, value=w)
bs.cell(row=ERSTE, column=6, value="=DATE(2025,1,15)")
bs.cell(row=ERSTE, column=16, value="=DATE(2040,1,31)")

S = LETZTE + 2
bs.cell(row=S, column=2, value="SUMME BESTAND").font = F_FETT
for col in (8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 25):
    L = get_column_letter(col)
    c = bs.cell(row=S, column=col, value=f"=SUM({L}{ERSTE}:{L}{LETZTE})")
    c.font = F_FETT
    c.number_format = EUR
    c.fill = FILL_ERGEBNIS
bs.cell(row=S + 1, column=2, value="Beleihungsauslauf gesamt (Restschuld ÷ Marktwert)").font = F_FETT
c = bs.cell(row=S + 1, column=14, value=f"=IF(U{S}>0,N{S}/U{S},\"\")")
c.number_format = PROZ
c.fill = FILL_ERGEBNIS
bs.cell(row=S + 2, column=2, value="Hinweis: Beispielzeile überschreiben oder löschen. Objektname muss im Blatt Ausgaben exakt gleich geschrieben werden.").font = F_HINWEIS

dv_bs_nutz = DataValidation(type="list", formula1='"Vermietung,Eigennutzung,Teilweise vermietet,Leerstand"', allow_blank=True)
bs.add_data_validation(dv_bs_nutz)
dv_bs_nutz.add(f"E{ERSTE}:E{LETZTE}")
bs.conditional_formatting.add(f"T{ERSTE}:T{LETZTE}", CellIsRule(operator="lessThan", formula=["0"], fill=ROT))
bs.conditional_formatting.add(f"T{ERSTE}:T{LETZTE}", CellIsRule(operator="greaterThan", formula=["0"], fill=GRUEN))
bs.conditional_formatting.add(
    f"P{ERSTE}:P{LETZTE}",
    FormulaRule(formula=[f'AND(P{ERSTE}<>"",P{ERSTE}-TODAY()<730)'], fill=GELB),
)
bs.freeze_panes = "C3"
breiten(bs, [5, 24, 26, 10, 14, 11, 9, 12, 12, 13, 13, 12, 13, 13, 8, 11, 10, 10, 10, 12, 13, 13, 13, 10, 13, 12])

# =====================================================================
# 7. Ausgaben
# =====================================================================
ag = wb.create_sheet("Ausgaben")
titel(ag, "Ausgaben je Objekt (Rechnungen, Belege)", 9)
kopfzeile(ag, 2, ["Datum", "Objektname (wie im Bestand)", "Art", "Kategorie / Position",
                  "Betrag (brutto)", "Auf Mieter umlagefähig?", "Steuerlich: sofort / AfA / nein",
                  "Beleg-Nr / Ablage", "Notiz"])
for r in range(3, 1003):
    for col in range(1, 10):
        c = ag.cell(row=r, column=col)
        c.fill = FILL_EINGABE
        c.border = RAHMEN
    ag.cell(row=r, column=1).number_format = DATUM
    ag.cell(row=r, column=5).number_format = EUR2
ag["A3"] = "=DATE(2025,3,1)"
ag["B3"] = "BEISPIEL Passau ETW"
ag["C3"] = "Investition (Sanierung/Modernisierung)"
ag["D3"] = "Neue Böden und Malerarbeiten"
ag["E3"] = 6500
ag["F3"] = "nein"
ag["G3"] = "prüfen: 15-%-Grenze"
ag["A4"] = "=DATE(2025,4,1)"
ag["B4"] = "BEISPIEL Passau ETW"
ag["C4"] = "Laufende Kosten"
ag["D4"] = "Vermieterrechtsschutz"
ag["E4"] = 240
ag["F4"] = "nein"
ag["G4"] = "sofort"
dv_ag_obj = DataValidation(type="list", formula1=f"=Bestand!$B${ERSTE}:$B${LETZTE}", allow_blank=True)
dv_ag_art = DataValidation(type="list", formula1='"Investition (Sanierung/Modernisierung),Laufende Kosten,Finanzierungskosten,Kaufnebenkosten"', allow_blank=True)
dv_ag_uml = DataValidation(type="list", formula1='"ja,nein,teilweise"', allow_blank=True)
dv_ag_st = DataValidation(type="list", formula1='"sofort,verteilt 2–5 Jahre,AfA,nein,prüfen: 15-%-Grenze"', allow_blank=True)
for dv, rng in ((dv_ag_obj, "B3:B1002"), (dv_ag_art, "C3:C1002"), (dv_ag_uml, "F3:F1002"), (dv_ag_st, "G3:G1002")):
    ag.add_data_validation(dv)
    dv.add(rng)
ag.freeze_panes = "A3"
ag.auto_filter.ref = "A2:I1002"
breiten(ag, [11, 26, 32, 36, 13, 14, 22, 16, 30])

# =====================================================================
# 8. Kostenkatalog
# =====================================================================
kk = wb.create_sheet("Kostenkatalog")
titel(kk, "Kostenkatalog – alle Zahlen, die ein Immobilieninvestor kennen muss", 7)
kopfzeile(kk, 2, ["Phase", "Position", "Erklärung", "Richtwert", "Auf Mieter umlagefähig?",
                  "Steuer bei Vermietung", "Hinweis / Falle"])
katalog = [
    # Kauf
    ("Kauf", "Grunderwerbsteuer", "Steuer des Bundeslandes auf den Kaufpreis", "Bayern 3,5 %, NRW 6,5 %", "nein", "Teil der Anschaffungskosten → über AfA (nur Gebäudeanteil)", "Mitverkaufte Einbauküche/Möbel separat und realistisch im Vertrag ausweisen – darauf fällt keine Grunderwerbsteuer an"),
    ("Kauf", "Notar", "Beurkundung Kaufvertrag, Vollzug", "ca. 1,0–1,5 %", "nein", "Anschaffungskosten; Anteil für Grundschuld = sofort absetzbare Finanzierungskosten", "Rechnung nach Kauf- und Grundschuldanteil aufteilen lassen"),
    ("Kauf", "Grundbuchamt", "Eigentumsumschreibung, Auflassungsvormerkung, Grundschuld", "ca. 0,5 %", "nein", "wie Notar", ""),
    ("Kauf", "Maklerprovision", "Vermittlung durch Makler", "typ. 3,57 % inkl. MwSt., verhandelbar", "nein", "Anschaffungskosten → AfA", "Bei ETW/EFH an Privatkäufer: Halbteilung (§ 656c BGB) – Käufer zahlt höchstens so viel wie Verkäufer"),
    ("Kauf", "Gutachter / Bausachverständiger", "Prüfung von Substanz, Feuchtigkeit, Dach, Heizung vor Kauf", "500–1.500 €", "nein", "i. d. R. Anschaffungsneben- oder Werbungskosten", "Bei Altbau fast immer sinnvoll"),
    ("Kauf", "Unterlagen prüfen (ETW)", "Teilungserklärung, Protokolle der letzten 3 Jahre, Wirtschaftsplan, Rücklagenhöhe, Energieausweis", "Arbeitszeit", "–", "–", "Geplante Sonderumlagen stehen in den Protokollen"),
    ("Kauf", "Bereitstellungszinsen", "Zins auf noch nicht ausgezahltes Darlehen", "oft 0,15–0,25 % pro Monat nach freier Zeit", "nein", "Finanzierungskosten, sofort", "Wichtig bei Sanierung/Neubau: lange bereitstellungsfreie Zeit verhandeln"),
    ("Kauf", "Wertermittlung / Schätzkosten Bank", "Manche Banken berechnen das Bankgutachten", "0–1.000 €", "nein", "Finanzierungskosten", ""),
    # Finanzierung laufend
    ("Finanzierung", "Zinsen", "Kosten des Darlehens", "abhängig von Zins, Beleihungsauslauf, Bonität", "nein", "sofort absetzbar (nur Vermietung)", "Vollfinanzierung = Zinsaufschlag gegenüber 80 %-Finanzierung"),
    ("Finanzierung", "Tilgung", "Rückzahlung des Darlehens", "1–3 % anfänglich", "nein", "nicht absetzbar (Vermögensaufbau)", "Belastet den Cashflow, baut aber Vermögen auf"),
    ("Finanzierung", "Sondertilgung", "Recht auf zusätzliche Rückzahlung", "meist 5 % pro Jahr kostenlos verhandelbar", "–", "–", "Flexibilität ist bei Vollfinanzierung viel wert"),
    ("Finanzierung", "Tilgungssatzwechsel", "Recht, die Tilgung während der Laufzeit zu ändern", "1–3 Wechsel kostenlos", "–", "–", ""),
    ("Finanzierung", "Anschlussfinanzierung / Forward-Darlehen", "Neuer Zins nach Ende der Zinsbindung", "Forward-Aufschlag je Vorlaufmonat", "–", "–", "Größtes Risiko bei 100 %-Finanzierung: hohe Restschuld trifft auf ggf. höheren Zins"),
    ("Finanzierung", "Vorfälligkeitsentschädigung", "Gebühr bei vorzeitiger Ablösung (z. B. Verkauf)", "kann mehrere Prozent der Restschuld betragen", "nein", "bei Verkauf: Veräußerungskosten", "Nach 10 Jahren ab Vollauszahlung gesetzliches Kündigungsrecht (§ 489 BGB)"),
    # Laufend – Bewirtschaftung
    ("Laufend", "Grundsteuer", "Steuer der Gemeinde", "regional unterschiedlich", "ja", "durchlaufend", ""),
    ("Laufend", "Wohngebäudeversicherung", "Feuer, Leitungswasser, Sturm, Hagel; ggf. Elementar", "stark abhängig von Gebäude und Region", "ja", "durchlaufend", "Bei ETW im Hausgeld enthalten. Elementarschutz (Hochwasser) – in Passau besonders prüfen"),
    ("Laufend", "Haus- und Grundbesitzerhaftpflicht", "Haftung als Eigentümer", "gering", "ja", "durchlaufend", ""),
    ("Laufend", "Vermieterrechtsschutz", "Rechtsstreit mit Mietern", "ca. 150–350 € pro Jahr", "nein", "sofort absetzbar", ""),
    ("Laufend", "Mietausfallversicherung", "Schutz bei Zahlungsausfall", "variabel", "nein", "sofort absetzbar", "Ersetzt keine gute Mieterauswahl"),
    ("Laufend", "Betriebskosten nach BetrKV", "Wasser, Abwasser, Müll, Heizung, Warmwasser, Hausmeister, Gartenpflege, Allgemeinstrom, Aufzug, Schornsteinfeger, Reinigung", "laut Abrechnung", "ja", "durchlaufend", "Nur umlegen, was im Mietvertrag vereinbart ist; jährliche Abrechnungsfrist 12 Monate"),
    ("Laufend", "WEG-Verwaltung", "Hausverwaltung der Eigentümergemeinschaft", "ca. 25–45 € pro Einheit und Monat", "nein", "sofort absetzbar", ""),
    ("Laufend", "Mietverwaltung (Sondereigentum)", "Verwalter kümmert sich um Mieter, Abrechnung", "ca. 25–45 € pro Einheit und Monat", "nein", "sofort absetzbar", "Lohnt sich bei Objekten fern vom Wohnort"),
    ("Laufend", "Erhaltungsrücklage (WEG)", "Ansparung der Gemeinschaft für Reparaturen", "laut Wirtschaftsplan", "nein", "erst absetzbar, wenn die WEG das Geld ausgibt", "Niedrige Rücklage + alter Bestand = Gefahr von Sonderumlagen"),
    ("Laufend", "Instandhaltung Sondereigentum", "Reparaturen in deiner Wohnung", "Faustregel 8–15 €/m² pro Jahr", "nein", "sofort absetzbar (Erhaltungsaufwand)", ""),
    ("Laufend", "Mietausfallwagnis / Leerstand", "Kalkulatorische Reserve", "2–4 % der Jahreskaltmiete", "–", "–", "Immer einrechnen, auch wenn vermietet"),
    ("Laufend", "Mieterwechsel", "Inserat, Besichtigungen, Renovierung, ggf. Vermietungsmakler", "Makler: bis 2 Kaltmieten + MwSt.", "nein", "sofort absetzbar", "Bestellerprinzip: wer den Makler beauftragt, zahlt"),
    ("Laufend", "Steuerberater, Kontoführung, Fahrten", "Verwaltungskosten des Vermieters", "variabel", "nein", "sofort absetzbar", "Fahrten zum Objekt dokumentieren"),
    # Sanierung
    ("Sanierung", "15-%-Grenze (anschaffungsnahe Herstellungskosten)", "Sanierung in den ersten 3 Jahren nach Kauf über 15 % der Gebäude-Anschaffungskosten (netto)", "Grenze objektbezogen berechnen", "–", "dann NICHT sofort absetzbar, sondern nur über AfA", "Wichtigste Steuerfalle bei Kauf + Sanierung! Vor dem Kauf mit Steuerberater planen"),
    ("Sanierung", "Erhaltungsaufwand", "Ersatz von Vorhandenem (Bad, Böden, Fenster in gleichem Standard)", "objektabhängig", "nein", "sofort oder auf 2–5 Jahre verteilt (§ 82b EStDV)", "Verteilen lohnt bei hohem Betrag und gleichbleibendem Steuersatz"),
    ("Sanierung", "Herstellungsaufwand / Standardhebung", "Wesentliche Verbesserung (z. B. 3 von 4 Kernbereichen: Heizung, Sanitär, Elektro, Fenster)", "objektabhängig", "nein", "nur über AfA", ""),
    ("Sanierung", "Modernisierungsumlage", "Mieterhöhung nach Modernisierung", "8 % der Kosten pro Jahr, mit Kappungsgrenzen", "teilweise", "Mehreinnahmen", "Ankündigungspflicht 3 Monate vorher (§ 555c BGB)"),
    ("Sanierung", "Energetische Förderung", "KfW/BAFA-Zuschüsse und Kredite; Eigennutzer: Steuerermäßigung § 35c EStG", "je nach Programm", "–", "Zuschüsse mindern die Kosten", "Förderantrag meist VOR Auftragsvergabe stellen – Programme ändern sich häufig"),
    ("Sanierung", "Badsanierung (Richtwert)", "Komplettbad", "[Vermutung] ca. 15.000–30.000 €", "nein", "meist Erhaltungsaufwand", "Regional stark schwankend, München deutlich teurer – Angebote einholen"),
    ("Sanierung", "Fenster (Richtwert)", "Austausch pro Fenster inkl. Einbau", "[Vermutung] ca. 700–1.500 €", "nein", "Erhaltung, bei Standardhebung Herstellung", ""),
    ("Sanierung", "Heizung Wärmepumpe (Richtwert)", "Einbau inkl. Nebenarbeiten, vor Förderung", "[Vermutung] ca. 25.000–45.000 €", "nein", "objektabhängig", "Gebäudeenergiegesetz und Förderung prüfen"),
    ("Sanierung", "Böden und Maler (Richtwert)", "Neue Böden / Wände streichen", "[Vermutung] Böden 40–100 €/m², Maler 15–30 €/m² Wohnfläche", "nein", "meist Erhaltungsaufwand", ""),
    ("Sanierung", "Elektrik (Richtwert)", "Erneuerung einer Wohnung", "[Vermutung] ca. 8.000–20.000 €", "nein", "objektabhängig", "Bei Altbau vor 1970 oft nötig"),
    # Vermietung
    ("Vermietung", "Mietpreisbremse / Kappungsgrenze", "Begrenzt Neuvermietungsmiete und Mieterhöhungen in angespannten Märkten", "Neuvermietung max. 10 % über ortsüblicher Vergleichsmiete", "–", "–", "Ob die Stadt betroffen ist, im Blatt Marktdaten prüfen (Landesverordnung)"),
    ("Vermietung", "Kaution", "Sicherheit des Mieters", "max. 3 Nettokaltmieten", "–", "keine Einnahme (Treuhand)", "Getrennt anlegen"),
    ("Vermietung", "Vermietung an Angehörige", "Günstige Miete an Familie", "mind. 66 % der ortsüblichen Miete", "–", "darunter Werbungskosten nur anteilig (§ 21 Abs. 2 EStG)", ""),
    # Verkauf
    ("Verkauf", "Spekulationsfrist", "Gewinn beim Verkauf steuerfrei?", "10 Jahre ab Kaufvertrag", "–", "innerhalb 10 Jahren steuerpflichtig (§ 23 EStG)", "Ausnahme Eigennutzung im Verkaufsjahr und den zwei Jahren davor"),
    ("Verkauf", "Makler und Vorfälligkeit beim Verkauf", "Kosten beim Ausstieg", "Makler ca. 3,57 %, Vorfälligkeit objektabhängig", "–", "mindern den Veräußerungsgewinn", ""),
]
for i, zeile_k in enumerate(katalog, start=3):
    for j, w in enumerate(zeile_k, start=1):
        c = kk.cell(row=i, column=j, value=w)
        c.alignment = WRAP
        c.border = RAHMEN
kk.freeze_panes = "C3"
kk.auto_filter.ref = f"A2:G{len(katalog) + 2}"
breiten(kk, [12, 30, 45, 28, 13, 32, 50])

# =====================================================================
# 9. Kennzahlen
# =====================================================================
kz = wb.create_sheet("Kennzahlen")
titel(kz, "Kennzahlen – Formel, Bedeutung, Richtwert", 4)
kopfzeile(kz, 2, ["Kennzahl", "Formel", "Was sie dir sagt", "Richtwert"])
kennzahlen = [
    ("Kaufpreisfaktor", "Kaufpreis ÷ Jahreskaltmiete", "Wie viele Jahresmieten du für das Objekt zahlst", "< 20 sehr gut, 20–25 ok, > 30 teuer (typisch für München)"),
    ("Bruttomietrendite", "Jahreskaltmiete ÷ Kaufpreis", "Schneller Vergleich zwischen Objekten", "≥ 4 % für Cashflow bei Vollfinanzierung meist nötig"),
    ("Nettomietrendite", "(Jahresmiete − nicht uml. Kosten) ÷ (Kaufpreis + Nebenkosten)", "Ehrlichere Rendite nach Kosten", "Sollte über dem Sollzins liegen, sonst negativer Hebel"),
    ("Kaufnebenkostenquote", "Kaufnebenkosten ÷ Kaufpreis", "Wie viel Eigenkapital du mindestens brauchst", "Bayern ca. 9 %, NRW ca. 12 % (mit Makler)"),
    ("Beleihungsauslauf (LTV)", "Darlehen ÷ Beleihungswert", "Risiko aus Sicht der Bank", "Je höher, desto teurer der Zins; 100 % = Vollfinanzierung"),
    ("Monatsrate", "Darlehen × (Zins + Tilgung) ÷ 12", "Was du jeden Monat an die Bank zahlst", "–"),
    ("Restschuld", "Rest nach Zinsbindung", "Wie viel du zum neuen Zins weiterfinanzieren musst", "Je kleiner, desto weniger Zinsrisiko"),
    ("Cashflow vor Steuern", "Miete − nicht uml. Kosten − Rücklagen − Rate", "Trägt sich das Objekt selbst?", "≥ 0 €"),
    ("Cashflow nach Steuern", "Cashflow vor Steuern + Steuereffekt", "Was wirklich auf dem Konto bleibt", "≥ 0 €"),
    ("Eigenkapitalrendite", "(Cashflow nach Steuern + Tilgung) ÷ eingesetztes Eigenkapital", "Verzinsung deines Geldes ohne Wertsteigerung", "Vergleich mit Alternativen (z. B. ETF)"),
    ("Kapitaldienstdeckung (DSCR)", "Miete nach Kosten ÷ Rate", "Kann die Miete die Rate decken?", "≥ 1,0; Banken wünschen oft ≥ 1,2"),
    ("Belastungsquote", "(Rate + Wohnkosten) ÷ Haushaltsnetto", "Tragfähigkeit bei Eigennutzung", "≤ 35 %"),
    ("AfA", "Gebäudeanteil × Satz", "Steuerliche Abschreibung", "2 % (Baujahr 1925–2022), 2,5 % (vor 1925), 3 % (ab 2023)"),
    ("Nettovermögen", "Marktwert − Restschuld", "Dein Vermögen in der Immobilie", "Sollte jedes Jahr steigen"),
    ("Preis pro m²", "Kaufpreis ÷ Wohnfläche", "Vergleich mit Marktdaten / Gutachterausschuss", "Unter Marktdurchschnitt = Verhandlungsspielraum genutzt"),
]
for i, z in enumerate(kennzahlen, start=3):
    for j, w in enumerate(z, start=1):
        c = kz.cell(row=i, column=j, value=w)
        c.alignment = WRAP
        c.border = RAHMEN
breiten(kz, [26, 42, 45, 45])

wb.save(ZIEL)
print("gespeichert:", ZIEL)
