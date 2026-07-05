import cv2
import json
import numpy as np
import os

def main():
    img = cv2.imread("p2_right.png")
    h, w = img.shape[:2]
    
    with open("cache/right_circles_coords.json", "r") as f:
        circles = json.load(f)
        
    print(f"Total circles to scan: {len(circles)}")
    
    # We will filter circles that contain handwritten strokes in the center
    candidates = []
    for c in circles:
        cx, cy, cr = c['x'], c['y'], c['r']
        
        # Crop central region (e.g. 30x30 pixels)
        pad = int(cr * 0.6)
        y0, y1 = max(0, cy - pad), min(h, cy + pad)
        x0, x1 = max(0, cx - pad), min(w, cx + pad)
        
        crop = img[y0:y1, x0:x1]
        if crop.size == 0:
            continue
            
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        # Count black/dark pixels (intensity < 180)
        dark_pixels = np.sum(gray < 180)
        
        # We also want to exclude very busy areas (like text stamps or borders) by ensuring
        # there is a clean layout around the circle
        if 15 < dark_pixels < 250: # perfect threshold for a single handwritten digit!
            c['dark_pixels'] = int(dark_pixels)
            candidates.append(c)
            
    print(f"Filtered to {len(candidates)} text-like circles.")
    
    # Create a grid image to view the candidates
    # We will display 8 candidates per row
    tile_size = 120
    cols = 8
    rows = (len(candidates) + cols - 1) // cols
    
    grid = np.ones((rows * tile_size, cols * tile_size, 3), dtype=np.uint8) * 255
    
    for i, c in enumerate(candidates):
        cx, cy, cr = c['x'], c['y'], c['r']
        
        # Crop 120x120 around circle
        y0 = max(0, cy - 60)
        y1 = min(h, cy + 60)
        x0 = max(0, cx - 60)
        x1 = min(w, cx + 60)
        
        tile = img[y0:y1, x0:x1].copy()
        # Pad tile to 120x120 if it was near borders
        th, tw = tile.shape[:2]
        if th < tile_size or tw < tile_size:
            tile = cv2.copyMakeBorder(tile, 0, tile_size - th, 0, tile_size - tw, cv2.BORDER_CONSTANT, value=[255, 255, 255])
            
        # Draw the label and pixel count on the tile
        cv2.putText(tile, f"{c['label']}", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(tile, f"x:{cx} y:{cy}", (5, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        r_idx = i // cols
        c_idx = i % cols
        grid[r_idx*tile_size:(r_idx+1)*tile_size, c_idx*tile_size:(c_idx+1)*tile_size] = tile
        
    cv2.imwrite("cache/candidate_circles_grid_right.jpg", grid)
    print("Saved grid to cache/candidate_circles_grid_right.jpg")

if __name__ == "__main__":
    main()
