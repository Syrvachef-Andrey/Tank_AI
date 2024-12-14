from ultralytics import settings

print(settings)
print()
print()

settings.update({"runs_dir": "/home/andrey/tank_AI/Tank_AI/runs", "datasets_dir": "/home/andrey/tank_AI/Tank_AI/dataset", "weights_dir": "/home/andrey/tank_AI/Tank_AI/weights"})

print(settings)