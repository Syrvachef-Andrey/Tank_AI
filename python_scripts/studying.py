from ultralytics import YOLO, settings
model = YOLO("../yolo_models/yolo11n.pt")

results = model.train(data='/home/andrey/PycharmProjects/Tank_AI/dataset/data.yaml', epochs=500 , imgsz=640)
