import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop around C260 (1553, 2444)
    x, y, r = 1553, 2444, 27
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c260.jpg", crop)
    print("Saved crop_c260.jpg")
    
    # Crop around C261 (1613, 2447)
    x, y, r = 1613, 2447, 27
    crop = img[y-100:y+100, x-100:x+100]
    cv2.circle(crop, (100, 100), r, (0, 0, 255), 2)
    cv2.imwrite("crop_c261.jpg", crop)
    print("Saved crop_c261.jpg")

if __name__ == "__main__":
    main()
