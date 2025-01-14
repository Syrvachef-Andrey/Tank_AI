import cv2

from ultralytics import YOLO

koefficent_of_speed = 0.75
coordinates_list = []
coordinate_of_points = ()
object_tracking_list = list()
x_len = 640
y_len = 480

model = YOLO("/home/andrey/PycharmProjects/Tank_AI/runs/detect/train2/weights/best.pt")

cap = cv2.VideoCapture(0)

def calculate_coordinates_of_point(coordinates_list):
    coordinate_of_points = ()
    if len(coordinates_list) == 4:
        coordinate_of_box_x_min, coordinate_of_box_y_min, coordinate_of_box_x_max, coordinate_of_box_y_max = \
            coordinates_list[0], coordinates_list[1], coordinates_list[2], coordinates_list[3]
        print(coordinate_of_box_x_min, coordinate_of_box_y_min, coordinate_of_box_x_max, coordinate_of_box_y_max)
        coordinate_of_points = (int((abs(coordinate_of_box_x_max + coordinate_of_box_x_min) // 2)),
                                int((abs(coordinate_of_box_y_max + coordinate_of_box_y_min)) // 2))
    print(coordinate_of_points)
    return coordinate_of_points

def calculate_object_tracking(x_len, y_len, list_of_center):
    list_of_numbers = [] # 1 - forward, 2 - right, 3 - left, 4 - backward
    if 0 < list_of_center[0] < x_len // 2 and 0 < list_of_center[1] < y_len // 2:
        print('alfa')
        list_of_numbers = [4, 1, (abs(x_len // 2 - list_of_center[0]) * koefficent_of_speed / 90) + 90,
                           (abs(y_len // 2 - list_of_center[1]) * koefficent_of_speed / 90) + (180 - 45) // 2]
    elif x_len // 2 < list_of_center[0] < x_len and 0 < list_of_center[1] < y_len // 2:
        print('betta')
        list_of_numbers = [2, 1, (abs(x_len // 2 - list_of_center[0]) * koefficent_of_speed / 90),
                           (abs(y_len // 2 - list_of_center[1]) * koefficent_of_speed / 90) + (180 - 45) // 2]
    elif 0 < list_of_center[0] < x_len // 2 and y_len // 2 < list_of_center[1] < y_len:
        print('gamma')
        list_of_numbers = [4, 3, (abs(x_len // 2 - list_of_center[0]) * koefficent_of_speed / 90) + 90,
                           (abs(y_len // 2 - list_of_center[1]) * koefficent_of_speed / 45)]
    else:
        list_of_numbers = [2, 3, (abs(x_len // 2 - list_of_center[0]) * koefficent_of_speed / 90),
                           (abs(y_len // 2 - list_of_center[1]) * koefficent_of_speed / 45)]
        print('tetta')
    return list_of_numbers

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model.track(frame, persist=True, conf=0.2)
        annotated_frame = results[0].plot()

        boxes =results[0].boxes
        for box in boxes:
            coordinates = box.xyxy.tolist()
            for lst in coordinates:
                for i in lst:
                    coordinates_list.append(i)
                    coordinate_of_points = calculate_coordinates_of_point(coordinates_list)

        if len(coordinate_of_points) == 2:
            cv2.circle(annotated_frame, coordinate_of_points, 5, (0, 255, 0), -1)

            object_tracking_list = calculate_object_tracking(x_len, y_len, coordinate_of_points)

            print(object_tracking_list)

        cv2.line(annotated_frame, (x_len // 2, 0), (x_len // 2, y_len), (255, 0, 0), thickness=2)
        cv2.line(annotated_frame, (0, y_len // 2), (x_len, y_len // 2), (255, 0, 0), thickness=2)

        cv2.imshow("TANKS", annotated_frame)

        coordinates_list.clear()
        coordinate_of_points = ()
        object_tracking_list.clear()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyWindow()