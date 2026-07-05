import cv2

def main():
    img = cv2.imread("p1_left.png")
    # Crop around C83 (152, 1675) with 200px padding
    x, y = 152, 1675
    crop = img[y-200:y+200, x-150:x+250]
    cv2.circle(crop, (150, 200), 40, (0, 0, 255), 3)
    cv2.imwrite("crop_c83.jpg", crop)
    print("Saved crop_c83.jpg")

if __name__ == "__main__":
    main()
