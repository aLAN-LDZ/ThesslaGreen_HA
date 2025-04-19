# ThesslaGreen_HA

## 🇵🇱 Integracja Home Assistant dla rekuperatorów Thessla Green z komunikacją Modbus TCP

> 🛠️ Projekt w wersji rozwojowej — ale już działa stabilnie i odczytuje większość danych!

### ✨ Funkcje

- Odczyt danych z rekuperatora Thessla Green przez **Modbus TCP**
- Automatyczne tworzenie encji:
  - `sensor` — temperatury, przepływy powietrza, statusy, błędy
  - `binary_sensor` — stany pracy, siłowniki bypassu
  - `switch` — np. włącz/wyłącz, bypass
  - `select` — tryby pracy, sezon (zima/lato)
  - `number` — ustawienie prędkości wentylatora (0–100%)
- Obsługa wielu encji jako jedno urządzenie w Home Assistant
- Konfiguracja przez interfejs graficzny (config flow)

---

### 📦 Instalacja

#### Przez HACS

1. Dodaj to repozytorium jako **Custom Repository** w HACS
2. Zainstaluj integrację **Thessla Green**
3. Zrestartuj Home Assistant
4. Przejdź do `Ustawienia → Integracje → Dodaj integrację`
5. Wybierz **Thessla Green** i skonfiguruj IP, port oraz numer slave

#### Ręcznie

1. Sklonuj to repozytorium do katalogu `custom_components`:
    ```bash
    git clone https://github.com/twoj_uzytkownik/ThesslaGreen_HA.git custom_components/thessla_green
    ```
2. Zrestartuj Home Assistant
3. Dodaj integrację jak wyżej

---

## 🇬🇧 ThesslaGreen_HA – Home Assistant integration for Thessla Green heat recovery units

> 🛠️ Work in progress – but already stable and supports most sensors!

### ✨ Features

- Read data from Thessla Green unit via **Modbus TCP**
- Automatically creates entities:
  - `sensor` — temperatures, airflows, statuses, errors
  - `binary_sensor` — state confirmations, bypass actuator
  - `switch` — on/off, bypass, etc.
  - `select` — operation modes, season (summer/winter)
  - `number` — fan speed setting (0–100%)
- Groups all entities into a single device in Home Assistant
- Fully configurable via UI (config flow)

---

### 📦 Installation

#### Using HACS

1. Add this repository as a **Custom Repository** in HACS
2. Install **Thessla Green** integration
3. Restart Home Assistant
4. Go to `Settings → Integrations → Add Integration`
5. Select **Thessla Green** and configure IP, port, and slave ID

#### Manual installation

1. Clone this repository into the `custom_components` folder:
    ```bash
    git clone https://github.com/your_username/ThesslaGreen_HA.git custom_components/thessla_green
    ```
2. Restart Home Assistant
3. Add the integration as described above
