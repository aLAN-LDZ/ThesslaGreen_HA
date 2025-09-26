<!-- Badges: start -->
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://hacs.xyz/)
[![GitHub - Downloads](https://img.shields.io/github/downloads/aLAN-LDZ/ThesslaGreen_HA/total?style=for-the-badge)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/releases)
[![Issues & PRs](https://img.shields.io/github/issues-pr/aLAN-LDZ/ThesslaGreen_HA?style=for-the-badge)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/issues)
[![Latest Release](https://img.shields.io/github/v/release/aLAN-LDZ/ThesslaGreen_HA?style=for-the-badge)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/releases)
[![Release Date](https://img.shields.io/github/release-date/aLAN-LDZ/ThesslaGreen_HA?style=for-the-badge&label=Latest%20Release)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/releases)
[![Pre-Release Date](https://img.shields.io/github/release-date-pre/aLAN-LDZ/ThesslaGreen_HA?style=for-the-badge&label=Latest%20Beta%20Release)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/releases)

[![Stars](https://img.shields.io/github/stars/aLAN-LDZ/ThesslaGreen_HA?style=for-the-badge)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/stargazers)
[![Forks](https://img.shields.io/github/forks/aLAN-LDZ/ThesslaGreen_HA?style=for-the-badge)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/network/members)
[![License](https://img.shields.io/github/license/aLAN-LDZ/ThesslaGreen_HA?style=for-the-badge)](./LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/aLAN-LDZ/ThesslaGreen_HA?style=for-the-badge)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/commits)

<!-- Jeśli masz Discorda – podmień ID i link zaproszenia -->
[![Discord](https://img.shields.io/discord/000000000000000000?style=for-the-badge&logo=discord&logoColor=white&label=Discord&color=7289da)](https://discord.gg/yourInviteCode)

<!-- Jeśli używasz GitHub Actions – podmień nazwę pliku workflow i gałąź -->
[![CI](https://img.shields.io/github/actions/workflow/status/aLAN-LDZ/ThesslaGreen_HA/ci.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/aLAN-LDZ/ThesslaGreen_HA/actions)
<!-- Badges: end -->


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
- Po podaniu encji poboru energii możliwość wyliczenia COP, Moc Odzysku oraz Sprawność

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
- After entering the energy consumption entity, it is possible to calculate COP, Recovery Power and Efficiency

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
