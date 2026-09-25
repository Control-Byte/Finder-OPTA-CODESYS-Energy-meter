from datetime import datetime
import csv
import struct
import time  
from pymodbus.client import ModbusTcpClient

OPTA_IP = "10.0.0.2"
PORT = 502
ADRES_REJESTRU = 0
INTERWAL_CZASOWY = 2  # Czas w sekundach między odczytami


def words_to_float(high_word, low_word):
  packed = struct.pack(">HH", high_word, low_word)
  return struct.unpack(">f", packed)[0]


print("Łączenie z Optą...")
client = ModbusTcpClient(OPTA_IP, port=PORT)

if client.connect():
  print(
      f"Połączenie nawiazane! Uruchomiono automatyczny zapis co"
      f" {INTERWAL_CZASOWY} sekundy."
  )
  print("Naciśnij Ctrl + C w terminalu, aby zatrzymać program.\n")

  try:
    while True:  # Pętla nieskończona 
      response = client.read_input_registers(address=ADRES_REJESTRU, count=50)

      if not response.isError():
        regs = response.registers
        wiersz_danych = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        nazwy_kolumn = ["Czas"]

        idx = 1
        for numer_licznika in range(1, 4):
          active_power = words_to_float(regs[idx], regs[idx + 1])
          reactive_power = words_to_float(regs[idx + 2], regs[idx + 3])
          apparent_power = words_to_float(regs[idx + 4], regs[idx + 5])
          power_factor = words_to_float(regs[idx + 6], regs[idx + 7])
          frequency = words_to_float(regs[idx + 8], regs[idx + 9])
          voltage = words_to_float(regs[idx + 10], regs[idx + 11])
          current = words_to_float(regs[idx + 12], regs[idx + 13])

          idx += 14

          wiersz_danych.extend([
              f"{active_power:.2f}",
              f"{reactive_power:.2f}",
              f"{apparent_power:.2f}",
              f"{power_factor:.2f}",
              f"{frequency:.2f}",
              f"{voltage:.2f}",
              f"{current:.2f}",
          ])

          l = numer_licznika
          nazwy_kolumn.extend([
              f"L{l}_MocCzynna",
              f"L{l}_MocBierna",
              f"L{l}_MocPozorna",
              f"L{l}_CosPhi",
              f"L{l}_Czestotliwosc",
              f"L{l}_Napiecie",
              f"L{l}_Prad",
          ])

        plik_csv = "pomiary_liczniki.csv"

        try:
          with open(plik_csv, "r", encoding="utf-8"):
            header_needed = False
        except FileNotFoundError:
          header_needed = True

        # Używamy średnika jako separatora, żeby Excel od razu dzielił na kolumny
        with open(plik_csv, mode="a", newline="", encoding="utf-8") as f:
          writer = csv.writer(f, delimiter=";")
          if header_needed:
            writer.writerow(nazwy_kolumn)
          writer.writerow(wiersz_danych)

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] Zapisano pomiar z 3"
            " liczników."
        )

      else:
        print("Błąd odczytu rejestrów z Opty w tym cyklu...")

      # Czekamy 2 sekundy przed kolejnym odczytem
      time.sleep(INTERWAL_CZASOWY)

  except KeyboardInterrupt:
    print("\nZatrzymano program przez użytkownika.")

  client.close()
else:
  print("Błąd połączenia TCP z Optą.")