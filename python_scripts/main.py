import cv2
from ultralytics import YOLO
import serial
import numpy as np
import time

name_of_object = None
x_len = 640
y_len = 480
angle_tracking_camera_horizontal = 60
angle_tracking_camera_vertical = 40
names_of_objects = ['abrams', 'btr-80', 'btr-striker', 'leopard', 'T-90', 'destroyed_tank']

port = '/dev/ttyUSB0'
arduino = serial.Serial(port, 115200, timeout=1)

model_ncnn_path = "/home/andrey/tank_ai/yolo_model/best_ncnn_model"
model_path = "/home/andrey/PycharmProjects/Tank_AI/runs/detect/train4/weights/best.pt"
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

# Списки для хранения последних значений координат центра
center_x_values = []
center_y_values = []

# Списки для хранения последних значений углов
servo_x_values = []
servo_y_values = []


def send_list(data_list):
    message = ",".join(map(str, data_list)) + "\n"
    arduino.write(message.encode())
    print(f"Sent: {data_list}")

    response = arduino.readline().decode().strip()
    print(f"Received: {response}")


def calculate_coordinates_of_point(coordinates_list):
    if len(coordinates_list) == 4:
        x_min, y_min, x_max, y_max = coordinates_list
        center_x = int((x_min + x_max) // 2)
        center_y = int((y_min + y_max) // 2)
        return center_x, center_y
    return None

def vector(center_point, x_len, y_len):
    delta_x, delta_y = 0, 0
    object_x, object_y = center_point[0], center_point[1]
    image_center_x = x_len // 2
    image_center_y = y_len // 2
    traking_vector_len = np.sqrt((image_center_x - object_x) ** 2 + (image_center_y - object_y) ** 2)
    if traking_vector_len == 0:
        return delta_x, delta_y
    koeff = int(np.log(traking_vector_len) / 3)
    if traking_vector_len <= 70:
        delta_x = 0
        delta_y = 0
    elif traking_vector_len > 70 and 0 < object_x <= 320 and 0 < object_y <= 240:
        delta_x += koeff
        delta_y += koeff
    elif traking_vector_len > 70 and 320 < object_x <= 640 and 0 < object_y <= 240:
        delta_x -= koeff
        delta_y += koeff
    elif traking_vector_len > 70 and 0 < object_x <= 320 and 240 < object_y <= 480:
        delta_x += koeff
        delta_y -= koeff
    elif traking_vector_len > 70 and 320 < object_x <= 640 and 240 < object_y <= 480:
        delta_x -= koeff
        delta_y -= koeff
    return delta_x, delta_y

try:
    angle_x, angle_y = 90, 90
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
                dx, dy = vector(center_point, x_len, y_len)
                cv2.circle(annotated_frame, center_point, 2, (0, 0, 255), thickness=2)
                cv2.line(annotated_frame, (x_len // 2, y_len // 2), center_point, (0, 255, 0), thickness=2)
                angle_x += dx
                angle_y += dy
                if angle_x >= 180:
                    angle_x = 90
                elif angle_x <= 0:
                    angle_x = 90
                elif angle_y >= 180:
                    angle_x = 90
                elif angle_y <= 0:
                    angle_y = 90
                servo_list = [angle_x, angle_y]
                for i in range(len(names_of_objects)):
                    if names_of_objects[i] == name_of_object:
                        servo_list.append(names_of_objects[i])
                send_list(servo_list)

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