import easyocr
import cv2

reader = easyocr.Reader(['en'], gpu=False)

def recognize_plate(frame, bbox):
    x1,y1,x2,y2 = bbox
    plate_img = frame[y1:y2, x1:x2]

    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(gray)

    if results:
        return results[0][1]
    return "Not Detected"
