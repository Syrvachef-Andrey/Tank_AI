from ultralytics import YOLO, settings
model = YOLO("yolo11s.pt")

print(settings)

results = model.train(data='/home/andrey/Загрузки/tanks.zip', epochs=40, imgsz=180)