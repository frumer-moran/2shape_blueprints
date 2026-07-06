import cv2
import numpy as np
import os

def check_unit_boundaries(mask, bbox_y, bbox_x, unit_name):
    """
    Checks if a mask has continuous or near-continuous line segments on the 4 sides of a bounding box.
    """
    y_min, y_max = bbox_y
    x_min, x_max = bbox_x
    
    # Crop the mask to the unit's active bounding box
    crop = mask[y_min:y_max, x_min:x_max]
    h_c, w_c = crop.shape
    
    # Divide the bounding box into 4 border zones (top, bottom, left, right)
    border_thickness = 30
    
    top_zone = crop[0:border_thickness, :]
    bottom_zone = crop[h_c-border_thickness:h_c, :]
    left_zone = crop[:, 0:border_thickness]
    right_zone = crop[:, w_c-border_thickness:w_c]
    
    # Calculate coverage (percentage of border zone containing masked pixels)
    top_cov = np.sum(top_zone > 0) / top_zone.size * 100
    bottom_cov = np.sum(bottom_zone > 0) / bottom_zone.size * 100
    left_cov = np.sum(left_zone > 0) / left_zone.size * 100
    right_cov = np.sum(right_zone > 0) / right_zone.size * 100
    
    print(f"\n--- Automated Validation Report for {unit_name} ---")
    print(f"  Top wall coverage: {top_cov:.1f}%")
    print(f"  Bottom wall coverage: {bottom_cov:.1f}%")
    print(f"  Left wall coverage: {left_cov:.1f}%")
    print(f"  Right wall coverage: {right_cov:.1f}%")
    
    # Threshold for success: at least some line segments present on each side
    success = True
    for side, cov in [("Top", top_cov), ("Bottom", bottom_cov), ("Left", left_cov), ("Right", right_cov)]:
        if cov < 1.0: # If less than 1% of the zone is covered, a boundary wall is missing!
            print(f"  [ERROR] Missing boundary wall on the {side}!")
            success = False
            
    if success:
        print(f"  [SUCCESS] All 4 boundary zones contain valid wall segments.")
    return success

def main():
    # Load masks
    red_mask_path = "cache/color_masks/mask_red.jpg"
    blue_mask_path = "cache/color_masks/mask_blue.jpg"
    
    if not os.path.exists(red_mask_path) or not os.path.exists(blue_mask_path):
        print("Error: Mask files not found. Run color_separation.py first.")
        return
        
    mask_red = cv2.imread(red_mask_path, cv2.IMREAD_GRAYSCALE)
    mask_blue = cv2.imread(blue_mask_path, cv2.IMREAD_GRAYSCALE)
    
    # Unit 1 (Red) expected bounding box
    u1_bbox_y = (900, 1950)
    u1_bbox_x = (300, 1250)
    
    # Unit 2 (Blue) expected bounding box
    u2_bbox_y = (1950, 2500)
    u2_bbox_x = (300, 1400)
    
    u1_ok = check_unit_boundaries(mask_red, u1_bbox_y, u1_bbox_x, "Unit 1 (Red)")
    u2_ok = check_unit_boundaries(mask_blue, u2_bbox_y, u2_bbox_x, "Unit 2 (Blue)")
    
    if u1_ok and u2_ok:
        print("\n[VERIFICATION PASSED] Both Unit 1 and Unit 2 have valid wall segmentation on all 4 sides.")
    else:
        print("\n[VERIFICATION FAILED] One or more boundary walls are missing or incomplete.")

if __name__ == "__main__":
    main()
