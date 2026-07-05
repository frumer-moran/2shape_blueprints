import os
import cv2
import numpy as np
import fitz  # PyMuPDF

def render_page_crops(pdf_path, dpi=200):
    """
    Renders:
    1. The left 35% of Page 1 (containing the left wing of the first floor plan).
    2. The right 35% of Page 2 (containing the right wing of the first floor plan).
    """
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    # Page 1
    page1 = doc.load_page(0)
    w1 = page1.rect.x1
    h1 = page1.rect.y1
    
    # Left crop of Page 1 (0% to 25% of width)
    rect1 = fitz.Rect(0, 0, w1 * 0.25, h1)
    print(f"Rendering Left crop of Page 1 (width: {w1*0.25:.1f}, height: {h1:.1f}) at {dpi} DPI...")
    pix1 = page1.get_pixmap(clip=rect1, dpi=dpi)
    img1_path = "p1_left.png"
    pix1.save(img1_path)
    
    # Page 2
    page2 = doc.load_page(1)
    w2 = page2.rect.x1
    h2 = page2.rect.y1
    
    # Right crop of Page 2 (71% to 100% of width)
    rect2 = fitz.Rect(w2 * 0.71, 0, w2, h2)
    print(f"Rendering Right crop of Page 2 (width: {w2*0.29:.1f}, height: {h2:.1f}) at {dpi} DPI...")
    pix2 = page2.get_pixmap(clip=rect2, dpi=dpi)
    img2_path = "p2_right.png"
    pix2.save(img2_path)
    
    doc.close()
    return img1_path, img2_path

def stitch_images(img1_path, img2_path, output_path="stitched_first_floor.jpg"):
    """
    Stitches img1 (left) and img2 (right) using SIFT feature matching and Homography warping.
    """
    print(f"Loading images for stitching:\n  Left: {img1_path}\n  Right: {img2_path}")
    img_left = cv2.imread(img1_path)
    img_right = cv2.imread(img2_path)
    
    if img_left is None or img_right is None:
        print("Error: Could not load rendered images.")
        return False
        
    # Convert to grayscale
    gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)
    
    # Initialize SIFT detector
    print("Detecting SIFT keypoints...")
    sift = cv2.SIFT_create()
    kp_left, des_left = sift.detectAndCompute(gray_left, None)
    kp_right, des_right = sift.detectAndCompute(gray_right, None)
    
    print(f"Keypoints detected:\n  Left: {len(kp_left)}\n  Right: {len(kp_right)}")
    
    if des_left is None or des_right is None:
        print("Error: Could not extract feature descriptors.")
        return False
        
    # Feature matching using Brute-Force Matcher with KNN
    print("Matching features...")
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des_right, des_left, k=2)  # Match right to left
    
    # Apply Lowe's ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
            
    print(f"Good matches found: {len(good_matches)}")
    
    # Draw matches and save for manual inspection
    matches_img_path = "sift_matches.png"
    print(f"Saving match visualization to {matches_img_path}...")
    img_matches = cv2.drawMatches(img_right, kp_right, img_left, kp_left, good_matches[:50], None, 
                                  flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imwrite(matches_img_path, img_matches)
    
    if len(good_matches) < 4:
        print("Error: Not enough keypoint matches to calculate homography (minimum 4 required).")
        return False
        
    # Extract locations of matched keypoints
    pts_right = np.float32([kp_right[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    pts_left = np.float32([kp_left[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    
    # Find Homography matrix
    print("Calculating Homography matrix using RANSAC...")
    H, mask = cv2.findHomography(pts_right, pts_left, cv2.RANSAC, 5.0)
    
    if H is None:
        print("Error: Homography calculation failed.")
        return False
        
    # Warp image_right to align with image_left
    print("Warping right image and blending...")
    h_l, w_l = img_left.shape[:2]
    h_r, w_r = img_right.shape[:2]
    
    # Calculate dimensions of the output stitched canvas
    # Warp the corners of the right image to estimate output width
    corners_right = np.float32([[0, 0], [0, h_r], [w_r, h_r], [w_r, 0]]).reshape(-1, 1, 2)
    warped_corners = cv2.perspectiveTransform(corners_right, H)
    
    # Find bounding box of warped corners + left image
    all_corners = np.vstack((warped_corners, np.float32([[0, 0], [0, h_l], [w_l, h_l], [w_l, 0]]).reshape(-1, 1, 2)))
    [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
    [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)
    
    # Translate mapping so all pixels are in positive space
    translation_dist = [-x_min, -y_min]
    H_translation = np.array([[1, 0, translation_dist[0]], [0, 1, translation_dist[1]], [0, 0, 1]], dtype=np.float32)
    
    # Perform translation-warp
    stitched_w = x_max - x_min
    stitched_h = y_max - y_min
    
    img_warped = cv2.warpPerspective(img_right, H_translation.dot(H), (stitched_w, stitched_h))
    
    # Copy left image into its translated position on the stitched canvas
    # The left image starts at (translation_dist[0], translation_dist[1])
    tx, ty = translation_dist[0], translation_dist[1]
    
    # Use blending or simple overlay. For blueprint lines, a simple pixel overlay is often cleanest:
    # Fill in the warped right image, then overlay the left image
    stitched_canvas = img_warped.copy()
    
    # Create mask of the left image to blend cleanly
    left_mask = np.zeros((h_l, w_l), dtype=np.uint8)
    left_mask.fill(255)
    warped_left_mask = cv2.warpPerspective(left_mask, H_translation, (stitched_w, stitched_h))
    
    # Overwrite pixels of the left image onto the canvas
    # We can do this directly where warped_left_mask is active
    indices = np.where(warped_left_mask > 0)
    
    # Crop the target area of the canvas matching the left image
    stitched_canvas[ty:ty+h_l, tx:tx+w_l] = img_left
    
    # Save the homography transformation details for grounding projection
    import json
    transform_data = {
        "tx": int(tx),
        "ty": int(ty),
        "H": H_translation.dot(H).tolist()
    }
    os.makedirs("cache", exist_ok=True)
    with open("cache/stitch_transform.json", "w") as f:
        json.dump(transform_data, f, indent=2)
    print("Saved transform matrix to cache/stitch_transform.json")
    
    # Save the output
    print(f"Saving final stitched image to {output_path}...")
    from PIL import Image
    # Convert OpenCV BGR to RGB
    rgb_canvas = cv2.cvtColor(stitched_canvas, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb_canvas)
    img.save(output_path, "JPEG", quality=80, optimize=True)
    print("Stitching complete!")
    return True

def main():
    pdf_path = "ostrovsky_31.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return
        
    img1, img2 = render_page_crops(pdf_path)
    success = stitch_images(img1, img2)
    if success:
        print("\nPOC Option A Succeeded!")
        print("Check the results:")
        print("  - sift_matches.png: Keypoint matching visualization.")
        print("  - stitched_first_floor.jpg: Stitched floor plan drawing.")
    else:
        print("\nPOC Option A Failed.")

if __name__ == "__main__":
    main()
