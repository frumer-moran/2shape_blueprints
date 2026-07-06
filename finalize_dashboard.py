import cv2
import json
import glob
import os

def main():
    # Load original stitched image or fallback to already cropped version
    img = cv2.imread("stitched_first_floor.png")
    if img is not None:
        h_orig, w_orig = img.shape[:2]
        print(f"Original stitched shape: {w_orig}x{h_orig}")
        
        # Crop horizontally between the two inner white dots
        x_start = 1976
        x_end = 5796
        crop = img[:, x_start:x_end]
        
        # Save as stitched_first_floor.jpg
        cv2.imwrite("stitched_first_floor.jpg", crop)
        print("Saved stitched_first_floor.jpg")
    else:
        print("stitched_first_floor.png not found, loading stitched_first_floor.jpg directly...")
        crop = cv2.imread("stitched_first_floor.jpg")
        if crop is None:
            print("Error: neither stitched_first_floor.png nor stitched_first_floor.jpg found.")
            return
            
    # Crop dimensions
    h_c, w_c = crop.shape[:2]
    print(f"Canvas size: {w_c}x{h_c}")
    
    # Set coordinates in cropped pixels: (unit_number, x_center, y_center, radius, border_color)
    unit_coords = {
        "1": (886, 1698, 39, "אדום"),
        "2": (1250, 1890, 36, "כחול"),
        "3": (2242, 1920, 36, "ירוק"),
        "4": (2638, 1618, 39, "אפור"),
        "5": (2628, 2136, 36, "כתום"),
        "6": (886, 2072, 40, "חום")
    }
    
    mapped_apts = []
    
    # Normalize coordinates to 0-1000 for web overlay boxes
    for unit_num, (cx, cy, r, col) in unit_coords.items():
        px0 = cx - r
        py0 = cy - r
        px1 = cx + r
        py1 = cy + r
        
        # Convert to 0-1000 scale
        sy0 = int((py0 / h_c) * 1000)
        sx0 = int((px0 / w_c) * 1000)
        sy1 = int((py1 / h_c) * 1000)
        sx1 = int((px1 / w_c) * 1000)
        
        mapped_apts.append({
            "apartment_number": unit_num,
            "label_box": [sy0, sx0, sy1, sx1],
            "border_color": col,
            "remarks": f"דירה {unit_num} ממוקמת בקומה ראשונה."
        })
        
    merged_result = {"apartments": mapped_apts}
    
    # Overwrite all grounding caches in cache/ to prevent loading outdated coordinate sets
    os.makedirs("cache", exist_ok=True)
    with open("cache/grounding_fixed.json", "w") as f:
        json.dump(merged_result, f, indent=2, ensure_ascii=False)
        
    grounding_files = glob.glob("cache/grounding_*.json")
    for f_path in grounding_files:
        with open(f_path, "w") as f:
            json.dump(merged_result, f, indent=2, ensure_ascii=False)
    print("Updated all grounding cache files with approved coordinates.")
    
    # Draw verification images
    img_verify = crop.copy()
    for unit_num, (cx, cy, r, col) in unit_coords.items():
        color_bgr = (0, 0, 255) if col == "אדום" else (255, 0, 0) if col == "כחול" else (0, 255, 0) if col == "ירוק" else (128, 128, 128) if col == "אפור" else (0, 165, 255)
        cv2.circle(img_verify, (cx, cy), r, color_bgr, 4)
        cv2.putText(img_verify, f"U{unit_num}", (cx - 15, cy - r - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_bgr, 3)
        
    cv2.imwrite("verify_final_grounding.jpg", img_verify)
    small = cv2.resize(img_verify, (1600, int(1600 * img_verify.shape[0] / img_verify.shape[1])))
    cv2.imwrite("verify_final_grounding_small.jpg", small)
    print("Saved verify_final_grounding_small.jpg")

if __name__ == "__main__":
    main()
