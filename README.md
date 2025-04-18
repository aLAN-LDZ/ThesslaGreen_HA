# ThesslaGreen_HA

Integracja Home Assistant dla rekuperatorów **Thessla Green** z komunikacją Modbus TCP.

> 🛠️ **Wersja rozwojowa** – projekt w toku, ale już działa stabilnie dla wielu sensorów!

---

## ✨ Funkcje

- Odczyt danych z rekuperatora Thessla Green przez Modbus TCP
- Automatyczne tworzenie:
  - sensorów (temperatury, przepływy, statusy, błędy)
  - binary sensorów (potwierdzenia pracy, siłownik bypassu)
  - przełączników (`switch`)
  - selektorów (`select`) — w przyszłości
- Obsługa wielu encji z przypisaniem do jednego urządzenia w Home Assistant
- Integracja z GUI Home Assistanta (config flow)

---

## 📦 Instalacja

### Przez HACS
1. Dodaj to repozytorium jako **custom repository** w HACS
2. Zainstaluj integrację `Thessla Green`
3. Zrestartuj Home Assistant
4. Przejdź do `Ustawienia → Integracje → Dodaj integrację`
5. Wybierz `Thessla Green` i skonfiguruj IP, port oraz numer slave

### Ręcznie

1. Sklonuj repozytorium do folderu `custom_components`:
