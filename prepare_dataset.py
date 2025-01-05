import glob
import os
import random
from math import floor
from tqdm import tqdm
import shutil

input_folders = [
    'dataset/tanks/abrams/images'
]

BASE_DIR_ABSOLUTE = "/home/andrey/tank_AI/Tank_AI"
OUT_DIR = 'dataset/tanks_prepared/abrams'

OUT_TRAIN_IMAGES = os.path.join(OUT_DIR, 'train/images')
OUT_TRAIN_LABELS = os.path.join(OUT_DIR, 'train/labels')
OUT_VAL_IMAGES = os.path.join(OUT_DIR, 'val/images')
OUT_VAL_LABELS = os.path.join(OUT_DIR, 'val/labels')

coeff = [80, 20]
exceptions = ['classes']

if int(coeff[0]) + int(coeff[1]) > 100:
    print("Coeff can't exceed 100%.")
    exit(1)

print(f"Preparing images data by {coeff[0]}/{coeff[1]} rule.")
print(f"Source folders: {len(input_folders)}")
print("Gathering data ...")

source = {}
for sf in input_folders:
    source.setdefault(sf, [])

    os.chdir(BASE_DIR_ABSOLUTE)
    os.chdir(sf)

    for filename in glob.glob("*.jpg"):
        source[sf].append(filename)

train = {}
val = {}
for sk, sv in source.items():
    random.shuffle(sv)  # Перемешиваем данные
    split_index = floor(len(sv) * (coeff[0] / 100))  # Вычисляем индекс разделения

    train.setdefault(sk, [])
    val.setdefault(sk, [])
    train[sk] = sv[:split_index]  # Первые 80% для тренировки
    val[sk] = sv[split_index:]  # Остальные 20% для валидации

train_sum = 0
val_sum = 0

for sk, sv in train.items():
    train_sum += len(sv)

for sk, sv in val.items():
    val_sum += len(sv)

print(f"\nOverall TRAIN images count: {train_sum}")
print(f"Overall VAL images count: {val_sum}")

os.chdir(BASE_DIR_ABSOLUTE)
print("\nCopying TRAIN source items to prepared folder ...")
for sk, sv in tqdm(train.items()):
    for item in tqdm(sv):
        # Копируем изображения
        imgfile_source = os.path.join(BASE_DIR_ABSOLUTE, sk, item)
        imgfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_TRAIN_IMAGES, item)

        os.makedirs(os.path.dirname(imgfile_dest), exist_ok=True)
        shutil.copyfile(imgfile_source, imgfile_dest)

        # Копируем соответствующие txt файлы
        txt_file = os.path.splitext(item)[0] + '.txt'
        txtfile_source = os.path.join(BASE_DIR_ABSOLUTE, 'dataset/tanks/abrams/labels', txt_file)
        txtfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_TRAIN_LABELS, txt_file)

        if os.path.exists(txtfile_source):
            os.makedirs(os.path.dirname(txtfile_dest), exist_ok=True)
            shutil.copyfile(txtfile_source, txtfile_dest)

os.chdir(BASE_DIR_ABSOLUTE)
print("\nCopying VAL source items to prepared folder ...")
for sk, sv in tqdm(val.items()):
    for item in tqdm(sv):
        # Копируем изображения
        imgfile_source = os.path.join(BASE_DIR_ABSOLUTE, sk, item)
        imgfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_VAL_IMAGES, item)

        os.makedirs(os.path.dirname(imgfile_dest), exist_ok=True)
        shutil.copyfile(imgfile_source, imgfile_dest)

        # Копируем соответствующие txt файлы
        txt_file = os.path.splitext(item)[0] + '.txt'
        txtfile_source = os.path.join(BASE_DIR_ABSOLUTE, 'dataset/tanks/abrams/labels', txt_file)
        txtfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_VAL_LABELS, txt_file)

        if os.path.exists(txtfile_source):
            os.makedirs(os.path.dirname(txtfile_dest), exist_ok=True)
            shutil.copyfile(txtfile_source, txtfile_dest)

print("\nData preparation completed!")