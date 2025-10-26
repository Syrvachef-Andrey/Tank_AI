import cv2
from ultralytics import YOLO
import serial
import numpy as np
import configparser
import torch
from simple_pid import PID


class Arduino:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.port = self.config["arduino"]["port"]
        self.arduino = serial.Serial(self.port, 115200, timeout=0.1)

    def send(self, data):
        message = ",".join(map(str, data))
        self.arduino.write(message.encode())
        print(f"Sent: {data}")

    def collect_data(self):
        response = self.arduino.readline().decode().strip()
        if not response:
            print("No data from arduino")
            return None
        print(f"Received: {response}")
        return response


class Computer:
    def __init__(self):
        self.xlen = 640
        self.ylen = 480
        self.angle_h = 60
        self.angle_v = 40
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.model = YOLO(self.config["yolo"]["path_to_model"])
        self.cap = cv2.VideoCapture(1)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.arduino = Arduino()

        # PID-регуляторы для X и Y
        self.pid_x = PID(1.0, 0.1, 0.07, setpoint=self.xlen // 2)
        self.pid_x.output_limits = (-90, 90)  # Ограничение угла
        self.pid_y = PID(1.0, 0.1, 0.07, setpoint=self.ylen // 2)
        self.pid_y.output_limits = (-90, 90)

        self.servo_x = 90
        self.servo_y = 90

    def calculate_center(self, box):
        # Получаем центр объекта (координаты YOLO)
        xmin, ymin, xmax, ymax = box
        cx = int((xmin + xmax) / 2)
        cy = int((ymin + ymax) / 2)
        return cx, cy

    def main(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                results = self.model.track(frame, persist=True, conf=0.2, max_det=1)
                if results and results[0].boxes:
                    boxes = results[0].boxes.xyxy.tolist()
                    if boxes:
                        center_x, center_y = self.calculate_center(boxes[0])

                        # ПИД-регуляция: вычисляем угол перехода для сервоприводов
                        delta_x = self.pid_x(center_x)
                        delta_y = self.pid_y(center_y)

                        # Плавно изменяем углы ардуино (сервоприводов)
                        self.servo_x = int(np.clip(90 + delta_x, 0, 180))
                        self.servo_y = int(np.clip(90 + delta_y, 0, 180))

                        print(f"PID X: {delta_x:.2f}, Servo X: {self.servo_x}")
                        print(f"PID Y: {delta_y:.2f}, Servo Y: {self.servo_y}")

                        self.arduino.send([self.servo_x, self.servo_y])

                    else:
                        print("No detection on image.")
                else:
                    print("No results.")

                cv2.imshow("TANKS", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.arduino.arduino.close()


if __name__ == "__main__":
    comp = Computer()
    comp.main()
