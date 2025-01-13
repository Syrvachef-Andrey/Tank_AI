from ultralytics import settings

print(settings)
print()
print()

settings.update({"datasets_dir": "/home/andrey/PycharmProjects/Tank_AI/dataset"})

print(settings)