import cv2
from ultralytics import YOLO
import serial
import time

koeff = 1.1
name_of_object = None
x_len = 640
y_len = 480
angle_tracking_camera_horizontal = 60
angle_tracking_camera_vertical = 40
names_of_objects = ['abrams', 'btr-80', 'btr-striker', 'leopard', 'T-90', 'destroyed_tank']

port = '/dev/ttyUSB0'
arduino = serial.Serial(port, 115200, timeout=1)
time.sleep(2)

model_ncnn_path = "/home/andrey/tank_ai/yolo_model/best_ncnn_model"
model_path = "/home/andrey/PycharmProjects/Tank_AI/runs/detect/train/weights/best.pt"
model = YOLO(model_path)
if model is None:
    print("no yolo model")
    exit(1)

# Инициализация веб-камеры
cap = cv2.VideoCapture(0)  # 0 — индекс веб-камеры по умолчанию
if not cap.isOpened():
    print("Ошибка: Не удалось открыть веб-камеру.")
    exit(1)

# Установка разрешения камеры
cap.set(cv2.CAP_PROP_FRAME_WIDTH, x_len)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, y_len)

# Размер окна для скользящего среднего
window_size = 5

# Списки для хранения последних значений углов
servo_x_values = []
servo_y_values = []


def send_list(data_list):
    message = ",".join(map(str, data_list)) + "\n"
    arduino.write(message.encode())
    print(f"Sent: {data_list}")

    response = arduino.readline().decode().strip()
    while not response:
        response = arduino.readline().decode().strip()
    print(f"Received: {response}")


def calculate_coordinates_of_point(coordinates_list):
    if len(coordinates_list) == 4:
        x_min, y_min, x_max, y_max = coordinates_list
        center_x = int((x_min + x_max) // 2)
        center_y = int((y_min + y_max) // 2)
        return center_x, center_y
    return None


def calculate_object_tracking(x_len, y_len, center_point, angle_horizontal, angle_vertical):
    if not center_point:
        return None

    center_x, center_y = center_point

    dx = center_x - x_len // 2
    dy = center_y - y_len // 2

    angle_x = (dx / (x_len // 2)) * (angle_horizontal / 2)
    angle_y = (dy / (y_len // 2)) * (angle_vertical / 2)

    servo_x = 90 - angle_x
    servo_x = max(0, min(180, servo_x))

    servo_y = 112.5 - angle_y
    servo_y = max(45, min(180, servo_y))

    return servo_x, servo_y


def moving_average(values, new_value, window_size):
    """
    Добавляет новое значение в список и возвращает среднее значение.
    :param values: Список последних значений.
    :param new_value: Новое значение для добавления.
    :param window_size: Размер окна (количество значений для усреднения).
    :return: Среднее значение.
    """
    values.append(new_value)
    if len(values) > window_size:
        values.pop(0)  # Удаляем самое старое значение
    return sum(values) / len(values)


try:
    while True:
        # Захват кадра с веб-камеры
        ret, frame = cap.read()
        if not ret:
            print("Ошибка: Не удалось захватить кадр.")
            break

        # Детекция объекта
        results = model.track(frame, persist=True, conf=0.2, max_det=1)

        if results and results[0].boxes:
            annotated_frame = results[0].plot()  # Визуализация bounding box
            boxes = results[0].boxes
            coordinates_list = []
            if len(boxes) > 0:
                for box in boxes:
                    name_of_object = model.names[box.cls.item()]
                confidences = boxes.conf
                max_confidence_idx = confidences.argmax()
                coordinates = boxes.xyxy[max_confidence_idx].tolist()
                coordinates_list.extend(coordinates)
            else:
                name_of_object = None

            center_point = calculate_coordinates_of_point(coordinates_list)
            if center_point:
                print(f"Detect image {center_point}")
                if 0 <= center_point[0] < x_len and 0 <= center_point[1] < y_len:
                    # Визуализация центра объекта
                    cv2.circle(annotated_frame, center_point, 5, (0, 255, 0), -1)

                    angles = calculate_object_tracking(x_len, y_len, center_point,
                                                       angle_tracking_camera_horizontal,
                                                       angle_tracking_camera_vertical)

                    if angles:
                        servo_x, servo_y = angles

                        # Применяем скользящее среднее для сглаживания углов
                        servo_x_smoothed = moving_average(servo_x_values, servo_x, window_size)
                        servo_y_smoothed = moving_average(servo_y_values, servo_y, window_size)

                        print(f"Smoothed angles for servo: X={servo_x_smoothed:.2f}, Y={servo_y_smoothed:.2f}")

                        # Коррекция угла servo_x (если нужно)
                        if servo_x_smoothed > 90:
                            servo_x_smoothed += 7
                        elif servo_x_smoothed < 90:
                            servo_x_smoothed -= 7

                        # Формируем список для отправки
                        servo_list = [servo_x_smoothed, servo_y_smoothed]
                        for i in range(len(names_of_objects)):
                            if name_of_object == names_of_objects[i]:
                                servo_list.append(i)
                        send_list(servo_list)
                else:
                    print("Coordinates are over the image")
            else:
                print("Center of object is not counted.")
        else:
            # Если объект не обнаружен
            annotated_frame = frame.copy()
            print("no detection on image.")

        # Визуализация центра кадра
        cv2.line(annotated_frame, (x_len // 2, 0), (x_len // 2, y_len), (255, 0, 0), thickness=2)
        cv2.line(annotated_frame, (0, y_len // 2), (x_len, y_len // 2), (255, 0, 0), thickness=2)

        # Отображение кадра
        cv2.imshow("TANKS", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()