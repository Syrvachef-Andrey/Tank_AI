import cv2
from ultralytics import YOLO

# Параметры
x_len = 640  # Ширина изображения
y_len = 480  # Высота изображения
angle_tracking_camera_horizontal = 60  # Угол обзора камеры по горизонтали
angle_tracking_camera_vertical = 40  # Угол обзора камеры по вертикали
name_of_object = None

# Загрузка модели YOLO
model = YOLO("/runs/detect/train/weights/best.pt")

# Инициализация видеопотока
cap = cv2.VideoCapture(0)

def calculate_coordinates_of_point(coordinates_list):
    """Вычисляет координаты центра объекта."""
    if len(coordinates_list) == 4:
        x_min, y_min, x_max, y_max = coordinates_list
        center_x = int((x_min + x_max) // 2)
        center_y = int((y_min + y_max) // 2)
        return center_x, center_y
    return None

def calculate_object_tracking(x_len, y_len, center_point, angle_horizontal, angle_vertical):
    """Вычисляет углы для сервоприводов с учетом ограничений."""
    if not center_point:
        return None

    center_x, center_y = center_point

    # Смещение центра объекта относительно центра изображения
    dx = center_x - x_len // 2
    dy = center_y - y_len // 2

    # Расчет углов
    angle_x = (dx / (x_len // 2)) * (angle_horizontal / 2)
    angle_y = (dy / (y_len // 2)) * (angle_vertical / 2)

    # Преобразование углов в диапазон сервоприводов
    # Сервопривод X: 0° (право) — 180° (лево)
    servo_x = 90 - angle_x  # 90° — центр, минус для инверсии направления
    servo_x = max(0, min(180, servo_x))  # Ограничение в диапазоне [0, 180]

    # Сервопривод Y: 45° (низ) — 180° (верх)
    servo_y = 112.5 - angle_y  # 112.5° — центр, минус для инверсии направления
    servo_y = max(45, min(180, servo_y))  # Ограничение в диапазоне [45, 180]

    return servo_x, servo_y

while cap.isOpened():
    success, frame = cap.read()

    if success:
        # Детекция объектов с помощью YOLO
        results = model.track(frame, persist=True, conf=0.2)
        annotated_frame = results[0].plot()

        boxes = results[0].boxes
        coordinates_list = []
        if len(boxes) > 0:
            for box in boxes:
                class_id = model.names[box.cls.item()]
                name_of_object = class_id
            confidences = boxes.conf
            max_confidence_idx = confidences.argmax()
            coordinates = boxes.xyxy[max_confidence_idx].tolist()
            coordinates_list.extend(coordinates)  # Добавляем координаты напрямую
        else:
            name_of_object = None
        # Вычисление центра объекта
        center_point = calculate_coordinates_of_point(coordinates_list)

        if center_point:
            # Отображение центра объекта на изображении
            cv2.circle(annotated_frame, center_point, 5, (0, 255, 0), -1)

            # Расчет углов для сервоприводов
            angles = calculate_object_tracking(x_len, y_len, center_point,
                                               angle_tracking_camera_horizontal,
                                               angle_tracking_camera_vertical)

            if angles:
                servo_x, servo_y = angles
                if name_of_object is not None:
                    print(name_of_object)
                print(f"Углы для сервоприводов: X={servo_x:.2f}°, Y={servo_y:.2f}°")

        # Отображение центральных линий
        cv2.line(annotated_frame, (x_len // 2, 0), (x_len // 2, y_len), (255, 0, 0), thickness=2)
        cv2.line(annotated_frame, (0, y_len // 2), (x_len, y_len // 2), (255, 0, 0), thickness=2)

        # Показ изображения
        cv2.imshow("TANKS", annotated_frame)

        # Выход по нажатию 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Освобождение ресурсов
cap.release()
cv2.destroyAllWindows()