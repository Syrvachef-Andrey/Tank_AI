import cv2

from ultralytics import YOLO

coordinates_list = []
coordinate_of_points = ()

model = YOLO("/home/andrey/PycharmProjects/Tank_AI/runs/detect/train2/weights/best.pt")

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model.track(frame, persist=True, conf=0.8)

        annotated_frame = results[0].plot()

        boxes =results[0].boxes
        print(boxes)
        for box in boxes:
            coordinates = box.xyxy.tolist()
            for lst in coordinates:
                for i in lst:
                    coordinates_list.append(i)
                    if len(coordinates_list) == 4:
                        coordinate_of_box_x_min, coordinate_of_box_y_min, coordinate_of_box_x_max, coordinate_of_box_y_max =\
                            coordinates_list[0], coordinates_list[1], coordinates_list[2], coordinates_list[3]
                        print(coordinate_of_box_x_min, coordinate_of_box_y_min, coordinate_of_box_x_max, coordinate_of_box_y_max)
                        coordinate_of_points = (int((abs(coordinate_of_box_x_max + coordinate_of_box_x_min) // 2)),
                                                int((abs(coordinate_of_box_y_max + coordinate_of_box_y_min)) // 2))
        print(coordinate_of_points)
        if len(coordinate_of_points) == 2:
            cv2.circle(annotated_frame, coordinate_of_points, 5, (0, 255, 0), -1)

        cv2.imshow("TANKS", annotated_frame)

        coordinates_list.clear()
        coordinate_of_points = ()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyWindow()