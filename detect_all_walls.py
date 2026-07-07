import cv2
import numpy as np
import os

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

def main():
    img_path = "stitched_first_floor.jpg"
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: {img_path} not found.")
        return
        
    print(f"Loaded image: {img_path} ({img.shape[1]}x{img.shape[0]})")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # ----------------------------------------
    # Run Line Segment Detector (LSD)
    # ----------------------------------------
    lsd = cv2.createLineSegmentDetector(0)
    lines, width, prec, nfa = lsd.detect(gray)
    if lines is None:
        print("Error: No lines detected by LSD.")
        return
        
    print(f"LSD detected {len(lines)} raw line segments.")
    
    # ----------------------------------------
    # Filter and calculate line geometry parameters
    # ----------------------------------------
    filtered_lines = []
    for line in lines:
        x1, y1, x2, y2 = line
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx*dx + dy*dy)
        if length < 25: # filter out small noise / text strokes
            continue
            
        u = np.array([dx / length, dy / length])
        n = np.array([-u[1], u[0]])
        theta = np.arctan2(u[1], u[0]) % np.pi
        
        filtered_lines.append({
            'pts': (x1, y1, x2, y2),
            'p1': np.array([x1, y1]),
            'q1': np.array([x2, y2]),
            'u': u,
            'n': n,
            'theta': theta,
            'length': length
        })
        
    print(f"Filtered to {len(filtered_lines)} segments (length >= 25).")
    
    # ----------------------------------------
    # Find closest parallel pairs (Wall thickness constraint)
    # ----------------------------------------
    n_lines = len(filtered_lines)
    best_partner = {} # maps line_idx -> (partner_idx, distance)
    
    for i in range(n_lines):
        li = filtered_lines[i]
        min_dist = float('inf')
        min_idx = -1
        for j in range(n_lines):
            if i == j:
                continue
            lj = filtered_lines[j]
            
            # 1. Parallel check (angle difference < ~4.5 degrees)
            diff_theta = abs(li['theta'] - lj['theta'])
            diff_theta = min(diff_theta, np.pi - diff_theta)
            if diff_theta > 0.08:
                continue
                
            # 2. Perpendicular distance check (5 to 18 pixels wall thickness range)
            p_diff = lj['p1'] - li['p1']
            dist = abs(np.dot(p_diff, li['n']))
            if not (5.0 <= dist <= 18):
                continue
                
            # 3. Overlap check along the line direction
            proj_p2 = np.dot(lj['p1'] - li['p1'], li['u'])
            proj_q2 = np.dot(lj['q1'] - li['p1'], li['u'])
            
            start1, end1 = 0.0, li['length']
            start2, end2 = min(proj_p2, proj_q2), max(proj_p2, proj_q2)
            
            overlap_start = max(start1, start2)
            overlap_end = min(end1, end2)
            overlap_len = overlap_end - overlap_start
            
            if overlap_len > 15: # Significant overlap required
                # Overlap ratio check to filter out noise lines (e.g., short folds/dimensions matching long walls)
                max_len = max(li['length'], lj['length'])
                if (overlap_len / max_len) > 0.4:
                    if dist < min_dist:
                        min_dist = dist
                        min_idx = j
                    
        if min_idx != -1:
            best_partner[i] = (min_idx, min_dist)
            
    # Enforce mutual pairing (i's best partner is j, and j's best partner is i)
    seen_pairs = set()
    for i, (j, dist) in best_partner.items():
        if j in best_partner and best_partner[j][0] == i:
            pair_key = tuple(sorted([i, j]))
            seen_pairs.add(pair_key)
            
    print(f"Found {len(seen_pairs)} mutual parallel line pairs representing walls.")
    
    # ----------------------------------------
    # Render detected walls with coordinate grid
    # ----------------------------------------
    canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    draw_grid(canvas)
    
    for i, j in seen_pairs:
        li = filtered_lines[i]
        lj = filtered_lines[j]
        
        x1, y1, x2, y2 = map(int, li['pts'])
        x3, y3, x4, y4 = map(int, lj['pts'])
        
        # Align line directions to prevent polygon self-crossing (hourglass shape)
        if np.dot(li['u'], lj['u']) < 0:
            x3, y3, x4, y4 = x4, y4, x3, y3
            
        # Draw the wall borders in yellow
        cv2.line(canvas, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.line(canvas, (x3, y3), (x4, y4), (0, 255, 255), 2)
        
        # Fill the wall thickness space
        poly = np.array([
            [x1, y1], [x2, y2], [x4, y4], [x3, y3]
        ], dtype=np.int32)
        cv2.fillPoly(canvas, [poly], (0, 255, 255))
        
    os.makedirs("cache/color_masks", exist_ok=True)
    cv2.imwrite("cache/color_masks/verify_all_walls.jpg", canvas)
    
    # Save a smaller preview image for verification
    small_canvas = cv2.resize(canvas, (1600, int(1600 * canvas.shape[0] / canvas.shape[1])))
    cv2.imwrite("cache/color_masks/verify_all_walls_small.jpg", small_canvas)
    print("Saved verify_all_walls_small.jpg to cache/color_masks/")

if __name__ == "__main__":
    main()
