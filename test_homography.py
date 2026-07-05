import cv2
import numpy as np

def main():
    img_left = cv2.imread("p1_left.png")
    img_right = cv2.imread("p2_right.png")
    
    gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)
    
    sift = cv2.SIFT_create()
    kp_left, des_left = sift.detectAndCompute(gray_left, None)
    kp_right, des_right = sift.detectAndCompute(gray_right, None)
    
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des_right, des_left, k=2)
    
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
            
    pts_right = np.float32([kp_right[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    pts_left = np.float32([kp_left[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    
    H, mask = cv2.findHomography(pts_right, pts_left, cv2.RANSAC, 5.0)
    
    h_l, w_l = img_left.shape[:2]
    h_r, w_r = img_right.shape[:2]
    
    corners_right = np.float32([[0, 0], [0, h_r], [w_r, h_r], [w_r, 0]]).reshape(-1, 1, 2)
    warped_corners = cv2.perspectiveTransform(corners_right, H)
    
    all_corners = np.vstack((warped_corners, np.float32([[0, 0], [0, h_l], [w_l, h_l], [w_l, 0]]).reshape(-1, 1, 2)))
    [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
    
    tx, ty = -x_min, -y_min
    H_translation = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], dtype=np.float32)
    
    H_final = H_translation.dot(H)
    
    print("tx:", tx, "ty:", ty)
    print("H original column 2:", H[:, 2])
    print("H_final column 2:", H_final[:, 2])

if __name__ == "__main__":
    main()
