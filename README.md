# DP Detection
 
Aplikace pro automatickou detekci a počítání objektů (osoby, kola, auta) z webkamery pomocí modelu YOLO. Data jsou v pravidelných intervalech odesílána na vzdálený server.
 
## Funkce
 
- Detekce osob, kol a aut v reálném čase pomocí YOLOv11n
- Sledování objektů přes unikátní track ID (každý objekt se počítá jen jednou za interval)
- Automatické odesílání dat na server každých 60 sekund
- Ukládání neúspěšně odeslaných dat a jejich opakované odeslání při obnovení připojení
- Automatický refresh přihlašovacího tokenu
- Zobrazení počtů a FPS přímo ve videu
- 
## Požadavky
 
- Python 3.8+
- Webkamera
### Python závislosti
 
```
ultralytics
opencv-python
requests
```
 
Instalace:
 
```bash
pip install ultralytics opencv-python requests
```
 
## Konfigurace
 
| Proměnná | Popis | Výchozí hodnota |
|---|---|---|
| `BASE_URL` | Adresa API serveru | `http://[2001:718:1c01:21:250:56ff:fe8e:6246]/:3000` |
| `STATION_ID` | ID stanice na serveru | *(id stanice na kterou má program aktuálně měřit)* |
| `USERNAME` | Přihlašovací e-mail | *(email uživatele)* |
| `PASSWORD` | Heslo | *(heslo uživatele)* |
| `RESET_INTERVAL` | Interval odesílání dat (sekundy) | `60` |
| `TOKEN_LIFETIME` | Platnost tokenu před refresh loginem (sekundy) | `5400` (1,5 h) |
| `MIN_CONF` | Minimální confidence pro detekci | `0.5` |
 
## Spuštění
 
```bash
python DP_detection.py
```
 
Aplikace se připojí k serveru, otevře kameru a začne detekovat objekty. Stisknutím klávesy **ESC** aplikaci ukončíte.
 
## API – formát odesílaných dat
 
Každých `RESET_INTERVAL` sekund se odešle POST požadavek na `/add_record`:
 
```json
{
  "stationId": "<ID stanice>",
  "recordTime": "2026-04-06T12:00:00.000000",
  "people": 3,
  "bikes": 1,
  "cars": 5
}
```
 
## Dodatek
 
- Model `yolo11n.pt` se při prvním spuštění automaticky stáhne z internetu.
- Pokud je server nedostupný, data se uloží lokálně a odešlou při příštím úspěšném připojení.
- Aplikace vyžaduje funkční webkameru na indexu `0`.
