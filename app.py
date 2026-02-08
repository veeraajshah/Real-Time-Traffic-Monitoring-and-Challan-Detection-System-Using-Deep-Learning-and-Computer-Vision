from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import cv2, os, urllib.parse
from detector import detect_objects
from ocr import recognize_plate
from utils import get_challan_status, log_results

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.abspath("../data")
current_video = None
latest_metadata = []
frame_count = 0

@app.get("/get_videos")
def get_videos():
    return {"videos": [f for f in os.listdir(DATA_DIR) if f.endswith(".mp4")]}

@app.get("/set_video")
def set_video(video: str):
    global current_video
    video = urllib.parse.unquote(video)
    current_video = os.path.join(DATA_DIR, video)
    return {"status": "ok"}

def generate_frames():
    global latest_metadata, frame_count

    cap = cv2.VideoCapture(current_video)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_count += 1
        frame = cv2.resize(frame, (960, 540))

        detections = []
        if frame_count % 3 == 0:  # process every 3rd frame
            detections = detect_objects(frame)
            latest_metadata = []

            for det in detections:
                plate = ""
                challan = {"status": "N/A"}

                if det["label"] in ["car", "bus", "truck", "motorbike"] and det["confidence"] > 60:
                    plate = recognize_plate(frame, det["bbox"])
                    challan = get_challan_status(plate)

                det["license_plate"] = plate
                det["challan"] = challan
                latest_metadata.append(det)
                log_results(det)

        for det in latest_metadata:
            x1, y1, x2, y2 = det["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 180), 2)
            cv2.putText(frame,
                        f"{det['label']} {det['confidence']}%",
                        (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 180), 2)

            if det["license_plate"]:
                cv2.putText(frame,
                            f"Plate: {det['license_plate']}",
                            (x1, y2 + 18),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55, (255, 255, 0), 2)

        _, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/metadata")
def metadata():
    return JSONResponse(latest_metadata)
