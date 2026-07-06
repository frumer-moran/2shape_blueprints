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
    mask_r_lw[800:1950, 300:1250] = mask_red[800:1950, 300:1250]

    # Combine Red and Blue masks inside Unit 2's bounding box to capture all its walls (since outer/shared walls are red)
    mask_b_lw = np.zeros_like(mask_blue)
    mask_b_lw[1935:2500, 300:1400] = cv2.bitwise_or(mask_red[1935:2500, 300:1400], mask_blue[1935:2500, 300:1400])
    
    # ----------------------------------------
    # ----------------------------------------
    # ----------------------------------------
    # Detect lines using Probabilistic Hough Transform
    # ----------------------------------------
    lines_u1 = cv2.HoughLinesP(mask_r_lw, rho=1, theta=np.pi/180, threshold=20, minLineLength=25, maxLineGap=40)
    lines_u2 = cv2.HoughLinesP(mask_b_lw, rho=1, theta=np.pi/180, threshold=20, minLineLength=25, maxLineGap=40)
    
    # Grid helper
    def draw_grid(img_canvas, step=100):
        h_c, w_c = img_canvas.shape[:2]
        # Vertical lines
        for x in range(0, w_c, step):
            cv2.line(img_canvas, (x, 0), (x, h_c), (220, 220, 220), 1)
            if x % 200 == 0:
                cv2.putText(img_canvas, str(x), (x + 5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120, 120, 120), 2)
                cv2.putText(img_canvas, str(x), (x + 5, h_c - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120, 120, 120), 2)
        # Horizontal lines
        for y in range(0, h_c, step):
            cv2.line(img_canvas, (0, y), (w_c, y), (220, 220, 220), 1)
            if y % 200 == 0:
                cv2.putText(img_canvas, str(y), (15, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120, 120, 120), 2)
                cv2.putText(img_canvas, str(y), (w_c - 90, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120, 120, 120), 2)

    # Line drawing helper
    def draw_labeled_lines(img_canvas, lines, label_prefix, color):
        line_list = []
        if lines is not None:
            for idx, line in enumerate(lines):
                x1, y1, x2, y2 = line.ravel()
                cv2.line(img_canvas, (x1, y1), (x2, y2), color, 4)
                # Draw label at midpoint
                mx = int((x1 + x2) / 2)
                my = int((y1 + y2) / 2)
                label = f"{label_prefix}{idx+1}"
                cv2.putText(img_canvas, label, (mx, my), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                cv2.putText(img_canvas, label, (mx, my), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                line_list.append((label, x1, y1, x2, y2))
        return line_list

    # ----------------------------------------
    # Draw Unit 1 lines over grayscale blueprint with grid
    # ----------------------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_u1 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    draw_grid(img_u1)
    lines_u1_list = draw_labeled_lines(img_u1, lines_u1, "R", (0, 0, 255))
            
    # ----------------------------------------
    # Draw Unit 2 lines over grayscale blueprint with grid
    # ----------------------------------------
    img_u2 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    draw_grid(img_u2)
    lines_u2_list = draw_labeled_lines(img_u2, lines_u2, "B", (255, 0, 0))
            
    # Save verification outputs
    os.makedirs("cache/color_masks", exist_ok=True)
    cv2.imwrite("cache/color_masks/verify_unit_1.jpg", img_u1)
    cv2.imwrite("cache/color_masks/verify_unit_2.jpg", img_u2)
    
    small_u1 = cv2.resize(img_u1, (1600, int(1600 * img_u1.shape[0] / img_u1.shape[1])))
    small_u2 = cv2.resize(img_u2, (1600, int(1600 * img_u2.shape[0] / img_u2.shape[1])))
    cv2.imwrite("cache/color_masks/verify_unit_1_small.jpg", small_u1)
    cv2.imwrite("cache/color_masks/verify_unit_2_small.jpg", small_u2)
    print("Saved verify_unit_1_small.jpg and verify_unit_2_small.jpg to cache/color_masks/")

    # ----------------------------------------
    # Write coordinates index to a Markdown file in artifacts
    # ----------------------------------------
    md_path = "/Users/moranfrumer/.gemini/antigravity/brain/2c07984b-8d84-46bb-9538-692e9bbaabad/detected_walls.md"
    with open(md_path, "w") as f:
        f.write("# Labeled Detected Wall Segments\n\n")
        f.write("Use this coordinate table to refer to specific lines on the verification grids.\n\n")
        
        f.write("## Unit 1 (Red Wall Outlines)\n")
        f.write("| Line ID | Start (X, Y) | End (X, Y) |\n")
        f.write("| --- | --- | --- |\n")
        for label, x1, y1, x2, y2 in lines_u1_list:
            f.write(f"| {label} | ({x1}, {y1}) | ({x2}, {y2}) |\n")
            
        f.write("\n## Unit 2 (Blue Wall Outlines)\n")
        f.write("| Line ID | Start (X, Y) | End (X, Y) |\n")
        f.write("| --- | --- | --- |\n")
        for label, x1, y1, x2, y2 in lines_u2_list:
            f.write(f"| {label} | ({x1}, {y1}) | ({x2}, {y2}) |\n")
            
    print(f"Saved coordinate table to: {md_path}")

if __name__ == "__main__":
    main()
