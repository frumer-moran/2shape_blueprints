import json
import numpy as np

def main():
    # Load detected circles for Left Wing
    with open("cache/left_circles_coords.json", "r") as f:
        left_circles = json.load(f)
        
    # Load detected circles for Right Wing
    with open("cache/right_circles_coords.json", "r") as f:
        right_circles = json.load(f)
        
    # Expected approximate coordinates in pixels (on stitched canvas):
    # Left Wing (x: 0 to 3792)
    # Unit 4: (1552, 1541)
    # Unit 5: (1544, 2059)
    # Unit 6: (2261, 2498) -> let's find closest circle in Left Wing
    
    print("--- Left Wing Circles Near Expected Locations ---")
    for name, target_x, target_y in [("Unit 4", 1552, 1541), ("Unit 5", 1544, 2059), ("Unit 6", 2261, 2498)]:
        # Left circles are relative to p1_left.png (x_stitched = x_left)
        closest = None
        min_dist = float('inf')
        for c in left_circles:
            dist = np.sqrt((c['x'] - target_x)**2 + (c['y'] - target_y)**2)
            if dist < min_dist:
                min_dist = dist
                closest = c
        if closest:
            print(f"{name} Target ({target_x}, {target_y}) -> Closest: {closest['label']} at ({closest['x']}, {closest['y']}) radius {closest['r']}, Distance: {min_dist:.1f}px")
            
    # Right Wing (x: x_offset to 6702)
    # x_offset_right = 6702 - 3286 = 3416
    # Unit 1: (5003, 1660)
    # Unit 2: (5359, 1847)
    # Unit 3: (5773, 2191)
    
    print("\n--- Right Wing Circles Near Expected Locations ---")
    for name, target_x, target_y in [("Unit 1", 5003, 1660), ("Unit 2", 5359, 1847), ("Unit 3", 5773, 2191)]:
        # Right circles are relative to p2_right.png (x_stitched = x_right + 3416)
        closest = None
        min_dist = float('inf')
        for c in right_circles:
            c_stitched_x = c['x'] + 3416
            dist = np.sqrt((c_stitched_x - target_x)**2 + (c['y'] - target_y)**2)
            if dist < min_dist:
                min_dist = dist
                closest = c
        if closest:
            print(f"{name} Target ({target_x}, {target_y}) -> Closest: {closest['label']} at ({closest['x'] + 3416}, {closest['y']}) radius {closest['r']}, Distance: {min_dist:.1f}px")

if __name__ == "__main__":
    main()
