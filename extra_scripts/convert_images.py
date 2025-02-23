import cv2
import os
import shutil

# Путь к папке с изображениями
input_folder = '/home/andrey/dataset_v2/soilders'
output_folder = '/home/andrey/dataset_v2/soilders_jpg'

# Создаем папку для сохранения изображений в формате JPG, если она не существует
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Перебираем все файлы в папке
for filename in os.listdir(input_folder):
    # Полный путь к файлу
    file_path = os.path.join(input_folder, filename)

    # Если файл уже в формате JPG, просто копируем его
    if filename.lower().endswith('.jpg'):
        new_file_path = os.path.join(output_folder, filename)
        shutil.copy(file_path, new_file_path)
        print(f"Скопирован JPG файл: {filename}")
    # Если файл является изображением другого формата, конвертируем его в JPG
    elif filename.lower().endswith(('.png', '.bmp', '.tiff', '.gif', '.jpeg', '.webp')):
        # Загружаем изображение с помощью OpenCV
        image = cv2.imread(file_path)

        # Если изображение успешно загружено
        if image is not None:
            # Формируем новое имя файла с расширением .jpg
            new_filename = os.path.splitext(filename)[0] + '.jpg'
            new_file_path = os.path.join(output_folder, new_filename)

            # Сохраняем изображение в формате JPG
            cv2.imwrite(new_file_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # 90 - качество JPG
            print(f"Конвертировано: {filename} -> {new_filename}")
        else:
            print(f"Ошибка загрузки изображения: {filename}")
    else:
        print(f"Файл не является изображением: {filename}")

print("Обработка завершена!")