import cv2
import json
import glob
import os

def main():
    # Find latest grounding cache
    cache_files = glob.glob("cache/grounding_*.json")
    if not cache_files:
        print("No grounding cache found!")
        return
    latest_file = max(cache_files, key=os.path.getmtime)
    print(f"Reading grounding from: {latest_file}")
    with open(latest_file, "r") as f:
        data = json.load(f)
        
    img_path = "stitched_first_floor.jpg"
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    
    # Create output directory for crops
    os.makedirs("debug_crops", exist_ok=True)
    
    for apt in data.get("apartments", []):
        num = apt.get("apartment_number")
        ymin, xmin, ymax, xmax = apt.get("label_box")
        
        # Convert normalized coordinates (0-1000) to actual pixel coordinates
        y0 = int(ymin * h / 1000)
        x0 = int(xmin * w / 1000)
        y1 = int(ymax * h / 1000)
        x1 = int(xmax * w / 1000)
        
        print(f"Unit {num}: Box pixels -> x: ({x0}, {x1}), y: ({y0}, {y1})")
        
        # Crop region with 150px padding to inspect context
        pad = 150
        cy0 = max(0, y0 - pad)
        cx0 = max(0, x0 - pad)
        cy1 = min(h, y1 + pad)
        cx1 = min(w, x1 + pad)
        
        crop = img[cy0:cy1, cx0:cx1].copy()
        
        # Draw the grounding box on the crop in bright red
        # Relative coordinates in the crop are offset by cx0, cy0
        rx0 = x0 - cx0
        ry0 = y0 - cy0
        rx1 = x1 - cx0
        ry1 = y1 - cy0
        
        cv2.rectangle(crop, (rx0, ry0), (rx1, ry1), (0, 0, 255), 3)
        cv2.putText(crop, f"Unit {num}", (rx0, ry0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        output_crop_path = f"debug_crops/unit_{num}.jpg"
        cv2.imwrite(output_crop_path, crop)
        print(f"Saved debug crop: {output_crop_path}")

if __name__ == "__main__":
    main()
