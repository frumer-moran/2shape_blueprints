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
    # Spatial Filtering (Bounding Boxes) to isolate left wing units
    # ----------------------------------------
    mask_r_lw = np.zeros_like(mask_red)
    mask_r_lw[800:2600, 300:1500] = mask_red[800:2600, 300:1500]

    mask_b_lw = np.zeros_like(mask_blue)
    mask_b_lw[800:2600, 300:1500] = mask_blue[800:2600, 300:1500]
    
    # ----------------------------------------
    # ----------------------------------------
    # Detect lines using Probabilistic Hough Transform
    # ----------------------------------------
    lines_u1 = cv2.HoughLinesP(mask_r_lw, rho=1, theta=np.pi/180, threshold=20, minLineLength=25, maxLineGap=40)
    lines_u2 = cv2.HoughLinesP(mask_b_lw, rho=1, theta=np.pi/180, threshold=20, minLineLength=25, maxLineGap=40)
    
    # ----------------------------------------
    # Draw Unit 1 lines over grayscale blueprint
    # ----------------------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_u1 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    if lines_u1 is not None:
        print(f"Detected {len(lines_u1)} red line segments for Unit 1.")
        for line in lines_u1:
            x1, y1, x2, y2 = line.ravel()
            cv2.line(img_u1, (x1, y1), (x2, y2), (0, 0, 255), 4) # Red lines
            
    # ----------------------------------------
    # Draw Unit 2 lines over grayscale blueprint
    # ----------------------------------------
    img_u2 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    if lines_u2 is not None:
        print(f"Detected {len(lines_u2)} blue line segments for Unit 2.")
        for line in lines_u2:
            x1, y1, x2, y2 = line.ravel()
            cv2.line(img_u2, (x1, y1), (x2, y2), (255, 0, 0), 4) # Blue lines
            
    # Save verification outputs
    os.makedirs("cache/color_masks", exist_ok=True)
    cv2.imwrite("cache/color_masks/verify_unit_1.jpg", img_u1)
    cv2.imwrite("cache/color_masks/verify_unit_2.jpg", img_u2)
    
    small_u1 = cv2.resize(img_u1, (1600, int(1600 * img_u1.shape[0] / img_u1.shape[1])))
    small_u2 = cv2.resize(img_u2, (1600, int(1600 * img_u2.shape[0] / img_u2.shape[1])))
    cv2.imwrite("cache/color_masks/verify_unit_1_small.jpg", small_u1)
    cv2.imwrite("cache/color_masks/verify_unit_2_small.jpg", small_u2)
    print("Saved verify_unit_1_small.jpg and verify_unit_2_small.jpg to cache/color_masks/")

if __name__ == "__main__":
    main()
