import cv2
import numpy as np
import os
import json

def detect_and_label_circles(img_path, output_path):
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not load {img_path}")
        return []
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Hough Circles Transform tuned for unit circles
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=40,
        param1=50,
        param2=28, # slightly more sensitive to find all circles
        minRadius=15,
        maxRadius=45
    )
    
    detected_list = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        
        # Sort circles top-to-bottom, then left-to-right to make labeling structured
        circles = sorted(circles, key=lambda c: (c[1] // 50, c[0]))
        
        output_img = img.copy()
        idx = 1
        for (x, y, r) in circles:
            # Check if this circle overlaps significantly with an already added one
            is_duplicate = False
            for prev in detected_list:
                dist = np.sqrt((x - prev['x'])**2 + (y - prev['y'])**2)
                if dist < 20: # too close, duplicate
                    is_duplicate = True
                    break
            if is_duplicate:
                continue
                
            circle_label = f"C{idx}"
            detected_list.append({
                'label': circle_label,
                'x': int(x),
                'y': int(y),
                'r': int(r)
            })
            
            # Draw green circle
            cv2.circle(output_img, (x, y), r, (0, 220, 0), 2)
            # Draw orange center dot
            cv2.circle(output_img, (x, y), 3, (0, 100, 255), -1)
            # Draw text label in high-contrast red with white outline
            text = circle_label
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 2
            
            # Draw white background outline for text readability
            cv2.putText(output_img, text, (x + r + 5, y + 5), font, font_scale, (255, 255, 255), thickness + 2)
            cv2.putText(output_img, text, (x + r + 5, y + 5), font, font_scale, (0, 0, 255), thickness)
            
            idx += 1
            
        cv2.imwrite(output_path, output_img)
        print(f"Labeled image saved to {output_path}. Detected {len(detected_list)} unique circles.")
    else:
        print(f"No circles found in {img_path}")
        
    return detected_list

def main():
    os.makedirs("cache", exist_ok=True)
    
    # Label Page 1 Left Wing (Units 4, 5, 6)
    left_circles = detect_and_label_circles("p1_left.png", "cache/p1_left_labeled.png")
    with open("cache/left_circles_coords.json", "w") as f:
        json.dump(left_circles, f, indent=2)
        
    # Label Page 2 Right Wing (Units 1, 2, 3)
    right_circles = detect_and_label_circles("p2_right.png", "cache/p2_right_labeled.png")
    with open("cache/right_circles_coords.json", "w") as f:
        json.dump(right_circles, f, indent=2)

if __name__ == "__main__":
    main()
