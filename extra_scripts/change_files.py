import os

directory_path = '/dataset/abrams/labels'

files = [f for f in os.listdir(directory_path) if
         os.path.isfile(os.path.join(directory_path, f)) and f.endswith('.txt')]

print(files)

for file_name in files:
    file_path = os.path.join(directory_path, file_name)

    with open(file_path, mode='r+') as f:
        lines = f.readlines()

        f.seek(0)

        f.truncate()

        for line in lines:
            if len(line) > 0:
                modified_line = '0' + line[1:]
                f.write(modified_line)
            else:
                f.write(line)