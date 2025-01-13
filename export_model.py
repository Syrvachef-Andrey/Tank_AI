from ultralytics import YOLO

model = YOLO("/home/andrey/PycharmProjects/Tank_AI/runs/detect/train2/weights/best.pt")

model.export(format="ncnn")