# ThesslaGreen_HA

## 🇵🇱 Integracja Home Assistant dla rekuperatorów Thessla Green z komunikacją Modbus TCP

> 🛠️ Projekt rozwijany — aktualnie stabilny i w pełni funkcjonalny!

### ✨ Funkcje

- Komunikacja z rekuperatorem Thessla Green przez **Modbus TCP**
- Wsparcie dla pełnego zakresu danych:
  - `sensor` — temperatury, przepływy powietrza, statusy, błędy
  - `binary_sensor` — stany pracy (także przez `coils`), siłowniki bypassu, alarmy
  - `switch` — bypass, on/off, zmiana trybu
  - `select` — wybór trybu pracy i sezonu (lato/zima)
  - `number` — ustawienie prędkości wentylatora (0–100%)
- Obsługa stanów w czasie rzeczywistym z szybkim odświeżaniem (domyślnie co 30s, konfigurowalne)
- Wsparcie błyskawicznego wykrywania utraty komunikacji
- Konfiguracja przez interfejs użytkownika (UI Config Flow)
- Integracja automatycznie grupuje wszystkie encje pod jedno urządzenie w Home Assistant
- Wsparcie dla HACS (Home Assistant Community Store)

---

### 📦 Instalacja

#### Przez HACS

1. Dodaj to repozytorium jako **Custom Repository** w HACS
2. Zainstaluj integrację **Thessla Green**
3. Zrestartuj Home Assistant
4. Przejdź do `Ustawienia → Integracje → Dodaj integrację`
5. Wybierz **Thessla Green** i skonfiguruj IP urządzenia, port oraz numer slave

#### Ręcznie

1. Sklonuj to repozytorium do katalogu `custom_components`:
    ```bash
    git clone https://github.com/twoj_uzytkownik/ThesslaGreen_HA.git custom_components/thessla_green
    ```
2. Zrestartuj Home Assistant
3. Dodaj integrację jak powyżej

---

## 🇬🇧 ThesslaGreen_HA – Home Assistant integration for Thessla Green heat recovery units

> 🛠️ Work in progress — now stable and fully functional!

### ✨ Features

- Communicates with Thessla Green units over **Modbus TCP**
- Full range of data supported:
  - `sensor` — temperatures, airflow, statuses, errors
  - `binary_sensor` — state confirmations (via coils), bypass actuator, alarms
  - `switch` — bypass, on/off, mode change
  - `select` — operation modes and season (summer/winter)
  - `number` — set fan speed (0–100%)
- Real-time updates with fast polling (default 30s, configurable)
- Robust error handling and reconnection logic
- Easy setup via Home Assistant UI (Config Flow)
- All entities grouped into a single device in Home Assistant
- Fully HACS-compatible (Home Assistant Community Store)

---

### 📦 Installation

#### Using HACS

1. Add this repository as a **Custom Repository** in HACS
2. Install **Thessla Green** integration
3. Restart Home Assistant
4. Go to `Settings → Integrations → Add Integration`
5. Select **Thessla Green** and configure IP address, port, and slave ID

#### Manual Installation

1. Clone this repository into your `custom_components` folder:
    ```bash
    git clone https://github.com/your_username/ThesslaGreen_HA.git custom_components/thessla_green
    ```
2. Restart Home Assistant
3. Add the integration as described above