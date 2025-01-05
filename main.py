from ultralytics import YOLO, settings
model = YOLO("yolo11s.pt")

print(settings)

results = model.train(data='/home/andrey/tank_AI/Tank_AI/dataset/data.yaml', epochs=150, imgsz=180)