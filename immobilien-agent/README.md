# Immobilien-Agent

Agentensystem für Immobilienkauf, Finanzierung und Bestandsverwaltung (Passau, München, Münster).
Läuft mit Claude Code: Koordinator in `CLAUDE.md`, Unteragenten in `.claude/agents/`.

## Start
```bash
cd immobilien-agent
cp vorlage/Immobilien-Investor-Vorlage.xlsx Immobilien-Investor.xlsx   # deine Arbeitsdatei, wird nicht committet
pip install openpyxl                                                    # LibreOffice zum Neuberechnen empfohlen
```
1. In `Immobilien-Investor.xlsx` das Blatt **Profil** ausfüllen (gelbe Felder).
2. Bei ImmoScout24 / Immowelt / Kleinanzeigen Suchaufträge für die drei Städte anlegen (Benachrichtigung per E-Mail).
3. Claude Code in diesem Ordner starten und z. B. sagen:
   - „Suche neue Objekte und erstelle die Rangliste.“
   - „Analysiere Standort Münster-Kreuzviertel.“
   - „Rechne Finanzierungsszenarien für O004.“
   - „Gib mir den Bestandsüberblick.“

## Agenten
| Agent | Aufgabe |
|---|---|
| Koordinator (`CLAUDE.md`) | verteilt Aufgaben, Rangliste, Bericht |
| `objekt-scout` | Angebote finden, Exposés auslesen, Pipeline befüllen, Duplikate erkennen |
| `standort-analyst` | Preise früher/heute, Mieten, Bevölkerung, Prognose, Standortnote |
| `finanzierungs-agent` | Zinsen, Szenarien, Anfragen als Entwurf, Angebotsvergleich |
| `investment-berater` | Kauf/Nicht-Kauf, Sanierung, Vermietung, Bestandsüberblick |

## Arbeitsmappe
Profil · Marktdaten · Pipeline · Objektanalyse · Bestand · Ausgaben · Kostenkatalog · Kennzahlen.
Vorlage neu erzeugen: `python3 tools/erstelle_excel.py vorlage/Immobilien-Investor-Vorlage.xlsx`

## Grenzen
- Nichts wird ohne Freigabe versendet. Portale werden nicht automatisiert ausgelesen.
- Steuerhinweise vereinfacht, keine Anlage- oder Steuerberatung.
- **Dieses Repository ist öffentlich** – persönliche Daten sind per `.gitignore` ausgeschlossen. Besser: eigenes privates Repository.
