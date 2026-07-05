import cv2
import numpy as np
import os
from PIL import Image

def stitch_fixed(img1_path, img2_path, output_path="stitched_first_floor.jpg", overlap_pct=0.08):
    print(f"Stitching fixed side-by-side: {img1_path} and {img2_path}")
    img_left = cv2.imread(img1_path)
    img_right = cv2.imread(img2_path)
    
    if img_left is None or img_right is None:
        print("Error: Could not load images.")
        return False
        
    h_l, w_l = img_left.shape[:2]
    h_r, w_r = img_right.shape[:2]
    
    # Ensure matching heights (resize right to match left height)
    if h_l != h_r:
        scale_factor = h_l / h_r
        img_right = cv2.resize(img_right, (int(w_r * scale_factor), h_l))
        h_r, w_r = img_right.shape[:2]
        
    overlap = int(w_l * overlap_pct)
    stitched_w = w_l + w_r - overlap
    stitched_h = h_l
    
    # Create white canvas
    stitched_canvas = np.ones((stitched_h, stitched_w, 3), dtype=np.uint8) * 255
    
    # Place right image (Right Wing) on the right side
    rx = w_l - overlap
    stitched_canvas[:, rx:rx+w_r] = img_right
    
    # Overlay left image (Left Wing) on the left side
    stitched_canvas[:, 0:w_l] = img_left
    
    # Save as compressed JPEG
    rgb_canvas = cv2.cvtColor(stitched_canvas, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb_canvas)
    img.save(output_path, "JPEG", quality=80, optimize=True)
    print(f"Successfully saved fixed stitched image to {output_path} (width: {stitched_w}, height: {stitched_h})")
    return True

def main():
    img1_path = "p1_left.png"
    img2_path = "p2_right.png"
    
    # We will test an overlap of 8% (which is standard for joining the stairwell lobby)
    success = stitch_fixed(img1_path, img2_path, overlap_pct=0.08)
    if success:
        print("Fixed stitch complete!")

if __name__ == "__main__":
    main()
