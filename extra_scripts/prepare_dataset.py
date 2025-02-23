import glob
import os
import random
from math import floor
from tqdm import tqdm
import shutil

input_folders = [
    'dataset/abrams/jpg_images',
    'dataset/btr-80/jpg_images',
    'dataset/destroyed_tank/jpg_images',
    # 'dataset/leopard/images',
    # 'dataset/btr-striker/images',
    # 'dataset/T-90/images'
]

BASE_DIR_ABSOLUTE = "/"
OUT_DIR = '/dataset_prepared'

OUT_IMAGES = os.path.join(OUT_DIR, 'images')
OUT_LABELS = os.path.join(OUT_DIR, 'labels')

OUT_TRAIN_IMAGES = os.path.join(OUT_IMAGES, 'train')
OUT_VAL_IMAGES = os.path.join(OUT_IMAGES, 'val')
OUT_TEST_IMAGES = os.path.join(OUT_IMAGES, 'test')
OUT_TRAIN_LABELS = os.path.join(OUT_LABELS, 'train')
OUT_VAL_LABELS = os.path.join(OUT_LABELS, 'val')
OUT_TEST_LABELS = os.path.join(OUT_LABELS, 'test')

coeff = [80, 10, 10]  # Распределение train/val/test
exceptions = ['classes']

if sum(coeff) != 100:
    print("Coefficients must sum up to 100%.")
    exit(1)

print(f"Preparing images data by {coeff[0]}/{coeff[1]}/{coeff[2]} rule.")
print(f"Source folders: {len(input_folders)}")
print("Gathering data ...")

source = {}
for sf in input_folders:
    source.setdefault(sf, [])

    os.chdir(BASE_DIR_ABSOLUTE)
    os.chdir(sf)

    for filename in glob.glob("*.*"):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            source[sf].append(filename)

train = {}
val = {}
test = {}
for sk, sv in source.items():
    random.shuffle(sv)  # Перемешиваем данные
    total_images = len(sv)
    train_split = floor(total_images * (coeff[0] / 100))  # 80% для train
    val_split = train_split + floor(total_images * (coeff[1] / 100))  # 10% для val

    train.setdefault(sk, [])
    val.setdefault(sk, [])
    test.setdefault(sk, [])
    train[sk] = sv[:train_split]  # Первые 80% для тренировки
    val[sk] = sv[train_split:val_split]  # Следующие 10% для валидации
    test[sk] = sv[val_split:]  # Остальные 10% для тестирования

    print(f"Folder: {sk}")
    print(f"Total images: {len(sv)}")
    print(f"Train images: {len(train[sk])}")
    print(f"Val images: {len(val[sk])}")
    print(f"Test images: {len(test[sk])}")

train_sum = 0
val_sum = 0
test_sum = 0

for sk, sv in train.items():
    train_sum += len(sv)

for sk, sv in val.items():
    val_sum += len(sv)

for sk, sv in test.items():
    test_sum += len(sv)

print(f"\nOverall TRAIN images count: {train_sum}")
print(f"Overall VAL images count: {val_sum}")
print(f"Overall TEST images count: {test_sum}")

os.chdir(BASE_DIR_ABSOLUTE)
print("\nCopying TRAIN source items to prepared folder ...")
for sk, sv in tqdm(train.items()):
    for item in tqdm(sv):
        imgfile_source = os.path.join(BASE_DIR_ABSOLUTE, sk, item)
        imgfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_TRAIN_IMAGES, f"{os.path.basename(sk)}_{item}")

        txt_file = os.path.splitext(item)[0] + '.txt'
        txtfile_source = os.path.join(BASE_DIR_ABSOLUTE, sk.replace('jpg_images', 'labels'), txt_file)

        if not os.path.exists(txtfile_source):
            print(f"Label file not found: {txtfile_source}")
            continue  # Пропускаем изображение, если нет файла с меткой

        os.makedirs(os.path.dirname(imgfile_dest), exist_ok=True)
        shutil.copyfile(imgfile_source, imgfile_dest)

        txtfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_TRAIN_LABELS, f"{os.path.basename(sk)}_{txt_file}")
        os.makedirs(os.path.dirname(txtfile_dest), exist_ok=True)
        shutil.copyfile(txtfile_source, txtfile_dest)

os.chdir(BASE_DIR_ABSOLUTE)
print("\nCopying VAL source items to prepared folder ...")
for sk, sv in tqdm(val.items()):
    for item in tqdm(sv):
        imgfile_source = os.path.join(BASE_DIR_ABSOLUTE, sk, item)
        imgfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_VAL_IMAGES, f"{os.path.basename(sk)}_{item}")

        txt_file = os.path.splitext(item)[0] + '.txt'
        txtfile_source = os.path.join(BASE_DIR_ABSOLUTE, sk.replace('jpg_images', 'labels'), txt_file)

        if not os.path.exists(txtfile_source):
            print(f"Label file not found: {txtfile_source}")
            continue  # Пропускаем изображение, если нет файла с меткой

        os.makedirs(os.path.dirname(imgfile_dest), exist_ok=True)
        shutil.copyfile(imgfile_source, imgfile_dest)

        txtfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_VAL_LABELS, f"{os.path.basename(sk)}_{txt_file}")
        os.makedirs(os.path.dirname(txtfile_dest), exist_ok=True)
        shutil.copyfile(txtfile_source, txtfile_dest)

os.chdir(BASE_DIR_ABSOLUTE)
print("\nCopying TEST source items to prepared folder ...")
for sk, sv in tqdm(test.items()):
    for item in tqdm(sv):
        imgfile_source = os.path.join(BASE_DIR_ABSOLUTE, sk, item)
        imgfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_TEST_IMAGES, f"{os.path.basename(sk)}_{item}")

        txt_file = os.path.splitext(item)[0] + '.txt'
        txtfile_source = os.path.join(BASE_DIR_ABSOLUTE, sk.replace('jpg_images', 'labels'), txt_file)

        if not os.path.exists(txtfile_source):
            print(f"Label file not found: {txtfile_source}")
            continue  # Пропускаем изображение, если нет файла с меткой

        os.makedirs(os.path.dirname(imgfile_dest), exist_ok=True)
        shutil.copyfile(imgfile_source, imgfile_dest)

        txtfile_dest = os.path.join(BASE_DIR_ABSOLUTE, OUT_TEST_LABELS, f"{os.path.basename(sk)}_{txt_file}")
        os.makedirs(os.path.dirname(txtfile_dest), exist_ok=True)
        shutil.copyfile(txtfile_source, txtfile_dest)

print("\nData preparation completed!")