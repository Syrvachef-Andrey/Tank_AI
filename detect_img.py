from ultralytics import YOLO

model = YOLO("/home/andrey/tank_AI/Tank_AI/runs/detect/train2/weights/best.pt")

# Выполнение обнаружения объектов на изображении
results = model.predict(source="img.png", save=True, conf=0.5)

# Вывод результатов
for result in results:
    print("Обнаруженные объекты:")
    for box in result.boxes:
        class_id = model.names[box.cls.item()]  # Имя класса
        confidence = box.conf.item()  # Уверенность
        print(f"Класс: {class_id}, Уверенность: {confidence}")

# Результаты сохраняются в папку 'runs/detect/predict' по умолчанию
print("Результаты сохранены в папке 'runs/detect/predict'")