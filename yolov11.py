from ultralytics import YOLO

# Load a pretrained YOLO model
model = YOLO("yolo11l.pt")

# Perform object detection on an image
results = model(r"C:\Users\38384\Pictures\Screenshots\屏幕截图 2025-04-28 213107.png")

# Visualize the results
for result in results:
    result.show()