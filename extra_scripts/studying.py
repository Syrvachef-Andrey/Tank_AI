from ultralytics import YOLO

model = YOLO("yolo11l.pt")

results = model.train(data='/home/andrey/PycharmProjects/Tank_AI/dataset/data.yaml', epochs=500 , imgsz=640, batch=16)