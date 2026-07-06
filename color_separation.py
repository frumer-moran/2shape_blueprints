import cv2
import numpy as np
import os

def main():
    # Load the cropped floor plan
    img_path = "stitched_first_floor.jpg"
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: {img_path} not found.")
        return
        
    print(f"Loaded image: {img_path} ({img.shape[1]}x{img.shape[0]})")
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # ----------------------------------------
    # ----------------------------------------
    # 1. Red Mask (Unit 1) - wraps around 0 and 180
    # ----------------------------------------
    lower_red1 = np.array([0, 80, 130])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 80, 130])
    upper_red2 = np.array([180, 255, 255])
    
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    
    # ----------------------------------------
    # 2. Blue Mask (Unit 2) - Low saturation threshold due to orange paper background neutralizing blue ink
    # ----------------------------------------
    lower_blue = np.array([80, 15, 30])
    upper_blue = np.array([150, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # ----------------------------------------
    # Morphological cleaning
    # ----------------------------------------
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    
    # Close to bridge gaps in the wall lines, open to remove fine print/noise
    clean_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel, iterations=2)
    clean_red = cv2.morphologyEx(clean_red, cv2.MORPH_OPEN, kernel, iterations=1)
    
    clean_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel, iterations=2)
    clean_blue = cv2.morphologyEx(clean_blue, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # ----------------------------------------
    # Save isolated masks
    # ----------------------------------------
    os.makedirs("cache/color_masks", exist_ok=True)
    cv2.imwrite("cache/color_masks/mask_red.jpg", clean_red)
    cv2.imwrite("cache/color_masks/mask_blue.jpg", clean_blue)
    print("Saved color masks to cache/color_masks/")
    
    # ----------------------------------------
    # Draw contours over grayscale blueprint for validation
    # ----------------------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    verify_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    # Find contours
    contours_red_all, _ = cv2.findContours(clean_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue_all, _ = cv2.findContours(clean_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter by size to remove small noise
    contours_red = [c for c in contours_red_all if cv2.contourArea(c) > 20]
    contours_blue = [c for c in contours_blue_all if cv2.contourArea(c) > 20]
    
    print(f"Detected {len(contours_red)} red contour segments (>20px).")
    cv2.drawContours(verify_img, contours_red, -1, (0, 0, 255), 3) # Red lines
    
    print(f"Detected {len(contours_blue)} blue contour segments (>20px).")
    cv2.drawContours(verify_img, contours_blue, -1, (255, 0, 0), 3) # Blue lines
    
    # Save verification outputs
    cv2.imwrite("cache/color_masks/verify_walls.jpg", verify_img)
    small_verify = cv2.resize(verify_img, (1600, int(1600 * verify_img.shape[0] / verify_img.shape[1])))
    cv2.imwrite("cache/color_masks/verify_walls_small.jpg", small_verify)
    print("Saved verify_walls_small.jpg to cache/color_masks/")

if __name__ == "__main__":
    main()
