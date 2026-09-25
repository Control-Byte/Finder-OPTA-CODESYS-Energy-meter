# Finder Opta + CODESYS - reading energy meters over Modbus

Read three energy meters over Modbus and log every measurement to a CSV file.

A **Finder Opta** controller polls the meters over Modbus RTU and exposes the
readings on Modbus TCP input registers. A Python script connects to the Opta
over the network, decodes the values and appends them to a CSV file every two
seconds.

```
energy meters  --Modbus RTU-->  Finder Opta  --Modbus TCP-->  Python  -->  CSV
```

## What is in this repository

| File | What it is |
|---|---|
| `liczniki_odczyt.project` | CODESYS project for the Finder Opta - polls the meters over Modbus RTU and publishes the values on Modbus TCP input registers |
| `pobierz.py` | Python client that reads the registers and writes the measurements to CSV |
| `pomiary_liczniki.csv` | sample data from a real run |

## Running it

### Controller

Open `liczniki_odczyt.project` in **CODESYS** and download it to the Finder
Opta. The controller does the RTU side of the job; the Python script only reads
what the Opta has already collected.

### Script

Python 3 and `pymodbus`:

```bash
pip install pymodbus
```

Set the controller address in `pobierz.py` if yours differs:

```python
OPTA_IP = "10.0.0.2"
PORT = 502
INTERWAL_CZASOWY = 2   # seconds between reads
```

Run it:

```bash
python pobierz.py
```

The script appends rows to `pomiary_liczniki.csv` until you stop it with
`Ctrl + C`. The header is written once, when the file is created, so repeated
runs add to the existing dataset instead of starting over.

## Register map

The script reads **50 input registers** starting at address 0. Register 0 is
skipped; the data starts at register 1.

Each meter occupies **14 registers**, that is 7 float values. Every float is two
16-bit registers, high word first (`>HH` -> `>f`).

| Offset inside the meter block | Value |
|---|---|
| 0-1 | active power |
| 2-3 | reactive power |
| 4-5 | apparent power |
| 6-7 | power factor |
| 8-9 | frequency |
| 10-11 | voltage |
| 12-13 | current |

The blocks follow one another: meter 1 starts at register 1, meter 2 at
register 15, meter 3 at register 29.

## CSV format

The separator is a **semicolon**, so Excel splits the data into columns without
an import step. The file has 22 columns: a timestamp plus 7 values for each of
the three meters. Column names are in Polish, matching the script.

```
Czas;L1_MocCzynna;L1_MocBierna;L1_MocPozorna;L1_CosPhi;L1_Czestotliwosc;L1_Napiecie;L1_Prad;L2_...;L3_...
```

| Polish | English |
|---|---|
| `Czas` | timestamp |
| `MocCzynna` | active power |
| `MocBierna` | reactive power |
| `MocPozorna` | apparent power |
| `CosPhi` | power factor |
| `Czestotliwosc` | frequency |
| `Napiecie` | voltage |
| `Prad` | current |

The sample file shows a typical bench: meters 1 and 3 measure running loads
(12.5 W and 16.4 W), meter 2 reads zeros because nothing is connected to it -
with no current the power factor is reported as 1, while voltage and frequency
are still measured normally.

## Practical notes

- **Negative reactive power** in the sample (-6 var) means a capacitive load.
  That is normal with switched-mode power supplies and is not a decoding error.
- **Word order.** If the values look like noise, check the word order. This
  script assumes high word first. For the opposite order, swap the arguments in
  `words_to_float`.
- **No reconnect logic.** If the network drops, the script reports a read error
  and keeps trying on the next cycle, but it does not re-establish the TCP
  connection. Worth adding for long runs.
- **A two second interval** produces about 1800 rows per hour. Logging around
  the clock will grow the file to tens of thousands of rows - at that point the
  data belongs in a database rather than a CSV.

## Why this exists

Built for the ControlByte courses on industrial communication and data
analysis. It shows the whole path from a DIN rail meter to a file you can open
in Excel or load into Python.

[controlbyte.tech](https://controlbyte.tech)
