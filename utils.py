import json, csv, os, datetime

RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)

CSV_PATH = os.path.join(RESULT_DIR, "detections.csv")
JSON_PATH = os.path.join(RESULT_DIR, "detections.json")

def get_challan_status(plate):
    with open("challan_db.json") as f:
        db = json.load(f)
    return db.get(plate, {"status": "No Pending Challan"})

def log_results(data):
    timestamp = datetime.datetime.now().isoformat()
    data["timestamp"] = timestamp

    with open(JSON_PATH,"a") as f:
        f.write(json.dumps(data) + "\n")

    with open(CSV_PATH,"a",newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp, data["label"], data["confidence"],
            data.get("license_plate",""),
            data.get("challan",{}).get("status","")
        ])
