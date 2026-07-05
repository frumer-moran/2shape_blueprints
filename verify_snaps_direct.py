import cv2
import json
import os
import numpy as np

def main():
    # Load stitched image
    img = cv2.imread("stitched_first_floor.jpg")
    h_stitched, w_stitched = img.shape[:2]
    
    # Load transformation details
    with open("cache/stitch_transform.json", "r") as f:
        transform_data = json.load(f)
    tx = transform_data["tx"]
    ty = transform_data["ty"]
    H_arr = np.array(transform_data["H"])
    
    # Defined Hough Circle coordinates
    # Format: (unit_number, x_local, y_local, radius, color_bgr)
    left_coords = [
        # Unit 4: Gray
        (4, 1551, 1541, 35, (128, 128, 128)),
        # Unit 5: Orange
        (5, 1544, 2061, 35, (0, 165, 255)),
        # Unit 6: Brown (looks like b)
        (6, 3751, 2245, 32, (42, 42, 165))
    ]
    
    right_coords = [
        # Unit 1: Red
        (1, 3680, 2135, 34, (0, 0, 255)),
        # Unit 2: Blue
        (2, 3247, 1735, 32, (255, 0, 0)),
        # Unit 3: Green
        (3, 2295, 1753, 32, (0, 255, 0))
    ]
    
    # Map and draw Left Wing
    for unit, x_l, y_l, r, col in left_coords:
        sx = int(x_l + tx)
        sy = int(y_l + ty)
        cv2.circle(img, (sx, sy), r, col, 4)
        cv2.putText(img, f"U{unit}", (sx - 15, sy - r - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, col, 3)
        print(f"Drawing Left Wing Unit {unit} at stitched pixel ({sx}, {sy})")
        
    # Map and draw Right Wing
    for unit, x_r, y_r, r, col in right_coords:
        pt = np.array([x_r, y_r, 1.0])
        warped_pt = np.dot(H_arr, pt)
        sx = int(warped_pt[0] / warped_pt[2])
        sy = int(warped_pt[1] / warped_pt[2])
        
        # Calculate warped radius
        pt_r = np.array([x_r + r, y_r, 1.0])
        warped_pt_r = np.dot(H_arr, pt_r)
        sx_r = warped_pt_r[0] / warped_pt_r[2]
        sy_r = warped_pt_r[1] / warped_pt_r[2]
        r_warped = int(((sx_r - sx)**2 + (sy_r - sy)**2)**0.5)
        
        cv2.circle(img, (sx, sy), r_warped, col, 4)
        cv2.putText(img, f"U{unit}", (sx - 15, sy - r_warped - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, col, 3)
        print(f"Drawing Right Wing Unit {unit} at stitched pixel ({sx}, {sy})")
        
    cv2.imwrite("verify_final_grounding.jpg", img)
    print("Saved verify_final_grounding.jpg")
    
    # Save a small version for viewing
    small = cv2.resize(img, (1600, int(1600 * img.shape[0] / img.shape[1])))
    cv2.imwrite("verify_final_grounding_small.jpg", small)
    print("Saved verify_final_grounding_small.jpg")

if __name__ == "__main__":
    main()
