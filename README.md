
---

# Iskolai Adatvizualizáció (Térkép Generátor)

Ez a Python script interaktív térképeket generál az iskolai felvételi/létszám adatokból, városonként csoportosítva, színkódolva.

## ⚠️ Fontos előkészületek és szabályok

1. **Adat konvertálása:** A program `.csv` fájlokkal dolgozik. Ha az adataid Excel (`.xls` vagy `.xlsx`) formátumban vannak, először a táblázatkezelőben használd a *Fájl -> Mentés másként... -> CSV (vesszővel elválasztott)* opciót vagy használj [formázó oldalt](https://tableconvert.com/)!
2. **Kötött fájlnevek:** Az adatokat tartalmazó fájlok neveit **tilos megváltoztatni** (pl. `iskola_adatok.csv`, `koordinatak.csv`), különben a script nem fogja megtalálni őket.
3. **Érintetlen fejlécek:** A CSV fájlok **első sora (a fejléc) pontosan maradjon az, ami volt** (pl. `Város,Iskola,2024_adat,2025_adat,változás,Státusz`). Ha átírod vagy törlöd ezeket, a program hibára fut, mert nem találja a megfelelő oszlopokat.

## 🛠️ Telepítés

Mielőtt futtatnád a kódot, telepítened kell a működéshez szükséges Python könyvtárakat. Nyiss egy parancssort (Terminal / CMD), és futtasd az alábbi parancsot:

```bash
pip install pandas folium

```

## 🚀 Használat (Térképek generálása)

1. Tedd egy közös mappába a Python scriptet (`.py` fájl) és a megfelelő CSV fájlokat.
2. Futtasd a scriptet a parancssorból:
```bash
python main.py

```


3. A script lefut, és a mappában létrehozza a kimeneti `.html` térképfájlokat (pl. `terkep_2024.html`, `terkep_2025.html`, `terkep_valtozas.html`).
4. **Megtekintés:** Csak kattints duplán a generált `.html` fájlok valamelyikére, és megnyílik a kedvenc böngésződben (Chrome, Firefox, Edge, stb.) az interaktív térkép!
