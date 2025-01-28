from ultralytics import YOLO, settings
import torch
torch.cuda.empty_cache()
model = YOLO("yolo11l.pt")

results = model.train(data='/home/andrey/PycharmProjects/Tank_AI/dataset/data.yaml', epochs=500 , imgsz=640)
