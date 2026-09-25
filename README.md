# Liczniki energii przez Modbus - Finder Opta + Python

Odczyt trzech liczników energii przez Modbus i zapis pomiarów do pliku CSV.

Sterownik **Finder Opta** zbiera dane z liczników i wystawia je na rejestrach
Modbus TCP. Skrypt w Pythonie łączy się z Optą po sieci, dekoduje wartości
i dopisuje je do pliku CSV co dwie sekundy.

```
liczniki energii  --Modbus RTU-->  Finder Opta  --Modbus TCP-->  Python  -->  CSV
```

## Co jest w repozytorium

| Plik | Co to jest |
|---|---|
| `pobierz.py` | skrypt odczytujący rejestry z Opty i zapisujący pomiary do CSV |
| `liczniki_odczyt.project` | projekt sterownika dla Finder Opta |
| `pomiary_liczniki.csv` | przykładowe dane z rzeczywistego odczytu |

## Jak to uruchomić

Potrzebny Python 3 i biblioteka `pymodbus`:

```bash
pip install pymodbus
```

Ustaw adres sterownika w `pobierz.py`, jeśli masz inny niż domyślny:

```python
OPTA_IP = "10.0.0.2"
PORT = 502
INTERWAL_CZASOWY = 2   # sekundy między odczytami
```

Uruchom:

```bash
python pobierz.py
```

Skrypt dopisuje kolejne wiersze do `pomiary_liczniki.csv` aż do przerwania
przez `Ctrl + C`. Nagłówek zapisuje tylko raz, przy tworzeniu pliku, więc
kolejne uruchomienia dokładają dane do istniejącego zbioru.

## Mapa rejestrów

Skrypt czyta **50 rejestrów wejściowych** od adresu 0. Rejestr 0 jest pomijany,
dane zaczynają się od rejestru 1.

Każdy licznik zajmuje **14 rejestrów**, czyli 7 wartości typu float. Każdy float
to dwa rejestry 16-bitowe w kolejności big-endian (`>HH` -> `>f`).

| Offset w bloku licznika | Wielkość |
|---|---|
| 0-1 | moc czynna |
| 2-3 | moc bierna |
| 4-5 | moc pozorna |
| 6-7 | współczynnik mocy (cos phi) |
| 8-9 | częstotliwość |
| 10-11 | napięcie |
| 12-13 | prąd |

Bloki idą po kolei: licznik 1 od rejestru 1, licznik 2 od rejestru 15,
licznik 3 od rejestru 29.

## Format pliku CSV

Separatorem jest **średnik**, żeby Excel od razu dzielił dane na kolumny bez
importu. Plik ma 22 kolumny: znacznik czasu i po 7 wielkości na każdy z trzech
liczników.

```
Czas;L1_MocCzynna;L1_MocBierna;L1_MocPozorna;L1_CosPhi;L1_Czestotliwosc;L1_Napiecie;L1_Prad;L2_...;L3_...
```

W dołączonym przykładzie widać typowy obraz stanowiska: licznik 1 i 3 mierzą
pracujące odbiorniki (12,5 W i 16,4 W), licznik 2 pokazuje zera, bo nie ma na
nim obciążenia - przy zerowym prądzie cos phi wynosi 1, a napięcie i
częstotliwość są mierzone normalnie.

## Uwagi praktyczne

- **Ujemna moc bierna** w przykładzie (-6 var) oznacza obciążenie pojemnościowe.
  To normalne przy zasilaczach impulsowych i nie jest błędem odczytu.
- **Kolejność bajtów.** Jeśli wartości wyglądają na przypadkowe, sprawdź
  kolejność słów. Ten skrypt zakłada starsze słowo jako pierwsze. Przy odwrotnej
  kolejności zamień argumenty w `words_to_float`.
- **Brak obsługi ponownego łączenia.** Przy zerwaniu sieci skrypt zgłosi błąd
  odczytu i będzie próbował dalej w kolejnych cyklach, ale nie odtwarza
  połączenia TCP. Przy dłuższych pomiarach warto to dopisać.
- **Interwał 2 sekundy** daje około 1800 wierszy na godzinę. Przy całodobowym
  zbieraniu plik urośnie do kilkudziesięciu tysięcy wierszy - wtedy lepszym
  miejscem na dane jest baza, nie CSV.

## Do czego to służy

Materiał powstał na potrzeby kursów ControlByte z komunikacji przemysłowej
i analizy danych. Pokazuje pełną ścieżkę od licznika na szynie DIN do pliku,
który da się otworzyć w Excelu albo wczytać do Pythona.

[controlbyte.pl](https://www.controlbyte.pl)
