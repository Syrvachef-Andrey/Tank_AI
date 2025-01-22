from ultralytics import YOLO

model = YOLO("/home/andrey/PycharmProjects/Tank_AI/runs/detect/train/weights/best.pt")

results = model.predict(source="/home/andrey/PycharmProjects/Tank_AI/images_for_test/img_3.png", save=True, conf=0.9)

for result in results:
    print("Обнаруженные объекты:")
    for box in result.boxes:
        class_id = model.names[box.cls.item()]
        confidence = box.conf.item()
        print(f"Класс: {class_id}, Уверенность: {confidence}")

print("Результаты сохранены в папке 'runs/detect/predict'")