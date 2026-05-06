import cv2
import time
import requests
from datetime import datetime
from ultralytics import YOLO

# Konfigurace
BASE_URL = "http://bifur.nti.tul.cz:3000"

LOGIN_URL = f"{BASE_URL}/login"
SERVER_URL = f"{BASE_URL}/add_record"

STATION_ID = "69ca124850282f6c40a4ea22"

USERNAME = "dada@dada.cz"
PASSWORD = "dada"

RESET_INTERVAL = 60
TOKEN_LIFETIME = 60 * 60 * 1.5

MIN_CONF = 0.5

# Model YOLO
model = YOLO("yolo11n.pt")
CLASS_NAMES = model.names

TARGET_CLASSES = {
    "car": 0,
    "bicycle": 0,
    "person": 0
}

counted_ids = set()
pending_batches = []

# Login
def login():
    try:
        res = requests.post(
            LOGIN_URL,
            json={"email": USERNAME, "password": PASSWORD},
            timeout=5
        )

        if res.status_code != 200:
            print("Login failed:", res.text)
            return None

        data = res.json()
        token = data.get("token")

        if not token:
            print("Backend nevrací token")
            return None

        print("Přihlášeno")
        return token

    except Exception as e:
        print("Login error:", e)
        return None


token = login()
token_time = time.time()

if not token:
    exit()

# Odeslání a ukládání dat
def send_data(payload):
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"token={token}"
    }

    try:
        r = requests.post(SERVER_URL, json=payload, headers=headers, timeout=5)

        if r.status_code == 401:
            print("Neautorizováno")

        print("Odesláno:", r.status_code)

    except Exception:
        print("Server je nedostupný")
        pending_batches.append(payload)


def flush_pending():
    global pending_batches

    if not pending_batches:
        return

    print("Odesílám uložená data")

    for p in pending_batches:
        try:
            requests.post(SERVER_URL, json=p, timeout=5)
        except:
            return

    pending_batches = []

# Kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

start_time = time.time()

fps_time = time.time()
fps_counter = 0

print("Spuštěno")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True, conf=MIN_CONF, verbose=False)

    if time.time() - start_time >= RESET_INTERVAL:

        payload = {
            "stationId": STATION_ID,
            "recordTime": datetime.utcnow().isoformat(),
            "people": TARGET_CLASSES["person"],
            "bikes": TARGET_CLASSES["bicycle"],
            "cars": TARGET_CLASSES["car"]
        }

        print("\n Odesílám:", TARGET_CLASSES)

        send_data(payload)
        flush_pending()

        for k in TARGET_CLASSES:
            TARGET_CLASSES[k] = 0

        counted_ids.clear()
        start_time = time.time()

    # ReLogin
    if time.time() - token_time > TOKEN_LIFETIME:
        print("Refresh login")
        token = login()
        token_time = time.time()

    # Detekce objektů
    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue

        for box in boxes:
            cls_id = int(box.cls[0])
            class_name = CLASS_NAMES[cls_id]

            track_id = int(box.id[0]) if box.id is not None else None

            if class_name in TARGET_CLASSES and track_id is not None:

                if track_id not in counted_ids:
                    TARGET_CLASSES[class_name] += 1
                    counted_ids.add(track_id)

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, class_name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # UI
    y = 30
    for k, v in TARGET_CLASSES.items():
        cv2.putText(frame, f"{k}: {v}", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y += 30

    # FPS
    fps_counter += 1
    if time.time() - fps_time >= 1:
        print("FPS:", fps_counter)
        fps_counter = 0
        fps_time = time.time()

    cv2.imshow("YOLO Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()