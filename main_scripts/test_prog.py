import time
from ultralytics import YOLO
import cv2
import configparser


class YoloCam:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.path_to_yolo_model = self.config['config_test']['path_to_test_model']
        self.model = YOLO(self.path_to_yolo_model)

        self.cam = int(self.config['config_test']['cam_port'])
        self.x_size_of_cam = 640
        self.y_size_of_cam = 640

        for i in range(5):
            self.cap = cv2.VideoCapture(self.cam)
            if not self.cap.isOpened():
                print("Error: Not available to open the camera\n Trying in one second")
                self.cam += 1
                time.sleep(1)
            else:
                break
        else:
            print("Can not open the camera")
            exit(1)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.x_size_of_cam)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.y_size_of_cam)

    def output(self):
        print(self.cam, type(self.cam), self.path_to_yolo_model)

    def main(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Ошибка: Не удалось захватить кадр")
                break

            results = self.model.track(frame, persist=True, conf=0.2)

            annotated_frame = results[0].plot()

            cv2.imshow("Test_prog", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


computer_1 = YoloCam()
computer_1.output()
computer_1.main()