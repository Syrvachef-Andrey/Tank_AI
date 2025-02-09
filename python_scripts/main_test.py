import cv2
from ultralytics import YOLO
import serial
import numpy as np
import time


class Arduino:
    def __init__(self):
        self.port = '/dev/ttyUSB1'
        self.arduino = serial.Serial(self.port, 115200, timeout=1)

    def send_list(self, data_list):
        message = ",".join(map(str, data_list)) + "\n"
        self.arduino.write(message.encode())
        print(f"Sent: {data_list}")

    def collect_data(self):
        response = self.arduino.readline().decode().strip()
        if not response:
            print("No data from arduino")
            return ''
        else:
            print(f"Received: {response}")
            return response

class Computer:
    def __init__(self):
        self.past_name_of_object = None
        self.name_of_object = None
        self.x_len = 640
        self.y_len = 480
        self.angle_tracking_camera_horizontal = 60
        self.angle_tracking_camera_vertical = 40
        self.names_of_objects = ['abrams', 'btr-80', 'btr-striker', 'leopard', 'T-90', 'destroyed_tank']

        self.string_from_arduino = ''

        self.model_ncnn_path = "/home/andrey/tank_ai/yolo_model/best_ncnn_model"
        self.model_path = "/home/andrey/PycharmProjects/Tank_AI/runs/detect/train4/weights/best.pt"
        self.model = YOLO(self.model_path)
        if self.model is None:
            print("no yolo model")
            exit(1)

        self.cap = cv2.VideoCapture(0)  # 0 — индекс веб-камеры по умолчанию
        if not self.cap.isOpened():
            print("Ошибка: Не удалось открыть веб-камеру.")
            exit(1)

        # Установка разрешения камеры
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.x_len)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.y_len)

        # Размер окна для скользящего среднего
        self.window_size = 5

        # Списки для хранения последних значений координат центра
        self.center_x_values = []
        self.center_y_values = []

        # Списки для хранения последних значений углов
        self.servo_x_values = []
        self.servo_y_values = []

        self.arduino_class = Arduino()

    def calculate_coordinates_of_point(self, coordinates_list):
        if len(coordinates_list) == 4:
            x_min, y_min, x_max, y_max = coordinates_list
            center_x = int((x_min + x_max) // 2)
            center_y = int((y_min + y_max) // 2)
            return center_x, center_y
        return None

    def vector(self, center_point, x_len, y_len):
        delta_x, delta_y = 0, 0
        object_x, object_y = center_point[0], center_point[1]
        image_center_x = x_len // 2
        image_center_y = y_len // 2
        traking_vector_len = np.sqrt((image_center_x - object_x) ** 2 + (image_center_y - object_y) ** 2)
        if traking_vector_len == 0:
            return delta_x, delta_y
        koeff = int(np.log(traking_vector_len) / 3)
        if traking_vector_len <= 80:
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

    def main(self):
        try:
            angle_x, angle_y = 90, 90
            while True:
                # Захват кадра с веб-камеры
                ret, frame = self.cap.read()
                if not ret:
                    print("Ошибка: Не удалось захватить кадр.")
                    break

                # Детекция объекта
                results = self.model.track(frame, persist=True, conf=0.2, max_det=1)

                if results and results[0].boxes:
                    annotated_frame = results[0].plot()  # Визуализация bounding box
                    boxes = results[0].boxes
                    coordinates_list = []
                    if len(boxes) > 0:
                        for box in boxes:
                            self.name_of_object = self.model.names[box.cls.item()]
                        confidences = boxes.conf
                        max_confidence_idx = confidences.argmax()
                        coordinates = boxes.xyxy[max_confidence_idx].tolist()
                        coordinates_list.extend(coordinates)
                    else:
                        self.name_of_object = None

                    center_point = self.calculate_coordinates_of_point(coordinates_list)
                    if center_point:
                        dx, dy = self.vector(center_point, self.x_len, self.y_len)
                        cv2.circle(annotated_frame, center_point, 2, (0, 0, 255), thickness=2)
                        cv2.line(annotated_frame, (self.x_len // 2, self.y_len // 2), center_point, (0, 255, 0), thickness=2)
                        angle_x += dx
                        angle_y += dy
                        if angle_x >= 180:
                            angle_x = 90
                        elif angle_x <= 0:
                            angle_x = 90
                        elif angle_y >= 180:
                            angle_y = 90
                        elif angle_y <= 0:
                            angle_y = 90
                        servo_list = [angle_x, angle_y]
                        for i in range(len(self.names_of_objects)):
                            if self.names_of_objects[i] == self.name_of_object:
                                servo_list.append(i)
                        self.arduino_class.send_list(servo_list)
                        self.string_from_arduino = self.arduino_class.collect_data()
                    self.past_name_of_object = self.name_of_object
                else:
                    # Если объект не обнаружен
                    annotated_frame = frame.copy()
                    self.string_from_arduino = None
                    print("no detection on image.")

                # Визуализация центра кадра
                cv2.line(annotated_frame, (self.x_len // 2, 0), (self.x_len // 2, self.y_len), (255, 0, 0), thickness=2)
                cv2.line(annotated_frame, (0, self.y_len // 2), (self.x_len, self.y_len // 2), (255, 0, 0), thickness=2)

                cv2.imshow("TANKS", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            # Освобождение ресурсов
            self.cap.release()
            cv2.destroyAllWindows()
            self.arduino_class.arduino.close()


if __name__ == "__main__":
    computer_class = Computer()
    computer_class.main()