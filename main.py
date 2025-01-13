import cv2

from ultralytics import YOLO

model = YOLO("/home/andrey/PycharmProjects/Tank_AI/runs/detect/train2/weights/best.pt")

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model.track(frame, persist=True, conf=0.8)

        annotated_frame = results[0].plot()

        cv2.imshow("TANKS", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyWindow()